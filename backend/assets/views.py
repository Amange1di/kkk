from rest_framework import viewsets, permissions, filters, status
from rest_framework.response import Response
from rest_framework.decorators import action, api_view
from rest_framework.permissions import BasePermission
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.core.cache import cache
from django.utils import ip_address
from .models import Asset, TransferHistory, AssetType
from .serializers import AssetSerializer, TransferHistorySerializer, AssetTypeSerializer
from accounts.models import CustomUser
from locations.models import Location
from reports.models import AuditLog
import qrcode
import io
import base64
from datetime import datetime
import ipaddress


def is_internal_ip(ip_string):
    """Проверяет, является ли IP-адрес внутренним (частным)"""
    try:
        ip = ipaddress.ip_address(ip_string)
        # Частные IP-адреса: 10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16, localhost
        return ip.is_private
    except ValueError:
        return False


class InternalNetworkOnlyPermission(BasePermission):
    """Разрешает доступ только из внутренней сети (частные IP-адреса)"""
    def has_permission(self, request, view):
        client_ip = request.META.get('REMOTE_ADDR', '')
        # Убираем IPv6 префикс если есть
        if client_ip.startswith('::ffff:'):
            client_ip = client_ip[7:]
        return is_internal_ip(client_ip)


def log_audit_action(request, action, model_name=None, object_id=None, object_name=None, changes=None):
    """Функция для логирования действий в аудит"""
    if request.user and request.user.is_authenticated:
        try:
            AuditLog.objects.create(
                user=request.user,
                action=action,
                model_name=model_name or '',
                object_id=str(object_id) if object_id else '',
                object_name=object_name or '',
                changes=changes,
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
        except Exception:
            pass


class RBACPermission(permissions.BasePermission):
    """Role-Based Access Control Permission"""
    
    ROLE_PERMISSIONS = {
        'super_admin': {'read', 'create', 'update', 'delete', 'audit', 'export', 'scan'},
        'inventory_manager': {'read', 'create', 'update', 'delete', 'transfer', 'audit', 'export', 'scan'},
        'staff': {'read', 'report_damage', 'request_transfer', 'scan'},
        'auditor': {'read', 'scan'},
    }
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        role = getattr(request.user, 'role', 'staff')
        user_permissions = self.ROLE_PERMISSIONS.get(role, set())
        
        method = request.method
        action_name = getattr(view, 'action', 'list')
        
        if method in ['GET', 'HEAD', 'OPTIONS']:
            required = {'read', 'scan'}
        elif method == 'POST':
            if action_name in ['checkout', 'checkin']:
                required = {'transfer'}
            elif action_name == 'report_damage':
                required = {'report_damage'}
            elif action_name == 'request_transfer':
                required = {'request_transfer'}
            elif action_name == 'scan':
                required = {'scan'}
            else:
                required = {'create'}
        elif method in ['PUT', 'PATCH']:
            required = {'update'}
        elif method == 'DELETE':
            required = {'delete'}
        else:
            required = {'read'}
        
        return bool(user_permissions & required)
    
    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)


