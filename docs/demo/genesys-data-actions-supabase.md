# Genesys Data Actions → Supabase RPC (live demo wiring)

Live actions POST to:

`https://njjkupupxvfvymelcjpg.supabase.co/rest/v1/rpc/<function_name>`

## Headers (required)

| Header | Value |
|--------|--------|
| `apikey` | Your `sb_secret_…` key (from Supabase project settings) |
| `Content-Type` | `application/json` |

Do **not** put `sb_secret_…` in `Authorization: Bearer`.

Store the secret in the Web Services integration **User Defined** field `apikey` (Admin → Integrations → `19717556-e7eb-4db8-884e-b07c6f50d927`) and use header `${credentials.apikey}` on actions.

The wire script tries that PUT first; if the Public API rejects credential shape, it falls back to an **inline** `apikey` header on each action (non-secure, visible to org admins — demo only). **Secure** actions cannot be referenced by AVA publish.

## Org integration

Actions are published on Web Services Data Actions integration:

- **Default ID:** `19717556-e7eb-4db8-884e-b07c6f50d927` (`Web Services Data Actions (1)`)
- Override when re-running the wire script: `EOHHS_WSDA_INTEGRATION_ID`

## Automated wiring

From repo root (`.env` with `SUPABASE_SECRET_KEY`; Genesys creds from `.cursor/mcp.json` or env):

```bash
./scripts/wire-genesys-supabase-data-actions.py --replace
```

Then publish a new AVA version so tool `target.id` values match the registry.

Registry: `.ava-lifecycle/eohhs-ma-front-door/data-actions-registry.md`

## RPC mapping

| Data Action name | RPC body JSON |
|------------------|---------------|
| `eohhs_resident_verify_miked` | `p_first_name`, `p_last_name`, `p_date_of_birth` (YYYY-MM-DD) |
| `eohhs_dta_case_status_miked` | `p_case_number`, `p_session_token` |
| `eohhs_dta_register_document_miked` | `p_case_number`, `p_session_token`, `p_document_type`, `p_channel`, `p_conversation_id` |
| `eohhs_masshealth_complete_screening_miked` | `p_session_token`, `p_household_size`, `p_income_band`, `p_coverage_status` |
| `eohhs_escalation_create_handoff_miked` | `p_session_token`, `p_program`, `p_summary`, `p_conversation_id`, `p_channel`, `p_payload` (json) |

## Supabase migration (flat SNAP notice fields)

Apply `supabase/migrations/20250915211000_dta_case_status_flat_notice.sql` so `dta_case_status` returns root-level `notice_type` / `notice_summary` (matches Genesys output schema):

```bash
supabase db push
```

## Escalation queue

Configure Architect / AVA escalation to queue **`support_miked`** (inbound flow **`miked direct to queue`**). See [`architect-voice-routing-miked.md`](architect-voice-routing-miked.md).

## Voice entry

Inbound **+1 781-277-3322** → **`miked direct to queue`** → AVA **EOHHS MA Experience Orchestrator** (v6.0).
