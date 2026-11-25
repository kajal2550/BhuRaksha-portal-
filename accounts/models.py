from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('public', 'Public (Citizen)'),
        ('farmer', 'Farmer (Land Owner)'),
        ('revenue_officer', 'Revenue Officer (Patwari / Tehsildar)'),
        ('agri_officer', 'Agricultural Officer'),
        ('auditor', 'Security & Compliance Auditor'),
        ('admin', 'System Administrator'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=30, choices=ROLE_CHOICES, default='public')
    phone = models.CharField(max_length=20, blank=True, null=True)
    aadhaar_number = models.CharField(max_length=20, blank=True, null=True, help_text="Stored for farmer lookup")
    department = models.CharField(max_length=100, blank=True, null=True)
    mfa_enabled = models.BooleanField(default=False)
    mfa_secret = models.CharField(max_length=64, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} [{self.get_role_display()}]"


class LoginHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='login_history', null=True, blank=True)
    username_attempted = models.CharField(max_length=150)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=[('SUCCESS', 'Success'), ('FAILED', 'Failed'), ('MFA_PENDING', 'MFA Pending'), ('LOCKED_OUT', 'Locked Out')])
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
