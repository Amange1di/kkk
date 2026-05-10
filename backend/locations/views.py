from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Location
from .serializers import LocationSerializer, LocationListSerializer


class LocationPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Проверка роли пользователя
        user_role = getattr(request.user, 'role', None)
        if user_role in ['super_admin', 'inventory_manager']:
            return True
        
        return False


class LocationViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'list':
            return LocationListSerializer
        return LocationSerializer

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['location_type', 'parent_location', 'is_active', 'building', 'floor']
    search_fields = ['name', 'building', 'floor', 'room_number', 'address']
    ordering_fields = ['name', 'created_at']

    def get_queryset(self):
        queryset = Location.objects.all()
        parent_id = self.request.query_params.get('parent_id')
        if parent_id:
            queryset = queryset.filter(parent_location_id=parent_id)
        return queryset