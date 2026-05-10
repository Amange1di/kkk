from django.middleware.csrf import CsrfViewMiddleware
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from reports.models import AuditLog
import re

UserModel = get_user_model()


class ApiCsrfExemptionMiddleware:
    """
    Middleware для пропуска CSRF проверки для API эндпоинтов
    Используется с JWT аутентификацией, где CSRF не нужен
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Пропускаем CSRF для всех /api/ путей
        if request.path.startswith('/api/'):
            # Отключаем CSRF проверку для этого запроса
            request._dont_enforce_csrf_checks = True
        
        return self.get_response(request)


class AuditMiddleware:
    """
    Middleware для логирования действий пользователей в аудит
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Логирование только для POST, PUT, PATCH, DELETE запросов
        if request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            if request.user and request.user.is_authenticated:
                try:
                    AuditLog.objects.create(
                        user=request.user,
                        action=request.method,
                        model_name=request.path.split('/')[2] if len(request.path.split('/')) > 2 else '',
                        object_id='',
                        object_name='',
                        changes={},
                        ip_address=request.META.get('REMOTE_ADDR'),
                        user_agent=request.META.get('HTTP_USER_AGENT', '')
                    )
                except Exception:
                    pass
        
        return response