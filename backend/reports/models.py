from django.db import models
from django.conf import settings


class AuditLog(models.Model):
    """Лог всех действий в системе для аудита"""
    
    ACTION_CHOICES = [
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('scan', 'QR Scan'),
        ('export', 'Export'),
        ('transfer', 'Transfer'),
        ('checkout', 'Checkout'),
        ('checkin', 'Checkin'),
        ('report_damage', 'Report Damage'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='audit_logs'
    )
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    model_name = models.CharField(max_length=100)
    object_id = models.CharField(max_length=100, blank=True, null=True)
    object_name = models.CharField(max_length=255, blank=True, null=True)
    changes = models.JSONField(blank=True, null=True, help_text="Changes made (old -> new)")
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Audit Log"
        verbose_name_plural = "Audit Logs"
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['action', '-timestamp']),
            models.Index(fields=['model_name', 'object_id']),
        ]
    
    def __str__(self):
        return f"{self.user.username if self.user else 'Anonymous'} - {self.action} on {self.model_name}"


class ExportLog(models.Model):
    """Лог экспорта отчетов"""
    
    FORMAT_CHOICES = [
        ('pdf', 'PDF'),
        ('excel', 'Excel'),
        ('csv', 'CSV'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='export_logs'
    )
    export_type = models.CharField(max_length=50, help_text="Type of export (assets, locations, transfers)")
    format = models.CharField(max_length=10, choices=FORMAT_CHOICES)
    file_path = models.CharField(max_length=500, blank=True, null=True)
    filters = models.JSONField(blank=True, null=True, help_text="Filters applied")
    record_count = models.IntegerField(default=0, help_text="Number of records exported")
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Export Log"
        verbose_name_plural = "Export Logs"
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.user.username if self.user else 'Anonymous'} - {self.export_type} ({self.format})"