from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from django.contrib.auth import login, logout
from .serializers import CustomUserSerializer, CustomTokenObtainPairSerializer
from reports.models import AuditLog
from rest_framework_simplejwt.views import TokenObtainPairView

UserModel = get_user_model()


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [permissions.AllowAny]


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


class UserViewSet(viewsets.ModelViewSet):
    queryset = UserModel.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['username', 'email', 'first_name', 'last_name', 'department']
    ordering_fields = ['date_joined', 'last_login', 'username']

    def get_permissions(self):
        if self.action in ['create', 'list', 'retrieve']:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'super_admin':
            return UserModel.objects.all()
        return UserModel.objects.filter(department=user.department)

    @action(detail=False, methods=['post'])
    def logout(self, request):
        """Logout пользователя и запись в аудит"""
        log_audit_action(request, 'logout', 'User', request.user.id, str(request.user))
        # Для JWT logout просто удаляем токен на клиенте, сервер не хранит сессию
        return Response({'status': 'Logged out successfully'})

    @action(detail=False, methods=['get'])
    def me(self, request):
        """Текущий пользователь"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)