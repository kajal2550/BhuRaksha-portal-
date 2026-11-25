# BhuRaksha Threat Model (STRIDE Framework)

| Category | Potential Threat | Threat Vector | Architectural Mitigation in BhuRaksha |
| :--- | :--- | :--- | :--- |
| **Spoofing** | Adversary impersonates a Revenue Patwari or Tehsildar | Stolen passwords, credential stuffing | Multi-Factor Authentication (TOTP OTP) enforced for administrative and officer roles. Django-Axes brute force lockout after 5 consecutive failures. |
| **Tampering** | Malicious insider or compromised admin silently modifies parcel boundary or area in database | Direct SQL execution or backend bypass | Every parcel computes a SHA-256 cryptographic fingerprint (`fingerprint`) over its boundary, area, and ownership. Discrepancies immediately fail integrity validation and alert SOC. |
| **Repudiation** | Officer denies approving a fraudulent transfer or rejecting a legitimate mutation | Lack of auditable logs | Append-only SHA-256 hash chained `AuditLog`. Each block references `prev_hash` and seals its own content in `current_hash`. Deletion or modification of logs is blocked at model and DB level. |
| **Information Disclosure** | Leakage of farmer National ID (Aadhaar) and contact numbers | Public queries, shoulder surfing, API dumps | Sensitive PII fields are encrypted at rest with symmetric Fernet (AES-128-CBC). Front-end views and public APIs strictly mask data (`XXXX-XXXX-4589`). |
| **Denial of Service** | Flooding public parcel verification or GeoJSON rendering endpoints | Automated bot scrapers | Django REST Framework anon/user rate throttling (100 req/day for anon, 1000 req/day for users). IP-level rate restriction. |
| **Elevation of Privilege** | Citizen or farmer modifying request payloads to self-approve mutation or edit land boundary | Parameter tampering | Server-side Role-Based Access Control (RBAC) enforced on both Django templates and DRF API views. |
