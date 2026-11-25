import json
import hashlib
from typing import Tuple, List, Dict
from security.models import AuditLog, SecurityAlert
from parcels.models import Parcel

def verify_audit_hash_chain() -> Tuple[bool, int, str]:
    """
    Traverse full AuditLog table from id=1 to end.
    Verifies that for every log:
      1. prev_hash equals previous log's current_hash
      2. current_hash equals calculate_hash()
    Returns: (is_valid, broken_log_id, message)
    """
    logs = list(AuditLog.objects.order_by('id'))
    if not logs:
        return True, 0, "Audit log is empty. Chain is pristine."

    expected_prev = '0' * 64
    for i, log in enumerate(logs):
        if log.prev_hash != expected_prev:
            return False, log.id, f"Broken chain link at log #{log.id}: prev_hash does not match previous block's hash."

        # Check recalculation
        recalc = log.calculate_hash()
        if log.current_hash != recalc:
            return False, log.id, f"Tampered record at log #{log.id}: stored hash {log.current_hash[:12]} does not match content hash {recalc[:12]}."

        expected_prev = log.current_hash

    return True, 0, f"Full audit chain verified OK. Total {len(logs)} tamper-evident blocks validated."


def log_security_event(user, action: str, parcel_ref: str, old_vals=None, new_vals=None, request=None) -> AuditLog:
    """Helper to append an immutable entry to the SHA-256 hash chain."""
    ip = request.META.get('REMOTE_ADDR') if request else '127.0.0.1'
    ua = request.META.get('HTTP_USER_AGENT', 'System/Backend') if request else 'System/Backend'
    
    role = 'system'
    if user and user.is_authenticated:
        if hasattr(user, 'profile'):
            role = user.profile.role
        elif user.is_superuser:
            role = 'admin'

    log_entry = AuditLog(
        user=user if (user and user.is_authenticated) else None,
        user_role=role,
        action=action,
        parcel_ref=parcel_ref,
        old_values=old_vals,
        new_values=new_vals,
        ip_address=ip,
        user_agent=ua
    )
    log_entry.save()
    return log_entry


def run_full_integrity_check(user=None) -> Dict:
    """
    Validates SHA-256 fingerprints across ALL parcels in the system.
    Identifies any record that was silently modified in the DB.
    """
    from security.models import IntegrityReport
    parcels = Parcel.objects.all()
    passed = 0
    failed = 0
    tampered_ids = []

    for p in parcels:
        if p.verify_integrity():
            passed += 1
        else:
            failed += 1
            tampered_ids.append({
                "parcel_id": p.parcel_id,
                "khasra_no": p.khasra_no,
                "stored_fingerprint": p.fingerprint,
                "recalculated": p.calculate_fingerprint()
            })
            # Mark parcel as tampered in memory/db
            if p.status != 'Tampered':
                p.status = 'Tampered'
                p.save(skip_fingerprint=True)
                # Create critical alert
                SecurityAlert.objects.get_or_create(
                    alert_type="CRYPTOGRAPHIC_INTEGRITY_FAIL",
                    parcel_ref=p.parcel_id,
                    defaults={
                        "severity": "CRITICAL",
                        "description": f"Silent modification detected! Parcel {p.parcel_id} fingerprint mismatch.",
                        "status": "open"
                    }
                )

    chain_valid, broken_id, chain_msg = verify_audit_hash_chain()

    report = IntegrityReport.objects.create(
        run_by=user if (user and user.is_authenticated) else None,
        total_parcels_checked=parcels.count(),
        passed_count=passed,
        failed_count=failed,
        tampered_parcels_list=tampered_ids,
        hash_chain_valid=chain_valid
    )

    return {
        "report_id": report.id,
        "total": parcels.count(),
        "passed": passed,
        "failed": failed,
        "tampered_parcels": tampered_ids,
        "hash_chain_valid": chain_valid,
        "chain_message": chain_msg
    }
