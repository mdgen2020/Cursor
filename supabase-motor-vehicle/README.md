# Supabase — `motor_vehicle` project

**Project ref:** `mdwdkiwtawqcoxdlrvbd`  
**Dashboard:** [motor_vehicle SQL editor](https://supabase.com/dashboard/project/mdwdkiwtawqcoxdlrvbd)

Migrations in this folder apply to **`motor_vehicle` only** (not `eohhs_demo` in repo `supabase/`).

Apply via Supabase MCP `apply_migration` or CLI linked to this project.

## RPCs (Genesys Custom REST)

| RPC | Purpose |
|-----|---------|
| `miked_mv_resident_verify` | ID&V → `session_token`, `work_email` |
| `miked_mv_get_profile` | License + registrations for session |
| `miked_mv_registration_renew` | Pay renew registration (`p_plate_number`) |
| `miked_mv_license_book_appointment` | Book RMV visit (`p_confirmation_code` from security generator) |
| `miked_mv_handoff_create` | Escalation structured packet |

Demo personas: [`.ava-lifecycle/miked-mv-front-door/demo-personas.md`](../.ava-lifecycle/miked-mv-front-door/demo-personas.md)

## Local credentials (keep independent from EOHHS)

| Project | Env file | URL host |
|---------|----------|----------|
| `eohhs_demo` | `.env` | `njjkupupxvfvymelcjpg.supabase.co` |
| `motor_vehicle` | `.env.motor-vehicle` | `mdwdkiwtawqcoxdlrvbd.supabase.co` |

Same **variable names** (`SUPABASE_URL`, `SUPABASE_SECRET_KEY`), different **values** per project. Copy [`.env.motor-vehicle.example`](../.env.motor-vehicle.example) → `.env.motor-vehicle` and paste the secret from [motor_vehicle → Project Settings → API](https://supabase.com/dashboard/project/mdwdkiwtawqcoxdlrvbd/settings/api).
