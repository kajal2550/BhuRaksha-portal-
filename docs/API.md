# BhuRaksha Open REST API Specification (v1)

Base URL: `http://127.0.0.1:8000/api/v1/`

### 1. GeoJSON Cadastral Parcels
- **Endpoint**: `GET /api/v1/parcels/`
- **Response**: GeoJSON `FeatureCollection` with EPSG:4326 geometry and embedded properties.
- **Query Parameters**:
  - `q`: Search string across Khasra, ULPIN, or Owner name.
  - `village`: Filter by village name.
  - `land_use`: Filter by land use category.
  - `status`: Filter by status (`Verified`, `Mutation Pending`, `Disputed`, `Tampered`).

### 2. Single Parcel Dossier
- **Endpoint**: `GET /api/v1/parcels/{parcel_id}/`
- **Response**: JSON payload with nested ownership, crops, mutations, and cryptographic fingerprint.

### 3. Interactive Documentation
- **Swagger UI**: `http://127.0.0.1:8000/api/docs/`
- **OpenAPI 3.0 Schema**: `http://127.0.0.1:8000/api/schema/`
