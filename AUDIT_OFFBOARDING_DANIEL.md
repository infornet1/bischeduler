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

### ✅ Completed 2026-07-13
- **OS account `dbongianni`** — LOCKED: login shell set to `/usr/sbin/nologin` and account locked (`passwd -S` → `L`). `webdev` group membership retained by decision. Verified no processes/cron/services/sessions ran as this user.
- **Shared/generic admin password rotated** — `admin@ueipab.edu.ve` (this app, sole `platform_admin`) re-hashed with werkzeug `pbkdf2:sha256`; new hash verified. Distinct from control_asistencias's password (cross-app reuse eliminated). Plaintext delivered out-of-band; **not recorded here**.

### Still pending
- Named/personal admin accounts — intentionally **not** rotated (scope limited to shared accounts by decision).
- App secrets exposed to prior filesystem access — not yet rotated.
- MySQL `root` has no password.
- Rotate the `infornet1` GitHub PAT exposed during this work.

> Note: earlier the audit commit was blocked (403); it was subsequently pushed to `infornet1/bischeduler` after a credential with org write access was provided.
