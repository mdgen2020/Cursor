# NY DOL Architect `.i3` imports (patched)

Import these in **Genesys Cloud Architect** (same division as **`Miked_Msgr_deploy`**).

| Order | File | Replaces |
|-------|------|----------|
| **1 (recommended)** | [`Dig_bot_nydol_v17_ava_minimal.i3DigitalBotFlow`](Dig_bot_nydol_v17_ava_minimal.i3DigitalBotFlow) | **`Dig_bot_nydol`** — **minimal VA-only** flow (from your org export, legacy tasks stripped) |
| **1 (legacy patch)** | [`Dig_bot_nydol_v16-0.i3DigitalBotFlow`](Dig_bot_nydol_v16-0.i3DigitalBotFlow) | Patched v15 + AVA on old full bot — **publish often fails** |
| **2** | [`msg_dig_nydol_miked_v10-0.i3InboundMessage`](msg_dig_nydol_miked_v10-0.i3InboundMessage) | **`msg_dig_nydol_miked`** v9 — skip if already on v10 |

Regenerate **v17 minimal** from your latest export:

`python3 scripts/build-dig-bot-ava-minimal-i3.py "/path/to/your/Dig_bot_nydol_export.i3DigitalBotFlow"`


**Format:** single-line **base64** payload (standard Genesys `.i3` export — not YAML).

## What changed

### `Dig_bot_nydol` v17 minimal (use this if publish fails on v16)

Built from **your** virtual-agent export; keeps only **Initial Greeting**:

**Communicate** → **Call Agentic Virtual Agent** (`DOL_Front_Door_miked` **5.0**) → **Exit Bot Flow**

- Removed **legacy dol bot**, FAQ, SNOW tasks, KB follow-up task binding, and **Update Data — INCtoScript** (EOHHS-style AVA → exit).
- AVA outputs: only **`claim_lookup.0.number`** → `Flow.incnumber`, **`claim_lookup.0.incident_state`** → `Flow.incident_state`; all other AVA output rows left **empty** (mode 3) so publish is not blocked by optional appointment mappings.

### `Dig_bot_nydol` v16 (legacy patch)

- **Agentic Virtual Agent enabled** on the digital bot flow.
- **Initial Greeting:** **Communicate** (`Welcome...`) → **Call Agentic Virtual Agent** → **`DOL_Front_Door_miked` 5.0** → **Update Data** (`Flow.INCtoScript = Flow.incnumber`) → **Exit Bot Flow**.
- AVA **outputs** mapped (mode 2): `claim_lookup.0.number` → `Flow.incnumber`, `claim_lookup.0.incident_state` → `Flow.incident_state`, `appointment_lookup.entities.contact_name.0` → `Slot.Name`.
- Former **Starting Task** renamed **`legacy dol bot`** (classic menu / SNOW path kept for reference, not entered from greeting).
- v15 changes retained: **`Flow.incident_state`**, **`Flow.short_des`**, **`Flow.priority`** outputs; **Status Request** still sets **`Flow.INCtoScript`** on legacy SNOW path.

### `msg_dig_nydol_miked` v10

- New variables **`Flow.IncState`**, **`Flow.ClaimShort`**.
- **Call Digital Bot Flow → Dig_bot_nydol → Outputs** maps incident, short description, and **`Flow.INCtoScript → Flow.INCScript`** (assignment **mode 2**, not expression mode).
- **Set Screen Pop** (both transfer tasks) maps script fields:
  - **`customer_selection` ← `Flow.IBVivrselection`**
  - **`claim_number`**, **`IncNum`**, **`TicketNumber` ← `Flow.incfrombot`**
  - **`claim_descript`**, **`banner_text` ← `Flow.ClaimShort`**
  - **`IncState`**, **`acct_status` ← `Flow.IncState`**
  - **`customer_name` ← `Flow.FirstName`**
  - **`agent_summary`** — fixed handoff line (literal)
  - **`banner_color` ← `#00447C`**

## Script pages

- **NYS DOL** landing: driven by **`customer_selection` / `Flow.IBVivrselection`** (e.g. **`132`** set before bot in inbound flow).
- **NYS DOL NBA**: **not** set by these flows — shown via **Copilot** only (no auto NBA code in Architect).

## After import

1. Confirm **`DOL_Front_Door_miked` 5.0** is **Published** (ProductionReady for production Messenger).
2. **Publish** **`Dig_bot_nydol`** then **`msg_dig_nydol_miked`** (if re-importing inbound).
3. Confirm **`Miked_Msgr_deploy`** still points at published **`msg_dig_nydol_miked`**.
4. Messenger smoke test: AVA conversation → escalate or complete → inbound **DOL transfer** → **`miked_script_2026`** fields populate.

Regenerate from repo: `python3 scripts/patch-nydol-i3-exports.py`

Decoded JSON (diff review): `Dig_bot_nydol_v16-0.json`, `msg_dig_nydol_miked_v10-0.json`

Older: `Dig_bot_nydol_v15-0.*` (classic greeting → Starting Task, no AVA).

## Publish failed (“unknown or unspecified error”)

Architect often hides the real API error. Try in order:

1. **Flow settings (digital bot)** — enable **Virtual Agent** and **Agentic Virtual Agent** together (working voice AVA bots have both `true`; v16 import only flipped agentic until you changed it in the UI).
2. **Canvas validation** — open **Initial Greeting** and **Call Agentic Virtual Agent**; fix any red fields before publish.
3. **Re-bind the AVA** — on **Call Agentic Virtual Agent**, choose **`DOL_Front_Door_miked`** again and a **Published** version (e.g. **5.0**). Stale `agentId~version` from import is a common silent publish failure.
4. **AVA outputs** — import often leaves outputs **looking** set ( **`A` / clear icon** ) but not bound; publish still fails. Re-map with the **variable picker** (database icon), not expression mode:
   - `claim_lookup.0.number` → **`Flow.incnumber`**
   - `claim_lookup.0.incident_state` → **`Flow.incident_state`**
   - `appointment_lookup.entities.contact_name.0` → **`Slot.Name`** (note **dots**: `entities.contact_name`, not `entities_contact_name`) — red **“There is no variable specified”** means this row is empty/invalid.
5. **Simplify the path** — temporarily delete **Update Data — INCtoScript** and wire AVA **Success** → **Exit Bot Flow** only; publish; then add Update Data back.
6. **Real error text** — browser **DevTools → Network**, click **Publish**, find the failed `flows` / `publish` request, read the **Response** JSON (`message`, `validationErrors`, `details`).
7. **Legacy bulk** — this flow still contains old tasks, KB, and data actions. If nothing else works, use a **new** minimal digital bot (greeting → AVA → exit) and point inbound at it (your “from scratch” plan).

Regenerate v16 with both VA flags: `python3 scripts/patch-nydol-i3-exports.py` (only if you re-import over the current flow).