@api_view(['GET', 'POST'])
def public_asset_scan(request, asset_tag=None):
    """Публичный endpoint для просмотра информации об активе по asset_tag без авторизации"""
    if not asset_tag:
        asset_tag = request.query_params.get('asset_tag') or request.data.get('asset_tag')
    
    if not asset_tag:
        return Response(
            {'error': 'asset_tag is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        asset = Asset.objects.select_related('current_location', 'assigned_to', 'asset_type').get(asset_tag=asset_tag)
        
        try:
            AuditLog.objects.create(
                user=None,
                action='public_scan',
                model_name='Asset',
                object_id=str(asset.id),
                object_name=str(asset),
                changes={'scanned_via': 'public_qr'},
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
        except Exception:
            pass
        
        return Response({
            'found': True,
            'asset': {
                'id': asset.id,
                'asset_tag': asset.asset_tag,
                'name': asset.name,
                'description': asset.description,
                'asset_type': asset.asset_type.name if asset.asset_type else None,
                'status': asset.get_status_display(),
                'status_key': asset.status,
                'location': asset.current_location.name if asset.current_location else None,
                'assigned_to': f"{asset.assigned_to.first_name} {asset.assigned_to.last_name}".strip() if asset.assigned_to else None,
                'manufacturer': asset.manufacturer,
                'model': asset.model,
                'serial_number': asset.serial_number,
                'purchase_date': asset.purchase_date.isoformat() if asset.purchase_date else None,
                'purchase_price': str(asset.purchase_price) if asset.purchase_price else None,
                'currency': asset.currency,
            }
        })
        
    except Asset.DoesNotExist:
        return Response({
            'found': False,
            'message': 'Asset not found',
            'asset_tag': asset_tag
        }, status=status.HTTP_404_NOT_FOUND)


class AssetViewSet(viewsets.ModelViewSet):
    queryset = Asset.objects.all()
    serializer_class = AssetSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'asset_type', 'current_location', 'assigned_to', 'department']
    search_fields = ['asset_tag', 'name', 'serial_number', 'manufacturer', 'model']
    ordering_fields = ['created_at', 'purchase_date', 'purchase_price']

    def perform_create(self, serializer):
        instance = serializer.save(created_by=self.request.user)
        log_audit_action(self.request, 'create', 'Asset', instance.id, str(instance), {'asset_tag': instance.asset_tag})
    
    @action(detail=True, methods=['post'], permission_classes=[RBACPermission])
    def checkout(self, request, pk=None):
        """Выдача актива пользователю"""
        asset = self.get_object()
        user = request.user
        
        if user.role not in ['super_admin', 'inventory_manager']:
            return Response({'error': 'Only Inventory Manager can checkout assets'}, status=status.HTTP_403_FORBIDDEN)
        
        with transaction.atomic():
            old_assigned = asset.assigned_to
            asset.status = 'in_use'
            asset.assigned_to_id = request.data.get('assigned_to')
            asset.assigned_date = datetime.now().date()
            asset.save()
            
            TransferHistory.objects.create(
                asset=asset, transfer_type='checkout',
                from_location=asset.current_location, to_user=asset.assigned_to,
                reason=request.data.get('reason', 'Asset checkout'), performed_by=user
            )
        
        log_audit_action(request, 'checkout', 'Asset', asset.id, str(asset), {'assigned_to': asset.assigned_to_id, 'status': asset.status})
        return Response({'status': 'Asset checked out successfully'})
    
    @action(detail=True, methods=['post'], permission_classes=[RBACPermission])
    def checkin(self, request, pk=None):
        """Возврат актива"""
        asset = self.get_object()
        user = request.user
        
        if user.role not in ['super_admin', 'inventory_manager']:
            return Response({'error': 'Only Inventory Manager can checkin assets'}, status=status.HTTP_403_FORBIDDEN)
        
        with transaction.atomic():
            old_assigned = asset.assigned_to
            asset.status = 'available'
            asset.assigned_to = None
            asset.assigned_date = None
            asset.save()
            
            TransferHistory.objects.create(
                asset=asset, transfer_type='checkin',
                to_location=asset.current_location, from_user=old_assigned,
                reason=request.data.get('reason', 'Asset checkin'), performed_by=user
            )
        
        log_audit_action(request, 'checkin', 'Asset', asset.id, str(asset), {'assigned_to': None, 'status': 'available'})
        return Response({'status': 'Asset checked in successfully'})
    
    @action(detail=True, methods=['post'], permission_classes=[RBACPermission])
    def transfer(self, request, pk=None):
        """Перемещение актива"""
        asset = self.get_object()
        user = request.user
        
        if user.role not in ['super_admin', 'inventory_manager']:
            return Response({'error': 'Only Inventory Manager can transfer assets'}, status=status.HTTP_403_FORBIDDEN)
        
        to_location_id = request.data.get('to_location')
        to_user_id = request.data.get('to_user')
        
        with transaction.atomic():
            old_location = asset.current_location
            old_user = asset.assigned_to
            
            if to_location_id:
                asset.current_location_id = to_location_id
            if to_user_id:
                asset.assigned_to_id = to_user_id
                asset.status = 'in_use'
            asset.save()
            
            TransferHistory.objects.create(
                asset=asset, transfer_type='transfer',
                from_location=old_location, to_location_id=to_location_id,
                from_user=old_user, to_user_id=to_user_id,
                reason=request.data.get('reason', 'Asset transfer'), performed_by=user
            )
        
        log_audit_action(request, 'transfer', 'Asset', asset.id, str(asset), {
            'from_location': old_location.id if old_location else None,
            'to_location': to_location_id,
            'from_user': old_user.id if old_user else None,
            'to_user': to_user_id
        })
        return Response({'status': 'Asset transferred successfully'})
    
    @action(detail=True, methods=['post'], permission_classes=[RBACPermission])
    def report_damage(self, request, pk=None):
        """Сообщить о повреждении"""
        asset = self.get_object()
        old_status = asset.status
        asset.status = 'in_repair'
        asset.save()
        
        TransferHistory.objects.create(
            asset=asset, transfer_type='maintenance',
            reason=request.data.get('description', 'Damage reported'), performed_by=request.user
        )
        
        log_audit_action(request, 'report_damage', 'Asset', asset.id, str(asset), {'status': {'old': old_status, 'new': 'in_repair'}})
        return Response({'status': 'Damage reported successfully'})
    
    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def qr_code(self, request, pk=None):
        """Генерация QR-кода для актива"""
        asset = self.get_object()
        log_audit_action(request, 'scan', 'Asset', asset.id, str(asset))
        
        qr_url = f"{request.scheme}://{request.get_host()}/api/assets/public/?asset_tag={asset.asset_tag}"
        
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(qr_url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        img_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        return Response({'asset_tag': asset.asset_tag, 'qr_code': f'data:image/png;base64,{img_base64}', 'url': qr_url})
    
    @action(detail=False, methods=['post'], permission_classes=[InternalNetworkOnlyPermission])
    def scan(self, request):
        """Сканирование QR-кода актива по asset_tag (доступ только из внутренней сети)"""
        asset_tag = request.data.get('asset_tag')
        
        if not asset_tag:
            return Response({'error': 'asset_tag is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            asset = Asset.objects.select_related('current_location', 'assigned_to', 'asset_type').get(asset_tag=asset_tag)
            
            try:
                AuditLog.objects.create(
                    user=None, action='public_scan', model_name='Asset',
                    object_id=str(asset.id), object_name=str(asset),
                    changes={'scanned_via': 'public_qr'},
                    ip_address=request.META.get('REMOTE_ADDR'),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')
                )
            except Exception:
                pass
            
            return Response({
                'found': True,
                'asset': {
                    'id': asset.id, 'asset_tag': asset.asset_tag, 'name': asset.name,
                    'description': asset.description,
                    'asset_type': asset.asset_type.name if asset.asset_type else None,
                    'status': asset.get_status_display(), 'status_key': asset.status,
                    'location': asset.current_location.name if asset.current_location else None,
                    'assigned_to': f"{asset.assigned_to.first_name} {asset.assigned_to.last_name}".strip() if asset.assigned_to else None,
                    'manufacturer': asset.manufacturer, 'model': asset.model,
                    'serial_number': asset.serial_number,
                    'purchase_date': asset.purchase_date.isoformat() if asset.purchase_date else None,
                    'purchase_price': str(asset.purchase_price) if asset.purchase_price else None,
                    'currency': asset.currency,
                }
            })
        except Asset.DoesNotExist:
            return Response({'found': False, 'message': 'Asset not found', 'asset_tag': asset_tag}, status=status.HTTP_404_NOT_FOUND)


class TransferHistoryViewSet(viewsets.ModelViewSet):
    queryset = TransferHistory.objects.all()
    serializer_class = TransferHistorySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['asset', 'transfer_type', 'from_location', 'to_location', 'from_user', 'to_user']
    search_fields = ['asset__asset_tag', 'asset__name', 'notes']
    ordering_fields = ['transfer_date']

    def perform_create(self, serializer):
        serializer.save(performed_by=self.request.user)
        log_audit_action(self.request, 'transfer', 'TransferHistory', serializer.instance.id if serializer.instance else None, str(serializer.instance) if serializer.instance else '')


class AssetTypeViewSet(viewsets.ModelViewSet):
    """ViewSet для управления типами активов"""
    queryset = AssetType.objects.all().order_by('name')
    serializer_class = AssetTypeSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['name', 'created_at']

    def perform_create(self, serializer):
        serializer.save()
        log_audit_action(self.request, 'create', 'AssetType', serializer.instance.id, str(serializer.instance), {'name': serializer.instance.name, 'code': serializer.instance.code})

    def perform_update(self, serializer):
        old_instance = self.get_object()
        serializer.save()
        log_audit_action(self.request, 'update', 'AssetType', old_instance.id, str(old_instance), {'name': {'old': old_instance.name, 'new': serializer.instance.name}})

    def perform_destroy(self, instance):
        log_audit_action(self.request, 'delete', 'AssetType', instance.id, str(instance), {'name': instance.name})
        instance.delete()
