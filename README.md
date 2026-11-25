# BhuRaksha: A Secure, Tamper-Proof GIS-based Digital Public Infrastructure for Land Governance

**Final Year Engineering Capstone Project**  
**Theme**: Agriculture, FoodTech & Rural Development, Cybersecurity & Land Governance DPI  

---

## 📌 Executive Summary
BhuRaksha resolves the historic fragmentation of Indian cadastral land governance where physical boundary maps, ownership registers (Khatauni), seasonal crop entries (Girdawari), and mutation records (Dakhil Kharij) are managed in isolated silos. By assigning each plot a standard 14-digit **Unique Land Parcel Identification Number (ULPIN)**, BhuRaksha links spatial cartography with relational databases, while applying defense-in-depth cybersecurity controls (Fernet AES PII encryption, SHA-256 fingerprinting, append-only hash chained audit trails, and Shapely geometric collision detection).

---

## 🚀 Quick Start Guide (Windows)

### 1. Requirements & Dependencies
Make sure Python 3.11+ is installed. Then run:
```powershell
pip install -r requirements.txt
```

### 2. Database Migrations
```powershell
python manage.py makemigrations accounts parcels records mutations disputes security
python manage.py migrate
```

### 3. Seed Realistic Demo Cadastre (50 Parcels in Punjab, 40 Owners, 6 RBAC Users)
```powershell
python manage.py seed_demo
```

### 4. Run Development Web Server
```powershell
python manage.py runserver 0.0.0.0:8000
```
Open your browser at: **`http://127.0.0.1:8000/`**

---

## 🔑 Demo RBAC User Credentials

| Role | Username | Password | Purpose & Access Level |
| :--- | :--- | :--- | :--- |
| **System Administrator** | `admin_user` | `admin123` | Full access, user provisioning, system settings |
| **Security Auditor** | `auditor_user` | `audit123` | SOC telemetry, Hash chain verification, Anomaly radar |
| **Revenue Officer** | `revenue_officer` | `patwari123` | Decrypted PII view, ownership records, mutation workflow |
| **Agricultural Officer** | `agri_officer` | `agri123` | Crop cultivation logs, yield estimates, scheme eligibility |
| **Farmer (Land Owner)** | `farmer_user` | `kisan123` | View own landholdings, raise disputes, track mutations |
| **Public Citizen** | `public_user` | `public123` | Read-only map, masked PII, public verify record |

*Note: For MFA-enabled officers, enter the 6-digit TOTP code from Google Authenticator, or use the demo bypass token `123456`.*

---

## 🧪 Demonstration of Silent Tamper Detection

1. Run the silent DB tamper simulator:
```powershell
python manage.py simulate_tamper
```
2. Navigate to **`http://127.0.0.1:8000/soc/`** or **`http://127.0.0.1:8000/security/integrity/`**.
3. Click **"Execute Full Integrity Check Now"**.
4. Observe the system detect the SHA-256 mismatch, mark the affected parcel in red as **`Tampered`**, and dispatch a critical alert to the SOC dashboard.

---

## 🗺️ How to Open in QGIS Desktop
1. Open QGIS.
2. Go to **Layer** -> **Add Layer** -> **Add Vector Layer...**
3. Select `data/parcels_phagwara_qgis.geojson` from the project directory, or point directly to the live URL: `http://127.0.0.1:8000/export/qgis-geojson/`.
4. All 50 cadastral polygons and attribute tables will render immediately.
