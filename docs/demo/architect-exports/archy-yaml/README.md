# MV voice — Archy YAML (primary deploy path)

Use these with **Archy MCP** or CLI. **`.i3` files** in the parent folder are for manual Architect import only.

| File | Flow type | Action |
|------|-----------|--------|
| **`miked_mv_VAbotflow_export_for_patch.yaml`** | `botFlow` | **update** + **publish** (live MV bot — handoff + screen pop + Profile) |
| `miked_mv_VAbotflow_v1.yaml` | `botFlow` | **create** only (greenfield / new org) |
| `miked_direct_to_queue_v5_mv.yaml` | `inboundCall` | **update** + **publish** (existing `miked direct to queue`) |

## OAuth client (`miked_Archy`)

`validateYaml` / `create` resolve **Call Agentic Virtual Agent** by name and need:

- **`agentic:virtualAgent:view`** (and usual Architect flow permissions)

If validate fails with `missing.permissions` for `agentic:virtualAgent:view`, add that role to the OAuth client in `~/.archy_config` (Admin → Integrations → OAuth).

**Set Screen Pop** resolves script **`miked_script_2026`** by name — the OAuth client also needs **`scripter:publishedScript:search`** (or equivalent script view) or `validateYaml` / `update` fails with 403 on script lookup.

The **ava-harness** client is not a drop-in substitute (different permission set).

## Commands

```bash
archy validateYaml --file docs/demo/architect-exports/archy-yaml/miked_mv_VAbotflow_export_for_patch.yaml
archy update --file docs/demo/architect-exports/archy-yaml/miked_mv_VAbotflow_export_for_patch.yaml
archy publish --file docs/demo/architect-exports/archy-yaml/miked_mv_VAbotflow_export_for_patch.yaml

archy validateYaml --file docs/demo/architect-exports/archy-yaml/miked_direct_to_queue_v5_mv.yaml
archy update --file docs/demo/architect-exports/archy-yaml/miked_direct_to_queue_v5_mv.yaml
archy publish --file docs/demo/architect-exports/archy-yaml/miked_direct_to_queue_v5_mv.yaml
```

Inbound YAML references **`miked_mv_VAbotflow`** `ver_latestPublished` — publish the bot before inbound.

## AVA binding

- Agent: **`miked_mv_front_door`**
- Version: **`21.0`** **ProductionReady** (use **`ver_latestPublished`** in bot YAML)
- Start context inputs: `first_name`, `state_code=MA`, `conversation_id`, `interaction_channel=voice`

Regenerate `.i3` + refresh docs: `python3 scripts/build-mv-archy-yaml.py`
