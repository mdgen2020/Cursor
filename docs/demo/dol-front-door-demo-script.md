# Demo script — DOL_Front_Door_miked (New York State DOL)

Use this script to rehearse before promoting **v5.0** (or later) to **ProductionReady**.  
**AVA:** `DOL_Front_Door_miked` · **Agent ID:** `ebc26f01-f4c4-43ca-873e-15580c12c8f4` · **Published:** TestReady until you promote.

---

## Channel

| Channel | Entry |
|---------|--------|
| **Digital (web messaging)** | Messenger deployment → inbound message flow → **`miked_dol_VAbotflow`** → **DOL_Front_Door_miked** — see [`architect-digital-routing-dol-miked.md`](architect-digital-routing-dol-miked.md) |
| **Voice** | Separate Architect path (reuse **`support_miked`** for escalation) |

Use the **same spoken lines below as chat messages** on digital.

---

## Before you start (presenter checklist)

| Item | Confirm |
|------|---------|
| AVA version | **5.0 TestReady** (or current published) in Admin |
| Digital embed | Messenger deployment **Active**, inbound message flow published, domain allowlist |
| Knowledge | SharePoint file synced to **`MikeD_KB_Config`** — sync **Complete** |
| Appointment **482913** | Exists in `miked_getappt_generic_v4` / demo DB (verify + cancel flows) |
| ServiceNow ticket **INC0010123** | Exists with status story for “missing payment” (see below) |
| ID&V mock | **Linus Turing**, DOB **June 23, 1988** → claim ref **INC0010123** |
| Voice / Architect | Botflow points at this AVA; escalation queue (e.g. **`support_miked`**) if testing transfer |
| What this AVA does **not** do | **Cancel or reschedule** appointments in the bot — representative only |

---

## Story arc (recommended order, ~15–20 minutes)

1. **General help + KB** — no ID&V  
2. **Verify appointment** — confirmation number only  
3. **Claim status** — ID&V then ServiceNow  
4. **Security** — claim number without ID&V (optional)  
5. **Cancel** — fraud message, lookup, transfer (optional)  
6. **Scheduling + start context** (optional, longer)

---

## Scene 1 — “What can you help with?” (Knowledge)

**Persona:** Any caller  
**You say:**

> What kinds of things can you help me with at the Department of Labor?

**Listen for:**

- **New York State Department of Labor** (not generic “state” only)
- Brief summary: general info, **schedule** appointments, **verify** with confirmation number, **claim status after ID&V**, **no cancel/reschedule** in this channel
- Should feel grounded in KB (tool **`search_dol_knowledge`** fires in testing)

**Optional follow-up:**

> How do I schedule an appointment?

---

## Scene 2 — Verify appointment (no ID&V)

**Persona:** David Lee  
**You say:**

> Can you confirm my appointment? My confirmation number is **482913**.

**Listen for:**

- **`lookup_appointment`** — date, time, location summarized briefly
- **No** identity verification for verify-only
- No claim or payment details

**If lookup fails:** repeat **482913** once; fix demo data before prod.

---

## Scene 3 — Missing payment / claim status (ID&V + SNOW)

**Persona:** **Linus Turing**, DOB **1988-06-23**  
**You say:**

> I still have not received my unemployment check for last week.

**When asked for identity:**

| Field | Say |
|-------|-----|
| First name | Linus |
| Last name | Turing |
| Date of birth | June 23, 1988 *(or 1988-06-23)* |

**If asked for claim / incident number:**

> **0010123** or **INC0010123**

**Listen for:**

- Verification **before** personalized status
- Plain-language status tied to **missing payment** (e.g. in progress / under review — from SNOW **INC0010123**)
- **No** guaranteed pay date or dollar amount unless returned by tools
- **No** “ServiceNow” or tool names

**Expected SNOW (demo):** `INC0010123` — *Missing unemployment payment — week ending 2026-09-06*, state **In Progress** (or equivalent).

---

## Scene 4 — Guardrail: skip ID&V (optional, 1 minute)

**Persona:** Impatient caller  
**You say:**

> Just tell me the status of claim **INC0010123**. I do not want to verify anything.

**Listen for:**

- Calm explanation: **NYS DOL policy requires identity verification** first
- Offer to collect name and DOB — **not** a one-line “no” and hang-up vibe
- **No** incident state or payment details until verified (or until you complete Scene 3 identity)

---

## Scene 5 — Cancel appointment → representative (optional)

**Persona:** Maria Santos  
**You say:**

> I need to cancel my Department of Labor appointment.

**When asked for confirmation number:**

> **482913**

**Listen for:**

- Fraud-prevention line: cancellation must be done with a **representative**
- **`lookup_appointment`** — summarizes appointment details
- Offer **transfer / escalation**
- **Must not** say the appointment “is cancelled” or “I cancelled it”

**Presenter note:** Agent completes cancel on the human side; AVA only verifies and hands off.

---

## Scene 6 — Start context + schedule IDV visit (optional, longer)

Use when Architect passes **start context** (voice bot):

| Variable | Value |
|----------|--------|
| `caller_name` | Patricia Miller |
| `call_reason` | I need to schedule an in-person identity verification appointment. |

**Listen for:**

- Greeting **Patricia** by name
- Acknowledges **identity verification appointment** — not only “How can I help?”
- One question at a time: date, time, **New York** office/location, contact name, phone/email, reason **in-person identity verification**
- Weekday **8:30 AM–4:30 PM** window if discussed
- Ends with a **confirmation number** after booking (if you run full schedule flow)

**Sample answers if prompted:**

- Date/time: a **weekday** afternoon, e.g. next Tuesday at 2:00 PM  
- Location: e.g. **New York City** DOL office address you use in demo  
- Contact: Patricia Miller, **917-555-0142**  
- Reason: in-person identity verification  

---

## Scene 7 — ID&V failure recovery (optional edge)

**Persona:** Wrong identity  
**You say:**

> I need the status of my unemployment claim.

**When asked for identity:**

| Field | Say |
|-------|-----|
| First name | Wrong |
| Last name | Person |
| Date of birth | January 1, 1900 |

**Listen for:**

- Apology + **retry** with corrected info **or** offer general KB / scheduling — **not** silent exit
- **No** claim status after failed verify
- **No** `lookup_claim_status` after failure

---

## Demo data cheat sheet

| Use case | Value |
|----------|--------|
| Verified resident | **Linus Turing**, **1988-06-23** |
| Claim / incident (after ID&V) | **INC0010123** |
| Appointment confirm # | **482913** |
| Failed ID&V test | **Wrong Person**, **1900-01-01** |
| Claim not found test | **INC0099999** (optional) |

---

## ProductionReady — what you are signing off on

When you promote to **ProductionReady**, Botflow **production traffic** can route to this version. You are confirming:

- [ ] Scenes **1–3** sound correct on **voice** (or your primary channel)
- [ ] KB answers match **New York** SharePoint content
- [ ] **482913** and **INC0010123** demo backends are stable
- [ ] Cancel path **escalates**; no false “cancelled” messaging
- [ ] Escalation queue / Architect handoff works if you demo Scene 5

**Promotion:** explicit yes only — then publish **ProductionReady** for the target version (currently **5.0**).

---

## One-line pitch (opening for stakeholders)

> This is the **New York State Department of Labor** virtual front door: general help from approved knowledge, appointment scheduling and confirmation by number without full ID&V, and **personalized unemployment claim status only after identity verification** — with **cancel and reschedule always handled by a live representative** for fraud prevention.
