# Phase 2 — EOHHS AVA

## Published in Genesys Cloud

| Field | Value |
|-------|--------|
| **AVA name** | EOHHS MA Experience Orchestrator |
| **Agent ID** | `96fe2bc6-7f11-41d5-8e6d-8a3ed20291b6` |
| **Version** | **`7.0`** published **TestReady** — live Supabase + ID&V DOB fix (was 6.0) |
| **Prior** | v3.0 mocks only; v5.0 draft failed (secure actions blocked by AVA) |
| **Lifecycle slug** | `eohhs-ma-front-door` |

Canonical artifact: `.ava-lifecycle/eohhs-ma-front-door/design-artifact.json`

## Live Supabase wiring (done)

| Item | Detail |
|------|--------|
| **Integration** | `19717556-e7eb-4db8-884e-b07c6f50d927` (Web Services Data Actions) |
| **Wire script** | `./scripts/wire-genesys-supabase-data-actions.py --replace` |
| **Registry** | `.ava-lifecycle/eohhs-ma-front-door/data-actions-registry.md` |
| **Auth** | `apikey` header on each action → Supabase `sb_secret_…` (inline for demo; move to User Defined integration credential when possible) |
| **DB migration** | `20250915211000_dta_case_status_flat_notice.sql` — run `supabase db push` for flat `notice_type` / `notice_summary` on case status |

Five tools unchanged by name; **action IDs** updated in v6.0.

## What v6.0 includes

- Front-door role, SNAP vs MassHealth routing, five gated tools with ToolOutput chaining
- Live RPCs: `resident_verify`, `dta_case_status`, `dta_register_document`, `masshealth_complete_screening`, `escalation_create_handoff`

## Remaining

- **Architect:** wire **`miked direct to queue`** → AVA → escalation **`support_miked`** — [`architect-voice-routing-miked.md`](architect-voice-routing-miked.md)
- Knowledge Fabric + AVA knowledge tool
- Digital embed (rent proof upload)
- **ProductionReady** AVA before stakeholder DID (if TestReady inbound blocked)
- Copilot / VS / presenter runbook
