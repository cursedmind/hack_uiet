from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DeviceViewSet,
    GeofenceZoneViewSet,
    ContentViewSet,
    device_telemetry,
)

# ---------------------------------------------------------------------------
# Router Registration:
# DefaultRouter automatically generates standard REST routes for viewsets:
#   - GET/POST /api/devices/
#   - GET/PUT/PATCH/DELETE /api/devices/{id}/
#   - GET/POST /api/zones/
#   - GET/PUT/PATCH/DELETE /api/zones/{id}/
#   - GET/POST /api/contents/
#   - GET/PUT/PATCH/DELETE /api/contents/{id}/
# ---------------------------------------------------------------------------
router = DefaultRouter()
router.register(r'devices', DeviceViewSet, basename='device')
router.register(r'zones', GeofenceZoneViewSet, basename='zone')
router.register(r'contents', ContentViewSet, basename='content')

urlpatterns = [
    # Custom telemetry & decision-engine endpoint pinged by screens
    path('telemetry/', device_telemetry, name='device-telemetry'),

    # Include all auto-generated ViewSet CRUD routes
    path('', include(router.urls)),
]