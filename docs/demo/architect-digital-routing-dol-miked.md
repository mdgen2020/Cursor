# Architect digital routing — NYS DOL demo (`_miked`)

Embed **`DOL_Front_Door_miked`** in **web messaging** (Genesys Messenger) via **Inbound Message Flow → Digital Bot Flow → Call Agentic Virtual Agent**.

**Data lineage to agent script:** [`nydol-digital-data-lineage-miked.md`](nydol-digital-data-lineage-miked.md) (Messenger **`Miked_Msgr_deploy`**, flow **`msg_dig_nydol_miked`**, script **`miked_script_2026`**).

Voice wiring stays in [`architect-voice-routing-miked.md`](architect-voice-routing-miked.md) (EOHHS). This doc is **DOL digital only**.

---

## Targets

| Asset | Value |
|-------|--------|
| **Messenger deployment** | **`Miked_Msgr_deploy`** |
| **Messenger configuration** | **`MikeD_NYDOL_WebMsg`** |
| **Inbound message flow** | **`msg_dig_nydol_miked`** (v9.0 export in repo) |
| **Digital bot flow** | **`Dig_bot_nydol`** (`d9c7a0f5-2a7c-490e-a626-379261b4f8b7`) |
| **Front-door AVA** | **`DOL_Front_Door_miked`** |
| **Agent ID** | `ebc26f01-f4c4-43ca-873e-15580c12c8f4` |
| **AVA version (select in Architect)** | **5.0** (or current **Published** / **ProductionReady** when you go live) |
| **Knowledge** | **`MikeD_KB_Config`** / `search_dol_knowledge` (SharePoint synced) |
| **Agent script (screen pop)** | **`miked_script_2026`** (`09d11916-8ffd-4feb-9e6b-9568aaf8bfe3`) — pages **NYS DOL** / **NYS DOL NBA** |
| **Escalation queue (same demo policy)** | **`support_miked`** (`dc15ad2c-7917-413f-9a00-4f52df4d4602`) |

---

## Architecture (digital path)

```text
Resident website (Messenger snippet)
    → Genesys Web Messaging session
    → Inbound Message Flow: "miked_dol_inbound_message"
    → Call Digital Bot Flow → "miked_dol_VAbotflow"
         → Call Agentic Virtual Agent (DOL_Front_Door_miked 5.0)
              → Success → end session / contained
              → Escalation → Transfer to ACD → support_miked
              → Failure / Timeout → queue or polite end (presenter choice)
```

Same AVA definition as voice rehearsal; **channel is an adapter** — tools, ID&V, KB, and SNOW claim lookup behave the same on messaging.

References:

