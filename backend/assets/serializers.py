from rest_framework import serializers
from .models import Asset, TransferHistory, AssetType
from locations.serializers import LocationSerializer
from accounts.serializers import CustomUserSerializer


class AssetTypeSerializer(serializers.ModelSerializer):
    """Serializer для типов активов"""
    assets_count = serializers.SerializerMethodField()

    class Meta:
        model = AssetType
        fields = ['id', 'name', 'code', 'description', 'is_active', 'created_at', 'updated_at', 'assets_count']
        read_only_fields = ['created_at', 'updated_at']

    def get_assets_count(self, obj):
        return obj.assets.count()


class AssetSerializer(serializers.ModelSerializer):
    current_location = LocationSerializer(read_only=True)
    current_location_id = serializers.PrimaryKeyRelatedField(
        queryset=LocationSerializer.Meta.model.objects.all(),
        source='current_location',
        write_only=True,
        required=False
    )
    assigned_to = CustomUserSerializer(read_only=True)
    assigned_to_id = serializers.PrimaryKeyRelatedField(
        queryset=CustomUserSerializer.Meta.model.objects.all(),
        source='assigned_to',
        write_only=True,
        required=False
    )
    auditor_user = CustomUserSerializer(read_only=True)
    auditor_user_id = serializers.PrimaryKeyRelatedField(
        queryset=CustomUserSerializer.Meta.model.objects.all(),
        source='auditor_user',
        write_only=True,
        required=False
    )
    created_by = CustomUserSerializer(read_only=True)
    asset_type = AssetTypeSerializer(read_only=True)
    asset_type_id = serializers.PrimaryKeyRelatedField(
        queryset=AssetType.objects.all(),
        source='asset_type',
        write_only=True,
        required=False
    )

    class Meta:
        model = Asset
        fields = [
            'id', 'asset_tag', 'name', 'description', 'asset_type', 'asset_type_id',
            'manufacturer', 'model', 'serial_number', 'purchase_date',
            'warranty_expires', 'purchase_price', 'currency', 'status',
            'current_location', 'current_location_id', 'assigned_to',
            'assigned_to_id', 'assigned_date', 'auditor', 'auditor_user',
            'auditor_user_id', 'department', 'image',
            'created_at', 'updated_at', 'created_by'
        ]
        read_only_fields = ['created_at', 'updated_at', 'created_by']


class TransferHistorySerializer(serializers.ModelSerializer):
    asset = AssetSerializer(read_only=True)
    from_location = LocationSerializer(read_only=True)
    to_location = LocationSerializer(read_only=True)
    from_user = CustomUserSerializer(read_only=True)
    to_user = CustomUserSerializer(read_only=True)
    performed_by = CustomUserSerializer(read_only=True)

    class Meta:
        model = TransferHistory
        fields = [
            'id', 'asset', 'transfer_type', 'from_location', 'to_location',
            'from_user', 'to_user', 'transfer_date', 'reason', 'notes',
            'performed_by'
        ]
        read_only_fields = ['transfer_date', 'performed_by']
