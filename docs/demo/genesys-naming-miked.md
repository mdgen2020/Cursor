# Genesys Cloud naming — `_miked`

All **new or recreated** assets in the demo org must include **`_miked`** in the name so they are identifiable as Mike’s demo work.

## Data Actions (Supabase RPC wrappers)

| Purpose | Name |
|---------|------|
| ID&V | `eohhs_resident_verify_miked` |
| SNAP case read | `eohhs_dta_case_status_miked` |
| Document register | `eohhs_dta_register_document_miked` |
| MassHealth screening | `eohhs_masshealth_complete_screening_miked` |
| Escalation handoff | `eohhs_escalation_create_handoff_miked` |

## AVA

| Asset | Name (when recreated / renamed) |
|-------|----------------------------------|
| Virtual agent | `EOHHS_MA_Experience_Orchestrator_miked` (or equivalent with `_miked`) |

Existing agent ID `96fe2bc6-7f11-41d5-8e6d-8a3ed20291b6` may be renamed in Admin or superseded on next create — confirm after delete/recreate.

## Knowledge (when attached)

Prefer `miked_` or `_miked` in Knowledge Source / Setting names (e.g. `miked_EOHHS_program_knowledge`).

## Architect / telephony (`_miked`)

| Asset | Name |
|-------|------|
| Inbound call flow | **`miked direct to queue`** (reuse; entry → AVA, escalation → queue) |
| Escalation queue | **`support_miked`** |
| Inbound DID | **+1 781-277-3322** |

See [`docs/demo/architect-voice-routing-miked.md`](docs/demo/architect-voice-routing-miked.md).

When you finish deleting the old five actions, say **recreate data actions** (or **continue phase 2b**) and we will create mocks + AVA v1.1 using these names only.
