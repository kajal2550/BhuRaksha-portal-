# BhuRaksha Engineering Implementation Plan

## 1. Project Overview & Architecture
- **System**: BhuRaksha: A Secure, Tamper-Proof GIS-based Digital Public Infrastructure (DPI) for Land Governance
- **Theme**: Agriculture, FoodTech & Rural Development + Cybersecurity (SOC, Hash Chains, Fernet encryption, Fraud Detection).
- **Core Architecture**:
  - Apps: `accounts`, `parcels`, `records`, `mutations`, `disputes`, `security`, `analytics`, `api`, `core`
  - Tech Stack: Django 5.x/6.x, DRF, SQLite with `shapely` for vector geometry validation, Leaflet.js (+ Draw, MarkerCluster), Chart.js, Vanilla JS with Dark Cyber SOC theme.
  - Security Stack: `django-axes`, `django-otp`, `djangorestframework-simplejwt`, `cryptography` (Fernet), `django-csp`, `django-cors-headers`, `drf-spectacular`.

---

## 2. Checklist of Modules & Acceptance Criteria

### Step 1: Dependencies & Settings Configuration
- [ ] Create `requirements.txt` with all required libraries: `django`, `djangorestframework`, `django-axes`, `django-otp`, `qrcode`, `django-cors-headers`, `django-csp`, `cryptography`, `shapely`, `djangorestframework-simplejwt`, `drf-spectacular`.
- [ ] Install missing packages in current Python environment.
- [ ] Configure `landgov_project/settings.py` (installed apps, middleware, authentication backends, Axes config, CSP headers, Fernet encryption key, JWT settings, templates & static dirs).

### Step 2: Database Models Across Apps
- [ ] `core`: Static pages, system settings.
- [ ] `accounts`: Custom User / Role profile (Public, Farmer, Revenue Officer, Agri Officer, Auditor, Admin), OTP secret, login history.
- [ ] `parcels`: `Village`, `Parcel` (unique `parcel_id`, `khasra_no`, `area_hectares`, `area_acres`, `geometry_geojson`, `centroid_lat/lng`, `land_use_type`, `soil_type`, `status`, `fingerprint` SHA-256).
- [ ] `records`: `Owner` (Fernet encrypted Aadhaar & Phone, masked properties), `OwnershipRecord` (share %), `CropRecord` (Kharif/Rabi/Zaid, yield, irrigation), `Scheme`, `SchemeEligibility`.
- [ ] `mutations`: `Mutation` (types: sale, inheritance, partition, gift, correction; status: Applied, Under Review, Approved, Rejected, Completed), `MutationStepComment`, `Document`.
- [ ] `disputes`: `Dispute` (parcel FK, raised_by, type, description, evidence, status: Open, In Review, Resolved, Closed, lat/lng pin).
- [ ] `security`:
  - `AuditLog` (SHA-256 hash chain: `prev_hash`, `current_hash`, immutable).
  - `SecurityAlert` (severity: Low, Medium, High, Critical; anomaly type, status).
  - `IntegrityReport` (batch verify result, timestamp, tampered count).
  - `Notification` (user, title, message, read status).
  - `APIToken` / `ClientApp` (for Bank, Crop Insurance, PM-KISAN integration).
- [ ] Run migrations for all models.

### Step 3: Core Security Utilities
- [ ] Hash Chain computation & verification helper (`AuditLog.calculate_hash()` & chain validator).
- [ ] Parcel fingerprint SHA-256 calculator & verification utility.
- [ ] Fernet encryption/decryption helper for PII fields.
- [ ] Anomaly detection engine (detect rapid mutations, off-hours edits, sudden area drift, overlapping geometries using `shapely`).

### Step 4: Seed Demo Data (`python manage.py seed_demo`)
- [ ] Generate 2 villages (around Phagwara, Punjab).
- [ ] Generate 50 realistic cadastral parcels with exact GeoJSON polygons & calculated SHA-256 fingerprints.
- [ ] Generate 40 owners with encrypted PII.
- [ ] Generate multi-season crop records (Wheat, Paddy, Mustard, Potato, Maize, Sugarcane).
- [ ] Generate 15 mutations across all workflow steps.
- [ ] Generate 8 disputes with geographic coordinates.
- [ ] Generate sample canal/irrigation lines.
- [ ] Create 6 standard demo users for all RBAC roles with predictable credentials.
- [ ] Export demo parcels to `data/parcels_phagwara_qgis.geojson`.

