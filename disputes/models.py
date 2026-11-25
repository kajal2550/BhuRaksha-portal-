from django.db import models
from django.contrib.auth.models import User
from parcels.models import Parcel

class Dispute(models.Model):
    DISPUTE_TYPES = [
        ('boundary_overlap', 'Boundary Dispute / Encroachment'),
        ('title_forgery', 'Fraudulent Sale / Forged Mutation'),
        ('inheritance_claim', 'Unrecorded Legal Heir Claim'),
        ('area_mismatch', 'Physical Area Mismatch with Cadastre'),
        ('bank_lien', 'Undisclosed Mortgage / Bank Lien'),
    ]

    STATUS_CHOICES = [
        ('Open', 'Open (Under Initial Review)'),
        ('In Review', 'Hearing Scheduled in Revenue Court'),
        ('Resolved', 'Resolved (Order Passed)'),
        ('Closed', 'Closed / Dismissed'),
    ]

    case_number = models.CharField(max_length=64, unique=True, verbose_name="Dispute Case ID")
    parcel = models.ForeignKey(Parcel, on_delete=models.CASCADE, related_name='disputes')
    dispute_type = models.CharField(max_length=50, choices=DISPUTE_TYPES)
    
    complainant_name = models.CharField(max_length=150)
    complainant_contact = models.CharField(max_length=50, blank=True, null=True)
    complainant_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    description = models.TextField()
    evidence_document = models.FileField(upload_to='dispute_evidence/', blank=True, null=True)
    
    # Specific location pin on map
    pin_lat = models.FloatField(blank=True, null=True)
    pin_lng = models.FloatField(blank=True, null=True)

    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='Open')
    assigned_officer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='handled_disputes')
    resolution_notes = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update parcel status to Disputed if dispute is open
        if self.status in ['Open', 'In Review']:
            if self.parcel.status != 'Disputed':
                self.parcel.status = 'Disputed'
                self.parcel.save(skip_fingerprint=True)

    def __str__(self):
        return f"{self.case_number} - {self.parcel.khasra_no} ({self.status})"
