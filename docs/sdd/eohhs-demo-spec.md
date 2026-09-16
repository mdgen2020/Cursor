# EOHHS Genesys Demo — Consolidated SDD Spec

**Status:** Decisions locked (presenter Q&A complete).  
**Audience:** Implementation, rehearsal, EOHHS stakeholder demo (10–15 min).  
**Resident persona:** Linus Turing (synthetic).  
**Case seed:** `SNAP-MA-100234` (missing proof of rent; pay stub received).

## North star

Move EOHHS from **managing contacts** to **orchestrating outcomes**. Genesys is the **experience orchestration layer** above Massachusetts systems of record (simulated in Supabase), not a replacement for BEACON/MassHealth processes.

**Target takeaway:** *"We thought Genesys was a contact-center company. They just showed us how we could fundamentally change how residents interact with Health and Human Services."*

## Six pillars (acceptance criteria)

1. **Containment** — End-to-end resolution without an employee when appropriate.
2. **Authenticated SoR-backed personalization** — Real authorization boundary, not UI-only.
3. **Cross-channel orchestration** — Same resident, context, case on voice and digital.
4. **Intelligent escalation** — Hand off at edge of authority with full context.
5. **Copilot** — Employee effort reduced via Genesys-native Copilot on live transfer.
6. **Virtual Supervisor** — Same interaction visible in VS/interaction analytics (enterprise sensor).

Generic FAQ behavior only supports these pillars.

## Locked presenter decisions

| # | Topic | Decision |
|---|--------|----------|
| 1 | Employee experience | Real **Agent Workspace** + live transfer + **real Agent Copilot** (Genesys-native). |
| 2 | Resident channel | **Voice primary**; **same AVA journeys** on voice and digital (channel as adapter in Genesys). |
| 3 | SNAP rent proof | **Voice** for notice/auth/explanation; **digital/messaging only** for upload beat (shared context). |
| 4 | Virtual Supervisor | **Real Genesys VS** (or org-equivalent) on **interaction screen for the interaction just run**. |
| 5 | AVA shape | **One EOHHS AVA** — intelligent front door; route SNAP vs MassHealth inside agent. |
| 6 | ID&V | **Conversational in AVA** → Data Action validates against `residents`; unlocks gated tools/RPCs. |
| 7 | Escalation routing | Single queue: **`support_miked`**; program/context via participant data + Copilot. |
| 8 | Integration topology | **No custom middleware/BFF.** AVA **Data Actions → Supabase RPC** (`apikey` secret, no Bearer). Upload + register via **AVA on digital**; **presenter reset = local script** (env secret). **No Edge Functions** (unless decision reopened). |
| 9 | Live failure | **No fallback UI** / no mock demo mode; reliability + abort/restart only. |
| 10 | Voice entry | **Inbound DID** **+1 781-277-3322** → Architect → EOHHS AVA. |

## Architecture layers (non-negotiable separation)

```
Resident (voice + digital)
    ↓
Genesys (AVA, Architect, Agent Workspace, Copilot, VS)
    ↓  Data Actions: POST /rest/v1/rpc/<name>  (apikey: secret)
Supabase (RLS-locked tables; security definer RPCs only)
    ↓
Simulated MA programs (BEACON-shaped SNAP, MassHealth screening)
```

**Not in scope:** Replacing BEACON, MassHealth Connector, or DTA Connect. **Demo-labeled** resident web may embed Genesys digital; it does not call Supabase with secrets.

## Persistence (existing — extend only)

See project brief §11A. Key integration points today:

- `dta_case_status(p_case_number)`
- `masshealth_screening_result(p_resident_first_name, p_resident_last_name)`

**Header rule:** New-format Supabase keys go in **`apikey` only**, not `Authorization: Bearer`.

### Planned Supabase extensions (RPC-first)

| RPC / artifact | Purpose | Auth | Phase 1 status |
|----------------|---------|------|----------------|
| `resident_verify(...)` | ID&V match Linus; return `session_token` | Open to Data Action | **Migration written** |
| `dta_case_status` | Case read | Gated | **Migration written** (breaking: adds `p_session_token`) |
| `dta_register_document(...)` | Mark rent proof received | Gated | **Migration written** |
| `masshealth_upsert_screening_answer` / `masshealth_complete_screening` | Screening capture | Gated | **Migration written** |
| `escalation_create_handoff(...)` | Handoff payload | Gated | **Migration written** |
| `demo_reset_scenario(...)` | Presenter reset | Reset key | **Migration written** |

Label in SQL comments: **known/public**, **reasonable simulation**, **demo abstraction**.

### Public credibility references

