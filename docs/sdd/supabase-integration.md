# Supabase integration — Phase 1

## Project

- **URL:** https://njjkupupxvfvymelcjpg.supabase.co
- **Integration style:** AVA Data Actions → `POST /rest/v1/rpc/<function_name>`
- **Headers:** `apikey: <secret key>`, `Content-Type: application/json` — **no** `Authorization: Bearer` for sb_* keys

## Synthetic resident — Linus Turing (ID&V)

Used in rehearsal and on stage for **conversational verify** (`resident_verify`).

| Field | Demo value |
|-------|------------|
| First name | `Linus` |
| Last name | `Turing` |
| Date of birth | `1988-06-23` |
| Postal code | `02139` |
| SNAP case (alternate verify) | `SNAP-MA-100234` |

**Primary verify (recommended on voice):** name + DOB  
**Alternate verify:** name + case number + postal code

On success, RPC returns `session_token` (≈2 hours). Pass that token into all gated RPCs.

## Gated RPC parameters

### `dta_case_status`

```json
{
  "p_case_number": "SNAP-MA-100234",
  "p_session_token": "<from resident_verify>"
}
```

### `dta_register_document` (containment — digital beat)

```json
{
  "p_case_number": "SNAP-MA-100234",
  "p_session_token": "<token>",
  "p_document_type": "<type from case documents list>",
  "p_channel": "digital",
  "p_conversation_id": "<genesys conversation id>"
}
```

Use the `document_type` value returned in `dta_case_status.documents` for the missing rent proof row.

### Presenter reset — `demo_reset_scenario`

```json
{
  "p_scenario": "all",
  "p_reset_key": "eohhs-demo-reset"
}
```

Change passphrase in table `demo_config` (`reset_passphrase`) before any external rehearsal.

## Local scripts

From repo root, with env vars set (see `.env.example`):

```bash
cp .env.example .env   # then set SUPABASE_SECRET_KEY only
./scripts/demo-reset.sh all
./scripts/test-rpc-flow.sh
```

## Authorization model (demo abstraction)

- Tables remain **RLS enabled, no client policies**.
- `security definer` RPCs enforce:
  - `resident_verify` → inserts `demo_auth_sessions`
  - Gated reads/writes require valid, unexpired `session_token` bound to resident/case

This is the real authorization boundary for the demo — not a UI toggle.

## Breaking change from initial setup

`dta_case_status(text)` and `masshealth_screening_result(text, text)` are **replaced** by token-gated signatures. Update any manual tests and Phase 2 AVA Data Actions accordingly.
