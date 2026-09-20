import math
import random
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import Device, GeofenceZone, Content
from .serializers import DeviceSerializer, GeofenceZoneSerializer, ContentSerializer


# ---------------------------------------------------------------------------
# Math Engine: Haversine Formula
# Calculates great-circle distance between two GPS coordinates (in km).
# ---------------------------------------------------------------------------
def calculate_haversine_distance(lat1, lon1, lat2, lon2):
    earth_radius_km = 6371.0

    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_lat / 2.0) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(delta_lon / 2.0) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return earth_radius_km * c


# ---------------------------------------------------------------------------
# Admin API ViewSets (Standard CRUD for Dashboard)
# ---------------------------------------------------------------------------
class DeviceViewSet(viewsets.ModelViewSet):
    queryset = Device.objects.all().order_by('-last_ping')
    serializer_class = DeviceSerializer
    permission_classes = [AllowAny]


class GeofenceZoneViewSet(viewsets.ModelViewSet):
    queryset = GeofenceZone.objects.all().order_by('-priority')
    serializer_class = GeofenceZoneSerializer
    permission_classes = [AllowAny]


class ContentViewSet(viewsets.ModelViewSet):
    queryset = Content.objects.all().order_by('-created_at')
    serializer_class = ContentSerializer
    permission_classes = [AllowAny]


# ---------------------------------------------------------------------------
# Core Telemetry & Geofence Evaluation Engine
# ---------------------------------------------------------------------------
@api_view(['POST'])
@permission_classes([AllowAny])
def device_telemetry(request):
    device_id = request.data.get('device_id')
    lat = request.data.get('latitude')
    lng = request.data.get('longitude')

    if not device_id:
        return Response(
            {'error': 'device_id parameter is required.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # 1. Update or auto-register the pinging device
    device, _ = Device.objects.get_or_create(
        device_id=device_id,
        defaults={'name': f"Screen-{device_id}"},
    )

    # Safe float parsing
    if lat is not None and lng is not None:
        try:
            device.current_lat = float(lat)
            device.current_lng = float(lng)
        except (ValueError, TypeError):
            return Response(
                {'error': 'latitude and longitude must be valid floating numbers.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

    device.status = 'ONLINE'
    device.last_ping = timezone.now()
    device.save()

    # 2. Evaluate geofence boundaries
    matched_zone = None
    if device.current_lat is not None and device.current_lng is not None:
        all_zones = GeofenceZone.objects.all().order_by('-priority')

        for zone in all_zones:
            dist = calculate_haversine_distance(
                device.current_lat,
                device.current_lng,
                zone.latitude,
                zone.longitude,
            )
            if dist <= zone.radius_km:
                matched_zone = zone
                break

    # 3. Resolve targeted or fallback campaign playlist
    playlist_contents = []
    if matched_zone:
        playlist_contents = list(Content.objects.filter(zone=matched_zone).order_by('id'))

    if not playlist_contents:
        playlist_contents = list(Content.objects.filter(is_fallback=True).order_by('id'))

    active_content = playlist_contents[0] if playlist_contents else None
    serialized_playlist = ContentSerializer(playlist_contents, many=True, context={'request': request}).data

    # 4. Return instructions to display client
    return Response(
        {
            'device_id': device.device_id,
            'status': device.status,
            'is_connected': device.is_connected,
            'matched_zone': matched_zone.name if matched_zone else 'Roaming / Fallback',
            'content': ContentSerializer(active_content, context={'request': request}).data if active_content else None,
            'playlist': serialized_playlist,
        },
        status=status.HTTP_200_OK,
    )