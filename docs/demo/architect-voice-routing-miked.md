# Architect voice routing — EOHHS demo (`_miked`)

Locked presenter wiring for **inbound voice** and **agent escalation**.

## Targets

| Asset | Value |
|-------|--------|
| **Inbound DID** | **+1 781-277-3322** |
| **Inbound call flow (reuse)** | **`miked direct to queue`** |
| **Front-door AVA** | **EOHHS MA Experience Orchestrator** |
| **Agent ID** | `96fe2bc6-7f11-41d5-8e6d-8a3ed20291b6` |
| **AVA version** | **11.0** — **ProductionReady** (live Supabase tools + Miked_SharePT knowledge) |
| **Voice bot flow** | **`miked_eohhs_VAbotflow`** (published **2.0**) — Call AVA; Failure/Timeout → queue above |
| **Inbound flow version** | **`miked direct to queue` v2.0** — greeting → Call Bot Flow → bot **1.0** |
| **Escalation queue** | **`support_miked`** (`dc15ad2c-7917-413f-9a00-4f52df4d4602`; Architect may show **`Support_MikeD`** — names are case-insensitive) |

## Call path (what you are building)

Genesys does **not** allow **Call Agentic Virtual Agent** inside an **Inbound Call Flow**. Use **two flows**:

```text
781-277-3322
    → Inbound Call Flow: "miked direct to queue"
    → Call Bot Flow → **`miked_eohhs_VAbotflow` 1.0**
         → Call Agentic Virtual Agent (**EOHHS MA Experience Orchestrator 11.0**)
              → Exit Bot Flow → Inbound **Disconnect** (current export)
```

**Exports (repo backup):** [`architect-exports/miked direct to queue_v2-0.i3InboundFlow`](architect-exports/miked%20direct%20to%20queue_v2-0.i3InboundFlow), [`architect-exports/miked_eohhs_VAbotflow_v1-0.i3BotFlow`](architect-exports/miked_eohhs_VAbotflow_v1-0.i3BotFlow). Supersedes v1.1 inbound export that incorrectly used Call AVA on the inbound flow.

```text
Escalation gap (wire before stakeholder demo):
              └─ Escalation / agent request → Transfer to ACD → **`support_miked`**
                 (not in v2.0 inbound export today — bot returns then Disconnect only)
```

Reference: [Call Agentic Virtual Agent action](https://help.genesys.cloud/articles/call-agentic-virtual-agent-action/) — action is only valid in a **bot flow** (Virtual Agent enabled); adding it changes the flow to **Agentic Virtual Agent**.

Reuse the **existing Transfer to Queue** block that targets **`support_miked`** on the **inbound** flow, on the **Call Bot Flow** exit path when the bot returns **Escalation** (or map AVA escalation exit inside the bot flow, then end the bot and transfer from inbound).

## 1. Create the bot flow (Call AVA lives here)

1. **Architect → Flows → Bot flows** → **`miked_eohhs_VAbotflow`** (voice, **Virtual Agent** / Agentic enabled).
2. **Call Agentic Virtual Agent** → **EOHHS MA Experience Orchestrator** **11.0** (ProductionReady / Published).
3. **v2.0 export:** **Failure** / **Timeout** → **Transfer to ACD** → escalation queue; **Success** → **Exit Bot Flow**. Still wire **Escalation** or Success **exit-reason** switch if “talk to an agent” exits Success only.
4. **Publish** bot flow **2.0**; inbound **Call Bot Flow** should target published **2.0**.

## 2. Reuse `miked direct to queue` (inbound only)

1. **Admin → Architect → Flows** → open **`miked direct to queue`** (Inbound Call Flow).
2. **Do not** add Call Agentic Virtual Agent here (platform error: action not available in Inbound Call Flow).
3. **Play Audio** (demo welcome TTS) → **Call Bot Flow** → **`miked_eohhs_VAbotflow` 1.0** (`flowLatestVersion: true` in export).
4. After bot return, export currently goes to **Disconnect** only — add **Transfer to ACD → `support_miked`** when exit reason is escalation (or handle transfer inside the bot flow).
5. **Publish** inbound **v2.0** and assign **781** to that published version.

## 3. Escalation exit → `support_miked`

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

- Queue **`support_miked`** / **`Support_MikeD`** — ID **`dc15ad2c-7917-413f-9a00-4f52df4d4602`** (same object; Genesys queue names are not case-sensitive).
- At least one **user** or **routing profile** can receive transfers for rehearsal.
- **Agent Workspace** is the answer surface for Copilot demo.

Optional: queue **wrap-up** / **in-queue** message — keep short; AVA already played escalation messaging.

## 5. AVA version vs inbound traffic

| Mode | When |
|------|------|
| **TestReady** | Cicero / internal rehearsal |
| **ProductionReady** (**11.0**) | **781** and Architect **Call Agentic Virtual Agent** — agent entity must show **Published** |

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
- [`phase2-ava-status.md`](phase2-ava-status.md) — AVA **11.0** + live actions
- [`genesys-naming-miked.md`](genesys-naming-miked.md) — `_miked` asset names
