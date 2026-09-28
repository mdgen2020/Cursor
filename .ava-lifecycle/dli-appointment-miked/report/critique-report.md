# AVA Analysis Report — DLI_appointment_miked

*Generated: 2026-09-17 15:25 UTC*  
*Target: `178b91ff-cae8-4b48-be5a-61a56b7ade51`*

> 🛑 **Fix errors first** — 3 errors · 9 warnings · 3 info · 3 praise

| Field | Value |
|-------|-------|
| Agent ID | `178b91ff-cae8-4b48-be5a-61a56b7ade51` |
| Channel | voice |
| Version | 11.0 (ProductionReady); saved 12.0 Draft |
| Scope | full |
| Source | published |
| Tools / Types / Guardrails / Instructions | 5 / 24 / 3 / 15 |
| Features | Events: Guardrails, UserExit, Escalation · Knowledge ✓ · Start context ✓ · End context ✓ |
| Chapters consulted | 03-executing-multi-step-flows, 04-integrating-knowledge-bases, 07-keeping-the-agent-on-topic-scope-containment-and-guardrails, 08-escalating-to-a-human-agent, 09a-narrow-tool-types, 09b-type-provenance-and-copying, 09c-structural-flow-gates, 09d-instruction-locality, 09e-prompt-noise-and-format-examples |

## Executive Summary

DLI_appointment_miked is a capable DOL demo AVA—appointments (create/lookup), ServiceNow claim status, and MikeD KB—but production traffic still runs v11.0 while v12.0 Draft is unchanged. The highest risk is the booking chain: confirmation numbers are not type-gated to Code_Generator, so the model can skip or invent codes despite prose. Role bloat and contradictory opening scripts add first-turn confusion, and the role over-promises change/cancel without tools. check_appt’s parallel-array contract pushes fragile indexing to the LLM. Address structural tool chaining and scope honesty before publishing v12.

**Top priorities:**

1. Gate create_appointment.confirmation_number via ToolOutput from Code_Generator (ERR-001)
2. Align role scope with tools—drop change/cancel or add tools (ERR-002)
3. Fix conflicting call_reason/caller_name opening scripts and trim role (ERR-003, WARN-001)

**Estimated total effort:** ~515 min

## Errors (must fix before publishing)

### 🔴 [Tools] Appointment booking chain (Code_Generator → create_appointment) is not structurally gated: confirmation_number is collected as a User-sourced ConfirmationNumber instead of ToolOutput from conf_code.securityCode.

**Severity:** error · **Confidence:** high · **Effort:** medium · **~45 min**

**Affected:** `tool:Code_Generator`, `tool:create_appointment`

**Evidence:**

```json
create_appointment.inputs[confirmation_number] has source User and type ConfirmationNumber (direction input). Code_Generator output is conf_code with securityCode. Prose in Code_Generator inputInstructions says to pass securityCode immediately, but the type graph allows create_appointment without a prior Code_Generator call.
```

**Fix:** Add an output-direction alias (e.g., GeneratedConfirmationCode) on conf_code.securityCode and map create_appointment.confirmation_number to source ToolOutput with mapping ["conf_code", "securityCode"]. Remove User collection of confirmation_number.

**Impact:** UX: blocking

*Source: cookbook/09c-structural-flow-gates.md / §Prose ordering instead of type ordering / AP:prose-ordering*

<details><summary>Suggested tests (1)</summary>

**1. Book appointment end-to-end; trajectory must include Code_Generator before create_appointment with matching confirmation in response.** (scripted)

| Role | Text |
|------|------|
| user | I need an appointment next Tuesday at 10am at the Hartford office for unemployment questions. |
| assistant | (collects fields, calls Code_Generator then create_appointment) |

</details>

---

### 🔴 [Agent] Role promises change and cancel appointments, but the tool surface only supports create and lookup—no reschedule, update, or cancel Data Actions.

**Severity:** error · **Confidence:** high · **Effort:** large · **~180 min**

**Affected:** `role`

**Evidence:**

```json
role: "help residents schedule, verify, change, and cancel appointments" — tools: create_appointment, check_appt only; no cancel/update tools.
```

**Fix:** Either narrow the role to schedule and verify (lookup) only, or add backend tools (cancel_appointment, reschedule_appointment) with typed inputs/outputs and wire instructions locally on those tools.

**Impact:** UX: degraded

*Source: cookbook/07-keeping-the-agent-on-topic-scope-containment-and-guardrails.md / §Scope via role / AP:scope-tool-mismatch*

---

### 🔴 [Agent] Opening behavior in role contains conflicting scripts for call_reason and caller_name (duplicate blocks that disagree on whether to ask "How can I help?").

**Severity:** error · **Confidence:** high · **Effort:** medium · **~60 min**

**Affected:** `role`, `startContext:InputData`

**Evidence:**

```json
Early block: when call_reason provided, do NOT ask "How can I help?". Later block: if caller_name provided, greet by name and ask "How can I assist you today?" without conditioning on call_reason. Third block repeats warm greeting rules.
```