- [Connect agentic virtual agents to Architect flows](https://help.genesys.cloud/articles/connect-agentic-virtual-agents-to-architect-virtual-agent-flows/)
- [Inbound message flow → digital bot flow](https://help.genesys.cloud/articles/add-an-inbound-message-flow-that-calls-a-digital-bot-flow/)
- [Configure and deploy Genesys Messenger](https://help.genesys.cloud/articles/configure-and-deploy-genesys-messenger/)

---

## Step 1 — AVA readiness

1. Confirm **`DOL_Front_Door_miked`** version **5.0+** is **Published**.
2. For **production** Messenger traffic (not just Cicero), promote the same version to **ProductionReady** (same rule as voice on **781**).
3. Knowledge Fabric sync **Complete** for the SharePoint source behind **`MikeD_KB_Config`**.

Optional AVA tweak for messaging (next publish): add one instruction such as *“On digital messaging, you may use slightly longer replies than voice, but still avoid walls of text.”* — not required to wire Architect.

---

## Step 2 — Create the digital bot flow

1. **Architect → Flows → Digital bot flows** → **Create** → name **`miked_dol_VAbotflow`**.
2. Enable **Virtual Agent** / **Agentic Virtual Agent** on the flow (required for **Call Agentic Virtual Agent**).
3. From **Toolbox → AI Studio**, drag **Call Agentic Virtual Agent**:
   - **Agent:** **`DOL_Front_Door_miked`**
   - **Version:** **5.0** (or **Latest published** if you always promote in lockstep)
4. Wire exits (mirror EOHHS voice bot policy):

   | Exit | Route |
   |------|--------|
   | **Success** (resident done) | **Disconnect** / end digital session |
   | **Escalation** | **Transfer to ACD** → **`support_miked`** |
   | **Failure / Timeout** | **`support_miked`** *or* end with apology (demo: prefer queue) |

5. **Publish** the digital bot flow (note version, e.g. **1.0**).

**Do not** put **Call Agentic Virtual Agent** on the inbound message flow itself — only inside the **digital bot flow** (same pattern as voice: inbound → call child flow → AVA inside child).

---

## Step 3 — Create the inbound message flow

1. **Architect → Flows → Inbound message flows** → **Create** → **`miked_dol_inbound_message`**.
2. **Call Digital Bot Flow** → select published **`miked_dol_VAbotflow`** (use **latest published** or pin version for stable demos).
3. Handle bot return paths if the platform exposes exit reasons (escalation vs success).
4. **Publish** the inbound message flow.

---

## Step 4 — Messenger configuration and deployment

1. **Admin → Message → Messenger configurations** → create e.g. **`miked_dol_messenger_config`**:
   - Languages: **English (US)** default
   - Branding: demo-appropriate (NYS DOL label in header if desired)
   - **Homescreen:** off for simple “open chat → AVA” demo (optional)
2. **Admin → Message → Messenger deployments** → create e.g. **`miked_dol_web_demo`**:
   - Status: **Active**
   - Assign **Messenger configuration** version from step 1
   - **Inbound message flow:** published **`miked_dol_inbound_message`**
   - **Domains:** add your demo site origin(s) (e.g. `https://your-demo-host.example.com`) — restrict in prod; allow-all only for dev
3. Save deployment → copy **snippet** (and **deployment key** if using custom SDK).

Embed on your page (structure only — replace with values from Admin):

```html
<!-- Genesys Messenger snippet from Admin → Deployments → miked_dol_web_demo -->
<script type="text/javascript" charset="utf-8">
  (function (g, e, n, es, ys) {
    g['_genesysJs'] = e;
    g[e] = g[e] || function () { (g[e].q = g[e].q || []).push(arguments); };
    g[e].t = 1 * new Date();
    g[e].c = es;
    ys = document.createElement('script'); ys.async = 1; ys.src = n; ys.charset = 'utf-8';
    document.head.appendChild(ys);
  })(window, 'Genesys', 'https://apps.mypurecloud.com/genesys-bootstrap/genesys.min.js', {
    environment: 'prod',
    deploymentId: '<DEPLOYMENT_ID_FROM_ADMIN>'
  });
</script>
```

Use the **exact** snippet from your org (region/host may differ from `mypurecloud.com`).

---

## Step 5 — Start context (optional, Patricia scheduling scene)

The AVA supports **Start Context** properties on type **`InputData`**:

| Property | Example |
|----------|---------|
| `caller_name` | Patricia Miller |
| `call_reason` | I need to schedule an in-person identity verification appointment. |

On **digital**, set participant / session attributes **before or at session start** if your integration supports it:

- **Messenger JavaScript SDK:** use documented APIs to pass **custom attributes** / **conversation metadata** mapped in Architect to AVA start context (exact mapping depends on your org’s **Call Agentic Virtual Agent** input configuration).
- **Architect test chat:** use flow debug / test panels to inject context when available.

If start context is not wired on v1 digital flow, the AVA still works — Patricia scene becomes a normal scheduling conversation without pre-filled name/reason.

---

## Step 6 — Digital smoke test

Use [`dol-front-door-demo-script.md`](dol-front-door-demo-script.md) lines on **messaging** (type instead of speak):

1. *What kinds of things can you help me with at the Department of Labor?* → KB + NY DOL wording  
2. *Confirmation number **482913*** → verify appointment  
3. Missing check → **Linus Turing**, **1988-06-23** → **INC0010123**  
4. *Cancel my appointment* → **482913** → fraud message + transfer offer (complete transfer in queue **`support_miked`**)

**Admin → Architect → Test chat** (or Live on deployment) before stakeholder demo.

---

## Step 7 — ProductionReady checklist (digital go-live)

Before pointing a public deployment at **ProductionReady**:

- [ ] Digital bot flow published and pinned in inbound message flow  
- [ ] AVA version **ProductionReady** matches Architect selection  
- [ ] Escalation lands in **`support_miked`** with agent available  
- [ ] Domain allowlist matches hosting URL  
- [ ] Demo data: **482913**, **INC0010123**, ID&V mock  

---

## What not to change

- No browser-side Supabase secrets — keep **AVA → Data Actions** only.  
- Do **not** attach **`dol_cancel_appointment_miked`** — cancel stays **representative + escalation**.  
- Do **not** reuse **EOHHS** inbound message flow for DOL unless you intentionally want one entry for both programs (not recommended for clear demo narrative).

---

## Repo artifacts (after you build in Architect)

Export and commit for backup (optional):

- `docs/demo/architect-exports/miked_dol_VAbotflow_v1-0.i3BotFlow`
- `docs/demo/architect-exports/miked_dol_inbound_message_v1-0.i3InboundMessageFlow`

---

## Related

- AVA lifecycle: `.ava-lifecycle/dol-front-door-miked/`
- Presenter script: [`dol-front-door-demo-script.md`](dol-front-door-demo-script.md)
- Voice / EOHHS: [`architect-voice-routing-miked.md`](architect-voice-routing-miked.md)
