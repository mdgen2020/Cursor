# Genesys org — retired / planned retirement assets

Track org objects removed while definitions remain in Git under `docs/demo/architect-exports/` and `.ava-lifecycle/`.

## Planned deletion (archived in repo)

| Name | Type | Action ID | Repo archive |
|------|------|-----------|--------------|
| `eohhs_resident_verify_miked` | Data Action → Supabase `resident_verify` | `custom_-_e7e7c05d-3432-4a71-b90a-e534d80ac5ea` | `org-archive-2026-09-28-data-actions/` + `data_actions/custom_-_e7e7c05d-….json` |
| `eohhs_dta_case_status_miked` | Data Action → `dta_case_status` | `custom_-_988e6409-cf34-4d74-b0fb-456ecc7b9395` | same folder |
| `eohhs_dta_register_document_miked` | Data Action → `dta_register_document` | `custom_-_ebb905ca-4f7b-49f1-984f-8d2f7e06a524` | same folder |
| `eohhs_masshealth_complete_screening_miked` | Data Action → `masshealth_complete_screening` | `custom_-_cf6faa3e-165f-4d24-bc92-069a0d949552` | same folder |
| `eohhs_escalation_create_handoff_miked` | Data Action → `escalation_create_handoff` | `custom_-_b0d5536a-b5e2-4a98-a517-d8b454f5ea91` | same folder |

**Integration (EOHHS only, not DOL):** `19717556-e7eb-4db8-884e-b07c6f50d927` — keep or delete separately; recreate via `scripts/wire-genesys-supabase-data-actions.py`.

## Keep in org (not for retirement)

| Name | ID | Notes |
|------|-----|-------|
| **`miked direct to queue`** | `77cd7c4d-14b4-4fd7-9a4c-dff044f98d7f` | Test / repurpose inbound; **published 4.0** — no EOHHS bot / no Call AVA. Export: `miked direct to queue_v4-0.i3InboundFlow` |

## Deleted in org

| Date | Name | Type | ID | Repo archive |
|------|------|------|-----|--------------|
| **2026-09-28** | **`miked_eohhs_VAbotflow`** | Bot flow (voice / Agentic VA) | `0ddb5a61-7d13-4d92-bf72-02ef2b70c07c` | `miked_eohhs_VAbotflow_v2-0_org-archive.i3BotFlow` + `.json`; `miked_eohhs_VAbotflow.flow-id`; legacy `*_v1-0`, `*_v2-0` |
| **2026-09-28** | **EOHHS MA Experience Orchestrator** | Agentic virtual agent | `96fe2bc6-7f11-41d5-8e6d-8a3ed20291b6` | `.ava-lifecycle/eohhs-ma-front-door/org-archive-2026-09-28-*`, `design-artifact.json`, `publish-eohhs-from-artifact.py` — last version **11.0 ProductionReady** |

**Context:** Inbound **`miked direct to queue` v4.0** has no Call Bot / Call AVA. Recreate EOHHS AVA = new agent in AI Studio + publish from artifact (new agent UUID).
