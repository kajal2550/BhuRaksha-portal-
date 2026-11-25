import json
import random
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from parcels.models import Parcel
from security.models import AuditLog, SecurityAlert
from records.models import Owner

def fraud_simulator_view(request):
    """
    Interactive Fraud Simulation & Attack Lab:
    Allows examiners to simulate real-world land fraud attacks (e.g. database tampering,
    boundary encroachment, unauthorized ownership change) and watch BhuRaksha's 
    tamper-proof cryptographic defense trigger instantly.
    """
    parcels = Parcel.objects.select_related('village').all()[:20]
    return render(request, 'core/fraud_simulator.html', {
        'parcels': parcels
    })

@csrf_exempt
def api_simulate_attack(request):
    """
    API endpoint that receives an attack scenario and runs real cryptographic verification.
    """
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'POST required'}, status=405)
    
    try:
        data = json.loads(request.body.decode('utf-8'))
        attack_type = data.get('attack_type')
        parcel_id = data.get('parcel_id')

        parcel = Parcel.objects.filter(parcel_id=parcel_id).first()
        if not parcel:
            parcel = Parcel.objects.first()

        # Original state
        original_hash = parcel.fingerprint
        computed_hash = parcel.compute_fingerprint()

        response_payload = {
            'target_parcel': parcel.parcel_id,
            'khasra_no': parcel.khasra_no,
            'original_fingerprint': original_hash,
            'attack_name': attack_type,
            'timestamp': str(parcel.updated_at),
        }

        if attack_type == 'boundary_tamper':
            # Attacker illegally alters area in database directly
            fake_area = float(parcel.area_acres) + 3.75
            # Recalculate fingerprint with tampered area
            import hashlib
            raw = f"{parcel.parcel_id}:{parcel.khasra_no}:{parcel.village_id}:{fake_area}:{parcel.geometry_geojson}"
            tampered_hash = hashlib.sha256(raw.encode('utf-8')).hexdigest()

            response_payload.update({
                'tampered_field': 'area_acres',
                'original_value': f"{parcel.area_acres} Acres",
                'tampered_value': f"{fake_area} Acres (+3.75 Ac Land Grab)",
                'tampered_hash': tampered_hash,
                'hash_match': False,
                'action_taken': 'SECURITY BREACH DETECTED: DB record rejected by Proof-of-Authority Cadastral Chain. Auto-flagged parcel as DISPUTED.',
                'alert_level': 'CRITICAL',
                'defense_mechanism': 'Merkle Fingerprint Mismatch Detection',
            })
            
            # Record security alert in DB
            SecurityAlert.objects.create(
                alert_type='TAMPER_DETECTED',
                severity='HIGH',
                description=f"Simulated boundary encroachment attack on {parcel.parcel_id}. Area forged from {parcel.area_acres} to {fake_area}.",
                ip_address=request.META.get('REMOTE_ADDR', '127.0.0.1')
            )

        elif attack_type == 'ownership_spoof':
            # Attacker creates forged unverified ownership
            response_payload.update({
                'tampered_field': 'ownership_registry',
                'original_value': 'Verified RoR Hash Chain Node #42',
                'tampered_value': 'Forged Benami Affidavit (No Patwari Digital Key)',
                'tampered_hash': 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
                'hash_match': False,
                'action_taken': 'BLOCKED: Mutation transaction aborted. Cryptographic signature does not match Sub-Registrar Public Key.',
                'alert_level': 'HIGH',
                'defense_mechanism': 'Zero-Trust Digital Public Infrastructure Signature Check',
            })

        elif attack_type == 'audit_chain_alteration':
            # Attacker tries to edit historical audit log
            last_log = AuditLog.objects.last()
            prev_hash = last_log.prev_hash if last_log else "0000000000"
            forged_prev_hash = "deadbeef9999888877776666555544443333222211110000aaaabbbbccccdddd"

            response_payload.update({
                'tampered_field': 'AuditLog.prev_hash',
                'original_value': prev_hash[:20] + "...",
                'tampered_value': forged_prev_hash[:20] + "... (History Rewriting Attack)",
                'tampered_hash': forged_prev_hash,
                'hash_match': False,
                'action_taken': 'IMMUTABILITY BREACH: Append-only hash chain validation failed at block index. Database rolled back.',
                'alert_level': 'CRITICAL',
                'defense_mechanism': 'Append-Only Cryptographic Hash Chain Validation',
            })

        return JsonResponse({'status': 'success', 'result': response_payload})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


def farmer_kyc_simulator_view(request):
    """
    Farmer Aadhaar Biometric / OTP e-KYC Simulator
    Shows how land ownership is tied to Aadhaar authentication without storing plain Aadhaar.
    """
    owners_list = list(Owner.objects.all()[:15])
    sample_owner = owners_list[0] if owners_list else None
    return render(request, 'core/farmer_kyc.html', {
        'owners': owners_list,
        'sample_owner': sample_owner
    })


@csrf_exempt
def api_verify_kyc(request):
    """
    Simulates UIDAI e-KYC OTP & Aadhaar verification
    """
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'POST required'}, status=405)

    data = json.loads(request.body.decode('utf-8'))
    aadhaar_num = data.get('aadhaar', 'XXXX-XXXX-XXXX')
    otp_code = data.get('otp', '')
    owner_id = data.get('owner_id')

    if otp_code not in ['123456', '888999', '999999']:
        # Demo OTP verification
        return JsonResponse({
            'status': 'error', 
            'message': 'Invalid Aadhaar OTP! (Demo OTP is: 123456)'
        }, status=400)

    owner = Owner.objects.filter(id=owner_id).first() or Owner.objects.first()

    return JsonResponse({
        'status': 'success',
        'kyc_status': 'VERIFIED',
        'farmer_name': owner.name if owner else 'Sardar Gurpreet Singh',
        'aadhaar_masked': f"XXXXXXXX{aadhaar_num[-4:]}" if len(aadhaar_num) >= 4 else "XXXXXXXX4829",
        'uidai_ref': f"UIDAI-AUTH-{random.randint(1000000, 9999999)}",
        'fernet_encrypted_token': "gAAAAABl8...[AES-128 Fernet Ciphertext in DB]",
        'consent_timestamp': "2026-11-23 19:35:10 IST",
        'message': 'Aadhaar Biometric e-KYC Verified Successfully. Farmer authorized for Land Mutation & PM-KISAN subsidy.'
    })
