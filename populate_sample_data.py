import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'landgov_project.settings')
django.setup()

from parcels.models import LandParcel

# Sample realistic cadastral parcels in Rampur village (Varanasi / Eastern UP region)
# Coords around lat: 25.32, lng: 82.98
sample_parcels = [
    {
        "khasra_number": "101/1",
        "ulpin": "IN-UP-VNS-2024-00101",
        "survey_number": "SRV-401",
        "village": "Rampur",
        "gram_panchayat": "Rampur Gram Sabha",
        "tehsil": "Sadar",
        "district": "Varanasi",
        "state": "Uttar Pradesh",
        "owner_name": "Ramesh Chandra Yadav",
        "co_owners": "Suresh Yadav (Brother)",
        "aadhaar_linked": True,
        "mutation_date": "2021-04-12",
        "land_use": "Agricultural",
        "area_hectares": 1.25,
        "area_acres": 3.09,
        "crop_type": "Wheat & Mustard (Rabi), Rice (Kharif)",
        "soil_health": "Alluvial",
        "irrigation_source": "Tube Well / Borewell",
        "annual_revenue_tax": 180.00,
        "pm_kisan_eligible": True,
        "status": "Clear / Verified",
        "centroid_lat": 25.3215,
        "centroid_lng": 82.9810,
        "polygon": [
            [82.9800, 25.3205],
            [82.9825, 25.3205],
            [82.9822, 25.3225],
            [82.9798, 25.3222],
            [82.9800, 25.3205]
        ]
    },
    {
        "khasra_number": "101/2",
        "ulpin": "IN-UP-VNS-2024-00102",
        "survey_number": "SRV-402",
        "village": "Rampur",
        "gram_panchayat": "Rampur Gram Sabha",
        "tehsil": "Sadar",
        "district": "Varanasi",
        "state": "Uttar Pradesh",
        "owner_name": "Kavita Devi",
        "co_owners": "None",
        "aadhaar_linked": True,
        "mutation_date": "2022-08-19",
        "land_use": "Agricultural",
        "area_hectares": 0.85,
        "area_acres": 2.10,
        "crop_type": "Paddy (Rice), Sugarcane",
        "soil_health": "Alluvial",
        "irrigation_source": "Canal",
        "annual_revenue_tax": 125.00,
        "pm_kisan_eligible": True,
        "status": "Clear / Verified",
        "centroid_lat": 25.3218,
        "centroid_lng": 82.9838,
        "polygon": [
            [82.9825, 25.3205],
            [82.9850, 25.3207],
            [82.9848, 25.3230],
            [82.9822, 25.3225],
            [82.9825, 25.3205]
        ]
    },
    {
        "khasra_number": "102/A",
        "ulpin": "IN-UP-VNS-2024-00103",
        "survey_number": "SRV-403",
        "village": "Rampur",
        "gram_panchayat": "Rampur Gram Sabha",
        "tehsil": "Sadar",
        "district": "Varanasi",
        "state": "Uttar Pradesh",
        "owner_name": "Mahendra Pratap Singh",
        "co_owners": "Devendra Singh, Virendra Singh",
        "aadhaar_linked": False,
        "mutation_date": "2018-02-15",
        "land_use": "Agricultural",
        "area_hectares": 2.10,
        "area_acres": 5.19,
        "crop_type": "Wheat, Pulses (Arhar / Gram)",
        "soil_health": "Sandy Loam",
        "irrigation_source": "Tube Well / Borewell",
        "annual_revenue_tax": 290.00,
        "pm_kisan_eligible": False,
        "status": "Disputed",
        "centroid_lat": 25.3238,
        "centroid_lng": 82.9815,
        "polygon": [
            [82.9798, 25.3222],
            [82.9822, 25.3225],
            [82.9820, 25.3252],
            [82.9795, 25.3248],
            [82.9798, 25.3222]
        ]
    },
    {
        "khasra_number": "103/K",
        "ulpin": "IN-UP-VNS-2024-00104",
        "survey_number": "SRV-404",
        "village": "Rampur",
        "gram_panchayat": "Rampur Gram Sabha",
        "tehsil": "Sadar",
        "district": "Varanasi",
        "state": "Uttar Pradesh",
        "owner_name": "Pooja Verma & Rajesh Verma",
        "co_owners": "Rajesh Verma (Husband)",
        "aadhaar_linked": True,
        "mutation_date": "2023-11-05",
        "land_use": "Residential",
        "area_hectares": 0.35,
        "area_acres": 0.86,
        "crop_type": "Abadi / Homestead & Kitchen Garden",
        "soil_health": "Alluvial",
        "irrigation_source": "Tube Well / Borewell",
        "annual_revenue_tax": 450.00,
        "pm_kisan_eligible": False,
        "status": "Clear / Verified",
        "centroid_lat": 25.3240,
        "centroid_lng": 82.9840,
        "polygon": [
            [82.9822, 25.3225],
            [82.9848, 25.3230],
            [82.9845, 25.3255],
            [82.9820, 25.3252],
            [82.9822, 25.3225]
        ]
    },
    {
        "khasra_number": "104/G",
        "ulpin": "IN-UP-VNS-2024-00105",
        "survey_number": "SRV-405",
        "village": "Rampur",
        "gram_panchayat": "Rampur Gram Sabha",
        "tehsil": "Sadar",
        "district": "Varanasi",
        "state": "Uttar Pradesh",
        "owner_name": "Kisan Sahakari Samiti (Food Processing Hub)",
        "co_owners": "Gram Sabha Rampur (Custody)",
        "aadhaar_linked": True,
        "mutation_date": "2024-01-20",
        "land_use": "Commercial",
        "area_hectares": 1.70,
        "area_acres": 4.20,
        "crop_type": "Agro-Storage, Cold Store & Solar Unit",
        "soil_health": "Alluvial",
        "irrigation_source": "Drip/Sprinkler",
        "annual_revenue_tax": 1200.00,
        "pm_kisan_eligible": False,
        "status": "Clear / Verified",
        "centroid_lat": 25.3262,
        "centroid_lng": 82.9822,
        "polygon": [
            [82.9795, 25.3248],
            [82.9845, 25.3255],
            [82.9840, 25.3275],
            [82.9790, 25.3268],
            [82.9795, 25.3248]
        ]
    },
    {
        "khasra_number": "105/M",
        "ulpin": "IN-UP-VNS-2024-00106",
        "survey_number": "SRV-406",
        "village": "Rampur",
        "gram_panchayat": "Rampur Gram Sabha",
        "tehsil": "Sadar",
        "district": "Varanasi",
        "state": "Uttar Pradesh",
        "owner_name": "Gram Sabha Rampur (Gaon Sabha)",
        "co_owners": "Panchayat Raj Department",
        "aadhaar_linked": True,
        "mutation_date": "2010-06-01",
        "land_use": "Forest/Barren",
        "area_hectares": 3.40,
        "area_acres": 8.40,
        "crop_type": "Social Forestry & Grazing Pasture",
        "soil_health": "Laterite",
        "irrigation_source": "Rainfed",
        "annual_revenue_tax": 0.00,
        "pm_kisan_eligible": False,
        "status": "Under Verification",
        "centroid_lat": 25.3235,
        "centroid_lng": 82.9870,
        "polygon": [
            [82.9850, 25.3207],
            [82.9890, 25.3212],
            [82.9885, 25.3260],
            [82.9845, 25.3255],
            [82.9848, 25.3230],
            [82.9850, 25.3207]
        ]
    }
]

