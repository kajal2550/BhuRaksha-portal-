import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.db.models import Count
from django.contrib import messages
from .models import AuditLog, SecurityAlert, IntegrityReport, Notification, APIToken
from .integrity_service import verify_audit_hash_chain, run_full_integrity_check, log_security_event
from .anomaly_engine import run_anomaly_detectors
from accounts.models import LoginHistory
from parcels.models import Parcel

def soc_dashboard_view(request):
    """Page 10: Security Operations Center (SOC) Dashboard (Auditor / Admin)."""
    logs = AuditLog.objects.order_by('-id')[:30]
    alerts = SecurityAlert.objects.order_by('-id')[:15]
    failed_logins = LoginHistory.objects.filter(status='FAILED')[:10]
    active_tokens = APIToken.objects.filter(is_active=True)

    total_parcels = Parcel.objects.count()
    tampered_parcels = Parcel.objects.filter(status='Tampered').count()
    integrity_rate = round(((total_parcels - tampered_parcels) / total_parcels * 100), 1) if total_parcels else 100

    chain_valid, broken_id, chain_msg = verify_audit_hash_chain()

    context = {
        'logs': logs,
        'alerts': alerts,
        'failed_logins': failed_logins,
        'active_tokens': active_tokens,
        'total_parcels': total_parcels,
        'tampered_parcels': tampered_parcels,
        'integrity_rate': integrity_rate,
        'chain_valid': chain_valid,
        'chain_message': chain_msg,
    }
    return render(request, 'security/soc_dashboard.html', context)


def audit_trail_view(request):
    """Page 11: Tamper-Evident Audit Log Module with Hash Chain verification."""
    q = request.GET.get('q', '').strip()
    action = request.GET.get('action', '').strip()

    logs = AuditLog.objects.all().order_by('-id')
    if q:
        logs = logs.filter(parcel_ref__icontains=q)
    if action:
        logs = logs.filter(action=action)

    chain_valid, broken_id, chain_msg = verify_audit_hash_chain()

    if request.GET.get('export') == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="bhuraksha_tamper_evident_audit.csv"'
        response.write("ID,TIMESTAMP,ACTION,PARCEL_REF,USER,ROLE,PREV_HASH,CURRENT_HASH\n")
        for l in logs:
            response.write(f'{l.id},"{l.timestamp}","{l.action}","{l.parcel_ref}","{l.user}","{l.user_role}","{l.prev_hash}","{l.current_hash}"\n')
        return response

    return render(request, 'security/audit_trail.html', {
        'logs': logs[:80],
        'chain_valid': chain_valid,
        'broken_id': broken_id,
        'chain_message': chain_msg,
        'q': q,
        'action': action,
    })


def verify_chain_action(request):
    """Triggers instant cryptographic hash chain verification."""
    chain_valid, broken_id, msg = verify_audit_hash_chain()
    if chain_valid:
        messages.success(request, f"Cryptographic Verification PASS: {msg}")
    else:
        messages.error(request, f"TAMPER ALERT DETECTED: {msg}")
    return redirect('audit_trail')


def integrity_verify_page(request):
    """Page 12: Integrity Verification Module."""
    reports = IntegrityReport.objects.all()[:10]
    
    if request.method == 'POST':
        res = run_full_integrity_check(request.user)
        if res['failed'] > 0:
            messages.error(request, f"CRITICAL: {res['failed']} tampered parcels detected! Marked in red on map.")
        else:
            messages.success(request, f"Integrity check completed: All {res['total']} parcels verified OK with 100% SHA-256 fingerprint matches.")
        return redirect('integrity_verify')

    return render(request, 'security/integrity.html', {'reports': reports})


def anomalies_list_view(request):
    """Page 13: Anomaly & Fraud Detection Module."""
    if request.method == 'POST':
        new_alerts = run_anomaly_detectors()
        messages.success(request, f"Anomaly detection scan completed. Found {len(new_alerts)} new threat anomalies.")
        return redirect('anomalies_list')

    alerts = SecurityAlert.objects.all()
    return render(request, 'security/anomalies.html', {'alerts': alerts})


def notifications_view(request):
    """Page 17: User In-App Notifications."""
    if not request.user.is_authenticated:
        return redirect('login')
    notifs = Notification.objects.filter(user=request.user)
    notifs.update(is_read=True)
    return render(request, 'security/notifications.html', {'notifications': notifs})


def profile_view(request):
    """Page 17: Profile & Sessions."""
    if not request.user.is_authenticated:
        return redirect('login')
    
    my_history = LoginHistory.objects.filter(user=request.user)[:10]
    my_logs = AuditLog.objects.filter(user=request.user).order_by('-id')[:10]
    return render(request, 'accounts/profile.html', {'history': my_history, 'logs': my_logs})


def admin_users_view(request):
    """Page 16: Admin User Management."""
    if not (request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.role == 'admin')):
        messages.error(request, "Permission denied. Administrator privileges required.")
        return redirect('home')

    users = User.objects.select_related('profile').all()
    return render(request, 'accounts/admin_users.html', {'users': users})