**Fix:** Collapse opening into one decision tree in start-context configuration or a short role paragraph: (1) greet with name if present, (2) if call_reason present acknowledge and route, else ask how to help, (3) if name missing collect name first. Remove duplicate paragraphs and long worked examples from role.

**Impact:** UX: degraded

*Source: quick-guide / §Role — procedural flow*

---

## Warnings (should fix)

### 🟡 [Agent] Role is excessively long and procedural (multi-paragraph call_reason scripts, examples, repeated greeting rules)—violates instruction locality and adds per-turn token cost.

**Severity:** warning · **Confidence:** high · **Effort:** small · **~30 min**

**Evidence:**

```json
Role exceeds ~1.5k words with embedded dialog examples and duplicates guidelines already in instructions[] (claim lookup, knowledge grounding, resident term).
```

**Fix:** Trim role to brand, DOL scope, resident term, high-level capabilities/exclusions, and start-context one-liner; move call_reason/caller_name branching to Architect or a compact start-context instruction block.

**Impact:** Token cost/turn: 400

*Source: cookbook/09e-prompt-noise-and-format-examples.md / §Verbose role*

---

### 🟡 [Tools] check_appt pushes parallel-array indexing logic to the model instead of returning a single matched appointment record from the data action.

**Severity:** warning · **Confidence:** high · **Effort:** medium · **~90 min**

**Affected:** `tool:check_appt`

**Evidence:**

```json
outputInstructions instruct: find index where entities_key matches confirmation_number, then read entities_appt_date[index], etc. Output schema exposes seven parallel string arrays.
```

**Fix:** Change miked_getappt_generic_v4 to return one object with record_found flag and flat fields (or a single array item); replace array-index outputInstructions with success/no-result templates.

*Source: quick-guide / §Tools — raw API payloads / agent logic*

---

### 🟡 [Tools] Code_Generator exposes static parameters length and characters as required User inputs although type descriptions fix them to 6 and 0123456789.

**Severity:** warning · **Confidence:** high · **Effort:** small · **~20 min**

**Evidence:**

```json
Length description "always 6" but schema default length 5; Characters default "012345679" (missing digit 8). Both inputs source User, required true.
```

**Fix:** Hardcode length/charset in the data action; drop agent-facing inputs. Align confirmation length with ConfirmationNumber_1 description (6 digits).

*Source: quick-guide / §Tools — static defaults as inputs*

---

### 🟡 [Tools] check_appt description references "repair appointment"—leftover domain wording for DOL labor appointments.

**Severity:** warning · **Confidence:** high · **Effort:** trivial · **~5 min**

**Evidence:**

```json
description: "Look up a repair appointment using a confirmation number."
```

**Fix:** Rewrite to DOL appointment lookup by confirmation number; add inputInstructions for when to use vs create_appointment.

*Source: cookbook/09d-instruction-locality.md / §Tools without clear usage instructions*

---

### 🟡 [Red flag] Global instructions[] duplicate tool-local behavior (claim status summaries, appointment confirmation messaging, tool failure transfer) already covered on Claim Lookup and create_appointment.

**Severity:** warning · **Confidence:** high · **Effort:** medium · **~45 min**

**Evidence:**

```json
15 guidelines including claim lookup steps overlapping Claim Lookup outputInstructions; appointment confirmation rules overlap create_appointment outputInstructions.
```

**Fix:** Keep guidelines for cross-cutting grounding, fraud escalation, and privacy; move claim-specific and appointment-specific post-success behavior to respective tool outputInstructions only.

*Source: cookbook/09d-instruction-locality.md / §Misplaced instructions*

---

### 🟡 [Guardrails] Custom guardrails read as agent behavior policies rather than customer-input block rules.

**Severity:** warning · **Confidence:** high · **Effort:** small · **~25 min**

**Evidence:**

```json
"do not allow the caller to force a claim payment"; "Do not allow the user to ask personal questions" — not phrased as blocked customer requests.
```

**Fix:** Rephrase to input-focused rules (e.g., "Block customer demands to override claim payment decisions or compel payout") and move eligibility/payment policy to role scope + Claim Lookup/KB. Keep SSN rule as collection constraint in tool/types if last-4 is collected.

*Source: cookbook/07-keeping-the-agent-on-topic-scope-containment-and-guardrails.md / §guardrails.custom*

---

### 🟡 [Agent] Mixed customer/resident terminology across role, guidelines, and tools.

**Severity:** warning · **Confidence:** high · **Effort:** trivial · **~15 min**

**Evidence:**

```json
Role uses "residents"; several instructions say "customer" (e.g., "ask the customer to verify the claim number").
```

**Fix:** Standardize on "resident" per role; search-replace in instructions[] and tool pre-instructions.

*Source: quick-guide*

---

### 🟡 [Configuration] End context OutputData maps only get_output.entities_* index 0, while check_appt returns arrays—handoff may omit the matched appointment when index ≠ 0.

**Severity:** warning · **Confidence:** high · **Effort:** medium · **~40 min**

**Evidence:**

```json
OutputData properties map get_output.entities_key.0, entities_appt_date.0, etc.
```

