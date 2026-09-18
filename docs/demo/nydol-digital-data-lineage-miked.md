# NY DOL digital — data lineage to Agent Script (`miked_script_2026`)

Connect **Messenger → AVA → inbound message flow → agent script pages** using your **existing** Genesys assets.

**Export analyzed:** `msg_dig_nydol_miked` **v9.0** — [`architect-exports/msg_dig_nydol_miked_v9-0.json`](architect-exports/msg_dig_nydol_miked_v9-0.json)  
**Digital bot analyzed:** `Dig_bot_nydol` **v14.0** — [`architect-exports/Dig_bot_nydol_v14-0.json`](architect-exports/Dig_bot_nydol_v14-0.json) (classic bot today; AVA not wired yet).

**Copy/paste Set Screen Pop expressions:** [`nydol-screen-pop-field-mappings.md`](nydol-screen-pop-field-mappings.md)

---

## Asset map (locked names)

| Layer | Name | ID / notes |
|-------|------|------------|
| Messenger **deployment** | **`Miked_Msgr_deploy`** | Points to inbound message flow below |
| Messenger **configuration** | **`MikeD_NYDOL_WebMsg`** | Branding / languages |
| **Inbound message flow** | **`msg_dig_nydol_miked`** | v9.0 |
| **Digital bot flow** | **`Dig_bot_nydol`** | `d9c7a0f5-2a7c-490e-a626-379261b4f8b7` — **Call Agentic Virtual Agent** lives here |
| **AVA** | **`DOL_Front_Door_miked`** | `ebc26f01-f4c4-43ca-873e-15580c12c8f4` — publish **5.0+** (ProductionReady for live Messenger) |
| **Agent script** | **`miked_script_2026`** | `09d11916-8ffd-4feb-9e6b-9568aaf8bfe3` |
| Script pages (Composer) | **NYS DOL** | Landing when page condition matches |
| Script pages (Composer) | **NYS DOL NBA** | Next-best-action page |
| Escalation queue | **`Support_MikeD` / `support_miked`** | `dc15ad2c-7917-413f-9a00-4f52df4d4602` |

---

## End-to-end path

```text
Website: Miked_Msgr_deploy (MikeD_NYDOL_WebMsg)
    → msg_dig_nydol_miked v9
         → [Update Data] Flow.IBVivrselection = "132"   ← page router seed (see below)
         → Initial State
              → Call Digital Bot Flow: Dig_bot_nydol
                   → Call Agentic Virtual Agent: DOL_Front_Door_miked
                   → Map AVA end-context / outputs → bot return parameters
              → Search / merge External Contact (email from Flow.CustEmail)
              → … data actions …
              → Call Task: "DOL transfer"
                   → Set Screen Pop → miked_script_2026  ← agent sees script
                   → Transfer to ACD → Support_MikeD
```

**When the agent gets data:** Screen pop runs inside task **`DOL transfer`** (and duplicate task **`Support Transfer`**), **not** at the first Messenger message. Resident chats with the AVA in **`Dig_bot_nydol`** first; script variables populate when the conversation **transfers to an agent**.

---

## Layer 1 — AVA → `Dig_bot_nydol` (you configure in the digital bot flow)

Map **`DOL_Front_Door_miked`** **OutputData** / session outputs on the **Call Agentic Virtual Agent** action to the bot parameters that **`msg_dig_nydol_miked`** already expects on return.

| AVA output (lifecycle `OutputData` / tool results) | Target bot / inbound variable | Used for |
|----------------------------------------------------|-------------------------------|----------|
| `claim_lookup.0.number` or verify `dol_claim_reference` | **`Flow.incfrombot`** | Incident / claim # on script (`TicketNumber`, `IncNum`, `claim_number`) |
| `claim_lookup.0.incident_state` | **`Flow.IncState`** or script **`acct_status`** | Claim status line on landing/NBA |
| Claim `short_description` / spoken summary | **`claim_descript`**, **`agent_summary`** | NBA + banner text |
| `verify` → `resident_name` or collected first name | **`Flow.FirstName`**, **`customer_name`** | Customer block on script |
| Last name (from conversation or verify) | **`Flow.LastName`** / **`Flow.lastn`** | Customer block |
| Appointment lookup fields | **`ApptDate`**, confirmation → **`Flow.incfrombot`** or dedicated script fields | Verify / cancel handoff |
| Escalation intent | Bot **exit reason** → inbound **Call Task `DOL transfer`** | Agent queue + screen pop |

**Minimum for DOL demo (Linus / missing payment):** after ID&V + `lookup_claim_status`, map **`INC0010123`** and **incident_state** into **`Flow.incfrombot`** and status fields before the bot returns to the inbound flow.

---

## Layer 2 — `Dig_bot_nydol` return → inbound flow variables

From **v9 export**, after **Call Digital Bot Flow**, these **inbound** variables are already wired from bot outputs:

| Inbound variable | Bot output binding (export) |
|------------------|-----------------------------|
| `Flow.incfrombot` | Primary incident/claim string from bot |
| `Flow.FirstName` | `Slot.Name` ← `Flow.FirstName` |
| `Flow.CustEmail` | `Slot.email` |
| `Flow.firstname` / `Flow.lastname` | `Flow.Firstn` / `Flow.lastn` (collections) |
| `Flow.addy1`, `Flow.CTY`, `Flow.st`, `Flow.zipcode` | Address collections |
| `Flow.ticketnumber` / `Flow.incnumber` | Ticket / incident aliases |

