from django.db import models
from parcels.models import Parcel
from security.crypto_utils import encrypt_pii, decrypt_pii, mask_aadhaar, mask_phone

class Owner(models.Model):
    name = models.CharField(max_length=150)
    # Stored encrypted at rest with Fernet
    encrypted_aadhaar = models.TextField(help_text="Fernet encrypted National ID / Aadhaar")
    encrypted_phone = models.TextField(help_text="Fernet encrypted phone number")
    
    address = models.TextField(blank=True, null=True)
    pm_kisan_id = models.CharField(max_length=50, blank=True, null=True, verbose_name="PM-KISAN Beneficiary ID")
    soil_health_card_no = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def plain_aadhaar(self) -> str:
        return decrypt_pii(self.encrypted_aadhaar)

    @property
    def masked_aadhaar(self) -> str:
        return mask_aadhaar(self.plain_aadhaar)

    @property
    def plain_phone(self) -> str:
        return decrypt_pii(self.encrypted_phone)

    @property
    def masked_phone(self) -> str:
        return mask_phone(self.plain_phone)

    def set_aadhaar(self, raw_val: str):
        self.encrypted_aadhaar = encrypt_pii(raw_val)

    def set_phone(self, raw_val: str):
        self.encrypted_phone = encrypt_pii(raw_val)

    def __str__(self):
        return f"{self.name} ({self.masked_aadhaar})"


class OwnershipRecord(models.Model):
    STATUS_CHOICES = [
        ('Active', 'Active Registered Owner'),
        ('Transferred', 'Historical / Transferred'),
        ('Disputed', 'Subject to Legal Dispute'),
    ]

    parcel = models.ForeignKey(Parcel, on_delete=models.CASCADE, related_name='ownership_records')
    owner = models.ForeignKey(Owner, on_delete=models.CASCADE, related_name='land_holdings')
    share_percentage = models.FloatField(default=100.0, help_text="Ownership share percentage (0 - 100%)")
    from_date = models.DateField(auto_now_add=True)
    to_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='Active')

    def __str__(self):
        return f"{self.owner.name} -> {self.parcel.parcel_id} ({self.share_percentage}%)"


class CropRecord(models.Model):
    SEASON_CHOICES = [
        ('Kharif', 'Kharif (Monsoon)'),
        ('Rabi', 'Rabi (Winter)'),
        ('Zaid', 'Zaid (Summer)'),
        ('Perennial', 'Perennial / Commercial'),
    ]

    parcel = models.ForeignKey(Parcel, on_delete=models.CASCADE, related_name='crop_records')
    season = models.CharField(max_length=30, choices=SEASON_CHOICES)
    crop = models.CharField(max_length=100)
    variety = models.CharField(max_length=100, default='Certified High Yield')
    sowing_date = models.DateField()
    harvest_date = models.DateField(blank=True, null=True)
    estimated_yield_quintals = models.FloatField(default=25.0)
    irrigation_used = models.CharField(max_length=100, default='Tube Well & Canal')
    soil_condition = models.CharField(max_length=100, default='Optimal NPK')
    recorded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-sowing_date']

    def __str__(self):
        return f"{self.crop} ({self.season}) on {self.parcel.khasra_no}"


class Scheme(models.Model):
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200)
    description = models.TextField()
    subsidy_amount_per_ha = models.DecimalField(max_digits=10, decimal_places=2, default=6000.00)
    eligible_crop = models.CharField(max_length=100, default='All Crops')
    max_area_hectares = models.FloatField(default=5.0)

    def __str__(self):
        return f"{self.code} - {self.name}"


class SchemeEligibility(models.Model):
    parcel = models.ForeignKey(Parcel, on_delete=models.CASCADE, related_name='scheme_eligibilities')
    scheme = models.ForeignKey(Scheme, on_delete=models.CASCADE)
    is_eligible = models.BooleanField(default=True)
    reason = models.CharField(max_length=255, default='Verified eligible under landholding threshold')
    checked_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('parcel', 'scheme')
