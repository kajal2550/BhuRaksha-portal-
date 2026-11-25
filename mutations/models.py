from django.db import models
from django.contrib.auth.models import User
from parcels.models import Parcel

class Mutation(models.Model):
    MUTATION_TYPES = [
        ('sale', 'Sale Deed / Registry Transfer'),
        ('inheritance', 'Inheritance / Varasat'),
        ('partition', 'Partition / Batwara'),
        ('gift', 'Gift Deed'),
        ('correction', 'Record Rectification / Correction'),
    ]

    STATUS_CHOICES = [
        ('Applied', 'Applied (Application Received)'),
        ('Under Review', 'Under Revenue Review'),
        ('Approved', 'Approved (Pending Ownership Commit)'),
        ('Completed', 'Completed (Ownership Transferred)'),
        ('Rejected', 'Rejected'),
    ]

    case_number = models.CharField(max_length=64, unique=True, verbose_name="Mutation Case ID")
    parcel = models.ForeignKey(Parcel, on_delete=models.CASCADE, related_name='mutations')
    mutation_type = models.CharField(max_length=30, choices=MUTATION_TYPES)
    
    applicant_name = models.CharField(max_length=150)
    applicant_aadhaar = models.CharField(max_length=20, default='XXXX-XXXX-9912')
    transferor_name = models.CharField(max_length=150)
    transferor_aadhaar = models.CharField(max_length=20, default='XXXX-XXXX-4412')
    
    assigned_officer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_mutations')
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='Applied')
    
    applied_date = models.DateField(auto_now_add=True)
    approved_date = models.DateField(blank=True, null=True)
    completion_date = models.DateField(blank=True, null=True)
    
    remarks = models.TextField(blank=True, null=True)
    document_proof = models.FileField(upload_to='mutation_docs/', blank=True, null=True)

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return f"{self.case_number} ({self.get_mutation_type_display()}) - {self.parcel.khasra_no}"


class MutationStepComment(models.Model):
    mutation = models.ForeignKey(Mutation, on_delete=models.CASCADE, related_name='steps')
    officer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    step_name = models.CharField(max_length=100)
    comment = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']


class Document(models.Model):
    parcel = models.ForeignKey(Parcel, on_delete=models.CASCADE, related_name='documents')
    title = models.CharField(max_length=150)
    doc_type = models.CharField(max_length=50, default='Registry / Sale Deed')
    file_url = models.CharField(max_length=255, default='/static/docs/sample_registry.pdf')
    uploaded_at = models.DateTimeField(auto_now_add=True)
