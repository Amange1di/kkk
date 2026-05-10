from django.contrib import admin
from .models import AuditLog, ExportLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['timestamp', 'user', 'action', 'model_name', 'object_name']
    list_filter = ['action', 'model_name', 'timestamp']
    search_fields = ['user__username', 'model_name', 'object_name', 'changes']
    readonly_fields = ['user', 'action', 'model_name', 'object_id', 'object_name', 'changes', 'ip_address', 'user_agent', 'timestamp']
    date_hierarchy = 'timestamp'
    
    def has_add_permission(self, request):
        return False


@admin.register(ExportLog)
class ExportLogAdmin(admin.ModelAdmin):
    list_display = ['timestamp', 'user', 'export_type', 'format', 'record_count']
    list_filter = ['format', 'export_type', 'timestamp']
    search_fields = ['user__username', 'export_type']
    readonly_fields = ['user', 'export_type', 'format', 'file_path', 'filters', 'record_count', 'timestamp']
    date_hierarchy = 'timestamp'
    
    def has_add_permission(self, request):
        return False