created_count = 0
for item in sample_parcels:
    poly_geom = {
        "type": "Polygon",
        "coordinates": [item["polygon"]]
    }
    
    obj, created = LandParcel.objects.update_or_create(
        khasra_number=item["khasra_number"],
        defaults={
            "ulpin": item["ulpin"],
            "survey_number": item["survey_number"],
            "village": item["village"],
            "gram_panchayat": item["gram_panchayat"],
            "tehsil": item["tehsil"],
            "district": item["district"],
            "state": item["state"],
            "owner_name": item["owner_name"],
            "co_owners": item["co_owners"],
            "aadhaar_linked": item["aadhaar_linked"],
            "mutation_date": item["mutation_date"],
            "land_use": item["land_use"],
            "area_hectares": item["area_hectares"],
            "area_acres": item["area_acres"],
            "crop_type": item["crop_type"],
            "soil_health": item["soil_health"],
            "irrigation_source": item["irrigation_source"],
            "annual_revenue_tax": item["annual_revenue_tax"],
            "pm_kisan_eligible": item["pm_kisan_eligible"],
            "status": item["status"],
            "geojson_data": json.dumps(poly_geom),
            "centroid_lat": item["centroid_lat"],
            "centroid_lng": item["centroid_lng"]
        }
    )
    if created:
        created_count += 1

print(f"Successfully populated {len(sample_parcels)} land parcels into the database! (New: {created_count})")
