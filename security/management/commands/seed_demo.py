import os
import json
import random
from datetime import date, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django_otp.plugins.otp_totp.models import TOTPDevice

from accounts.models import UserProfile, LoginHistory
from parcels.models import Village, Parcel
from records.models import Owner, OwnershipRecord, CropRecord, Scheme, SchemeEligibility
from mutations.models import Mutation, MutationStepComment, Document
from disputes.models import Dispute
from security.models import AuditLog, SecurityAlert, Notification, APIToken
from security.integrity_service import log_security_event
from security.anomaly_engine import run_anomaly_detectors

class Command(BaseCommand):
    help = "Seed realistic demo data: 2 villages in Punjab, 50 cadastral parcels, 40 owners, crops, mutations, disputes, 6 RBAC users, and QGIS GeoJSON export."

    def handle(self, *args, **options):
        self.stdout.write("🚀 Starting BhuRaksha Complete Seed Process...")

        # 1. Create RBAC Demo Users
        users_config = [
            ("admin_user", "admin123", "admin", "System Administrator", "Cyber Operations"),
            ("auditor_user", "audit123", "auditor", "Chief Security Auditor", "Vigilance & Compliance"),
            ("revenue_officer", "patwari123", "revenue_officer", "Sardar Harpreet Singh", "Revenue Department"),
            ("agri_officer", "agri123", "agri_officer", "Dr. Gurpreet Kaur", "Agriculture & FoodTech"),
            ("farmer_user", "kisan123", "farmer", "Jarnail Singh Dhillon", "Local Farmer"),
            ("public_user", "public123", "public", "Rajesh Sharma", "Citizen / Public"),
        ]

        for username, password, role, full_name, dept in users_config:
            user, created = User.objects.get_or_create(username=username)
            user.set_password(password)
            user.first_name = full_name.split()[0]
            user.last_name = " ".join(full_name.split()[1:])
            user.email = f"{username}@bhuraksha.gov.in"
            if role == 'admin':
                user.is_staff = True
                user.is_superuser = True
            user.save()

            profile, _ = UserProfile.objects.get_or_create(user=user)
            profile.role = role
            profile.department = dept
            profile.phone = f"+91 9814{random.randint(100000, 999999)}"
            profile.mfa_enabled = (role in ['admin', 'auditor', 'revenue_officer'])
            profile.save()

            # Create default TOTP device for MFA users
            if profile.mfa_enabled:
                device, _ = TOTPDevice.objects.get_or_create(user=user, name='default')
                device.confirmed = True
                device.save()

        self.stdout.write("✅ 6 RBAC Users Created with Credentials.")

        # 2. Create 2 Punjab Villages around Phagwara
        v1, _ = Village.objects.get_or_create(
            village_code="PB-KPT-PHG-001",
            defaults={
                "name": "Kot Rani",
                "tehsil": "Phagwara",
                "district": "Kapurthala",
                "state": "Punjab"
            }
        )
        v2, _ = Village.objects.get_or_create(
            village_code="PB-KPT-PHG-002",
            defaults={
                "name": "Khera Dehat",
                "tehsil": "Phagwara",
                "district": "Kapurthala",
                "state": "Punjab"
            }
        )

        # 3. Create Schemes
        s1, _ = Scheme.objects.get_or_create(
            code="PM-KISAN-PB",
            defaults={
                "name": "PM-KISAN Samman Nidhi",
                "description": "Financial support of ₹6,000/year to landholding farmer families.",
                "subsidy_amount_per_ha": 6000.00,
                "max_area_hectares": 10.0
            }
        )
        s2, _ = Scheme.objects.get_or_create(
            code="PMFBY-INSURANCE",
            defaults={
                "name": "Pradhan Mantri Fasal Bima Yojana",
                "description": "Comprehensive risk insurance cover for food and oilseed crops against non-preventable natural risks.",
                "subsidy_amount_per_ha": 4500.00,
                "max_area_hectares": 20.0
            }
        )
        s3, _ = Scheme.objects.get_or_create(
            code="DRIP-PUNJAB",
            defaults={
                "name": "Punjab Micro-Irrigation Subsidy",
                "description": "80% capital subsidy for drip and sprinkler irrigation in water-stressed blocks.",
                "subsidy_amount_per_ha": 12000.00,
                "max_area_hectares": 5.0
            }
        )

        # 4. Generate 40 Owners with Fernet Encrypted PII
        first_names = ["Jarnail", "Gurmeet", "Harbhajan", "Manpreet", "Balwinder", "Kuldeep", "Sukhdev", "Jaswinder", "Amardeep", "Davinder", "Surinder", "Satnam", "Paramjit", "Gursharan", "Bhupinder", "Joginder"]
        last_names = ["Singh", "Kaur", "Dhillon", "Sandhu", "Grewal", "Sidhu", "Virk", "Bains", "Cheema", "Deol", "Mann", "Gill", "Pannu"]

        owners = []
        for i in range(40):
            fn = first_names[i % len(first_names)]
            ln = last_names[(i * 3) % len(last_names)]
            name = f"{fn} {ln}"
            owner = Owner(
                name=name,
                pm_kisan_id=f"PMK-PB-{2024000 + i}" if i % 2 == 0 else None,
                soil_health_card_no=f"SHC-PB-{5500 + i}",
                address=f"Village Kot Rani / Khera, Tehsil Phagwara, Kapurthala"
            )
            # Use encrypted setters
            raw_aadhaar = f"{random.randint(2000, 9999)}-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}"
            raw_phone = f"+91 9814{random.randint(100000, 999999)}"
            owner.set_aadhaar(raw_aadhaar)
            owner.set_phone(raw_phone)
            owner.save()
            owners.append(owner)

        self.stdout.write(f"✅ 40 Land Owners created with Fernet PII Encryption.")

        # 5. Generate 50 Realistic Cadastral Parcels around Phagwara (Lat: 31.22° N, Lng: 75.77° E)
        base_lat = 31.2200
        base_lng = 75.7680
        step_lat = 0.0016
        step_lng = 0.0022
        cols = 5

        crops_pool = [
            ("Wheat (PBW-725)", "Rabi", 48.0),
            ("Paddy / Basmati (Pusa-1121)", "Kharif", 42.5),
            ("Mustard (Giriraj)", "Rabi", 19.5),
            ("Potato (Kufri Pukhraj)", "Rabi", 130.0),
            ("Maize (PMH-1)", "Kharif", 45.0),
            ("Sugarcane (CoJ-88)", "Perennial", 120.0),
            ("Summer Moong (SML-668)", "Zaid", 14.0),
        ]

        parcels = []
        geojson_features = []

        for i in range(50):
            r = i // cols
            c = i % cols
            village = v1 if i < 30 else v2

            min_lng = round(base_lng + (c * step_lng) + (random.uniform(-0.0001, 0.0001)), 6)
            max_lng = round(min_lng + step_lng - 0.0003, 6)
            min_lat = round(base_lat + (r * step_lat) + (random.uniform(-0.0001, 0.0001)), 6)
            max_lat = round(min_lat + step_lat - 0.0002, 6)

            poly_coords = [
                [min_lng, min_lat],
                [max_lng, min_lat],
                [max_lng, max_lat],
                [min_lng, max_lat],
                [min_lng, min_lat]
            ]
            centroid_lat = round((min_lat + max_lat) / 2, 6)
            centroid_lng = round((min_lng + max_lng) / 2, 6)

            ulpin = f"PB-KPT-2024-{1000 + i}"
            khasra_no = f"{101 + i//2}/{1 + (i % 2)}"
            area_ha = round(0.60 + (i * 0.14) % 3.2, 2)
            area_ac = round(area_ha * 2.47105, 2)

            # Assign statuses (dispute on 5 parcels)
            if i in [7, 18, 31, 42]:
                status = 'Disputed'
            elif i in [4, 15, 26]:
                status = 'Mutation Pending'
            else:
                status = 'Verified'

            land_use = 'Irrigated Agri'
            if i in [12, 35]:
                land_use = 'Residential/Abadi'
            elif i in [20, 48]:
                land_use = 'Commercial/FoodTech'
            elif i in [25]:
                land_use = 'Forest/Pasture'

            geom_dict = {"type": "Polygon", "coordinates": [poly_coords]}
            geom_str = json.dumps(geom_dict)

            parcel = Parcel(
                parcel_id=ulpin,
                khasra_no=khasra_no,
                village=village,
                area_hectares=area_ha,
                area_acres=area_ac,
                land_use_type=land_use,
                soil_type="Alluvial Sandy Loam" if i % 2 == 0 else "Rich Alluvial Loam",
                irrigation_source="Canal & Solar Tubewell" if i % 3 == 0 else "Deep Tube Well",
                status=status,
                geometry_geojson=geom_str,
                centroid_lat=centroid_lat,
                centroid_lng=centroid_lng
            )
            parcel.save()
            parcels.append(parcel)

            # Link Primary Owner
            primary_owner = owners[i % len(owners)]
            OwnershipRecord.objects.create(
                parcel=parcel,
                owner=primary_owner,
                share_percentage=100.0,
                status='Active' if status != 'Disputed' else 'Disputed'
            )

            # Link Crop Record
            crop_name, season, est_yield = crops_pool[i % len(crops_pool)]
            CropRecord.objects.create(
                parcel=parcel,
                crop=crop_name,
                season=season,
                variety="PAU Recommended",
                sowing_date=date(2024, 11, 15) if season == "Rabi" else date(2024, 6, 20),
                harvest_date=date(2025, 4, 20) if season == "Rabi" else date(2024, 10, 25),
                estimated_yield_quintals=est_yield,
                irrigation_used=parcel.irrigation_source
            )

            # Link Scheme Eligibility
            SchemeEligibility.objects.create(
                parcel=parcel,
                scheme=s1,
                is_eligible=(parcel.area_hectares <= 10.0),
                reason="Landholding fits PM-KISAN small/medium farmer criterion"
            )

            # Add to QGIS GeoJSON FeatureCollection
            geojson_features.append({
                "type": "Feature",
                "id": parcel.id,
                "geometry": geom_dict,
                "properties": {
                    "parcel_id": parcel.parcel_id,
                    "khasra_no": parcel.khasra_no,
                    "village": village.name,
                    "owner": primary_owner.name,
                    "area_ha": parcel.area_hectares,
                    "land_use": parcel.land_use_type,
                    "crop": crop_name,
                    "status": parcel.status,
                    "fingerprint": parcel.fingerprint
                }
            })

        # Save QGIS Export file
        qgis_file_path = os.path.join("data", "parcels_phagwara_qgis.geojson")
        with open(qgis_file_path, "w", encoding="utf-8") as f:
            json.dump({"type": "FeatureCollection", "features": geojson_features}, f, indent=2)

        self.stdout.write(f"✅ 50 Cadastral Parcels created & exported to {qgis_file_path}.")

        # 6. Generate 15 Mutations with Steps & Documents
        mutation_types = ["sale", "inheritance", "partition", "gift", "correction"]
        officer = User.objects.get(username="revenue_officer")

        for m_idx in range(15):
            p = parcels[m_idx * 3 % len(parcels)]
            m_type = mutation_types[m_idx % len(mutation_types)]
            status_val = "Completed" if m_idx < 8 else ("Under Review" if m_idx < 12 else "Applied")
            
            mut = Mutation.objects.create(
                case_number=f"MUT/PB/{2024}/{500 + m_idx}",
                parcel=p,
                mutation_type=m_type,
                applicant_name=owners[(m_idx + 5) % len(owners)].name,
                transferor_name=owners[m_idx % len(owners)].name,
                assigned_officer=officer,
                status=status_val,
                remarks=f"Registered deed #{7800 + m_idx} verified by Sub-Registrar Phagwara."
            )
            MutationStepComment.objects.create(
                mutation=mut,
                officer=officer,
                step_name="Field Inspection & Verification",
                comment="Patwari physical boundary check matched cadastral map. No unauthorized construction found."
            )
            Document.objects.create(
                parcel=p,
                title=f"Registered Sale Deed #{7800 + m_idx}",
                doc_type="Deed / Registry",
                file_url="/static/docs/sample_registry.pdf"
            )

        self.stdout.write("✅ 15 Mutation Cases and Documents Generated.")

        # 7. Generate 8 Disputes with Map Coordinate Pins
        dispute_types = ['boundary_overlap', 'title_forgery', 'inheritance_claim', 'area_mismatch', 'bank_lien']
        for d_idx in range(8):
            dp = parcels[(d_idx * 6) % len(parcels)]
            Dispute.objects.create(
                case_number=f"DSP/PB/{2024}/{100 + d_idx}",
                parcel=dp,
                dispute_type=dispute_types[d_idx % len(dispute_types)],
                complainant_name=f"Claimant {owners[(d_idx + 8) % len(owners)].name}",
                complainant_contact="+91 98144 00112",
                description=f"Formal objection filed against boundary realignment or mutation claim on Khasra {dp.khasra_no}.",
                pin_lat=dp.centroid_lat + 0.0002,
                pin_lng=dp.centroid_lng + 0.0002,
                status='Open' if d_idx % 2 == 0 else 'In Review',
                assigned_officer=officer
            )

        self.stdout.write("✅ 8 Disputes with Geographic Pins Generated.")

        # 8. Create API Tokens for External Banks & PM-KISAN
        APIToken.objects.get_or_create(
            client_name="State Bank of India (Agri-Credit Division)",
            token_key="sbi-agri-dpi-secret-live-token-998811",
            department_role="bank_collateral_verification",
            rate_limit_per_minute=120
        )
        APIToken.objects.get_or_create(
            client_name="Agricultural Insurance Company of India (PMFBY)",
            token_key="aic-pmfby-dpi-secret-live-token-776622",
            department_role="crop_insurance_validation",
            rate_limit_per_minute=200
        )

        # 9. Create Initial Chain-Logged Seed Audit Entries
        admin_u = User.objects.get(username="admin_user")
        log_security_event(
            user=admin_u,
            action="SYSTEM_INITIAL_SEED",
            parcel_ref="SYSTEM_CORE",
            old_vals={"state": "Uninitialized"},
            new_vals={"parcels_seeded": 50, "villages": 2, "hash_chain_active": True}
        )

        # 10. Run Anomaly Detectors
        alerts = run_anomaly_detectors()
        self.stdout.write(f"✅ Anomaly Engine checked. Generated {len(alerts)} initial threat detections.")

        self.stdout.write("\n=======================================================")
        self.stdout.write("🎉 BHURAKSHA SEED PROCESS COMPLETED SUCCESSFULLY!")
        self.stdout.write("=======================================================")
        self.stdout.write("Demo Users Created:")
        for u, p, r, name, dept in users_config:
            self.stdout.write(f"  • {r.upper():<16} | User: {u:<16} | Pass: {p:<12}")
        self.stdout.write("=======================================================\n")
