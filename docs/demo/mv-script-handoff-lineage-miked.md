# Massachusetts RMV voice — script handoff lineage (`miked_script_2026`)

Keep **Architect** aligned with other demos that screen-pop **`miked_script_2026`**: route script pages with **`Flow.IBVivrselection`**, then map **`customer_selection`** from that flow variable on **Set Screen Pop** (typically **`ToString(Flow.IBVivrselection)`** when the flow variable is an **Integer**).

Reference (NYS DOL Messenger): [`nydol-digital-data-lineage-miked.md`](nydol-digital-data-lineage-miked.md), [`nydol-screen-pop-field-mappings.md`](nydol-screen-pop-field-mappings.md).

## Script routing (Composer)

| Script variable | Script router |
|-----------------|---------------|
| **`customer_selection`** | Custom action **`startpageselect`** on **Redirect Page** |

| **`customer_selection`** value | Page |
|--------------------------------|------|
| **`123`** | **MA RMV** (landing) |
| *(in-page navigation)* | **MA RMV Real ID** (Copilot NBA; not selected via `123`) |

NYS DOL landing uses **`132`** the same way.

## Architect pattern (inbound + handoff)

```text
[Inbound or bot entry]
  → Update Data: Flow.IBVivrselection = 123     ← RMV page code (DOL uses 132)
  → … Call Bot / Call AVA …
  → (on transfer) Search External Contact → Set External Contact
  → Set Screen Pop → miked_script_2026
       customer_selection ← ToString(Flow.IBVivrselection)
       … contact / handoff fields …
  → Transfer to ACD → support_miked
```

**Do not** hard-code **`123`** only on **Set Screen Pop** while other flows use **`IBVivrselection`**. Seed **`Flow.IBVivrselection`**, then map **`customer_selection`** from it so NBA flows can change the integer/string later (e.g. a future REAL ID NBA code) without diverging from the DOL pattern.

### Set Screen Pop — minimum RMV mapping

| Script input | Architect expression (MV) |
|--------------|-------------------------|
| **`customer_selection`** | **`ToString(Flow.IBVivrselection)`** *(or direct ref if the variable is already String)* |
| **`CustomerFirstName`** / **`CustomerLastName`** | External contact or flow fields after email lookup |
| **`CustomerEmail`** | From **`work_email`** / contact merge |
| **`TicketNumber`** | Optional demo placeholder or handoff id |
| **`agent_summary`** | Handoff intent (when wired on script UI) |

Script input **`customer_selection`** reference id: **`a69ab769-a1e4-41e5-ac73-4df05811c0dc`**.

## Repo / org gap (2026-09-30)

**Archy YAML** ([`miked_mv_VAbotflow_v1.yaml`](architect-exports/archy-yaml/miked_mv_VAbotflow_v1.yaml), [`miked_direct_to_queue_v5_mv.yaml`](architect-exports/archy-yaml/miked_direct_to_queue_v5_mv.yaml)) implements the DOL-style chain:

- Inbound + bot **Update Data** → **`Flow.IBVivrselection = 123`**
- Task **`MV handoff transfer`**: **External Contact by eMail** → **Set Screen Pop** (`customer_selection` ← **`ToString(Flow.IBVivrselection)`**) → **Transfer to ACD** **`Support_MikeD`**
- **Call AVA** agent outputs → **`Flow.CustEmail`**, **`Flow.HandoffSummary`**, **`Flow.TicketNumber`**, **`Flow.FirstName`**
- Failure / timeout / agent escalation (**Exit**, not raw Transfer) → same handoff task

**Org (2026-10-12):** AVA **21.0** ProductionReady; bot **v29** maps full **`handoff.*`** + **`handoff.genesys_external_contact_id`** → **`Flow.ContactGUID`** (Profile). Snapshot: [MV-WIRING-STATUS.md](architect-exports/MV-WIRING-STATUS.md). Step-by-step: [MV-AVA-bot-output-mapping.md](MV-AVA-bot-output-mapping.md).

| AVA agent output | Bot variable |
|------------------|--------------|
| `handoff.contact_email` | `Flow.CustEmail` |
| `handoff.intent_summary` | `Flow.HandoffSummary` |
| `handoff.handoff_id` | `Flow.TicketNumber` |
| `handoff.genesys_external_contact_id` | `Flow.ContactGUID` |
| `handoff.license_number` / `plate_number` / appointment fields | `Flow.Handoff*` → script |

## Related

- [`MV-greenfield-import-readme.md`](architect-exports/MV-greenfield-import-readme.md)
- [`architect-voice-routing-mv-miked.md`](architect-voice-routing-mv-miked.md)
