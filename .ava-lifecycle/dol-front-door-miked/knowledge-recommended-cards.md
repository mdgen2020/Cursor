# Recommended Knowledge Fabric cards — DOL_Front_Door_miked

**Knowledge setting:** `MikeD_KB_Config` (`6b16df4b-37fb-4ac5-ba06-a9d2319724d3`)  
**AVA tool:** `search_dol_knowledge`

Author **one card per section** in your upload doc (~100–300 words each). Use plain metadata lines (see RMV cards under `.ava-lifecycle/miked-rmv-appointment/knowledge/`). No YAML frontmatter.

Each card must pass: *If the AI only saw this section, could it answer the question completely?*

---

## Priority 1 — required for demo + eval coverage

| # | Suggested filename / section title | User question (use as **Question:** line) | Must include in **Answer:** |
|---|-----------------------------------|-------------------------------------------|-----------------------------|
| 1 | `dol-virtual-front-door-what-we-help-with.md` | What kinds of things can you help me with at the Department of Labor? | General DOL information from approved knowledge; schedule **new** appointments; **verify** an existing appointment with a **confirmation number** (no ID&V); **unemployment claim status** only **after identity verification**; **cannot** cancel or reschedule in this channel—representative required for fraud prevention. |
| 2 | `scheduling-dol-appointment.md` | How do I schedule a Department of Labor appointment? | Weekdays **Monday–Friday**, **8:30 AM–4:30 PM** office time; collect date, time, location/address, contact name, phone/email, reason; resident receives a **confirmation number** to keep; in-person **identity verification** is a valid appointment reason. |
| 3 | `verify-dol-appointment-confirmation-number.md` | How can I confirm my Department of Labor appointment? | Provide the **confirmation number**; agent can confirm date, time, and location; no identity verification required for verify-only; keep the number for changes with a representative. |
| 4 | `unemployment-claim-status-identity-verification.md` | How do I check my unemployment claim status? | Personalized status requires **identity verification** (name and date of birth); claim/incident numbers often start with **INC**; agent explains status in plain language; does not promise payment dates or dollar amounts not returned by systems. |
| 5 | `cancel-or-reschedule-dol-appointment.md` | How do I cancel or reschedule my Department of Labor appointment? | **Fraud prevention:** cancellations and reschedules must be completed with a **Department of Labor representative**; if resident has a confirmation number, details can be looked up before transfer; the virtual assistant does **not** cancel the appointment in the automated channel. |

---

## Priority 2 — strong demo stories (align with scenarios + ID&V mock)

| # | Suggested section | User question | Must include |
|---|-------------------|---------------|--------------|
| 6 | `missing-unemployment-payment.md` | I have not received my unemployment check. What should I do? | Treat as claim-status concern; verify identity first; payment timing varies; do not guarantee amounts or pay dates; representative for disputes. |
| 7 | `in-person-identity-verification-visit.md` | I need to come in to verify my identity for unemployment. | Schedule an appointment with reason **in-person identity verification**; weekday office hours; bring ID documents per local office policy (generic: government-issued photo ID). |
| 8 | `dol-appointment-office-hours.md` | What are Department of Labor office hours for appointments? | Monday–Friday 8:30 AM–4:30 PM (local office time); closed weekends; voice channel keeps answers brief. |

---

## Priority 3 — optional depth

| # | Topic | Question |
|---|--------|----------|
| 9 | General unemployment program (non-personalized) | What is unemployment insurance? |
| 10 | Where to get help | How do I speak to a Department of Labor representative? |

---

## After upload

1. Re-sync Knowledge Fabric for the FileUpload source tied to `MikeD_KB_Config`.
2. In Architect / test, ask: *“What kinds of things can you help me with at the Department of Labor?”* — confirm **Knowledge** tool fires and snippets come from card **#1**.

## Note on the failed KB eval scenario

The last run failed **tool_use**, not empty KB: the AVA answered from **role text** without calling `search_dol_knowledge`. Card **#1** still matters for retrieval quality, but you may also add a design instruction such as: *For questions about what services the front door offers, call search_dol_knowledge before answering.*

Appointment **482913** in `miked_appointment_generic` should unblock verify/cancel lookup scenarios on re-run.