- DTA **BEACON** / **DTA Connect** — [dtaconnect.eohhs.mass.gov](https://dtaconnect.eohhs.mass.gov/), [DTA Connect Online (policy help)](https://eohhs.ehs.state.ma.us/DTA/PolicyOnline/BEACON5/!SSL!/WebHelp/SelfServ/SSO_DTAConOnline.htm)
- SNAP verifications — [Verifications at Application](https://eohhs.ehs.state.ma.us/DTA/PolicyOnline/BEACON5/!SSL!/WebHelp/CrossProg/Verifications/Vers_Basic_Application.htm)
- MassHealth eligibility process — [130 CMR 502.001](https://www.law.cornell.edu/regulations/massachusetts/130-CMR-502-001), [Apply for MassHealth](https://www.mass.gov/how-to/apply-for-masshealth-the-health-safety-net-or-the-childrens-medical-security-plan)

**Naming:** DTA **BEACON** ≠ Beacon Health Strategies — never conflate in copy/code.

## Genesys integration

### AVA (single front door)

- **Voice:** Inbound **+1 781-277-3322** → Architect → AVA.
- **Digital:** Same AVA via messaging/web channel; participant attributes carry `demo_session_token`, `program`, `conversation_id` where supported.
- **Tools:** Narrow Data Actions per RPC; unauthenticated tool set excludes case/screening writes.
- **Knowledge:** Controlled cards for verification types and general program info (no free-form policy invention).
- **Governance (MassHealth):** Language tiers — screening / next step / **official determination by MassHealth agency only**.

### Escalation

- AVA recognizes edge cases (e.g., rent increase, no lease).
- Pre-transfer: call `escalation_create_handoff` + set participant attributes for **Copilot** and agent.
- Transfer to queue **`support_miked`**.

### Copilot

- Live on transferred interaction; handoff fields map to summary/suggested action (configure in org).

### Virtual Supervisor

- After interaction, show **VS on interaction-centric view** for that interaction.
- Implementation: Genesys-native tagging/metadata (Analytics, categories, custom attributes — exact mechanism during build against org capabilities).

## Use case flows

### SNAP / DTA (containment)

1. Voice: notice concern → ID&V → `dta_case_status` → explain gap (rent proof missing).
2. Digital beat: resident submits proof via **Genesys digital** → AVA Data Action `dta_register_document`.
3. Voice or digital: confirm closure — **contained**, no agent.

### SNAP (escalation)

- Trigger: complex rent/lease judgment.
- Escalation packet + `support_miked` + Copilot.

### MassHealth

- Screening conversation → structured answers → **likely eligible** (not approved).
- Offer next step (application); escalation available to `support_miked`.

## Resident web

- Lightweight, **demo/prototype** labeled; loose MA digital government tone.
- Primary roles: embed/link **Genesys digital**, optional static content; **no Supabase secret in browser**.
- Hosting: static (e.g., GitHub Pages) — TBD at deploy step.

## Presenter control (no cloud BFF)

- **Local reset script** (npm/shell): calls `demo_reset_scenario` with secret from env; restores Linus seed.
- **Scenario jumps:** Reset + documented entry (call DID, open digital with starter context); clipboard starter utterances in runbook.
- **Non-linear:** Reset script variants or flags for SNAP contain / SNAP escalate / MassHealth / anonymous path.
- **Final deliverable:** Presenter instruction sheet reflecting actual script and Genesys entry points.

## Cross-channel context

Owned by **Genesys** (one AVA, participant attributes, conversation model). Same `demo_session_token` and case binding when moving voice → digital for upload beat.

## Implementation phases

1. Link Supabase project; migrations for gated RPCs + handoff + reset.
2. Design/build/publish **EOHHS AVA** (`.ava-lifecycle/eohhs/`) — tools, knowledge, escalation, guardrails.
3. Architect: inbound **781-277-3322** → AVA; digital channel parity.
4. Configure **`support_miked`** transfer + Copilot handoff mapping.
5. VS interaction tagging + rehearsal path for moment 5.
6. Minimal resident web + digital embed.
7. Local presenter scripts + **presenter runbook**.

## Definition of success

Stakeholder understands: conversational access, anonymous vs authenticated, Genesys integrates with SoR, containment, intelligent escalation, Copilot value, voice+digital, VS/enterprise intelligence, extensibility beyond SNAP/MassHealth — without feeling like a product pitch or FAQ bot.

## Open items (non-blocking, resolve during build)

- Copilot field mapping and VS interaction attributes available in demo org.
- **ProductionReady** publish for AVA **6.0** when **781-277-3322** must use production routing (TestReady may block inbound).
- Supabase flat notice migration pushed (`20250915211000_*`) if not already on `njjk`.

**Locked (Architect):** Inbound flow **`miked direct to queue`**, DID **781-277-3322**, escalation queue **`support_miked`** — see [`docs/demo/architect-voice-routing-miked.md`](../demo/architect-voice-routing-miked.md).
