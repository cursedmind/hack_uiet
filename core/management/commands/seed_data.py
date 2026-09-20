from django.core.management.base import BaseCommand
from core.models import GeofenceZone, Content, Device

class Command(BaseCommand):
    help = "Seed initial zones, demo devices, and media content for hackathon evaluation"

    def handle(self, *args, **options):
        self.stdout.write("Clearing previous demo data...")
        Content.objects.all().delete()
        GeofenceZone.objects.all().delete()
        Device.objects.all().delete()

        # -------------------------------------------------------------------
        # 1. Create Hackathon Prompt Zones (Chandigarh -> Delhi -> Mumbai)
        # -------------------------------------------------------------------
        self.stdout.write("Creating Geofence Zones...")
        zone_chd = GeofenceZone.objects.create(
            name="Chandigarh",
            latitude=30.7333,
            longitude=76.7794,
            radius_km=15.0,
            priority=1
        )

        zone_delhi = GeofenceZone.objects.create(
            name="Delhi",
            latitude=28.6139,
            longitude=77.2090,
            radius_km=25.0,
            priority=2
        )

        zone_mumbai = GeofenceZone.objects.create(
            name="Mumbai",
            latitude=19.0760,
            longitude=72.8777,
            radius_km=20.0,
            priority=1
        )

        # -------------------------------------------------------------------
        # 2. Create Targeted Media Campaigns for Each Zone
        # -------------------------------------------------------------------
        self.stdout.write("Creating Content Campaigns...")
        Content.objects.create(
            title="Chandigarh City Cleanliness Drive & Tourism",
            media_type="IMAGE",
            media_url="https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=1200&q=80",
            zone=zone_chd,
            is_fallback=False
        )

        Content.objects.create(
            title="Delhi Metro Mega Retail Festival",
            media_type="IMAGE",
            media_url="https://images.unsplash.com/photo-1587474260584-136574528ed5?auto=format&fit=crop&w=1200&q=80",
            zone=zone_delhi,
            is_fallback=False
        )

        Content.objects.create(
            title="Mumbai Marine Drive Monsoon Campaign",
            media_type="IMAGE",
            media_url="https://images.unsplash.com/photo-1570168007204-dfb528c6958f?auto=format&fit=crop&w=1200&q=80",
            zone=zone_mumbai,
            is_fallback=False
        )

        # National fallback campaign (runs on highway / outside all zones)
        Content.objects.create(
            title="National Brand Fallback - Pan India",
            media_type="IMAGE",
            media_url="https://images.unsplash.com/photo-1557804506-669a67965ba0?auto=format&fit=crop&w=1200&q=80",
            zone=None,
            is_fallback=True
        )

        # -------------------------------------------------------------------
        # 3. Create Sample Devices
        # -------------------------------------------------------------------
        self.stdout.write("Creating Fleet Devices...")
        Device.objects.create(
            device_id="SCREEN-CHD-01",
            name="Cab Fleet #12 - Chandigarh",
            current_lat=30.7333,
            current_lng=76.7794,
            status="ONLINE"
        )
        Device.objects.create(
            device_id="SCREEN-DEL-02",
            name="Delivery Van #8 - Delhi",
            current_lat=28.6139,
            current_lng=77.2090,
            status="ONLINE"
        )

        self.stdout.write(self.style.SUCCESS("Successfully seeded database with demo data!"))