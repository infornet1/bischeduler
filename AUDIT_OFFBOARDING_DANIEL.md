# Audit — Offboarding: Daniel Bongianni

**App:** bischeduler (`/bischeduler`, port 5005) — schedule management ("horarios")
**Date:** 2026-07-13
**Performed by:** Gustavo Perdomo (gustavo.perdomo@ueipab.edu.ve)
**Reason:** User no longer works with the organization. Access verification for audit vault.

## Subject
| Field | Value |
|---|---|
| Name | Daniel Bongianni |
| Email | daniel.bongianni@ueipab.edu.ve |

## Access footprint found — NONE
Verified in the `bischeduler_master` database:
- `users` where `username`/`email LIKE '%daniel%'`, `first_name LIKE '%Daniel%'`, `last_name LIKE '%ongianni%'` → **0 rows**.
- `user_audit_logs` where `description`/`user_agent`/`new_values LIKE '%daniel%'` → **0 rows**.
- Total accounts in system: 1 (`admin`, role `platform_admin`) — Daniel is not among them.

**Conclusion:** Daniel never had an account in bischeduler. No disable action required.

## Related note (schedule apps)
The legacy `scheduler` app (DB `gestion_horarios`) is decommissioned — its nginx location is commented out, no process running, and it has no authentication/users table. No Daniel presence there either.

## Follow-up (tracked separately)
- [ ] Rotate superadmin password: `admin@ueipab.edu.ve` (role `platform_admin`) — note this email is also an admin in control_asistencias; verify credentials are not reused across apps.
