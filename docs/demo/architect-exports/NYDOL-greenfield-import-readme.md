# NYS DOL Messenger — greenfield Architect flows (new names)

**Live org (2026-09-18, end of day):** published **`miked_dol_VAbotflow` 6.0** and **`miked_dol_inbound_message` 3.0**. AVA **`DOL_Front_Door_miked` 12.0** is ProductionReady. Screen pop showed Linus Turing, full address, and **INC0010123**. Repo export filenames (`*_v2-0`, `*_v1-0`) are not these Architect version numbers.

Use these instead of **`Dig_bot_nydol`** / **`msg_dig_nydol_miked`**. Nothing legacy is imported.

| Order | Import file | Flow name in org |
|-------|-------------|------------------|
| **1** | [`miked_dol_VAbotflow_v2-0.i3DigitalBotFlow`](miked_dol_VAbotflow_v2-0.i3DigitalBotFlow) | **`miked_dol_VAbotflow`** — **re-import v2 after regenerate** (includes **Transfer to ACD** on AVA Failure/Timeout; v2 without regenerate sent Failure/Timeout to Exit only) |
| **2** | [`miked_dol_inbound_message_v1-0.i3InboundMessage`](miked_dol_inbound_message_v1-0.i3InboundMessage) | **`miked_dol_inbound_message`** — **rebuild with your bot UUID** (see below) |

### Inbound import (requires published bot flow ID)

The v1 inbound is a **full copy** of working **`msg_dig_nydol_miked` v10** (all **Call Digital Bot Flow** inputs/outputs + screen pop). It must reference the **Architect UUID** of your published **`miked_dol_VAbotflow`**, not `Dig_bot_nydol`.

1. Copy the flow ID (Architect → **Digital bot flows** → **`miked_dol_VAbotflow`** → details / URL).
2. Save one line to [`miked_dol_VAbotflow.flow-id`](miked_dol_VAbotflow.flow-id) (see [`miked_dol_VAbotflow.flow-id.example`](miked_dol_VAbotflow.flow-id.example)).
3. Regenerate and import:

```bash
python3 scripts/build-nydol-greenfield-flows.py --inbound-only
```

Or: `MIKED_DOL_VABOTFLOW_ID=<uuid> python3 scripts/build-nydol-greenfield-flows.py --inbound-only`

Then **Import** `miked_dol_inbound_message_v1-0.i3InboundMessage` → verify **Call Digital Bot Flow** shows **`miked_dol_VAbotflow`** and output mappings (e.g. `Flow.incnumber` → `Flow.incfrombot`, mode **variable** not expression).

Regenerate: `python3 scripts/build-nydol-greenfield-flows.py`

Decoded JSON: `miked_dol_VAbotflow_v1-0.json`, `miked_dol_inbound_message_v1-0.json`

---

## `miked_dol_VAbotflow` (digital bot / virtual agent)

**Import `v2-0`** into **Architect → Digital bot flows** (type **`digitalbot`**). Do **not** import this file as an inbound message flow.

Built from **`Dig_bot_nydol_v17_ava_minimal`** event/user-input settings (no broken builder sequences) plus an EOHHS-style canvas: **Call Agentic Virtual Agent → Exit**; **Failure/Timeout → Transfer to ACD**.

- **Virtual Agent + Agentic Virtual Agent** enabled, type **`digitalbot`**.
- Single state **Default Bot**: **Call Agentic Virtual Agent** only at start (no Communicate welcome). **Exit Bot Flow** on AVA success; **Transfer to ACD** → **`Support_MikeD` / `support_miked`** on AVA **Failure** or **Timeout**.
- Bot variables (for inbound handoff): **`Flow.incnumber`**, **`Flow.incident_state`**, **`Flow.INCtoScript`**, **`Slot.Name`**, **`Slot.email`**, **`Slot.LastName`**, **`Flow.address1`**, **`Flow.city`**, **`Flow.state`**, **`Flow.zip`**. Claim **`Flow.*`** vars are **output-only** (`isInput: false`) — do not mark them as flow inputs or import will fail with “variable input settings do not match.”

**After import:** canvas should read **Call AVA → Hydrate external contact for handoff → Update Data — INCtoScript → Exit Bot Flow**. On **Call Agentic Virtual Agent → Outputs**, map claim + email/name only (address collections come from the hydrate step):


