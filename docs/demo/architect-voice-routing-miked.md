# Architect voice routing — EOHHS demo (`_miked`)

Locked presenter wiring for **inbound voice** and **agent escalation**.

## Targets

| Asset | Value |
|-------|--------|
| **Inbound DID** | **+1 781-277-3322** |
| **Inbound call flow (reuse)** | **`miked direct to queue`** |
| **Front-door AVA** | **EOHHS MA Experience Orchestrator** |
| **Agent ID** | `96fe2bc6-7f11-41d5-8e6d-8a3ed20291b6` |
| **AVA version (rehearsal)** | **6.0** — **TestReady** (live Supabase tools) |
| **Escalation queue** | **`support_miked`** |

## Call path (what you are building)

```text
781-277-3322
    → Inbound Call Flow: "miked direct to queue"
    → Call AVA (EOHHS MA Experience Orchestrator v6.0)
         ├─ Contained (SNAP upload on digital, MassHealth screening, FAQ) → AVA ends call / user exit
         └─ Escalation (AVA Escalation event + create_escalation_handoff) → Transfer to ACD → queue support_miked
              → Agent Workspace + Copilot (Phase 3)
```

Reuse the **existing Transfer to Queue** (or equivalent ACD) block that already targets **`support_miked`** — wire the **Call AVA** action’s **On Escalation** (and optionally **On Error**) exit to that block instead of sending every caller straight to the queue.

## 1. Reuse `miked direct to queue`

1. **Admin → Architect → Flows** → open **`miked direct to queue`**.
2. **Duplicate** or note the current published version (rollback safety).
3. Identify the node that **transfers to `support_miked`** (keep it; do not rename the queue).
4. **Before** that direct-to-queue entry (or replace the first transfer after **Start**):
   - Add **Call Agentic Virtual Agent** / **Call AVA** (product label varies by release).
   - **Virtual agent:** `EOHHS MA Experience Orchestrator`
   - **Version:** `6.0` (TestReady for rehearsal; switch to **ProductionReady** before a live-audience DID — see below).

## 2. Escalation exit → `support_miked`

On the **Call AVA** action, set outbound paths:

| Exit | Route to |
|------|-----------|
| **Escalation** (or “Transfer to agent”) | Existing **Transfer to ACD** → queue **`support_miked`** |
| **Error / timeout** (demo policy) | Same queue **`support_miked`** *or* polite disconnect (presenter choice; spec says no fallback UI — prefer queue if AVA fails mid-demo) |
| **Success / disconnect** | **Disconnect** or **End flow** (contained calls) |

The AVA already calls **`create_escalation_handoff`** before escalation language; Copilot context comes from Supabase + conversation metadata (Phase 3 mapping).

## 3. Assign the DID

1. **Admin → Telephony → Phone Numbers** → **+1 781-277-3322**.
2. **Inbound route:** **`miked direct to queue`** (published version).
3. Confirm trunk/DID is **voice** and in the same **environment** as the AVA (prod org).

## 4. Queue `support_miked`

Confirm (no rename required):

- Queue name **`support_miked`** exists.
- At least one **user** or **routing profile** can receive transfers for rehearsal.
- **Agent Workspace** is the answer surface for Copilot demo.

Optional: queue **wrap-up** / **in-queue** message — keep short; AVA already played escalation messaging.

## 5. AVA version vs inbound traffic

| Mode | When |
|------|------|
| **TestReady** (current **6.0**) | Cicero, internal test calls, rehearsal if org allows TestReady on inbound |
| **ProductionReady** | Live **781** in front of stakeholders — publish **6.0** (or later) with `testOnly: false` |

If inbound calls do not reach the AVA, the org often requires **ProductionReady** on the version selected in Architect.

## 6. Smoke test checklist

After publish:

1. `./scripts/demo-reset.sh all`
2. Call **781-277-3322**
3. Ask for SNAP case help → ID&V **Linus Turing**, DOB **1988-06-23** → case / missing rent proof (live Supabase)
4. Ask for an agent → should land in **`support_miked`** with prior AVA context
5. Presenter reset again before next scenario

## 7. What not to change

- Do **not** add a middleware BFF; voice stays **Architect → AVA → Data Actions → Supabase**.
- Do **not** route contained SNAP/MassHealth calls to **`support_miked`** unless the resident escalates or AVA errors per your Architect exits.

## Related docs

- [`eohhs-demo-spec.md`](../sdd/eohhs-demo-spec.md) — locked decisions Q7, Q10
- [`phase2-ava-status.md`](phase2-ava-status.md) — AVA **6.0** + live actions
- [`genesys-naming-miked.md`](genesys-naming-miked.md) — `_miked` asset names
