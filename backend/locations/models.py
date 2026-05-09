from django.db import models


class Location(models.Model):
    LOCATION_TYPE_CHOICES = [
        ('building', 'Building'),
        ('floor', 'Floor'),
        ('room', 'Room'),
        ('office', 'Office'),
        ('warehouse', 'Warehouse'),
        ('other', 'Other'),
    ]

    name = models.CharField(max_length=200, verbose_name="Location Name")
    location_type = models.CharField(max_length=20, choices=LOCATION_TYPE_CHOICES, verbose_name="Location Type")
    
    # Hierarchy
    parent_location = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='child_locations',
        verbose_name="Parent Location"
    )
    
    # Details
    building = models.CharField(max_length=100, blank=True, null=True, verbose_name="Building")
    floor = models.CharField(max_length=10, blank=True, null=True, verbose_name="Floor")
    room_number = models.CharField(max_length=50, blank=True, null=True, verbose_name="Room Number")
    
    address = models.TextField(blank=True, null=True, verbose_name="Address")
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    
    # Contact
    contact_person = models.CharField(max_length=100, blank=True, null=True, verbose_name="Contact Person")
    contact_phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Contact Phone")
    
    # Capacity
    capacity = models.IntegerField(blank=True, null=True, verbose_name="Capacity")
    
    # Metadata
    is_active = models.BooleanField(default=True, verbose_name="Is Active")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")

    class Meta:
        verbose_name = "Location"
        verbose_name_plural = "Locations"
        ordering = ['name']
        unique_together = ['parent_location', 'name']

    def __str__(self):
        if self.parent_location:
            return f"{self.parent_location.name} - {self.name}"
        return self.name