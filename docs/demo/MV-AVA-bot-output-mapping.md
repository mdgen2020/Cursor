# MV 781 — AVA end context → bot → script

**Live org:** [MV-WIRING-STATUS.md](architect-exports/MV-WIRING-STATUS.md) · AVA **21.0** · bot **v29** · patch YAML **`miked_mv_VAbotflow_export_for_patch.yaml`**.

## 1. AVA (done in org)

| Item | Value |
|------|--------|
| Agent | **`miked_mv_front_door`** `0490c8a0-4830-4c57-981b-0623f5a5a466` |
| Published | **21.0** **ProductionReady** |
| End-context | `session.contact_email`; `handoff.contact_email`, `handoff.intent_summary`, `handoff.handoff_id`, license/plate/appointment fields, **`handoff.genesys_external_contact_id`** ← **`create_handoff`** |

Bot uses **`ver_latestPublished`**.

## 2. Bot — `miked_mv_VAbotflow` (published from patch YAML — verify-email coalesce + richer script pop)

**Call Agentic Virtual Agent (#12)** mappings:

| AVA input | Value |
|-----------|--------|
| `conversation_id` | *(unset — `Call.ConversationId` is not valid on bot flows)* |
| `state_code` | `MA` |
| `interaction_channel` | `voice` |

| AVA agent output | Bot flow variable |
|------------------|-------------------|
| **`session.contact_email`** | **`Flow.VerifiedCustEmail`** |
| **`handoff.contact_email`** | **`Flow.CustEmail`** |
| **`handoff.intent_summary`** | **`Flow.HandoffSummary`** |
| **`handoff.handoff_id`** | **`Flow.TicketNumber`** |
| **`handoff.license_number`** | **`Flow.HandoffLicenseNumber`** → script **`IncNum`** |
| **`handoff.plate_number`** | **`Flow.HandoffPlateNumber`** → script **`Violation1`** |
| **`handoff.appointments_summary`** | **`Flow.HandoffApptSummary`** → script **`booking_notes`** |
| **`handoff.appointment_*`** | **`Flow.HandoffApptDate`**, **`Loc`**, **`Time`**, **`Conf`** → script appt fields |

**`MV handoff transfer`** first step: **`Flow.CustEmail`** ← handoff email if set, else **`Flow.VerifiedCustEmail`** (verified Supabase `work_email` for external-contact hydrate + script).

**Exit Reason:** **`Flow.AvaExitReason`**

Repo export: `docs/demo/architect-exports/archy-yaml/miked_mv_VAbotflow_export_for_patch.yaml`

Bot **virtual agent** settings: **summarization on**, **MikeD_Summary_Config**, wrap-up codes **RealID** / **Account Information** / **Document Information/Assistance** (required for all MV VA bot flows).

## 3. What the script receives

**Set Screen Pop** (handoff task) already wires:

| Script input | Source |
|--------------|--------|
| `CustomerEmail` | `Flow.CustEmail` |
| `agent_summary` | `Flow.HandoffSummary` |
| `TicketNumber` | `Flow.TicketNumber` |
| `customer_selection` | `ToString(Flow.IBVivrselection)` |
| Name / address | Hydrate data action → `Flow.firstname`, etc. |

If **`agent_summary`** / **`TicketNumber`** are still blank after mapping, check **Composer** bindings on **MA RMV** page (controls must display those script variables).

## 4. Smoke test (Linus)

1. Call **781** as **Linus Smith** → representative → verify → agree to transfer.
2. At handoff: **`Flow.CustEmail`**, **`Flow.HandoffSummary`**, **`Flow.TicketNumber`**, **`Flow.ContactGUID`**, license/plate populated.
3. Agent script + Profile: Linus / Quincy; ticket, license, plate, appointments on script.

## Repo

- Definition: `.ava-lifecycle/miked-mv-front-door/design-artifact.json`
- Republish: `publish-mv-from-artifact.py` (TestReady) then **`publish_version`** ProductionReady, or ava-harness MCP
- Lineage: [mv-script-handoff-lineage-miked.md](mv-script-handoff-lineage-miked.md)
