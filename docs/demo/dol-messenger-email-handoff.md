# DOL Messenger — email verification → external contact → script pop

**Live org (2026-09-18):** **`miked_dol_VAbotflow` published 6.0**, **`miked_dol_inbound_message` published 3.0**, AVA **12.0** ProductionReady. Agent script showed name, address, and **INC0010123**.

## Option 2 (implemented) — early email + full profile to agent

### AVA **12.0**

1. Tool **`lookup_external_contact_for_handoff`** → Data Action **`External Contact by eMail - MikeD - Full`** (`workEmail`).
2. **Early verification:** After welcome and the resident states their need, ask for the **email on their NY DOL account** and call the lookup tool **once**. Do **not** ask for email again at the end or right before transfer.
3. **Agent outputs** (populated when lookup succeeds; passed on escalation):
   - **`handoff.contact_email`** ← `workEmail`
   - **`handoff.resident_name`** ← `firstName`
   - **`handoff.contact_last_name`** ← `lastName`
   - **`handoff.address_line1`** ← `address.street1`
   - **`handoff.city`** ← `address.city`
   - **`handoff.state`** ← `address.state`
   - **`handoff.postal_code`** ← `address.postalCode`

### Digital bot **`miked_dol_VAbotflow` v2**

**Call AVA → Outputs** (repo export `miked_dol_VAbotflow_v2-0.*`):

| AVA agent output | Bot variable |
|------------------|--------------|
| `handoff.contact_email` | `Slot.email` |
| `handoff.resident_name` | `Slot.Name` |
| `handoff.contact_last_name` | `Slot.LastName` |
| `handoff.address_line1` | `Flow.address1` |
| `handoff.city` | `Flow.city` |
| `handoff.state` | `Flow.state` |
| `handoff.postal_code` | `Flow.zip` |
| `claim_lookup.0.number` | `Flow.incnumber` |
| `claim_lookup.0.incident_state` | `Flow.incident_state` |

Point **Call Agentic Virtual Agent** at **`DOL_Front_Door_miked` 11.0** (ProductionReady). After AVA exits successfully, the bot runs **Hydrate external contact for handoff** (same Data Action as the AVA tool, input **`Slot.email`**) so **`Flow.address1` / city / state / zip** collection variables populate for inbound—AVA agent outputs alone cannot fill those collection vars.

Re-import bot export after pulling latest from `docs/demo/architect-exports/`.

### Inbound **`miked_dol_inbound_message` v2**

Map bot outputs into inbound **`Flow.*`** before external contact search and screen pop:

| Bot output | Inbound variable |
|------------|------------------|
| `Slot.email` | `Flow.CustEmail` |
| `Slot.Name` | `Flow.FirstName` |
| `Slot.LastName` | `Flow.LastName` |
| `Flow.address1` | `Flow.addy1` |
| `Flow.city` | `Flow.CTY` |
| `Flow.state` | `Flow.st` |
| `Flow.zip` | `Flow.zipcode` |
| `Flow.incnumber` | `Flow.incfrombot` |
| `Flow.incident_state` | `Flow.IncState` (if used) |

Then: **Search External Contacts** → **Get External Contact by Email** → **Set External Contact** → transfer → **Set Screen Pop** on **`miked_script_2026`**.

## Demo data

| Item | Value |
|------|--------|
| Test email | **`mdgen2020@gmail.com`** (live; external contact `workEmail`) |
| External contact | Genesys profile must include **full address** (street, city, state, zip) or script address fields stay blank |
| Claim | **INC0010123** in SNOW (aligned with verify mock) |

## Messenger test script

1. State your need → AVA asks for **account email** → **`mdgen2020@gmail.com`** → lookup runs.  
2. Claim ID&V (Linus Turing, **1988-06-23**) → claim status.  
3. Escalate — agent script should show **first/last name, full address, email**, and **INC** ticket.

## Related

- [nydol-screen-pop-field-mappings.md](./nydol-screen-pop-field-mappings.md)
- `.ava-lifecycle/dol-front-door-miked/data-actions-registry.md`