**Gap:** If **`Dig_bot_nydol`** does not yet call **`DOL_Front_Door_miked`** or does not map AVA outputs into these parameters, **`Flow.incfrombot`** and names stay empty through transfer — script pages will look blank except hardcoded **`132`**.

---

## Layer 3 — Inbound flow → **`miked_script_2026`** (Set Screen Pop)

Both **`DOL transfer`** and **`Support Transfer`** tasks run **Set Screen Pop** on script **`09d11916-8ffd-4feb-9e6b-9568aaf8bfe3`**.

### Already mapped (v9 export)

| Script variable | Source expression |
|-----------------|-------------------|
| `CustomerFirstName` | `Flow.FirstName` |
| `CustomerLastName` | `ToString(Flow.LastName)` |
| `CustomerAddressLine1` | `ToString(Flow.addy1)` |
| `CustomerCity` | `ToString(Flow.CTY)` |
| `CustomerState` | `ToString(Flow.st)` |
| `CustomerPostalCode` | `ToString(Flow.zipcode)` |
| `CustomerEmail` | `Flow.CustEmail` |
| `TicketNumber` | `Flow.incfrombot` |
| `IncNum` | `Flow.incfrombot` |

### Not mapped today (empty literals) — **fix for DOL + NBA**

| Script variable | Purpose | Recommended source |
|-----------------|---------|-------------------|
| **`customer_selection`** | **Page router** (NYS DOL vs NYS DOL NBA) | **`Flow.IBVivrselection`** |
| `claim_number` | DOL claim display | `Flow.incfrombot` or dedicated `Flow.claimnum` |
| `claim_descript` | Claim narrative | From AVA/SNOW short description (new flow var) |
| `IncState` | Status text | `Flow.IncState` or mapped incident_state |
| `customer_name` | Full name line | `Append(Flow.FirstName, Flow.LastName)` |
| `acct_status` | Status headline | `Flow.IncState` or friendly mapped state |
| `agent_summary` | Handoff summary | Static or AVA-generated summary var |
| `banner_text` / `banner_color` | NBA styling | Rules table / AVA outcome (optional) |
| `Claim_level` | Priority | SNOW priority mapped in bot |

**Critical fix for your two script pages:**

1. In **`msg_dig_nydol_miked`**, on **both** Set Screen Pop actions, set  
   **`customer_selection`** = **`Flow.IBVivrselection`** (today it is an **empty literal** in v9).
2. In **`miked_script_2026`**, confirm page conditions:
   - **NYS DOL** (landing) when **`customer_selection`** equals the value you use for landing (v9 sets **`Flow.IBVivrselection = "132"`** in **Update Data** before the bot — verify **132** matches your Composer condition).
   - **NYS DOL NBA** when **`customer_selection`** equals your NBA code (set dynamically when AVA recommends next best action — e.g. update `Flow.IBVivrselection` in **`Dig_bot_nydol`** before return, or map from bot exit reason).

---

## Page routing model (`132` + NBA)

| Step | Where | What |
|------|--------|------|
| 1 | **`msg_dig_nydol_miked`** — Update Data (before Initial State) | Sets **`Flow.IBVivrselection = "132"`** → default **NYS DOL** landing when script opens |
| 2 | **`Dig_bot_nydol`** (recommended) | On NBA-worthy outcomes, set outbound **`IBVivrselection`** (or inbound variable) to your **NBA page code** before ending bot |
| 3 | Set Screen Pop | **`customer_selection` ← `Flow.IBVivrselection`** |
| 4 | **`miked_script_2026`** | Page visibility: **NYS DOL** vs **NYS DOL NBA** |

**Action for you in Composer:** Open script **`miked_script_2026`**, note the exact **`customer_selection`** values on **NYS DOL** and **NYS DOL NBA** page conditions, and align **`132`** (and any NBA code) in Architect.

---

## Messenger deployment checklist

1. **Admin → Message → Deployments → `Miked_Msgr_deploy`**
   - Inbound message flow: **`msg_dig_nydol_miked`** (published **v9** or current).
   - Configuration: **`MikeD_NYDOL_WebMsg`**.
2. **`Dig_bot_nydol`** published; **Call Agentic Virtual Agent** = **`DOL_Front_Door_miked`** (version matches ProductionReady).
3. Apply **Set Screen Pop** fixes above; republish inbound flow.
4. Test: Messenger chat → claim status scenario → escalate → agent in **`Support_MikeD`** → script shows **NYS DOL** with **Linus** / **INC0010123** populated.

---

## AVA-side optional enhancement (next publish)

If Architect cannot build expressions easily, add **agentOutput** properties on **`OutputData`** in the AVA for stable handoff names, for example:

- `handoff_claim_number`
- `handoff_claim_status`
- `handoff_customer_first_name`
- `handoff_page_selection` (e.g. `132` vs NBA code)

Then map those directly in **`Dig_bot_nydol`** instead of parsing tool arrays in Architect.

---

## Related files

- Inbound export (binary): [`architect-exports/msg_dig_nydol_miked_v9-0.i3InboundMessage`](architect-exports/msg_dig_nydol_miked_v9-0.i3InboundMessage)
- Decoded JSON: [`architect-exports/msg_dig_nydol_miked_v9-0.json`](architect-exports/msg_dig_nydol_miked_v9-0.json)
- AVA definition: `.ava-lifecycle/dol-front-door-miked/design-artifact.json`
- Presenter script: [`dol-front-door-demo-script.md`](dol-front-door-demo-script.md)
- Generic digital notes: [`architect-digital-routing-dol-miked.md`](architect-digital-routing-dol-miked.md)
