# Requirements — `miked_mv_front_door`

Consolidated decisions (pre-build). Naming: **`miked_mv_*`**, all lowercase.

| Area | Decision |
|------|-----------|
| AVA | **`miked_mv_front_door`**, EN + ES enabled; KB/seed English-first v1 |
| Multi-state | Supabase `state_code`; **MA** seed; later states = seed + new state AVA |
| Supabase | Project **`motor_vehicle`** (`mdwdkiwtawqcoxdlrvbd`) |
| Backends | Live Custom REST → RPC only (no mock data actions) |
| v1 topics | License renewal, registration renewal, REAL ID requirements |
| Knowledge | SharePoint **`Miked_SharePT`** (`93cb697a-…`); setting **`miked_mv_KB`** (`048d8a14-e178-4301-beb6-499a71dacb09`) |
| Verify | Session token; phone last-4 where transcripts use it |
| Escalation | Customer ask, platform failure, out-of-scope after brief KB → **`support_miked`** |
| Script | **`miked_script_2026`** — add pages only; structured handoff fields |
| Architect | Voice: **`miked_mv_VAbotflow`** + inbound **`miked direct to queue` v5-mv** — see [`docs/demo/architect-voice-routing-mv-miked.md`](../../docs/demo/architect-voice-routing-mv-miked.md) |
| Reuse | Queue **`support_miked`**, DID **+1 781-277-3322**, **`miked_security_code_generator`** if needed |
| Personas | 4 — Linus + Diane, Kimberly, Jack (from transcripts) |
| Contact link | Verify → Supabase **`work_email`** → GC external contact search |
| Start context | **`first_name`**, **`state_code`**, **`conversation_id`**, **`interaction_channel`** (Architect passes voice/digital; property name satisfies platform snake_case rules) |

### Start context (Field 7 — design)

| Property | Usage |
|----------|--------|
| `first_name` | When populated, open with a brief personalized greeting using the resident’s first name once; if empty, use a neutral greeting and ask how you can help. Not identity proof—still run **`verify_resident`** before record-specific work. |
| `state_code` | Two-letter state for this session (v1 **`MA`**). Use for verify and transactional tools (e.g. External → `p_state_code` where wired). |
| `conversation_id` | Genesys conversation id for logging/handoff (External → `p_conversation_id` on **`create_handoff`** when present). |
| `interaction_channel` | **`voice`** or **`digital`**—shorter replies on voice; External → `p_channel` on handoff when present. |

Architect should populate from external contact / IVR when known (especially **`first_name`** and **`work_email`** path after verify).

Transcripts: **`transcripts/`** (200 files). Analysis: [`transcript-analysis.md`](transcript-analysis.md).
