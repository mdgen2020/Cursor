# 781 transfer drop — root cause and inbound fix

## Cause

After AVA handoff, **`miked_mv_VAbotflow`** runs **MV handoff transfer** → **Transfer to ACD** → returns to the bot → **Exit Bot Flow**. The inbound flow **`miked direct to queue`** then runs **Disconnect**, which tears down the caller leg even though they were already queued.

The inbound **Call Bot Flow** action is a **single block**: when the bot **returns**, Architect runs the configured **Disconnect**. You cannot branch inside that block. So the bot must **not return** to inbound after a successful queue handoff.

## Bot (fix here)

In task **`MV handoff transfer`**, the last actions must be **Transfer to ACD** → **`Support_MikeD`** with **no End Task** after transfer.

- **Goodbye:** AVA success → **Exit Bot Flow** → bot returns → inbound **Disconnect** (correct).
- **Handoff:** escalation **callTask** → handoff → **Transfer to ACD** → call/task **does not complete** → bot does not hit **Exit Bot Flow (11)** → inbound **Call Bot Flow** stays active → **Disconnect does not run** → caller stays with the queue.

Repo YAML: `miked_mv_VAbotflow_v1.yaml` (handoff task without **End Task** after transfer). Publish **miked_mv_VAbotflow** after this change (Architect UI if Archy validation complains about the task terminator).

## Inbound (task-level terminator)

**Call Bot Flow** is one action on the task. Architect still requires a **terminating action on the task main sequence** (sibling **after** Call Bot Flow), not only inside the bot block.

1. Seed IBV  
2. **Call Bot Flow** → **`miked_mv_VAbotflow`** (do **not** rely on a Disconnect nested only inside the Call Bot box for validation).  
3. On the task canvas, use **“Drag action here”** **below** the Call Bot Flow action → add **Disconnect** (same task, next step down — parallel to Call Bot Flow, not inside it).

Repo YAML matches this: `callBotFlow` then `disconnect` as siblings in `miked_direct_to_queue_v5_mv.yaml`.

No Decision on inbound if the bot handoff task does not End Task after transfer (see above).

## Retest

- Agent logged into **`Support_MikeD`**.
- 781 → Linus Smith → agent handoff → caller should **stay connected** and ring the queue (screen pop IBV **123**).
