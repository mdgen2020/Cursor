# NY DOL — Set Screen Pop field mappings (`miked_script_2026`)

You fixed **`customer_selection` ← `Flow.IBVivrselection`**. Use this for the remaining **Set Screen Pop** inputs on **`DOL transfer`** and **`Support Transfer`** in **`msg_dig_nydol_miked`**.

**Context:** **`Dig_bot_nydol` v14** is still a **classic** digital bot (`agenticVirtualAgentEnabled: false`). It already loads **`Flow.incnumber`**, **`Flow.incident_state`**, **`Flow.short_des`**, **`Slot.Name`**, **`Slot.email`** from the claim / contact path. Those must be **exported to the inbound flow**, then into the script.

---

## Step A — `Dig_bot_nydol` v14 (digital bot flow)

Export reference: [`architect-exports/Dig_bot_nydol_v14-0.json`](architect-exports/Dig_bot_nydol_v14-0.json)

### A1. Mark bot variables as **Output** (Architect → Variables)

So the parent inbound flow can receive them on **Call Digital Bot Flow → Outputs**:

| Bot variable | Today `isOutput` | Set to |
|--------------|------------------|--------|
| `Flow.incnumber` | true | keep |
| `Flow.INCtoScript` | true | keep |
| `Flow.incident_state` | **false** | **true** |
| `Flow.short_des` | **false** | **true** |
| `Flow.priority` | false | optional **true** (for `Claim_level` / `priority_level`) |
| `Slot.Name` | true | keep |
| `Slot.email` | true | keep |

### A2. **Update Data** before **Exit Bot Flow** (claim-status path)

On the path where SNOW returns claim status (after **`Flow.incnumber`** and **`Flow.incident_state`** are set), add **Update Data** immediately **before** **Exit Bot Flow** (or before the handoff that returns control to **`msg_dig_nydol_miked`**):

| Variable | Expression |
|----------|------------|
| **`Flow.INCtoScript`** | **`Flow.incnumber`** |

(`Flow.INCtoScript` is declared as an output but is **never assigned** in v14 — this fixes **`Flow.INCScript`** on the inbound side.)

Optional (NBA / script banner text):

| Variable | Expression |
|----------|------------|
| **`Flow.INCtoScript`** | **`Append(Flow.incnumber, " — ", Flow.incident_state)`** | if you want status in the string passed to script |

Publish **`Dig_bot_nydol` v14+**.

---

## Step B — `msg_dig_nydol_miked` (inbound message flow)

### B1. Add two inbound variables (Architect → Variables)

| Name | Type | Purpose |
|------|------|---------|
| **`Flow.IncState`** | String | SNOW **`incident_state`** |
| **`Flow.ClaimShort`** | String | SNOW **`short_description`** |

(Names must match what you wire below.)

### B2. **Call Digital Bot Flow** → **`Dig_bot_nydol`** → **Outputs**

You already map **`Flow.incnumber` → `Flow.incfrombot`** and **`Slot.Name` → `Flow.FirstName`**. **Add** output rows:

| Bot output parameter | Assign to inbound variable |
|----------------------|----------------------------|
| **`Flow.incident_state`** | **`Flow.IncState`** |
| **`Flow.short_des`** | **`Flow.ClaimShort`** |
| **`Flow.INCtoScript`** | **`Flow.INCScript`** (already partially wired on inputs; ensure **return** maps into **`Flow.INCScript`**) |

Publish inbound flow.

---

## Step C — **Set Screen Pop** → script **`miked_script_2026`**

On **both** tasks **`DOL transfer`** and **`Support Transfer`**, set each script input **Value** to:

| Script variable | Architect expression |
|-----------------|----------------------|
| **`customer_selection`** | **`Flow.IBVivrselection`** *(you did this)* |
| **`claim_number`** | **`Flow.incfrombot`** |
| **`IncNum`** | **`Flow.incfrombot`** *(already wired)* |
| **`TicketNumber`** | **`Flow.incfrombot`** *(already wired)* |
| **`claim_descript`** | **`Flow.ClaimShort`** |
| **`IncState`** | **`Flow.IncState`** |
| **`acct_status`** | **`Flow.IncState`** |
| **`priority_level`** | **`Flow.IncState`** *or* map bot **`Flow.priority`** if you exported it |
| **`Claim_level`** | **`Flow.IncState`** *(demo: same as status; change if you add priority output)* |
| **`customer_name`** | **`Trim(Append(ToDisplayString(Flow.FirstName), If(IsNotSetOrEmpty(ToDisplayString(Flow.FirstName)), "", " "), ToString(Flow.LastName)))`** |
| **`CustomerFirstName`** | **`Flow.FirstName`** *(already wired)* |
| **`agent_summary`** | **`Trim(Append("NYS DOL Messenger handoff — claim ", ToDisplayString(Flow.incfrombot), If(IsNotSetOrEmpty(ToDisplayString(Flow.IncState)), "", Append(", status: ", Flow.IncState)), If(IsNotSetOrEmpty(ToDisplayString(Flow.ClaimShort)), "", Append(". ", Flow.ClaimShort))))`** |

### Banners (optional demo polish)

| Script variable | Suggested value |
|-----------------|-----------------|
| **`banner_text`** | **`Flow.ClaimShort`** *or* literal **`Review claim with the resident`** |
| **`banner_color`** | Literal **`#00447C`** *(NY-style blue)* *or* leave blank |

Leave **`balance_due`**, **`due_date`**, RMV **`Viol*`** fields empty unless you reuse them for DOL.

---

## Step D — Page routing (NYS DOL landing only)

| Page | Mechanism |
|------|-----------|
| **NYS DOL** (landing) | **`customer_selection` ← `Flow.IBVivrselection`** (e.g. **`132`** before bot in inbound flow) |
| **NYS DOL NBA** | **Copilot only** — not set by Messenger / inbound / bot exports |

Import patched flows: [`architect-exports/NYDOL-i3-import-readme.md`](architect-exports/NYDOL-i3-import-readme.md)

---

## Quick test (Linus / INC0010123)

1. Messenger → complete claim path in **`Dig_bot_nydol`** so **`Flow.incnumber`** = **`INC0010123`** and status/description are set.  
2. Trigger **`DOL transfer`** (agent path).  
3. Agent script should show:  
   - **NYS DOL** page (`132`)  
   - **claim_number** / **IncNum** = **INC0010123**  
   - **IncState** / **acct_status** = SNOW state  
   - **claim_descript** = short description  
   - **customer_name** from **`Flow.FirstName`**

---

## Later: **`DOL_Front_Door_miked`** AVA in this bot

**v14 does not call the AVA yet.** To replace the classic claim dialog with the AVA:

1. Enable **Agentic Virtual Agent** on **`Dig_bot_nydol`**.  
2. Add **Call Agentic Virtual Agent** → **`DOL_Front_Door_miked`** **5.0+**.  
3. Map AVA **OutputData** (`claim_lookup.0.number`, `claim_lookup.0.incident_state`, appointment fields) into the **same** bot output variables above (`Flow.incnumber`, `Flow.IncState`, `Flow.ClaimShort`, `Slot.Name`).

Until then, the table above uses **existing** bot + SNOW behavior in v14.

---

## Related

- [`nydol-digital-data-lineage-miked.md`](nydol-digital-data-lineage-miked.md)  
- Inbound v9: [`architect-exports/msg_dig_nydol_miked_v9-0.json`](architect-exports/msg_dig_nydol_miked_v9-0.json)  
- Bot v14: [`architect-exports/Dig_bot_nydol_v14-0.json`](architect-exports/Dig_bot_nydol_v14-0.json)
