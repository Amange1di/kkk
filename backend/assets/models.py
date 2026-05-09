from django.db import models
from django.conf import settings
from locations.models import Location


class AssetType(models.Model):
    """Модель типов активов для динамического управления"""
    name = models.CharField(max_length=100, unique=True, verbose_name="Название типа")
    code = models.SlugField(max_length=50, unique=True, verbose_name="Код типа")
    description = models.TextField(blank=True, null=True, verbose_name="Описание")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создан")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлен")

    class Meta:
        verbose_name = "Тип актива"
        verbose_name_plural = "Типы активов"
        ordering = ['name']

    def __str__(self):
        return self.name


class Asset(models.Model):
    ASSET_STATUS_CHOICES = [
        ('available', 'Available'),
        ('in_use', 'In Use'),
        ('in_repair', 'In Repair'),
        ('retired', 'Retired'),
        ('lost', 'Lost'),
    ]

    # Basic Information
    asset_tag = models.CharField(max_length=50, unique=True, verbose_name="Asset Tag")
    name = models.CharField(max_length=200, verbose_name="Asset Name")
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    asset_type = models.ForeignKey(
        AssetType,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='assets',
        verbose_name="Тип актива"
    )
    
    # Specifications
    manufacturer = models.CharField(max_length=100, blank=True, null=True, verbose_name="Manufacturer")
    model = models.CharField(max_length=100, blank=True, null=True, verbose_name="Model")
    serial_number = models.CharField(max_length=100, blank=True, null=True, verbose_name="Serial Number")
    purchase_date = models.DateField(blank=True, null=True, verbose_name="Purchase Date")
    warranty_expires = models.DateField(blank=True, null=True, verbose_name="Warranty Expiration")
    
    # Financial
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="Purchase Price")
    currency = models.CharField(max_length=3, default='RUB', verbose_name="Currency")
    
    # Status and Location
    status = models.CharField(max_length=20, choices=ASSET_STATUS_CHOICES, default='available', verbose_name="Status")
    current_location = models.ForeignKey(
        Location, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='assets',
        verbose_name="Current Location"
    )
    
    # Assignment
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_assets',
        verbose_name="Assigned To"
    )
    assigned_date = models.DateField(blank=True, null=True, verbose_name="Assignment Date")
    
    # Auditor Information
    auditor = models.CharField(max_length=100, blank=True, null=True, verbose_name="Auditor (Auditorium/Room)")
    auditor_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='auditor_assets',
        verbose_name="Responsible User"
    )
    
    # Organization
    department = models.CharField(max_length=100, blank=True, null=True, verbose_name="Department")
    
    # Media
    image = models.ImageField(upload_to='assets/', blank=True, null=True, verbose_name="Asset Image")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_assets',
        verbose_name="Created By"
    )

    class Meta:
        verbose_name = "Asset"
        verbose_name_plural = "Assets"
        ordering = ['asset_tag']

    def __str__(self):
        return f"{self.asset_tag} - {self.name}"


class TransferHistory(models.Model):
    TRANSFER_TYPE_CHOICES = [
        ('checkout', 'Checkout'),
        ('checkin', 'Check-in'),
        ('transfer', 'Transfer'),
        ('maintenance', 'Maintenance'),
        ('return', 'Return'),
    ]

    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='transfer_history', verbose_name="Asset")
    transfer_type = models.CharField(max_length=20, choices=TRANSFER_TYPE_CHOICES, verbose_name="Transfer Type")
    
    from_location = models.ForeignKey(
        Location, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='transfer_from',
        verbose_name="From Location"
    )
    to_location = models.ForeignKey(
        Location, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='transfer_to',
        verbose_name="To Location"
    )
    
    from_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='transfer_from',
        verbose_name="From User"
    )
    to_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='transfer_to',
        verbose_name="To User"
    )
    
    transfer_date = models.DateTimeField(auto_now_add=True, verbose_name="Transfer Date")
    reason = models.TextField(blank=True, null=True, verbose_name="Reason")
    notes = models.TextField(blank=True, null=True, verbose_name="Notes")
    
    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='transfers_performed',
        verbose_name="Performed By"
    )

    class Meta:
        verbose_name = "Transfer History"
        verbose_name_plural = "Transfer Histories"
        ordering = ['-transfer_date']

    def __str__(self):
        return f"{self.asset.asset_tag} - {self.transfer_type} on {self.transfer_date}"