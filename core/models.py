from django.db import models
from django.utils import timezone


# ---------------------------------------------------------------------------
# 1. GeofenceZone Model
# Represents a geographic circular region (e.g., Chandigarh, Delhi, Mumbai).
# Used by the matching engine to determine if a device is physically inside.
# ---------------------------------------------------------------------------
class GeofenceZone(models.Model):
    name = models.CharField(max_length=100)
    latitude = models.FloatField()
    longitude = models.FloatField()
    radius_km = models.FloatField(default=15.0)
    priority = models.IntegerField(default=1)

    def __str__(self):
        return self.name


# ---------------------------------------------------------------------------
# 2. Content Model
# Represents an ad or media payload scheduled/assigned to a geofence.
# ---------------------------------------------------------------------------
class Content(models.Model):
    MEDIA_TYPES = (
        ('IMAGE', 'Image'),
        ('VIDEO', 'Video'),
    )

    title = models.CharField(max_length=200)
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPES, default='IMAGE')
    media_url = models.URLField(max_length=500, blank=True, null=True)
    media_file = models.FileField(upload_to='campaigns/', blank=True, null=True)
    zone = models.ForeignKey(
        GeofenceZone,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='contents'
    )
    is_fallback = models.BooleanField(
        default=False,
        help_text="Display as highway/default ad when outside defined geofences."
    )

    # Scheduling & Expiration Controls
    is_active = models.BooleanField(default=True)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def effective_media_url(self):
        """Returns uploaded file URL if present, otherwise returns media_url."""
        if self.media_file:
            return self.media_file.url
        return self.media_url

    @property
    def is_currently_valid(self):
        if not self.is_active:
            return False
        now = timezone.now()
        if self.start_time and now < self.start_time:
            return False
        if self.end_time and now > self.end_time:
            return False
        return True

    def __str__(self):
        return f"{self.title} ({'Active' if self.is_currently_valid else 'Inactive'})"


# ---------------------------------------------------------------------------
# 3. Device Model
# Represents a physical or simulated display screen (billboard/tablet/kiosk).
# ---------------------------------------------------------------------------
class Device(models.Model):
    STATUS_CHOICES = (
        ('ONLINE', 'Online'),
        ('OFFLINE', 'Offline'),
        ('ERROR', 'Error'),
    )

    device_id = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=100, blank=True)
    current_lat = models.FloatField(null=True, blank=True)
    current_lng = models.FloatField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='OFFLINE')
    last_ping = models.DateTimeField(null=True, blank=True)

    @property
    def is_connected(self):
        """
        Dynamically calculates connectivity health.
        If the device fails to send a heartbeat ping within 30 seconds,
        it is automatically treated as disconnected/offline.
        """
        if not self.last_ping:
            return False
        return (timezone.now() - self.last_ping).total_seconds() < 30

    def save(self, *args, **kwargs):
        if not self.name:
            self.name = f"Screen-{self.device_id}"
        if self.last_ping:
            self.status = 'ONLINE' if self.is_connected else 'OFFLINE'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.device_id})"