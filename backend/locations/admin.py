from django.contrib import admin
from .models import Location


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ['name', 'location_type', 'parent_location', 'building', 'floor', 'room_number', 'is_active']
    list_filter = ['location_type', 'is_active', 'building', 'floor']
    search_fields = ['name', 'building', 'floor', 'room_number', 'address']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'location_type', 'parent_location')
        }),
        ('Details', {
            'fields': ('building', 'floor', 'room_number', 'address', 'description')
        }),
        ('Contact', {
            'fields': ('contact_person', 'contact_phone')
        }),
        ('Capacity', {
            'fields': ('capacity',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at')
        }),
    )