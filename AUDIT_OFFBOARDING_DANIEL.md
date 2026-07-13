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

---

## Status recap — 2026-07-13 (cross-app offboarding)

### Daniel — application account access
| App | Account | Status |
|---|---|---|
| control_asistencias | profesor `id_usuario=2` | ✅ DISABLED (`activo=0`) |
| control_minutas | none | ✅ N/A — no account |
| bischeduler (horarios) | none | ✅ N/A — no account (this app) |
| scheduler (`gestion_horarios`) | no auth (decommissioned) | ✅ N/A |

### Still PENDING
- 🔴 **OS account `dbongianni`** — still has shell + `webdev` write access to production code. Highest remaining risk. Not yet locked.
- 🔴 **Admin password rotation** — nothing rotated yet:
  - Priority 1 (shared/reused): `admin@ueipab.edu.ve` (this app + control_asistencias), `admin@sistema.com` (minutas).
  - Priority 2: named admin accounts across apps (policy rotation after departure).
  - Priority 3: app secrets readable from disk; MySQL `root` currently has no password.

> Note: this repo's audit commit could not be pushed to `infornet1/bischeduler` (403 — stored credential `Ueipabdev1` lacks write access). Pending a credential with access to the `infornet1` org.
