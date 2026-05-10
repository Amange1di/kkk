from django.contrib import admin
from .models import Asset, TransferHistory


@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ['asset_tag', 'name', 'asset_type', 'status', 'current_location', 'assigned_to', 'purchase_date']
    list_filter = ['asset_type', 'status', 'manufacturer', 'purchase_date']
    search_fields = ['asset_tag', 'name', 'serial_number', 'model']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('asset_tag', 'name', 'description', 'asset_type')
        }),
        ('Specifications', {
            'fields': ('manufacturer', 'model', 'serial_number', 'purchase_date', 'warranty_expires')
        }),
        ('Financial', {
            'fields': ('purchase_price', 'currency')
        }),
        ('Status and Location', {
            'fields': ('status', 'current_location')
        }),
        ('Assignment', {
            'fields': ('assigned_to', 'assigned_date', 'department')
        }),
        ('Media', {
            'fields': ('image',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at', 'created_by')
        }),
    )


@admin.register(TransferHistory)
class TransferHistoryAdmin(admin.ModelAdmin):
    list_display = ['asset', 'transfer_type', 'transfer_date', 'from_user', 'to_user', 'performed_by']
    list_filter = ['transfer_type', 'transfer_date']
    search_fields = ['asset__asset_tag', 'asset__name', 'notes']
    readonly_fields = ['transfer_date']
    
    fieldsets = (
        ('Asset', {
            'fields': ('asset',)
        }),
        ('Transfer Details', {
            'fields': ('transfer_type', 'from_location', 'to_location', 'from_user', 'to_user')
        }),
        ('Timing and Performer', {
            'fields': ('transfer_date', 'performed_by')
        }),
        ('Notes', {
            'fields': ('reason', 'notes')
        }),
    )