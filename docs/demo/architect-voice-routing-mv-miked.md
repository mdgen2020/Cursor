# Architect voice routing — Massachusetts RMV (`miked_mv_front_door`)

Greenfield voice demo reusing **781** inbound plumbing and **`support_miked`** escalation.

## Targets

| Asset | Value |
|-------|--------|
| **Inbound DID** | **+1 781-277-3322** |
| **Inbound call flow** | **`miked direct to queue`** (import **v5-mv** export) |
| **Front-door AVA** | **`miked_mv_front_door`** |
| **Agent ID** | `0490c8a0-4830-4c57-981b-0623f5a5a466` |
| **AVA version (org)** | **21.0** **ProductionReady** (eval baseline historically **7.0**) |
| **Voice bot flow** | **`miked_mv_VAbotflow`** |
| **Escalation queue** | **`support_miked`** (`dc15ad2c-7917-413f-9a00-4f52df4d4602`) |
| **Agent script (screen pop)** | **`miked_script_2026`** (`09d11916-8ffd-4feb-9e6b-9568aaf8bfe3`) — add **RMV pages only** |

## Call path

```text
781-277-3322
  → Inbound: miked direct to queue (v5-mv)
  → Play welcome (RMV TTS)
  → Call Bot Flow → miked_mv_VAbotflow
       → Call Agentic Virtual Agent (miked_mv_front_door ver_latestPublished)
            → Success → Exit Bot Flow → Inbound Disconnect
            → Failure / Timeout / Escalation → Transfer to ACD → support_miked
  → (Optional) Set Screen Pop → miked_script_2026 on transfer path
```

Genesys requires **Call Agentic Virtual Agent** inside a **bot flow**, not inside the inbound call flow.

## Build import files (repo)

```bash
python3 scripts/build-mv-greenfield-flows.py
```

Outputs:

| File | Import as |
|------|-----------|
| `docs/demo/architect-exports/miked_mv_VAbotflow_v1-0.i3BotFlow` | Architect → **Bot flows** |
| `docs/demo/architect-exports/miked direct to queue_v5-mv-0.i3InboundFlow` | Architect → **Inbound call flows** |

Details: [`MV-greenfield-import-readme.md`](architect-exports/MV-greenfield-import-readme.md)

## Start context (Call AVA inputs)

The bot export pre-wires **InputData** for the AVA:

| Property | Default in export | Architect binding |
|----------|-------------------|-------------------|
| `first_name` | empty | Optional: ANI / external contact / IVR |
| `state_code` | `MA` | Literal (v1) |
| `conversation_id` | empty | `Call.ConversationId` or platform conversation variable |
| `interaction_channel` | `voice` | Literal |

These map to AVA **InputData** in `design-artifact.json`.

## Handoff + script

1. AVA calls **`create_handoff`** (Supabase `miked_mv_handoff_create`) before **Escalation**.
2. On transfer, Architect should **Search External Contacts** by **`work_email`** from verify/handoff (same pattern as NY DOL Messenger).
3. Seed **`Flow.IBVivrselection` = `123`**, then **Set Screen Pop** on **`miked_script_2026`** with **`customer_selection` ← `ToString(Flow.IBVivrselection)`** (same IBV pattern as DOL **`132`**). Add RMV contact/handoff fields (intent summary, topic from `p_fields_json` when used). See [`mv-script-handoff-lineage-miked.md`](mv-script-handoff-lineage-miked.md).

See [`.ava-lifecycle/miked-mv-front-door/demo-personas.md`](../../.ava-lifecycle/miked-mv-front-door/demo-personas.md) for persona ↔ `work_email` linkage.

## Publish order (voice — current)

1. **AVA** — create/publish from [`.ava-lifecycle/miked-mv-front-door/design-artifact.json`](../../.ava-lifecycle/miked-mv-front-door/design-artifact.json) (**21.0+** ProductionReady).
2. **Bot** — `archy update` + `publish` on [`miked_mv_VAbotflow_export_for_patch.yaml`](architect-exports/archy-yaml/miked_mv_VAbotflow_export_for_patch.yaml) (org **v29.0** as of 2026-10-12).
3. **Inbound** — `miked_direct_to_queue_v5_mv.yaml` if welcome/routing changes (org **v11.0**); keep **781** on published inbound.
4. Smoke: **781** → **Linus Smith** — profile, reg renewal, appointment, agent handoff → [`MV-linus-smith-demo-cheat-sheet.md`](MV-linus-smith-demo-cheat-sheet.md).

Org snapshot: [`architect-exports/MV-WIRING-STATUS.md`](architect-exports/MV-WIRING-STATUS.md).

## Eval baseline

**`mv-v1-extended`**: 10/10 on **7.0** (`eval-run-2026-09-30-001`). Architect wiring does not replace Cicero regression before promote.

## Related

- [`architect-voice-routing-miked.md`](architect-voice-routing-miked.md) — EOHHS pattern (deleted org assets; archive exports only)
- [`genesys-data-actions-supabase-mv.md`](genesys-data-actions-supabase-mv.md) — live `miked_mv_*` actions
- [`nydol-screen-pop-field-mappings.md`](nydol-screen-pop-field-mappings.md) — screen pop expression patterns for **`miked_script_2026`**
