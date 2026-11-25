import os
import sys
import json
import random
import hashlib
from datetime import date

# Setup Django Environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'landgov_project.settings')

import django
django.setup()

from parcels.models import Village, Parcel
from records.models import Owner, OwnershipRecord, CropRecord
from mutations.models import Mutation
from security.models import AuditLog

def generate_grid_polygon(center_lat, center_lng, row, col, size=0.0018):
    """
    Generates realistic rectangular/trapezoidal cadastral farm polygons 
    around actual village coordinates in India.
    """
    offset_x = (col - 2) * size
    offset_y = (row - 2) * size

    # Subtle natural boundary jitter to mimic real BhuNaksha field boundaries
    j1 = random.uniform(-0.0001, 0.0001)
    j2 = random.uniform(-0.0001, 0.0001)

    min_lng = center_lng + offset_x
    max_lng = min_lng + size
    min_lat = center_lat + offset_y
    max_lat = min_lat + size

    coords = [
        [round(min_lng, 6), round(min_lat, 6)],
        [round(max_lng + j1, 6), round(min_lat, 6)],
        [round(max_lng, 6), round(max_lat + j2, 6)],
        [round(min_lng + j2, 6), round(max_lat, 6)],
        [round(min_lng, 6), round(min_lat, 6)]
    ]

    geojson = {
        "type": "Polygon",
        "coordinates": [coords]
    }
    return json.dumps(geojson), round((min_lat + max_lat)/2, 6), round((min_lng + max_lng)/2, 6)

def seed_national_cadastre():
    print("=== SEEDING ALL-INDIA MULTI-STATE BHUNAKSHA CADASTRAL CLUSTERS ===")

    # 5 Major Indian Agricultural States & Real Villages
    STATE_VILLAGES = [
        {
            "name": "Kot Rani (Phagwara)",
            "code": "PB-KOT-01",
            "district": "Kapurthala",
            "state": "Punjab",
            "lat": 31.2245,
            "lng": 75.7721,
            "crops": ["Wheat", "Paddy (Basmati)", "Mustard", "Sugarcane"],
            "soil": "Alluvial Loam"
        },
        {
            "name": "Chhata Rural (Mathura)",
            "code": "UP-CHH-02",
            "district": "Mathura",
            "state": "Uttar Pradesh",
            "lat": 27.7214,
            "lng": 77.5028,
            "crops": ["Wheat", "Mustard", "Bajra", "Potato"],
            "soil": "Clayey Alluvial"
        },
        {
            "name": "Bicholi Mardana (Indore)",
            "code": "MP-IND-03",
            "district": "Indore",
            "state": "Madhya Pradesh",
            "lat": 22.6841,
            "lng": 75.9189,
            "crops": ["Soybean", "Wheat", "Gram (Chana)", "Cotton"],
            "soil": "Black Cotton Soil"
        },
        {
            "name": "Baramati Rural (Pune)",
            "code": "MH-BAR-04",
            "district": "Pune",
            "state": "Maharashtra",
            "lat": 18.1524,
            "lng": 74.5768,
            "crops": ["Sugarcane", "Jowar", "Grapes", "Onion"],
            "soil": "Medium Black"
        },
        {
            "name": "Mandar Rural (Ranchi)",
            "code": "JH-MAN-05",
            "district": "Ranchi",
            "state": "Jharkhand",
            "lat": 23.4568,
            "lng": 85.0842,
            "crops": ["Paddy", "Maize", "Mustard", "Pulses"],
            "soil": "Red Laterite"
        }
    ]

    total_parcels_created = 0

    for v_info in STATE_VILLAGES:
        # Create or update Village
        village, _ = Village.objects.get_or_create(
            name=f"{v_info['name']}, {v_info['state']}",
            defaults={
                'village_code': v_info['code'],
                'district': v_info['district'],
                'tehsil': v_info['district'],
                'state': v_info['state'],
                'boundary_geojson': json.dumps({
                    "type": "Polygon",
                    "coordinates": [[[v_info['lng']-0.01, v_info['lat']-0.01], [v_info['lng']+0.01, v_info['lat']-0.01], [v_info['lng']+0.01, v_info['lat']+0.01], [v_info['lng']-0.01, v_info['lat']+0.01], [v_info['lng']-0.01, v_info['lat']-0.01]]]
                })
            }
        )

        print(f"Creating parcels for State: {v_info['state']} | Village: {village.name}...")

        # 16-20 Plots per village to build an All-India cluster
        plot_idx = 1
        for r in range(4):
            for c in range(4):
                khasra = f"{100 + plot_idx}/{r+1}"
                ulpin = f"{v_info['code'][:2]}2026{random.randint(10000000, 99999999)}"
                geom_json, c_lat, c_lng = generate_grid_polygon(v_info['lat'], v_info['lng'], r, c)
                area_acres = round(random.uniform(1.2, 5.8), 2)
                area_ha = round(area_acres * 0.404686, 2)
                status = random.choice(['Verified', 'Verified', 'Verified', 'Mutation Pending', 'Disputed'])

                # Merkle Hash Fingerprint
                raw_fp = f"{ulpin}:{khasra}:{village.id}:{area_acres}:{geom_json}"
                fingerprint = hashlib.sha256(raw_fp.encode('utf-8')).hexdigest()

                parcel, created = Parcel.objects.get_or_create(
                    parcel_id=ulpin,
                    defaults={
                        'khasra_no': khasra,
                        'village': village,
                        'area_acres': area_acres,
                        'area_hectares': area_ha,
                        'land_use_type': random.choice(['Agricultural Irrigated', 'Agricultural Rainfed', 'Orchard']),
                        'soil_type': v_info['soil'],
                        'irrigation_source': random.choice(['Tubewell / Canal', 'Borewell', 'Canal Irrigation']),
                        'status': status,
                        'geometry_geojson': geom_json,
                        'centroid_lat': c_lat,
                        'centroid_lng': c_lng,
                        'fingerprint': fingerprint
                    }
                )

                if created:
                    total_parcels_created += 1

                    # Assign Owner
                    owner = Owner.objects.order_by('?').first()
                    if owner:
                        OwnershipRecord.objects.create(
                            parcel=parcel,
                            owner=owner,
                            share_percentage=100.0,
                            from_date=date(2018, 5, 12),
                            status='ACTIVE'
                        )

                    # Assign Crop Record
                    CropRecord.objects.create(
                        parcel=parcel,
                        season=random.choice(['Kharif 2026', 'Rabi 2025-26']),
                        crop=random.choice(v_info['crops']),
                        variety='Hybrid-Grade A',
                        sowing_date=date(2025, 11, 10),
                        estimated_yield_quintals=round(area_acres * random.uniform(18.0, 24.5), 1),
                        irrigation_used=True,
                        soil_condition='Optimal Fertile'
                    )

                plot_idx += 1

    print(f"SUCCESS! Added {total_parcels_created} All-India parcels across Punjab, UP, MP, Maharashtra & Jharkhand!")

if __name__ == '__main__':
    seed_national_cadastre()
