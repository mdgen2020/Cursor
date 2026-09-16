# Supabase — EOHHS demo backend

**Project URL:** `https://njjkupupxvfvymelcjpg.supabase.co`  
**Project ref:** `njjkupupxvfvymelcjpg`

Persistence for simulated Massachusetts programs (BEACON-shaped SNAP, MassHealth screening). Genesys AVA Data Actions call **RPC functions only** — not raw tables.

## Migrations

| Order | File | Purpose |
|-------|------|---------|
| 1 | `20250915200000_baseline_eohhs_schema.sql` | Tables, RLS (no policies), Linus seed |
| 2 | `20250915203000_phase1_auth_handoff_reset.sql` | Auth sessions, gated RPCs, handoff, reset |

## Canonical project

**Use `njjkupupxvfvymelcjpg` only.** (Phase 1 was mistakenly pushed to `mdwdkiwtawqcoxdlrvbd` once; ignore that project.)

## Link and apply migrations

1. Create a [Supabase access token](https://supabase.com/dashboard/account/tokens) (PAT — not the project secret key).
2. Login and link:

```bash
export SUPABASE_ACCESS_TOKEN="sbp_..."
cd /Users/michael.debiase/Genesys/AXL/sc12
supabase login
supabase link --project-ref njjkupupxvfvymelcjpg
supabase db push
```

3. Optional: pull remote schema into a baseline migration after first link:

```bash
supabase db pull
```

## API key header rule

New-format keys (`sb_publishable_...`, `sb_secret_...`) go in the **`apikey`** header only. Do **not** use `Authorization: Bearer` for those keys.

Genesys Data Actions and local scripts use the **secret** key as `apikey`.

## Phase 1 RPC surface

| RPC | Purpose |
|-----|---------|
| `resident_verify` | ID&V → `session_token` |
| `dta_case_status` | Gated case read (requires token) |
| `dta_register_document` | Mark document received (containment) |
| `masshealth_upsert_screening_answer` | Capture screening answers |
| `masshealth_complete_screening` | Finish screening (`likely_*` only) |
| `masshealth_screening_result` | Read latest screening (gated) |
| `escalation_create_handoff` | Persist Copilot/handoff payload |
| `demo_reset_scenario` | Presenter reset (local script) |

See [`docs/sdd/supabase-integration.md`](../docs/sdd/supabase-integration.md) for Linus ID&V test values and script usage.
