from rest_framework import viewsets, permissions, filters, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from django.http import FileResponse, HttpResponse
from django.db.models import Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
from .models import AuditLog, ExportLog
from accounts.models import CustomUser
from assets.models import Asset, TransferHistory
from locations.models import Location
import csv
import io

try:
    from openpyxl import Workbook
    OPENPYXL_AVAILABLE = True
except ImportError:
    OPENPYXL_AVAILABLE = False

try:
    from xhtml2pdf import pisa
    XHTML2PDF_AVAILABLE = True
except ImportError:
    XHTML2PDF_AVAILABLE = False


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


class AuditLogPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        # Только super_admin и inventory_manager могут просматривать логи
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        return request.user.role in ['super_admin', 'inventory_manager']


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AuditLog.objects.all()
    serializer_class = None  # Will be set dynamically
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['user', 'action', 'model_name']
    search_fields = ['user__username', 'model_name', 'object_name', 'changes']
    ordering_fields = ['timestamp', 'action']
    
    def get_serializer_class(self):
        from rest_framework import serializers
        from accounts.serializers import CustomUserSerializer
        
        class AuditLogSerializer(serializers.ModelSerializer):
            user = CustomUserSerializer(read_only=True)
            
            class Meta:
                model = AuditLog
                fields = '__all__'
        
        return AuditLogSerializer