- `claim_lookup.0.number` → **`Flow.incnumber`**
- `claim_lookup.0.incident_state` → **`Flow.incident_state`**
- `handoff.contact_email` → **`Slot.email`**
- `handoff.resident_name` → **`Slot.Name`**
- `handoff.contact_last_name` → **`Slot.LastName`**

Do **not** map `handoff.address_*` on the AVA action—they are scalars and will not populate **`Flow.address1`** collections. Address is filled by **Hydrate external contact for handoff** using **`Slot.email`**.

Leave other OutputData rows empty. Re-select **DOL_Front_Door_miked** **11.0** **ProductionReady** on the AVA action if Architect shows a stale agent binding.

**Prerequisite:** **`DOL_Front_Door_miked` 11.0** **ProductionReady** in AI Studio.

**Handoff email in Messenger tests:** **`mdgen2020@gmail.com`** (Genesys external contact `workEmail`).

Deprecated: `miked_dol_VAbotflow_v1-0` (built from `Dig_bot_nydol` slim export — Draft AVA embed, pre-mapped outputs).

---

## `miked_dol_inbound_message` (inbound message)

Same behavior as your working **`msg_dig_nydol_miked`** handoff, without the old bot name:

- **`Flow.IBVivrselection = 132`** (NYS DOL script landing)
- **Call Digital Bot Flow** → **`miked_dol_VAbotflow`** (latest published)
- External contact search / merge
- **DOL transfer** + **Support Transfer** → **Set Screen Pop** → **`miked_script_2026`**
- Queue **`Support_MikeD`** / **`support_miked`**

---

## After publish

1. **Admin → Message → Deployments → `Miked_Msgr_deploy`**
2. Set **Inbound message flow** to published **`miked_dol_inbound_message`** (not `msg_dig_nydol_miked`).
3. Smoke test in Messenger: AVA conversation → agent transfer → script fields.

---

## Messenger smoke test (demo script)

| Step | Say / type |
|------|------------|
| Missing check | *I haven't received a check* (or similar) |
| ID&V | **Linus Turing**, DOB **June 23, 1988** (mock is case-sensitive on surname — **Turing**, not Turin) |
| Expected after verify | Claim **INC0010009** (ServiceNow) / incident context |
| Transfer | When offered, *yes please* — you should see **one** hold message (*Please hold while I connect you…*) then the session leaves the AVA (agent queue or inbound **DOL transfer**) |

**If transfer loops** (“I'm transferring you now” forever): the AVA did not fire the **Escalation** event (only scripted text). Republish **`DOL_Front_Door_miked`** from this repo (`python3 scripts/publish-dol-from-artifact.py`), point the bot action at the new **TestReady** version, and re-import regenerated **`miked_dol_VAbotflow_v2-0`**.

**Double greeting:** Remove or disable the bot **Communicate** “Welcome… Connecting you…” before **Call Agentic Virtual Agent** (greenfield export has no Communicate; hybrid bots from **`Dig_bot_nydol`** still do).

**If Event Handling / User Input still show errors after import:** you are on an **old v2 export** cloned from EOHHS (7s no-input timeout, empty `sequenceItems` on transfers). Regenerate with `python3 scripts/build-nydol-greenfield-flows.py --bot-only` and re-import.

**Two Transfer to ACD steps (Failure + Timeout)** on the canvas is intentional; point both at **`Support_MikeD`**. Pre-transfer and failed-transfer **Communication** use valid **empty** expressions (`outOfService`); failed-transfer audio has no broken `sequenceItems`. If you still see red errors, regenerate with `python3 scripts/build-nydol-greenfield-flows.py --bot-only` and re-import **`miked_dol_VAbotflow_v2-0`**. **Bot-level Agent Escalation should stay Off** — handoff is AVA Escalation and/or **Exit → inbound DOL transfer**.

**Agent not answering:** Log an agent into **`Support_MikeD`** / **`support_miked`** before testing transfer.

---

## Old flows

You can **archive or unpublish** **`Dig_bot_nydol`** and **`msg_dig_nydol_miked`** in Architect so nothing still points at them.

Patched legacy exports remain in this folder for reference only — see [`NYDOL-i3-import-readme.md`](NYDOL-i3-import-readme.md).