### Step 5: Templates & Dark Cyber SOC UI Layout
- [ ] Cyber SOC UI Design System:
  - Background `#0a0e14`, panels `#111826`, borders `#1f293d`, accent `#00ff9c` (neon green), cyan `#00e5ff`, danger `#ff3b5c`, amber `#ffb020`.
  - Monospace font for data/hashes, clean sans for UI, glow badges, terminal feeds.
- [ ] Master `base.html` with responsive cyber navbar (role badge, session indicator, notification dropdown, user menu), collapsible sidebar, and footer.
- [ ] Loading states, empty states, error alert banners.

### Step 6: Implement All 18 Pages
- [ ] **Page 1: Landing / Home Page** (`/`): Cyber hero, animated stats, security pillars, how it works, CTA.
- [ ] **Page 2: Authentication & MFA** (`/login/`, `/register/`, `/logout/`, `/mfa/setup/`, `/mfa/verify/`, `/lockout/`): Terminal style login, Axes lockout, TOTP QR setup.
- [ ] **Page 3: Main GIS Map (The Centerpiece)** (`/map/`): Fullscreen CartoDB Dark Matter Leaflet map, layer controls, "Color by" toggle, search autocomplete & zoom, slide-in sidebar with 6 tabs, Leaflet.draw for parcel split & dispute pin, measure tool, print map, marker clusters.
- [ ] **Page 4: Parcel Detail Page** (`/parcel/<id>/`): Full-page dossier with mini-map, ownership timeline, crop history, mutations, linked documents, integrity status, QR code, and printable certificate.
- [ ] **Page 5: Public Parcel Verification** (`/verify/`): Public verification search by Parcel ID or hash matching.
- [ ] **Page 6: Ownership & Records Management** (`/records/owners/`): CRUD for revenue officers, 100% share validation, role-based field masking.
- [ ] **Page 7: Mutation Workflow Module** (`/mutations/`): Applied -> Under Review -> Approved -> Completed timeline, officer review, auto-ownership update, farmer tracking.
- [ ] **Page 8: Crop & Land-Use Management** (`/records/crops/`, `/schemes/`): Agri officer CRUD, rule-based scheme eligibility checker (PM-KISAN, crop insurance).
- [ ] **Page 9: Dispute Management** (`/disputes/`): Raise dispute with map coordinate pin, review workflow, status updates, turns parcel red.
- [ ] **Page 10: Security Operations Center (SOC) Dashboard** (`/soc/`): Real-time polling terminal log feed, failed-login chart, active sessions, threat alerts, integrity gauge.
- [ ] **Page 11: Tamper-Evident Audit Log** (`/security/audit/`): Hash chain list, pagination, CSV export, "Verify Full Chain" validator.
- [ ] **Page 12: Integrity Verification Module** (`/security/integrity/`): "Verify All Parcels" engine, tamper detection report, management command `simulate_tamper`.
- [ ] **Page 13: Anomaly & Fraud Detection** (`/security/anomalies/`): Alert list with severities, `run_detectors` engine.
- [ ] **Page 14: Analytics & Reports** (`/analytics/`): Chart.js visualizations, yield trends, export CSV.
- [ ] **Page 15: Open API & Developer Hub** (`/developers/`, `/api/docs/`): drf-spectacular Swagger UI, API keys / token generation for bank/insurance DPI partners.
- [ ] **Page 16: User & Admin Management** (`/admin-portal/users/`): User CRUD, role assignments, MFA reset, login history.
- [ ] **Page 17: Profile & Notifications** (`/profile/`, `/notifications/`): Active sessions, personal audit log, notification center.
- [ ] **Page 18: Static / Support Pages** (`/about/`, `/architecture/`, `/threat-model/`, `/security-policy/`, `/help/`, custom 403, 404, 500 error pages).

### Step 7: REST API v1 (`/api/v1/`)
- [ ] GeoJSON parcels endpoint with filtering and role-based field masking.
- [ ] Nested parcel detail endpoint.
- [ ] Mutations, crops, disputes endpoints with JWT authentication and throttling.
- [ ] Swagger / OpenAPI schema endpoint.

### Step 8: Testing, Verification & Documentation
- [ ] Unit tests for hash chain, integrity verification, RBAC permissions, PII masking, mutation auto-update, anomaly detection.
- [ ] Management commands: `seed_demo`, `simulate_tamper`, `run_detectors`.
- [ ] Documentation files in `docs/`: `README.md`, `ARCHITECTURE.md`, `THREAT_MODEL.md`, `USER_MANUAL.md`, `DEMO_SCRIPT.md`, `API.md`.
- [ ] Final verification against all acceptance criteria.