class ReportSummaryViewSet(viewsets.ViewSet):
    """ViewSet только для сводки (не для экспорта)"""
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['get'], url_path='assets-summary')
    def assets_summary(self, request):
        """Сводка по активам"""
        queryset = Asset.objects.all()
        
        # По статусу
        by_status = queryset.values('status').annotate(count=Count('id'))
        
        # По типу
        by_type = queryset.values('asset_type').annotate(count=Count('id'))
        
        # По локациям
        by_location = queryset.values('current_location__name').annotate(count=Count('id')).filter(current_location__name__isnull=False)
        
        # Недавние
        recent = queryset.order_by('-created_at')[:10]
        
        return Response({
            'by_status': list(by_status),
            'by_type': list(by_type),
            'by_location': list(by_location),
            'recent_count': recent.count(),
            'total': queryset.count()
        })
    
    @action(detail=False, methods=['get'], url_path='export-assets')
    def export_assets(self, request):
        """Экспорт активов в Excel/CSV/PDF"""
        format = request.query_params.get('format', 'csv')
        
        queryset = Asset.objects.all()
        
        # Фильтры
        status_filter = request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        location_id = request.query_params.get('location_id')
        if location_id:
            queryset = queryset.filter(current_location_id=location_id)
        
        record_count = queryset.count()
        
        # Лог экспорта
        ExportLog.objects.create(
            user=request.user,
            export_type='assets',
            format=format,
            filters={
                'status': status_filter,
                'location_id': location_id
            },
            record_count=record_count
        )
        
        # Запись в аудит
        log_audit_action(
            request, 'export', 'Export', None, f'Assets export ({format})',
            {'format': format, 'count': record_count, 'filters': {'status': status_filter, 'location_id': location_id}}
        )
        
        if format == 'csv':
            return self._export_csv(queryset)
        elif format == 'excel':
            return self._export_excel(queryset)
        elif format == 'pdf':
            return self._export_pdf(queryset)
        else:
            return Response({'error': 'Unsupported format'}, status=status.HTTP_400_BAD_REQUEST)

    def _export_csv(self, queryset):
        """Экспорт в CSV"""
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Заголовки
        writer.writerow([
            'Asset Tag', 'Name', 'Type', 'Status', 'Location',
            'Assigned To', 'Manufacturer', 'Model', 'Serial Number',
            'Purchase Date', 'Price'
        ])
        
        # Данные
        for asset in queryset:
            writer.writerow([
                asset.asset_tag,
                asset.name,
                asset.get_asset_type_display(),
                asset.get_status_display(),
                asset.current_location.name if asset.current_location else '',
                asset.assigned_to.username if asset.assigned_to else '',
                asset.manufacturer or '',
                asset.model or '',
                asset.serial_number or '',
                asset.purchase_date or '',
                asset.purchase_price or ''
            ])
        
        response = HttpResponse(output.getvalue(), content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="assets_{datetime.now().strftime("%Y%m%d")}.csv"'
        return response
    
    def _export_excel(self, queryset):
        """Экспорт в Excel"""
        if not OPENPYXL_AVAILABLE:
            return Response(
                {'error': 'Excel export requires openpyxl package'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        wb = Workbook()
        ws = wb.active
        ws.title = 'Assets'
        
        # Заголовки
        headers = [
            'Asset Tag', 'Name', 'Type', 'Status', 'Location',
            'Assigned To', 'Manufacturer', 'Model', 'Serial Number',
            'Purchase Date', 'Price'
        ]
        ws.append(headers)
        
        # Данные
        for asset in queryset:
            ws.append([
                asset.asset_tag,
                asset.name,
                asset.get_asset_type_display(),
                asset.get_status_display(),
                asset.current_location.name if asset.current_location else '',
                asset.assigned_to.username if asset.assigned_to else '',
                asset.manufacturer or '',
                asset.model or '',
                asset.serial_number or '',
                asset.purchase_date.isoformat() if asset.purchase_date else '',
                str(asset.purchase_price) if asset.purchase_price else ''
            ])
        
        # Сохраняем в buffer
        buffer = io.BytesIO()
        wb.save(buffer)
        buffer.seek(0)
        
        response = HttpResponse(buffer.getvalue(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename="assets_{datetime.now().strftime("%Y%m%d")}.xlsx"'
        return response
    
    def _export_pdf(self, queryset):
        """Экспорт в PDF"""
        if not XHTML2PDF_AVAILABLE:
            return Response(
                {'error': 'PDF export requires xhtml2pdf package'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Создаем HTML
        html_content = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                h1 {{ color: #333; }}
                table {{ width: 100%; border-collapse: collapse; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #4CAF50; color: white; }}
                tr:nth-child(even) {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <h1>Assets Report</h1>
            <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>Total Assets: {queryset.count()}</p>
            <table>
                <thead>
                    <tr>
                        <th>Asset Tag</th>
                        <th>Name</th>
                        <th>Type</th>
                        <th>Status</th>
                        <th>Location</th>
                        <th>Assigned To</th>
                        <th>Price</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        for asset in queryset:
            html_content += f"""
                <tr>
                    <td>{asset.asset_tag}</td>
                    <td>{asset.name}</td>
                    <td>{asset.get_asset_type_display()}</td>
                    <td>{asset.get_status_display()}</td>
                    <td>{asset.current_location.name if asset.current_location else ''}</td>
                    <td>{asset.assigned_to.username if asset.assigned_to else ''}</td>
                    <td>{asset.purchase_price or ''}</td>
                </tr>
            """
        
        html_content += """
                </tbody>
            </table>
        </body>
        </html>
        """
        
        # Генерируем PDF
        buffer = io.BytesIO()
        pdf = pisa.pisaDocument(io.StringIO(html_content), buffer)
        
        if pdf.err:
            return Response(
                {'error': 'Error generating PDF'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="assets_{datetime.now().strftime("%Y%m%d")}.pdf"'
        return response


class ReportExportViewSet(viewsets.ViewSet):
    """ViewSet только для экспорта активов"""
    permission_classes = [permissions.IsAuthenticated]
    
    def list(self, request):
        """Экспорт активов в Excel/CSV/PDF"""
        format = request.query_params.get('format', 'csv')
        
        queryset = Asset.objects.all()
        
        # Фильтры
        status_filter = request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        location_id = request.query_params.get('location_id')
        if location_id:
            queryset = queryset.filter(current_location_id=location_id)
        
        record_count = queryset.count()
        
        # Лог экспорта
        ExportLog.objects.create(
            user=request.user,
            export_type='assets',
            format=format,
            filters={
                'status': status_filter,
                'location_id': location_id
            },
            record_count=record_count
        )
        
        # Запись в аудит
        log_audit_action(
            request, 'export', 'Export', None, f'Assets export ({format})',
            {'format': format, 'count': record_count, 'filters': {'status': status_filter, 'location_id': location_id}}
        )
        
        if format == 'csv':
            return self._export_csv(queryset)
        elif format == 'excel':
            return self._export_excel(queryset)
        elif format == 'pdf':
            return self._export_pdf(queryset)
        else:
            return Response({'error': 'Unsupported format'}, status=status.HTTP_400_BAD_REQUEST)