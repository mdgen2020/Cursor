# MV voice wiring — org status

**Last verified:** 2026-10-12 (Archy **`miked_Archy`**, org **GenesysSC12**)

| Flow | Type | Flow ID | Published | Notes |
|------|------|---------|-----------|--------|
| **`miked_mv_VAbotflow`** | bot | `59413631-2d7d-4303-8f7f-39e5e8f9ac4a` | **v29.0** | Call AVA **`ver_latestPublished`** → **`MV handoff transfer`** (hydrate, **Set External Contact**, **`miked_script_2026`**) → **Support_MikeD** on failure/timeout/escalation |
| **`miked direct to queue`** | inboundcall | `77cd7c4d-14b4-4fd7-9a4c-dff044f98d7f` | **v11.0** | RMV welcome → bot → disconnect or queue via bot handoff |
| **`miked_eohhs_VAbotflow`** | bot | — | — | Removed from org (repo archive only) |

**Canonical bot YAML (patch/deploy):** [`archy-yaml/miked_mv_VAbotflow_export_for_patch.yaml`](archy-yaml/miked_mv_VAbotflow_export_for_patch.yaml)

**Inbound YAML:** [`archy-yaml/miked_direct_to_queue_v5_mv.yaml`](archy-yaml/miked_direct_to_queue_v5_mv.yaml) (name unchanged; org version **11.0**)

## AVA

| | |
|--|--|
| Agent | **`miked_mv_front_door`** (`0490c8a0-4830-4c57-981b-0623f5a5a466`) |
| Published | **25.0** **ProductionReady** ( verify-before-escalation in tool pre-instructions; 3 custom guardrails ) |
| Eval | **`mv-v1-extended`** **10/10** on **25.0** ([`eval-run-2026-10-13-006`](../../.ava-lifecycle/miked-mv-front-door/eval-runs/eval-run-2026-10-13-006/scorecard.html)) |
| Handoff DA | **`miked_mv_handoff_create`** → `custom_-_65ba764d-f804-40c6-9670-c8a01fc104f7` (includes **`genesys_external_contact_id`**) |
| Design artifact | [`.ava-lifecycle/miked-mv-front-door/design-artifact.json`](../../.ava-lifecycle/miked-mv-front-door/design-artifact.json) |

## Telephony / escalation

| | |
|--|--|
| DID | **+1 781-277-3322** |
| Queue | **`support_miked`** |
| Script | **`miked_script_2026`** |
| Default demo persona | **Linus Smith** — [`MV-linus-smith-demo-cheat-sheet.md`](../MV-linus-smith-demo-cheat-sheet.md) |

## Voice demo checklist (complete)

1. External contacts aligned with Supabase **`work_email`** (Linus: **`mdgen2020@gmail.com`**).
2. **Phase A** — script fields from AVA **`handoff.*`** + hydrate ([`MV-handoff-script-and-profile-miked.md`](../MV-handoff-script-and-profile-miked.md)).
3. **Phase B** — Profile via **`handoff.genesys_external_contact_id`** + Vivek **Set External Contact** on voice.
4. Smoke: **781** → verify → profile / renew / appointment / agent → script + Profile.

## Deploy commands (bot)

```bash
archy validateYaml --file docs/demo/architect-exports/archy-yaml/miked_mv_VAbotflow_export_for_patch.yaml
archy update --file docs/demo/architect-exports/archy-yaml/miked_mv_VAbotflow_export_for_patch.yaml
archy publish --file docs/demo/architect-exports/archy-yaml/miked_mv_VAbotflow_export_for_patch.yaml
```

Publish **AVA 21.0+** before bot if **`OutputData`** / handoff outputs change. Inbound uses bot **`ver_latestPublished`**.

## Archy checks

```bash
archy doesFlowExist --flowName "miked_mv_VAbotflow" --flowType bot
archy isPublished --flowName "miked_mv_VAbotflow" --flowType bot
archy isPublished --flowName "miked direct to queue" --flowType inboundcall
```

## Related

- [`archy-yaml/README.md`](archy-yaml/README.md) — permissions + YAML index  
- [`MV-781-TRANSFER-FIX.md`](MV-781-TRANSFER-FIX.md) — do not End Task after queue transfer  
- [`genesys-data-actions-supabase-mv.md`](../genesys-data-actions-supabase-mv.md)
