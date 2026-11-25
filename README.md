# 🌾 BhuRaksha (भू-रक्षा)
### **An Integrated GIS-Based Digital Public Infrastructure (DPI) for Land Governance & Tamper-Proof Cadastral Title Management**

[![Django Version](https://img.shields.io/badge/Django-6.1-092E20?style=for-the-badge&logo=django)](https://www.djangoproject.com/)
[![Python Version](https://img.shields.io/badge/Python-3.13-3776AB?style=for-the-badge&logo=python)](https://www.python.org/)
[![GIS Engine](https://img.shields.io/badge/GIS-Leaflet.js%20%7C%20Shapely-199900?style=for-the-badge&logo=leaflet)](https://leafletjs.com/)
[![Security](https://img.shields.io/badge/Cryptography-SHA--256%20%7C%20Fernet%20AES--128-red?style=for-the-badge&logo=security)](https://cryptography.io/)
[![Standard](https://img.shields.io/badge/Standard-EPSG%3A4326%20WGS84-blue?style=for-the-badge)](https://epsg.io/4326)

---

## 📌 Executive Summary

In traditional land revenue administrations across India, cadastral maps (*Aks Shajra / Map Polygons*) and ownership registers (*Jamabandi / Records of Rights - RoR*) are maintained in silos across distinct physical offices. This separation breeds critical socio-economic vulnerabilities:
1. **Illegal Encroachment & Boundary Shifting**: Malicious alterations of physical plot boundary pegs.
2. **Double-Selling & Forged Benami Deeds**: Submitting unauthorized sale deeds without titleholder verification.
3. **Database Records Tampering**: Insiders or attackers silently altering plot areas or names directly in legacy databases.
4. **Delayed Inheritance Partitions (*Batwara*)**: Cumbersome multi-month land division disputes among legal heirs.

**BhuRaksha** is an engineering-grade **Digital Public Infrastructure (DPI)** that bridges spatial Geographic Information Systems (Web GIS) with cryptographic record authentication. Every land parcel is assigned a 14-digit **ULPIN** (*Unique Land Parcel Identification Number / Bhu-Aadhaar*) and cryptographically sealed with a **SHA-256 Merkle Fingerprint**. Any silent manipulation of geometry or ownership breaks the append-only hash chain immediately, triggering real-time Security Operations Center (SOC) containment alerts.

---

## 🏛️ Key Architectural Highlights & Innovation

* **Zero-GDAL Portable Web GIS Architecture**: Eliminates heavy C++ GDAL/GEOS system dependencies on Windows. Cadastral geometries are stored in GeoJSON format (EPSG:4326 WGS84) with spatial intersection and overlap collision checks handled by Python's native `shapely` engine.
* **National Multi-State BhuNaksha Ingestion**: Scaled beyond single-state boundaries with pre-seeded, survey-grade cadastral clusters across **5 major agricultural states**:
  - **Uttar Pradesh**: Chhata Rural (*Mathura*)
  - **Madhya Pradesh**: Bicholi Mardana (*Indore*)
  - **Maharashtra**: Baramati Rural (*Pune*)
  - **Jharkhand**: Mandar Rural (*Ranchi*)
  - **Punjab**: Kot Rani & Khera Dehat (*Phagwara, Kapurthala*)
* **Cryptographic Hash-Chained Audit Trail**: Immutability enforced via an append-only ledger (`AuditLog`) linking blocks through `prev_hash` (`SHA256(Block_N + prev_hash)`). Existing records cannot be updated or deleted.
* **Fernet AES-128 PII Encryption**: Farmer national identity numbers (Aadhaar / UID) and contact details are encrypted at rest using AES-128-CBC with PKCS7 padding.
* **Interactive Engineering Simulator Labs**: Built-in hands-on simulation environments allowing examiners to launch simulated attacks (boundary grab, deed forgery, history rewrite) and verify instant mitigation.

---

## 🚀 Live Functional Modules & Interactive Features

| Module | Route / Endpoint | Description & Technical Capability |
| :--- | :--- | :--- |
| **GIS Cadastre Map** | `/map/` | Full-screen interactive Leaflet map rendering 130+ national plots. Includes layer switchers (CartoDB Dark Matter / Satellite), live Khasra search, status filter, and live Dossier Inspector. |
| **Live Plot Drawing** | `/map/` $\rightarrow$ *Draw Tool* | Real-time boundary polygon drawing that posts to `/api/parcels/draw-save/`, auto-computes acre area, allocates a ULPIN, and stores it directly into the database. |
| **Parcel Split Simulator** | `/parcel-split-simulator/` | Inheritance partition (*Batwara*) engine that algorithmically divides Khasra plots into compliant sub-plots, generating Sub-ULPINs (e.g. `101/1-A`, `101/1-B`). |
| **Land Valuation & Taxes** | `/land-valuation/` | Government circle rate projection engine calculating circle market valuation, 7% state stamp duty, and registration charges for property sales. |
| **RoR Digital Certificate** | `/parcel/<id>/download-pdf/` | Government-style Record of Rights (*Fard / Jamabandi*) certificate with embedded verification QR code, landholder shares, and SHA-256 seal. |
| **Fraud Attack Simulator** | `/fraud-simulator/` | Live cybersecurity attack lab testing Merkle hash detection, boundary expansion attempts, and append-only database rollback. |
| **Farmer Aadhaar e-KYC** | `/farmer-kyc/` | UIDAI-simulated OTP verification pipeline issuing cryptographic identity passes and storing Fernet-encrypted ciphertext tokens. |
| **Precision Agro Advisory** | `/weather-advisory/` | Micro-climate spray window analysis, soil moisture index, and seasonal Kharif/Rabi crop cultivation recommendations. |
| **SOC Terminal & Chain** | `/soc/` & `/security/audit/` | SOC security event stream and 1-click cryptographic hash chain verification (`/security/audit/verify-chain/`). |
| **Open REST API Docs** | `/api/docs/` & `/api/schema/` | OpenAPI 3.0 / Swagger documentation for institutional queries (banks, crop insurers, PM-KISAN subsidy). |

---

## 🛠️ Technology Stack & Dependencies

```
┌─────────────────────────────────────────────────────────────┐
│                       Frontend Layer                        │
│  HTML5 + Modern Enterprise CSS (Clean White/Royal Blue UI) │
│  Leaflet.js 1.9.4 • Leaflet.draw • Leaflet.markercluster   │
│  Bootstrap 5 Grid Utilities • Bootstrap Icons • Chart.js    │
└──────────────────────────────┬──────────────────────────────┘
                               │ HTTP / GeoJSON REST API
┌──────────────────────────────▼──────────────────────────────┐
│                    Application / API Layer                  │
│       Python 3.13 • Django 6.1 • Django REST Framework      │
│  drf-spectacular (OpenAPI 3.0) • django-otp (TOTP 2FA)      │
└──────────────────────────────┬──────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────┐
│                  Spatial & Security Engines                 │
│  Shapely (Geometry Collision, Intersection, Area Checks)   │
│  Cryptography (Fernet AES-128 Encryption for PII at rest)   │
│  Hashlib SHA-256 (Merkle Tree & Append-Only Audit Chains)   │
└──────────────────────────────┬──────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────┐
│                       Data Storage                          │
│     SQLite (Development) / PostgreSQL + PostGIS Ready       │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔐 Role-Based Access Control (RBAC)

The application implements granular Role-Based Access Control across views, template navigation, and REST endpoints:

| Role | Username | Password | Privileges & Permissions |
| :--- | :--- | :--- | :--- |
| **Revenue Officer (Patwari)** | `revenue_officer` | `patwari123` | Create/update ownership, file and approve mutations, split Khasra boundaries. |
| **Farmer / Landholder** | `farmer_user` | `farmer123` | View own unmasked plots, apply for mutation, raise boundary disputes, download RoR. |
| **System Administrator** | `admin_user` | `admin123` | Full administrative control, user role management, system settings, audit logs. |
| **Agricultural Officer** | `agri_officer` | `agri123` | Register crop records, update soil health profiles, link PM-KISAN eligibility. |
| **Auditor / Vigilance** | `auditor_user` | `audit123` | Read-only inspection of append-only hash chains, SOC telemetry, and tamper alarms. |
| **Public Citizen** | *Unauthenticated* | — | Read-only access to GIS map (masked PII), public certificate verification. |

> **⚡ Quick 1-Click Login**: The login screen (`/login/`) features one-click demo login buttons for instant role switching without typing credentials.

---

## 📦 Installation & Setup Guide (Windows / Linux / macOS)

### 1. Clone the Repository
```bash
git clone https://github.com/kajal2550/BhuRaksha-portal-.git
cd BhuRaksha-portal-
```

### 2. Create and Activate Virtual Environment
```bash
# Windows
python -m venv env
.\env\Scripts\activate

# Linux / macOS
python3 -m venv env
source env/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Database Migrations
```bash
python manage.py migrate
```

### 5. Seed Demonstration & Cadastral Data
```bash
# Seed All-India Multi-State clusters (UP, MP, MH, JH, PB)
python seed_all_india.py

# Optional: Run default demo seeder
python manage.py seed_demo
```

### 6. Run the Development Server
```bash
python manage.py runserver 127.0.0.1:8000
```
Open **[http://127.0.0.1:8000/](http://127.0.0.1:8000/)** in your browser.

---

## 🧪 Automated Testing & Verification

BhuRaksha includes an automated test suite verifying cryptographic hashing, tamper detection, and URL accessibility:

```bash
python manage.py test security
```

**Expected Test Results:**
* `test_append_only_immutability`: Ensures historical audit logs reject updates.
* `test_chain_verification_intact`: Validates unbroken SHA-256 block hash integrity.
* `test_fernet_encryption`: Verifies Aadhaar number encryption and decryption.
* `test_tamper_detection_triggers`: Confirms geometry alteration invalidates the Merkle fingerprint.

---

## 📊 Presentation / Viva Quick Talking Points

When demonstrating this project to academic examiners or evaluators:
1. **The Real-World Problem**: Land records and village maps (*Aks Shajra*) are isolated, leading to 66% of civil court cases in India being land/property related.
2. **The DPI Solution**: A unified Digital Public Infrastructure where every plot has a unique ULPIN (*Bhu-Aadhaar*), coordinates are mapped via GIS, and ownership is cryptographically sealed.
3. **Key Differentiator**: Traditional portals (*Bhulekh*) are simple databases where an admin could alter numbers. BhuRaksha uses **SHA-256 Merkle Fingerprints**—any silent change turns the plot red on the map and fails cryptographic chain verification.
4. **All-India Coverage**: Pre-seeded with survey-grade cadastral clusters from **Punjab, Uttar Pradesh, Madhya Pradesh, Maharashtra, and Jharkhand**.

---

## 📄 License & Academic Attribution
* **Course**: CA-3 Capstone Engineering Project
* **Authors / Maintainers**: Team BhuRaksha (Lead: Kajal Kumari)
* **License**: MIT Open Source License. Designed for academic and research evaluation.
