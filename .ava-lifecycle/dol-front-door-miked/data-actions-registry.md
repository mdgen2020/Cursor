# DOL Front Door — Data Actions (_miked)

Created in **GenesysSC12** for `DOL_Front_Door_miked` (design in progress).

## AVA tools → backends

| AVA tool | Genesys name | Action ID |
|----------|--------------|-----------|
| `verify_resident_identity` | `dol_resident_verify_miked` | `custom_-_edb03823-1ada-455e-a1d1-57567503789c` |
| `generate_confirmation_code` | `miked_SecurityCodeGenerator` | `custom_-_753dd321-a959-40c9-92f3-ebe5e65b1f77` |
| `create_appointment` | `miked_create_appt_generic` | `custom_-_17ced550-d470-467e-a69c-c3c328c89283` |
| `lookup_appointment` | `miked_getappt_generic_v4` | `custom_-_a5bfa326-a85f-45af-90da-a5030e522c28` |
| `lookup_claim_status` | `ServiceNow Get Ticket by Incident No (Copy)` (**SNOW 212585**) | `custom_-_97d05ed0-dd93-4176-833e-c6856c5f7154` |
| `search_dol_knowledge` | Knowledge setting `MikeD_KB_Config` | `6b16df4b-37fb-4ac5-ba06-a9d2319724d3` |

**No cancel Data Action.** Cancel/reschedule → live agent; see [cancel-and-escalation-policy.md](./cancel-and-escalation-policy.md).

## `dol_resident_verify_miked`

- Category: AVA-Harness-Mock-Echo-DataAction (demo; re-wire to Supabase optional).
- Demo verify: **Linus / Turing / 1988-06-23** → `dol_claim_reference` **INC0010009** (ServiceNow ticket).

## `lookup_external_contact_for_handoff` (AVA tool)

- Data Action: **`External Contact by eMail - MikeD - Full`** · `custom_-_816547b6-db32-410d-8aae-9f6824846583`
- Input: **`workEmail`**. Call **early** after welcome + stated need (account verification). Agent outputs: **`handoff.contact_email`**, **`handoff.resident_name`**, **`handoff.contact_last_name`**, **`handoff.address_line1`**, **`handoff.city`**, **`handoff.state`**, **`handoff.postal_code`** → bot **`Slot.email`**, **`Slot.Name`**, **`Slot.LastName`**, **`Flow.address1`**, **`Flow.city`**, **`Flow.state`**, **`Flow.zip`** → inbound **`Flow.CustEmail`**, **`Flow.FirstName`**, **`Flow.LastName`**, **`Flow.addy1`**, **`Flow.CTY`**, **`Flow.st`**, **`Flow.zipcode`**.
- Demo: external contact **`workEmail`** = **`mdgen2020@gmail.com`** (live demo profile; use in Messenger handoff tests).

## Claim lookup — SNOW 212585

See [servicenow-demo-tickets.md](./servicenow-demo-tickets.md).

## Deprecated (do not use)

| Name | ID | Reason |
|------|-----|--------|
| `dol_cancel_appointment_miked` | `custom_-_fb440661-2261-4943-a11b-18dda944f2e1` | Mock; not wired to appointment table |
