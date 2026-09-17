# Cancel policy — agent handoff (no AVA cancel tool)

**Decision:** The AVA does **not** cancel appointments. Fraudulent cancellation is prevented by requiring a **live agent**.

## Resident-facing language (guideline)

When a resident asks to **cancel** (or **reschedule**) an appointment:

1. Explain briefly: *To prevent fraudulent cancellation, cancellations must be completed with a Department of Labor representative.*
2. If they have a **confirmation number**, call **`lookup_appointment`** and confirm date, time, and location.
3. Summarize for transfer: **confirmation number**, **contact name**, **date**, **time**, **location**, **contact info**, and **reason** (when known).
4. Trigger **Escalation** (transfer to queue, e.g. **`support_miked`** per Architect wiring).
5. Do not claim the appointment is cancelled in the AVA.

## Agent context (technical)

Map successful lookup (and any collected cancel intent) into **end context / OutputData** so Copilot or the agent screen receives:

- Confirmation number (`key` / confirmation_number)
- `contact_name`, `appt_date`, `appt_time`, `appt_addy`, `contact_info`, `appt_reason`
- Short **handoff summary** (e.g. “Resident requested cancellation; appointment verified by confirmation number.”)

Optional later: DOL-specific **`dol_escalation_handoff_miked`** Data Action (pattern: `eohhs_escalation_create_handoff_miked`).

## Not used

- **`dol_cancel_appointment_miked`** (`custom_-_fb440661-2261-4943-a11b-18dda944f2e1`) — created in error; **do not attach** to this AVA. Safe to delete in Admin when convenient.
