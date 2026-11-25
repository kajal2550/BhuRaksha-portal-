from django.db import models
import hashlib
import json

class Village(models.Model):
    name = models.CharField(max_length=100)
    village_code = models.CharField(max_length=50, unique=True)
    tehsil = models.CharField(max_length=100, default='Phagwara')
    district = models.CharField(max_length=100, default='Kapurthala')
    state = models.CharField(max_length=100, default='Punjab')
    boundary_geojson = models.TextField(blank=True, null=True, help_text="Polygon / MultiPolygon of village boundary")

    def __str__(self):
        return f"{self.name} ({self.tehsil}, {self.district})"


class Parcel(models.Model):
    LAND_USE_TYPES = [
        ('Irrigated Agri', 'Irrigated Agricultural Land'),
        ('Rain-fed Agri', 'Rain-fed Agricultural Land'),
        ('Residential/Abadi', 'Residential / Abadi Area'),
        ('Commercial/FoodTech', 'Commercial / FoodTech Storage'),
        ('Forest/Pasture', 'Forest / Pasture / Community Land'),
    ]

    STATUS_CHOICES = [
        ('Verified', 'Verified (Clear Title)'),
        ('Mutation Pending', 'Mutation Pending'),
        ('Disputed', 'Disputed / Litigated'),
        ('Tampered', 'Tampered / Integrity Failed'),
    ]

    # Unique 14-character ULPIN (Digital Public Infrastructure Common Key)
    parcel_id = models.CharField(max_length=64, unique=True, verbose_name="ULPIN / Unique Parcel ID")
    khasra_no = models.CharField(max_length=50, verbose_name="Khasra / Plot Number")
    village = models.ForeignKey(Village, on_delete=models.CASCADE, related_name='parcels')
    
    area_hectares = models.FloatField(verbose_name="Area (Hectares)")
    area_acres = models.FloatField(verbose_name="Area (Acres)")
    
    land_use_type = models.CharField(max_length=50, choices=LAND_USE_TYPES, default='Irrigated Agri')
    soil_type = models.CharField(max_length=50, default='Alluvial Loam')
    irrigation_source = models.CharField(max_length=100, default='Canal & Tubewell')
    
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Verified')
    
    # Standard GeoJSON Polygon string (EPSG:4326)
    geometry_geojson = models.TextField(help_text="WGS84 GeoJSON Polygon coordinates")
    centroid_lat = models.FloatField()
    centroid_lng = models.FloatField()

    # Cryptographic Fingerprint for Tamper Detection
    fingerprint = models.CharField(max_length=64, blank=True, null=True, help_text="SHA-256 of critical parcel fields")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['khasra_no']

    def calculate_fingerprint(self) -> str:
        """Compute SHA-256 over critical fields: parcel_id, khasra, area, geometry, status."""
        raw_payload = f"{self.parcel_id}|{self.khasra_no}|{self.village_id}|{self.area_hectares:.4f}|{self.land_use_type}|{self.geometry_geojson.strip()}"
        return hashlib.sha256(raw_payload.encode('utf-8')).hexdigest()

    def verify_integrity(self) -> bool:
        """Check if stored fingerprint matches real-time recalculation."""
        if not self.fingerprint:
            return False
        return self.fingerprint == self.calculate_fingerprint()

    def save(self, *args, **kwargs):
        # Auto-calculate area in acres if not provided
        if not self.area_acres and self.area_hectares:
            self.area_acres = round(self.area_hectares * 2.47105, 2)
        # Update fingerprint on save unless specifically disabled
        if kwargs.pop('skip_fingerprint', False) is False:
            self.fingerprint = self.calculate_fingerprint()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Khasra {self.khasra_no} [{self.parcel_id}] - {self.village.name}"
