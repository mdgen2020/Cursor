# Massachusetts RMV — greenfield Architect flows

**Live org (2026-10-12):** see **[`MV-WIRING-STATUS.md`](MV-WIRING-STATUS.md)** — AVA **21.0** ProductionReady, bot **v29**, inbound **v11**, **781** live.  
**Greenfield / new org:** exports below; eval baseline **`mv-v1-extended`** 10/10 on **7.0** (`eval-run-2026-09-30-001`).

## Generate exports

```bash
python3 scripts/build-mv-archy-yaml.py   # Archy YAML + .i3
# or
python3 scripts/build-mv-greenfield-flows.py
```

## Deploy (preferred): Archy YAML + MCP

See **[`archy-yaml/README.md`](archy-yaml/README.md)** — live patches use **`miked_mv_VAbotflow_export_for_patch.yaml`**; greenfield uses **`miked_mv_VAbotflow_v1.yaml`** + **`miked_direct_to_queue_v5_mv.yaml`**.

## Manual `.i3` import order

### 1. Bot flow `miked_mv_VAbotflow`

1. Architect → **Flows** → **Bot flows** → **Import** → `miked_mv_VAbotflow_v1-0.i3BotFlow`
2. Open **Call Agentic Virtual Agent** → confirm **`miked_mv_front_door`** version **7.0** (or latest **ProductionReady**).
3. Bind **start context** inputs if needed (`first_name`, `conversation_id`).
4. Confirm both **Transfer to ACD** actions target **`Support_MikeD`** / **`support_miked`**.
5. **Publish** bot flow (note version, e.g. **1.0**).

### 2. Record bot flow ID

```bash
echo '<published-bot-flow-uuid>' > docs/demo/architect-exports/miked_mv_VAbotflow.flow-id
python3 scripts/build-mv-greenfield-flows.py --inbound-only
```

### 3. Inbound `miked direct to queue` (MV variant)

1. Import `miked direct to queue_v5-mv-0.i3InboundFlow`
2. Verify welcome TTS references **Registry of Motor Vehicles**.
3. **Call Bot Flow** points at **`miked_mv_VAbotflow`** (published).
4. **Publish** inbound flow; assign **+1 781-277-3322** to this published version.

## Post-import (manual, Composer)

Agent script **`miked_script_2026`** already includes RMV pages in org export (see `miked_script_2026.script`):

| Page | Role |
|------|------|
| **MA RMV** | Landing screen after redirect |
| **MA RMV Real ID** | Copilot next-best-action (REAL ID) content; linked from landing via in-script navigation |

**Redirect:** **`Generic Start Page` → `Redirect Page`** runs custom action **`startpageselect`**, which routes on script variable **`customer_selection`** (same pattern as NYS DOL **`132`**, etc.).

| **`customer_selection`** | Target page |
|--------------------------|-------------|
| **`123`** | **MA RMV** |

### Keep consistent with other inbound flows (IBV → script)

Same pattern as NYS DOL (**`Flow.IBVivrselection` = `132`** → script **`customer_selection`**):

1. **Update Data** (inbound before **Call Bot Flow**, or at bot entry): **`Flow.IBVivrselection` = `123`** (Integer or String; match your other flows).
2. **Set Screen Pop** on transfer: **`customer_selection` ← `ToString(Flow.IBVivrselection)`** (Architect shows the Integer→String note when the flow variable is numeric).

Full lineage: [`mv-script-handoff-lineage-miked.md`](../mv-script-handoff-lineage-miked.md).

**Note:** YAML/i3 builds from **`build-mv-greenfield-flows.py`** do not yet encode this chain; live **v2/v6** publishes may need an Architect patch until the builder is updated.

**Fields on MA RMV today:** `CustomerFirstName`, `CustomerLastName`, address lines, `CustomerEmail`, `TicketNumber` (script JSON). Wire Architect from verify/handoff/external contact; add **`agent_summary`** on the page or map an existing text component if you extend the export.

Optional: structured fields from AVA **`p_fields_json`** on `create_handoff` → new script variables + page bindings.

On **Transfer to ACD** (in bot or inbound), chain:

**Search External Contacts** (by email) → **Set External Contact** → **Set Screen Pop** → **`miked_script_2026`**

Reuse data action **`External Contact by eMail - MikeD - Full`** (`custom_-_816547b6-db32-410d-8aae-9f6824846583`) where email comes from verify/handoff.

## Smoke test

1. `./scripts/demo-reset.sh all` (if MV reset script available) or verify Supabase personas.
2. Call **781-277-3322**.
3. **Linus Smith**, DOB **1988-06-23** → profile summary.
4. Ask for a **representative** → queue **`support_miked`** with handoff row in Supabase.

## Flags

```bash
python3 scripts/build-mv-greenfield-flows.py --bot-only
python3 scripts/build-mv-greenfield-flows.py --inbound-only
```

Environment override: `MIKED_MV_VABOTFLOW_ID=<uuid>` instead of `.flow-id` file.
