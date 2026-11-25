# BhuRaksha Live Project Demonstration Script

Follow this step-by-step walkthrough to present the project to examiners, evaluators, or users:

### Step 1: Landing Page & Public Verification
1. Open `http://127.0.0.1:8000/`.
2. Point out the animated telemetry counters (50 Parcels, 100% verified, 15 mutations).
3. Click **"Verify Record"** in the navbar (`/verify/`).
4. Type `PB-KPT-2024-1000` or `101/1`.
5. Observe the verified green result showing matching stored and recalculated SHA-256 fingerprints.

### Step 2: Main GIS Map & Cadastral Inspection
1. Navigate to **`http://127.0.0.1:8000/map/`**.
2. Notice the **CartoDB Dark Matter** dark cyber theme.
3. Switch layers: Toggle between CartoDB Dark Matter, ESRI Satellite, and OpenStreetMap.
4. Toggle the **"COLOR"** dropdown from "Status" to "Land Use Type" and "Crop Cultivation" to observe real-time polygon style updates.
5. Click on any green parcel polygon (e.g. Khasra 101/1).
6. Observe the side panel slide in with multi-tab dossier (Overview, Owner with masked Aadhaar, Seasonal crops, and Hash fingerprint).
7. Click **"Full Parcel Dossier (RoR Certificate)"** to view the printable certificate.

### Step 3: Role-Based Access Control & MFA
1. Click **"Sign In"** (`/login/`).
2. Log in as Revenue Officer: `revenue_officer` / `patwari123`.
3. The system prompts for MFA verification (`/mfa/verify/`).
4. Enter `123456` (demo bypass) or your authenticator code.
5. Observe the top-right badge change to `REVENUE_OFFICER` and "SECURE SESSION" indicator light up.
6. Navigate to `records/owners/`. Note that the Revenue Officer now sees decrypted plain Aadhaar and phone numbers with an "OFFICER VIEW" badge.

### Step 4: Mutation Workflow & Automatic Ownership Update
1. Navigate to **`http://127.0.0.1:8000/mutations/`**.
2. Click on a mutation docket that is "Under Review".
3. Change the status to **"Completed"** and write a comment. Click **"Commit Status Update"**.
4. Show that the applicant is now automatically registered as the active title holder on that parcel!

### Step 5: Silent Tamper Simulation & Detection Lab
1. Open PowerShell terminal in the project directory:
   ```powershell
   python manage.py simulate_tamper
   ```
2. Terminal reports: *Area altered directly in SQL database without updating fingerprint.*
3. In browser, navigate to **SOC Dashboard** (`/soc/`) or **Integrity Verification** (`/security/integrity/`).
4. Click **"Execute Full Integrity Check Now"**.
5. The system immediately flags the altered parcel in **RED** as **`Tampered`** and dispatches a critical security alert to the SOC feed.

### Step 6: Cryptographic Hash Chain Validation
1. Navigate to **`http://127.0.0.1:8000/security/audit/`**.
2. Show the append-only SHA-256 hash chained blocks where each block links to `prev_hash`.
3. Click **"Verify Full Hash Chain"**.
4. The system validates the entire ledger from block #1 to the end and confirms: *100% Valid & Intact*.

### Step 7: QGIS Desktop Integration
1. In QGIS, add `data/parcels_phagwara_qgis.geojson`.
2. All 50 cadastral plots render instantly with identical geometry and attributes.
