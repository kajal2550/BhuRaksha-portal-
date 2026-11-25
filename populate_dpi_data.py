import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'landgov_project.settings')
django.setup()

from parcels.models import Village, Parcel
from records.models import Owner, OwnershipRecord, CropRecord, MutationTransaction, AuditLog

# 1. Create Villages
village1, _ = Village.objects.get_or_create(
    village_code="UP-VNS-001",
    defaults={
        "name": "Rampur Khurd",
        "gram_panchayat": "Rampur Gram Sabha",
        "block_tehsil": "Sadar Tehsil",
        "district": "Varanasi",
        "state": "Uttar Pradesh"
    }
)

village2, _ = Village.objects.get_or_create(
    village_code="UP-VNS-002",
    defaults={
        "name": "Shivpur Dehat",
        "gram_panchayat": "Shivpur Panchayat",
        "block_tehsil": "Harahua",
        "district": "Varanasi",
        "state": "Uttar Pradesh"
    }
)

# 2. Cadastral Grid Parcels (32 sample digitized parcels in Rampur & Shivpur)
# Generating adjacent cadastral polygons around 25.32° N, 82.98° E
base_lat = 25.3200
base_lng = 82.9800
step_lat = 0.0018
step_lng = 0.0022

parcels_meta = [
    # (khasra, land_use, soil, irr, status, crop, season, yield_q, owner_name, aadhaar, pm_kisan, mutation_type)
    ("101/1", "Irrigated Agri", "Alluvial Loam", "Tube Well & Canal", "Clear", "Wheat (HD-2967)", "Rabi", 38.5, "Ramesh Chandra Yadav", "XXXX-XXXX-4102", "PMK-UP-88912", "Inheritance"),
    ("101/2", "Irrigated Agri", "Alluvial Loam", "Canal Irrigation", "Clear", "Paddy (Basmati-1509)", "Kharif", 42.0, "Kavita Devi", "XXXX-XXXX-5521", "PMK-UP-77210", "Sale Deed"),
    ("102/A", "Rain-fed Agri", "Sandy Loam", "Rainfed / Borewell", "Disputed", "Mustard & Gram (Chana)", "Rabi", 18.2, "Mahendra Pratap Singh", "XXXX-XXXX-9912", "", "Partition"),
    ("102/B", "Irrigated Agri", "Alluvial Loam", "Tube Well", "Clear", "Sugarcane (Co-0238)", "Perennial", 110.0, "Suresh Kumar Patel", "XXXX-XXXX-3341", "PMK-UP-99214", "Sale Deed"),
    ("103/K", "Residential/Abadi", "Sandy Clay", "Municipal & Borewell", "Clear", "Kitchen Garden / Homestead", "Zaid", 5.0, "Pooja Verma & Rajesh Verma", "XXXX-XXXX-1142", "", "Sale Deed"),
    ("104/G", "Commercial/Agri-Hub", "Clay Loam", "Drip & Micro-Irrigation", "Clear", "Agro-Cold Storage & Solar", "Perennial", 0.0, "Kisan Sahakari Samiti (FoodTech)", "XXXX-XXXX-0012", "", "Government Acquisition"),
    ("105/M", "Fallow/Barren", "Laterite", "Rainfed", "Under Mutation", "Social Forestry & Grassland", "Perennial", 8.0, "Gram Sabha Rampur (Gaon Sabha)", "XXXX-XXXX-0000", "", "Inheritance"),
    ("106/1", "Irrigated Agri", "Alluvial Loam", "Tube Well", "Clear", "Wheat (Sharbati)", "Rabi", 35.0, "Dinesh Kumar Bind", "XXXX-XXXX-7788", "PMK-UP-44512", "Inheritance"),
    ("106/2", "Irrigated Agri", "Alluvial Loam", "Tube Well", "Clear", "Potato (Kufri Jyoti)", "Rabi", 125.0, "Ram Ashrey Maurya", "XXXX-XXXX-6632", "PMK-UP-33214", "Sale Deed"),
    ("107/A", "Irrigated Agri", "Black Cotton Soil", "Canal Irrigation", "Clear", "Paddy (Swarna Sub-1)", "Kharif", 45.0, "Manoj Pandey", "XXXX-XXXX-8821", "PMK-UP-55123", "Inheritance"),
    ("107/B", "Rain-fed Agri", "Sandy Loam", "Rainfed", "Clear", "Pigeon Pea / Arhar", "Kharif", 16.0, "Anita Devi", "XXXX-XXXX-4412", "PMK-UP-66712", "Partition"),
    ("108/1", "Irrigated Agri", "Alluvial Loam", "Solar Pump & Tube Well", "Clear", "Vegetables (Tomato & Chilli)", "Zaid", 65.0, "Santosh Kumar Gupta", "XXXX-XXXX-2234", "PMK-UP-99120", "Sale Deed"),
    ("108/2", "Residential/Abadi", "Alluvial Loam", "Piped Water", "Clear", "Rural Abadi Housing", "Perennial", 0.0, "Brijesh Mishra", "XXXX-XXXX-9901", "", "Sale Deed"),
    ("109/X", "Irrigated Agri", "Alluvial Loam", "Canal Irrigation", "Disputed", "Wheat & Mustard", "Rabi", 32.0, "Gajendra Narayan Roy", "XXXX-XXXX-5544", "", "Partition"),
    ("110/1", "Irrigated Agri", "Clay Loam", "Tube Well", "Clear", "Maize (Hybrid Ganga-11)", "Kharif", 48.0, "Subhash Chandra Chaurasia", "XXXX-XXXX-7721", "PMK-UP-22119", "Inheritance"),
    ("110/2", "Irrigated Agri", "Alluvial Loam", "Tube Well", "Clear", "Green Peas & Lentils (Masoor)", "Rabi", 22.0, "Geeta Devi", "XXXX-XXXX-8819", "PMK-UP-11994", "Inheritance"),
    ("111/A", "Irrigated Agri", "Alluvial Loam", "Canal", "Clear", "Paddy (MTU 7029)", "Kharif", 44.0, "Virendra Kumar Singh", "XXXX-XXXX-3321", "PMK-UP-66114", "Sale Deed"),
    ("111/B", "Commercial/Agri-Hub", "Alluvial Loam", "Borewell", "Clear", "Grain Silo & Seed Grading", "Perennial", 0.0, "Purvanchal Agro Producer Co.", "XXXX-XXXX-0099", "", "Sale Deed"),
    ("112/1", "Rain-fed Agri", "Sandy Loam", "Rainfed", "Clear", "Pearl Millet (Bajra)", "Kharif", 28.0, "Kallu Ram Prajapati", "XXXX-XXXX-6612", "PMK-UP-88221", "Inheritance"),
    ("112/2", "Irrigated Agri", "Alluvial Loam", "Tube Well", "Clear", "Barley (Jau) & Mustard", "Rabi", 30.0, "Hira Lal Gond", "XXXX-XXXX-4491", "PMK-UP-77441", "Inheritance"),
    ("113/M", "Fallow/Barren", "Sandy Loam", "Rainfed", "Clear", "Community Pond & Pasture", "Perennial", 0.0, "Gram Panchayat Rampur", "XXXX-XXXX-0000", "", "Government Acquisition"),
    ("114/1", "Irrigated Agri", "Black Cotton Soil", "Drip Irrigation", "Clear", "Banana (G9 Variety)", "Perennial", 180.0, "Alok Kumar Srivastava", "XXXX-XXXX-3319", "PMK-UP-99332", "Sale Deed"),
    ("115/A", "Irrigated Agri", "Alluvial Loam", "Canal & Borewell", "Disputed", "Wheat & Sugarcane", "Rabi", 75.0, "Ram Prasad vs. Tribhuvan", "XXXX-XXXX-1188", "", "Partition"),
    ("116/1", "Irrigated Agri", "Alluvial Loam", "Tube Well", "Clear", "Rice & Wheat Rotation", "Kharif", 40.0, "Shanti Devi", "XXXX-XXXX-5529", "PMK-UP-55442", "Inheritance"),
    ("117/1", "Irrigated Agri", "Alluvial Loam", "Canal", "Clear", "Cabbage & Cauliflower", "Rabi", 85.0, "Devendra Nath Tiwari", "XXXX-XXXX-9933", "PMK-UP-44118", "Sale Deed"),
    ("118/G", "Residential/Abadi", "Sandy Clay", "Borewell", "Clear", "Pradhan Mantri Awas Unit", "Perennial", 0.0, "Basanti Devi", "XXXX-XXXX-2299", "", "Government Acquisition"),
    ("119/1", "Irrigated Agri", "Alluvial Loam", "Tube Well", "Clear", "Mentha / Mint Crop", "Zaid", 24.0, "Jitendra Kumar Rajbhar", "XXXX-XXXX-7766", "PMK-UP-88339", "Inheritance"),
    ("120/1", "Irrigated Agri", "Alluvial Loam", "Canal & Solar", "Clear", "Wheat (PBW-502)", "Rabi", 37.0, "Satish Chandra Dubey", "XXXX-XXXX-3388", "PMK-UP-11228", "Sale Deed"),
    ("121/A", "Rain-fed Agri", "Sandy Loam", "Rainfed", "Under Mutation", "Sesame (Til) & Moong", "Kharif", 12.0, "Kamla Kant Pathak", "XXXX-XXXX-4477", "PMK-UP-99441", "Inheritance"),
    ("122/1", "Irrigated Agri", "Alluvial Loam", "Tube Well", "Clear", "Organic Paddy & Black Rice", "Kharif", 32.0, "Kisan Agro FPO Unit 4", "XXXX-XXXX-6677", "PMK-UP-33881", "Sale Deed"),
    ("123/1", "Irrigated Agri", "Clay Loam", "Canal", "Clear", "Garlic & Onion Crop", "Rabi", 90.0, "Vindhyavasini Prasad", "XXXX-XXXX-1123", "PMK-UP-77112", "Inheritance"),
    ("124/M", "Fallow/Barren", "Alluvial", "Rainfed", "Clear", "Buffer Canal Embankment", "Perennial", 0.0, "Irrigation Dept Uttar Pradesh", "XXXX-XXXX-0000", "", "Government Acquisition")
]

