from django.db import models
from django.contrib.auth.models import User
import hashlib
import json

class AuditLog(models.Model):
    """
    Append-only SHA-256 Hash Chained Audit Log.
    prev_hash links to previous block, current_hash seals the record.
    """
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    user_role = models.CharField(max_length=50, default='system')
    action = models.CharField(max_length=100)
    parcel_ref = models.CharField(max_length=100, default='SYSTEM')
    old_values = models.JSONField(blank=True, null=True)
    new_values = models.JSONField(blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    prev_hash = models.CharField(max_length=64, default='0' * 64)
    current_hash = models.CharField(max_length=64, blank=True, null=True)

    class Meta:
        ordering = ['id']

    def calculate_hash(self) -> str:
        """Compute SHA-256(prev_hash + user + action + parcel_ref + timestamp + new_values)."""
        ts_str = self.timestamp.isoformat() if self.timestamp else "NEW"
        payload = f"{self.prev_hash}|{self.user_id}|{self.action}|{self.parcel_ref}|{json.dumps(self.new_values, sort_keys=True)}|{ts_str}"
        return hashlib.sha256(payload.encode('utf-8')).hexdigest()

    def save(self, *args, **kwargs):
        # Enforce append-only: block edits on existing rows
        if self.pk:
            raise PermissionError("AuditLog entries are immutable and cannot be updated.")
        
        # Link to the previous hash
        last_log = AuditLog.objects.order_by('-id').first()
        self.prev_hash = last_log.current_hash if (last_log and last_log.current_hash) else '0' * 64
        
        super().save(*args, **kwargs)
        
        # Now seal with current_hash using generated timestamp
        if not self.current_hash:
            self.current_hash = self.calculate_hash()
            super().save(update_fields=['current_hash'])

    def delete(self, *args, **kwargs):
        raise PermissionError("AuditLog entries cannot be deleted.")

    def __str__(self):
        return f"[{self.id}] {self.action} on {self.parcel_ref} ({self.current_hash[:8]}...)"


class SecurityAlert(models.Model):
    SEVERITY_CHOICES = [
        ('LOW', 'Low Risk'),
        ('MEDIUM', 'Medium Risk'),
        ('HIGH', 'High Risk'),
        ('CRITICAL', 'Critical Fraud Alert'),
    ]
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('investigating', 'Investigating'),
        ('resolved', 'Resolved'),
    ]

    alert_type = models.CharField(max_length=100)
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='MEDIUM')
    parcel_ref = models.CharField(max_length=100, blank=True, null=True)
    user_involved = models.CharField(max_length=150, blank=True, null=True)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.severity}] {self.alert_type} - {self.parcel_ref}"


class IntegrityReport(models.Model):
    run_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    total_parcels_checked = models.IntegerField()
    passed_count = models.IntegerField()
    failed_count = models.IntegerField()
    tampered_parcels_list = models.JSONField(default=list)
    hash_chain_valid = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=150)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']


class APIToken(models.Model):
    client_name = models.CharField(max_length=150, help_text="e.g. State Bank of India, PM-KISAN Portal, AIC of India")
    token_key = models.CharField(max_length=64, unique=True)
    department_role = models.CharField(max_length=50, default='bank_verification')
    rate_limit_per_minute = models.IntegerField(default=60)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.client_name} ({self.department_role})"
