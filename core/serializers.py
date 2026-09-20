from rest_framework import serializers
from .models import GeofenceZone, Device, Content

# ---------------------------------------------------------------------------
# 1. GeofenceZoneSerializer
# Handles serialization of geographic circular zones (e.g., Chandigarh, Delhi).
# Used by:
# - Admin Dashboard: to list existing zones and populate zone dropdowns.
# - Spatial Engine: to transmit center coordinates (lat/lng) and radius (km).
# ---------------------------------------------------------------------------
class GeofenceZoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeofenceZone
        fields = '__all__'


# ---------------------------------------------------------------------------
# 2. DeviceSerializer
# Handles fleet screen telemetry and connectivity health.
# Used by:
# - Admin Dashboard: to display live vehicle/kiosk statuses (Online/Offline)
#   and monitor last GPS ping coordinates.
# ---------------------------------------------------------------------------
class DeviceSerializer(serializers.ModelSerializer):
    # Dynamically exposes the model property to the frontend.
    # Evaluates whether the device sent a ping within the last 30 seconds.
    is_connected = serializers.ReadOnlyField()

    class Meta:
        model = Device
        fields = '__all__'


# ---------------------------------------------------------------------------
# 3. ContentSerializer
# Handles ad creative payloads, zone bindings, and scheduling validity.
# Used by:
# - Admin Dashboard: to create, preview, schedule, and delete campaigns.
# - Smart Display / Telemetry Engine: to deliver active playlists to vehicles.
# ---------------------------------------------------------------------------
class ContentSerializer(serializers.ModelSerializer):
    # This ensures media_url always returns the active URL (whether remote link or uploaded file)
    effective_url = serializers.SerializerMethodField()

    class Meta:
        model = Content
        fields = [
            'id',
            'title',
            'media_type',
            'media_url',
            'media_file',
            'effective_url',
            'zone',
            'is_fallback',
            'is_active',
            'is_currently_valid',
            'start_time',
            'end_time',
            'created_at',
        ]

    def get_effective_url(self, obj):
        request = self.context.get('request')
        if obj.media_file:
            if request:
                return request.build_absolute_uri(obj.media_file.url)
            return obj.media_file.url
        return obj.media_url

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # If media_file was uploaded, override media_url so KioskDisplay works without breaking changes
        if instance.media_file:
            data['media_url'] = self.get_effective_url(instance)
        return data