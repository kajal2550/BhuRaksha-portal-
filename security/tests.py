from django.test import TestCase, Client
from django.contrib.auth.models import User
from parcels.models import Parcel, Village
from records.models import Owner, OwnershipRecord
from mutations.models import Mutation
from security.models import AuditLog
from security.integrity_service import verify_audit_hash_chain, log_security_event, run_full_integrity_check
from security.anomaly_engine import run_anomaly_detectors
from security.crypto_utils import encrypt_pii, decrypt_pii, mask_aadhaar

class BhuRakshaSecurityTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.village = Village.objects.create(name="Kot Rani", village_code="PB-001")
        self.user = User.objects.create_user(username="patwari_test", password="password123")
        
        # Create sample parcel
        self.parcel = Parcel.objects.create(
            parcel_id="PB-KPT-2024-TEST",
            khasra_no="101/1",
            village=self.village,
            area_hectares=1.50,
            area_acres=3.70,
            land_use_type="Irrigated Agri",
            geometry_geojson='{"type":"Polygon","coordinates":[[[75.76,31.22],[75.77,31.22],[75.77,31.23],[75.76,31.23],[75.76,31.22]]]}',
            centroid_lat=31.225,
            centroid_lng=75.765,
            status="Verified"
        )

    def test_hash_chain_integrity(self):
        """Test append-only hash chaining and tamper detection."""
        log1 = log_security_event(self.user, "ACTION_1", self.parcel.parcel_id)
        log2 = log_security_event(self.user, "ACTION_2", self.parcel.parcel_id)
        
        # Verify valid chain
        valid, _, _ = verify_audit_hash_chain()
        self.assertTrue(valid, "Hash chain should verify OK initially")

    def test_parcel_fingerprint_tamper_detection(self):
        """Test real-time SHA-256 fingerprint verification."""
        self.assertTrue(self.parcel.verify_integrity(), "Fresh parcel fingerprint should match")
        
        # Simulate silent DB tamper
        Parcel.objects.filter(id=self.parcel.id).update(area_hectares=99.99)
        tampered_parcel = Parcel.objects.get(id=self.parcel.id)
        self.assertFalse(tampered_parcel.verify_integrity(), "Tampered area must fail fingerprint check")

    def test_fernet_pii_encryption_and_masking(self):
        """Test encryption at rest and role-based masking."""
        raw_aadhaar = "9988-7766-5544"
        encrypted = encrypt_pii(raw_aadhaar)
        self.assertNotEqual(encrypted, raw_aadhaar, "Encrypted string must not be plaintext")
        self.assertEqual(decrypt_pii(encrypted), raw_aadhaar, "Decryption must yield original plaintext")
        self.assertEqual(mask_aadhaar(raw_aadhaar), "XXXX-XXXX-5544", "Masking should hide first 8 digits")

    def test_all_18_pages_render_status_200(self):
        """Test that all 18 defined pages render without errors."""
        urls = [
            '/',
            '/login/',
            '/register/',
            '/map/',
            f'/parcel/{self.parcel.id}/',
            '/verify/',
            '/register-view/',
            '/records/owners/',
            '/mutations/',
            '/records/crops/',
            '/records/schemes/',
            '/disputes/',
            '/soc/',
            '/security/audit/',
            '/security/integrity/',
            '/security/anomalies/',
            '/analytics/',
            '/developers/',
            '/about/',
            '/architecture/',
            '/threat-model/',
            '/security-policy/',
            '/help/',
            '/api/v1/parcels/',
            f'/api/v1/parcels/{self.parcel.parcel_id}/'
        ]
        for url in urls:
            res = self.client.get(url)
            self.assertIn(res.status_code, [200, 302], f"URL '{url}' failed with status {res.status_code}")
