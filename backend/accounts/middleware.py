import logging
from django.utils.deprecation import MiddlewareMixin
from accounts.models import CustomUser
from reports.models import AuditLog

logger = logging.getLogger(__name__)


class AuditMiddleware(MiddlewareMixin):
    """
    Middleware для автоматического логирования действий пользователей
    """
    
    def process_request(self, request):
        # Сохраняем IP и user_agent для аудита
        request.audit_ip = self.get_client_ip(request)
        request.audit_user_agent = request.META.get('HTTP_USER_AGENT', '')
    
    def process_response(self, request, response):
        # Логирование login/logout
        if hasattr(request, 'session'):
            if 'user_id' in request.session and not hasattr(request, 'audit_logged'):
                # Проверяем, был ли это логин
                if 'login' in request.path:
                    self.log_action(request, 'login')
        
        return response
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def log_action(self, request, action, model_name=None, object_id=None, object_name=None, changes=None):
        """Создание записи аудита"""
        if not request.user or not request.user.is_authenticated:
            return
        
        try:
            AuditLog.objects.create(
                user=request.user,
                action=action,
                model_name=model_name or '',
                object_id=str(object_id) if object_id else '',
                object_name=object_name or '',
                changes=changes,
                ip_address=request.audit_ip if hasattr(request, 'audit_ip') else None,
                user_agent=request.audit_user_agent if hasattr(request, 'audit_user_agent') else None
            )
            logger.info(f"Audit: {request.user.username} - {action} on {model_name}:{object_id}")
        except Exception as e:
            logger.error(f"Failed to create audit log: {e}")


def log_audit_action(request, action, model_name=None, object_id=None, object_name=None, changes=None):
    """
    Функция для ручного логирования действий
    Используется в views для специфичных действий
    """
    middleware = AuditMiddleware()
    middleware.log_action(request, action, model_name, object_id, object_name, changes)