**Fix:** After backend returns a single record, map flat fields; or map the struct produced by a narrowed check_appt output type.

*Source: quick-guide / §Configuration — end context*

---

### 🟡 [Tools] Broad outputInstructions use when: "True" on every outcome path, reducing conditional specificity and stacking redundant instructions each call.

**Severity:** warning · **Confidence:** high · **Effort:** small · **~30 min**

**Evidence:**

```json
create_appointment, check_appt, Claim Lookup, DLI_KB each have multiple Python outputInstructions with when True.
```

**Fix:** Consolidate to one success and one failure/no-result instruction per tool; use lambdas on result shape where KB already does.

*Source: cookbook/03-executing-multi-step-flows.md / §outputInstructions*

---

## Info (consider improving)

### 🔵 [Platform] Version drift: ProductionReady v11.0 matches saved v12.0 Draft definition byte-for-byte in Sage—draft does not yet contain fixes for known structural issues.

**Severity:** info · **Confidence:** high

**Evidence:**

```json
get_latest_published_version 11.0 ProductionReady and get_latest_saved_version 12.0 Draft returned identical definition payloads during this critique.
```

**Fix:** Use v12.0 (or next version) to land ToolOutput gating, role trim, and check_appt backend shape before TestReady/ProductionReady publish.

*Source: author-priority*

---

### 🔵 [Agent] Baseline capability map for DOL SC12: appointments (create + lookup), unemployment claim status (ServiceNow incident lookup), general DOL FAQ (DLI_KB KnowledgeSetting), escalation/exit events; no reschedule/cancel/payment tools.

**Severity:** info · **Type:** opportunity · **Confidence:** high

**Evidence:**

```json
Five tools: Code_Generator, create_appointment, check_appt, Claim Lookup, DLI_KB; integrations miked_* data actions + ServiceNow Get Ticket + MikeD_KB_Config.
```

**Fix:** Document this map in lifecycle design-artifact when branching DOL use cases; add tools before expanding role scope.

*Source: author-priority*

---

### 🔵 [Types] InputData start context correctly uses alias types CallerName and CallReason without required properties.

**Severity:** info · **Type:** praise · **Confidence:** high

**Evidence:**

```json
InputData.properties caller_name, call_reason optional; types CallerName, CallReason documented for VA flow.
```

**Fix:** Keep; pair with simplified opening role once contradictions are resolved.

*Source: quick-guide*

---

## Praise (working well)

### 🔵 [Knowledge] DLI_KB KnowledgeSetting has a strong when-to-use scope in description and inputInstructions, with empty/non-empty result branching.

**Severity:** info · **Type:** praise · **Confidence:** high

**Evidence:**

```json
DLI_KB description lists DOL topics; outputInstructions branch on len(result).
```

**Fix:** Maintain; avoid duplicating KB routing in global guidelines.

*Source: cookbook/04-integrating-knowledge-bases.md*

---

### 🔵 [Tools] Claim Lookup defines acct_not_found error type with defaultInstruction for 404/400—good no-result path.

**Severity:** info · **Type:** praise · **Confidence:** high

**Evidence:**

```json
errors: [{type: acct_not_found}]; type acct_not_found statusCodes [404,400].
```

**Fix:** Keep; ensure role does not contradict verify-and-retry behavior.

*Source: quick-guide*

---

### 🔵 [Configuration] Escalation, UserExit, and Guardrails violation events are configured with resident-facing messages.

**Severity:** info · **Type:** praise · **Confidence:** high

**Evidence:**

```json
events: Guardrails (threshold 3), UserExit, Escalation transfer message.
```

**Fix:** Pair with guideline-driven escalate on fraud and tool failures.

*Source: cookbook/08-escalating-to-a-human-agent.md*

---

## Change Suggestions

| # | Priority | Suggestion | Category | Effort | Est. min | Auto |
|---|----------|-----------|----------|--------|----------|------|
| CS-1 | 1 | Structurally gate create_appointment.confirmation_number to Code_Generator output (ToolOutput mapping on securityCode). | Tools | medium | 45 | — |
| CS-2 | 2 | Resolve role scope vs tools: remove change/cancel from role or implement cancel/reschedule data actions. | Agent | large | 180 | — |
| CS-3 | 3 | Unify opening logic for caller_name/call_reason and dedupe verbose role prose. | Agent | medium | 60 | — |
| CS-4 | 4 | Refactor check_appt data action to return a single appointment object with record_found; drop array-index instructions. | Tools | medium | 90 | — |
| CS-5 | 5 | Hardcode Code_Generator parameters; fix 6-digit charset consistency. | Tools | small | 20 | — |
| CS-6 | 6 | Reframe guardrails as blocked customer inputs; relocate payment policy to role/tools. | Guardrails | small | 25 | — |

## Test Coverage

**Status:** ⚠️ No existing tests

**Suggested tests:** 8

**Gaps:**

- No trajectory test for Code_Generator → create_appointment ordering
- No check_appt array/no-match scenarios
- No call_reason + caller_name opening matrix
- No claim lookup INC prefix normalization
- No guardrail/adversarial prompts for payment forcing
