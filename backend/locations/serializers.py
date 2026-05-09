from rest_framework import serializers
from .models import Location


class LocationSerializer(serializers.ModelSerializer):
    child_locations = serializers.SerializerMethodField()
    asset_count = serializers.SerializerMethodField()

    class Meta:
        model = Location
        fields = [
            'id', 'name', 'location_type', 'parent_location', 'building',
            'floor', 'room_number', 'address', 'description', 'contact_person',
            'contact_phone', 'capacity', 'is_active', 'child_locations',
            'asset_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_child_locations(self, obj):
        return LocationSerializer(obj.child_locations.all(), many=True).data

    def get_asset_count(self, obj):
        return obj.assets.count()


class LocationListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ['id', 'name', 'location_type', 'parent_location', 'is_active']