created_count = 0
cols = 4  # 4x8 grid for 32 cadastral plots

for i, meta in enumerate(parcels_meta):
    r = i // cols
    c = i % cols

    min_lng = base_lng + (c * step_lng)
    max_lng = min_lng + step_lng - 0.0003
    min_lat = base_lat + (r * step_lat)
    max_lat = min_lat + step_lat - 0.0002

    # Polygon coords (WGS84 EPSG:4326)
    poly_coords = [
        [round(min_lng, 6), round(min_lat, 6)],
        [round(max_lng, 6), round(min_lat, 6)],
        [round(max_lng, 6), round(max_lat, 6)],
        [round(min_lng, 6), round(max_lat, 6)],
        [round(min_lng, 6), round(min_lat, 6)]
    ]
    centroid_lat = round((min_lat + max_lat) / 2, 6)
    centroid_lng = round((min_lng + max_lng) / 2, 6)

    khasra_no, land_use, soil, irr, status, crop, season, yield_q, owner_name, aadhaar, pm_kisan, mut_type = meta
    ulpin = f"IN-UP-VNS-2024-{1000 + i}"
    area_ha = round(0.45 + (i * 0.12) % 2.5, 2)
    area_acres = round(area_ha * 2.47105, 2)

    village = village1 if i < 20 else village2

    parcel, _ = Parcel.objects.update_or_create(
        parcel_id=ulpin,
        defaults={
            "khasra_no": khasra_no,
            "village": village,
            "area_hectares": area_ha,
            "area_acres": area_acres,
            "land_use_type": land_use,
            "soil_type": soil,
            "irrigation_source": irr,
            "status": status,
            "geometry_geojson": json.dumps({"type": "Polygon", "coordinates": [poly_coords]}),
            "centroid_lat": centroid_lat,
            "centroid_lng": centroid_lng
        }
    )

    # 3. Create or Get Owner
    owner, _ = Owner.objects.get_or_create(
        name=owner_name,
        defaults={
            "aadhaar_masked": aadhaar,
            "contact": f"+91 9839{100000 + i}",
            "pm_kisan_beneficiary_id": pm_kisan if pm_kisan else None,
            "address": f"Village {village.name}, Tehsil {village.block_tehsil}, Varanasi"
        }
    )

    # 4. Link OwnershipRecord
    OwnershipRecord.objects.get_or_create(
        parcel=parcel,
        owner=owner,
        defaults={
            "share_percentage": 100.0,
            "status": "Active" if status != "Disputed" else "Disputed"
        }
    )

    # 5. Crop Record
    CropRecord.objects.get_or_create(
        parcel=parcel,
        crop=crop,
        season=season,
        defaults={
            "variety": "ICAR Recommended",
            "sowing_date": "2024-11-10" if season == "Rabi" else "2024-07-15",
            "estimated_yield_quintals": yield_q,
            "fertilizer_used": "DAP + Neem Coated Urea & Bio-fertilizer"
        }
    )

    # 6. Mutation Record
    MutationTransaction.objects.get_or_create(
        case_number=f"MUT/VNS/{2024}/{200 + i}",
        defaults={
            "parcel": parcel,
            "transaction_type": mut_type,
            "applicant_name": owner_name,
            "transferor_name": f"Late Predecessor / Seller {i+1}",
            "status": "Approved / mutated" if status == "Clear" else "Objection Raised",
            "submission_date": "2024-03-15",
            "approval_date": "2024-04-20" if status == "Clear" else None,
            "remarks": "Verified by Revenue Patwari via Digital Cadastral Registry"
        }
    )
    created_count += 1

# Initial Audit Log
AuditLog.objects.create(
    action="INITIAL_CADASTRE_SYNC",
    parcel_ref="SYSTEM_BATCH_32",
    old_values={"source": "QGIS Cadastral Shapefile Export"},
    new_values={"total_parcels_imported": created_count, "village": "Rampur Khurd & Shivpur"},
    ip_address="127.0.0.1"
)

print(f"✅ Successfully loaded {created_count} cadastral parcels with full linked DPI models (Owners, Crops, Mutations, Audit)!")
