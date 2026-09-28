# AVA Analysis Report — miked_RMV_appointment

*Generated: 2026-09-09 16:36 UTC*  
*Target: `a9e0db74-1d91-4646-b509-3940f4cd90e3`*

> 🛑 **Fix errors first** — 6 errors · 8 warnings · 3 info · 3 praise

| Field | Value |
|-------|-------|
| Agent ID | `a9e0db74-1d91-4646-b509-3940f4cd90e3` |
| Channel | voice |
| Version | 20.0 |
| Scope | full |
| Source | published |
| Tools / Types / Guardrails / Instructions | 2 / 10 / 2 / 9 |
| Features | Events: Guardrails, UserExit, Escalation · Start context ✓ |
| Chapters consulted | quick-guide, 02-collecting-multiple-inputs, 04-integrating-knowledge-bases, 07-scope-containment, 08-escalating, 09a-narrow-tool-types, 09b-type-provenance, 09c-structural-flow-gates, 09d-instruction-locality, 09e-prompt-noise |

## Executive Summary

miked_RMV_appointment has a clear RMV scheduling scope and sensible voice collection rules, but three structural issues undermine reliability: the agent is told to invent confirmation codes (a backend responsibility), global instructions reference tool names that do not exist, and a guardrail promises knowledge answers without a connected KB. Fixing code generation in the data action, aligning tool names, and either adding knowledge or narrowing scope will materially improve booking integrity. Secondary wins come from moving tool-specific rules out of global instructions/guardrails, adding verbatim capture on ConfCode, and declaring proper error types instead of 'Not Found' sentinel strings.

**Top priorities:**

1. Stop agent-generated confirmation codes — return ConfCode from the create data action instead
2. Align tool names (create_appointment / verify_appointment) with every instruction reference
3. Add a knowledge source for RMV business FAQs or remove that capability from guardrails

**Estimated total effort:** ~200 min

## Errors (must fix before publishing)

### 🔴 [Tools] The create tool instructs the agent to generate the confirmation code and accepts ConfCode as a User-sourced input.

**Severity:** error · **Confidence:** high · **Effort:** medium · **~45 min**

**Affected:** `tool:Appoint_create`

**Evidence:**

```json
Appoint_create description/inputInstructions: 'Generate a random 6-character confirmation code (e.g., MIKE01)'; inputs include ConfCode with source User.
```

**Fix:** Remove ConfCode from agent inputs. Have the data action generate and return the code in BookingResponse (add ConfCode to output). Map the returned code into the spoken response via outputInstructions.

**Impact:** Security: medium · UX: blocking

*Source: quick-guide.md / §Tools*

---

### 🔴 [Agent] Global instructions reference tool names that do not exist in the definition.

**Severity:** error · **Confidence:** high · **Effort:** small · **~15 min**

**Affected:** `instruction`, `tool:Appoint_create`, `tool:appointment_verify`

**Evidence:**

```json
instructions[] says 'use the create_appointment tool' and 'use the verify_appointment tool', but tools are named Appoint_create and appointment_verify.
```

**Fix:** Align names: either rename tools to create_appointment / verify_appointment or update every instruction to match the published tool names exactly.

**Impact:** UX: blocking

*Source: 09d-instruction-locality.md*

---

### 🔴 [Guardrails] Custom guardrails define normal agent behavior and scope rules instead of blocking prohibited customer inputs.

**Severity:** error · **Confidence:** high · **Effort:** small · **~20 min**

**Affected:** `guardrail[0]`, `guardrail[1]`

**Evidence:**

```json
guardrails.custom[0]: 'Never invent or guess a confirmationId...' (output policy). guardrails.custom[1]: 'Only assist with scheduling or verifying appointments...' (scope steering).
```

**Fix:** Move scope and confirmation-ID policy to role/guidelines and tool outputInstructions. Reserve guardrails for input attacks (jailbreak, prompt reveal) and domain blocks (e.g., 'Block requests for legal advice').

**Impact:** UX: degraded

*Source: quick-guide.md / §Guardrails*

---

### 🔴 [Red flag] Role contains a procedural greeting script and turn-by-turn dialog flow.

**Severity:** error · **Confidence:** high · **Effort:** small · **~15 min**

**Affected:** `role`

**Evidence:**

```json
role: 'Greet the user with Hello first_name if it is populated' and 'Greet the user with "I can help with scheduling..."'
```

**Fix:** Keep role to identity, capabilities, exclusions, and customer term. Move greeting/opening to a single guideline or handle in Architect.

**Impact:** UX: degraded

*Source: quick-guide.md / §Agent / Red flags*

---

### 🔴 [Knowledge] Guardrail promises business knowledge answers but no KnowledgeBase or KnowledgeSetting tool is connected.

**Severity:** error · **Confidence:** high · **Effort:** medium · **~60 min**

**Affected:** `guardrail[1]`

**Evidence:**

```json
guardrails.custom[1] references 'business knowledge source'; tools[] contains only two DataAction tools.
```

**Fix:** Add a KnowledgeSetting or KnowledgeBase tool for RMV FAQs (hours, locations, required documents) or remove the knowledge promise from guardrails and role.

**Impact:** UX: blocking

*Source: 04-integrating-knowledge-bases.md*

---

### 🔴 [Types] Output struct confcode_output uses bare string primitives for semantic fields instead of aliased types.

**Severity:** error · **Confidence:** high · **Effort:** small · **~20 min**

**Affected:** `type:confcode_output`

**Evidence:**

```json
confcode_output properties GuestName, ApptDetails, PhoneNumber all type string with no semantic aliases.
```

**Fix:** Declare output aliases (e.g., GuestNameOut, ApptDetailsOut, PhoneNumberOut) and reference them in the struct per tool checklist.

*Source: quick-guide.md / §Tools checklist*

---

## Warnings (should fix)

### 🟡 [Agent] Tool-specific routing and post-success behavior live in global instructions instead of on the tools.

**Severity:** warning · **Confidence:** high · **Effort:** medium · **~40 min**

**Affected:** `instruction`

**Evidence:**

```json
instructions include verify/create flows, ConfCode retry, cancel/reschedule transfer, and exit-after-success — none tied to tool outputInstructions/inputValidation.
```

**Fix:** Move verify flow to appointment_verify inputInstructions; move post-booking speech to Appoint_create outputInstructions; move escalation-on-failure to appointment_verify outputInstructions.

*Source: 09d-instruction-locality.md*

---

### 🟡 [Types] Confirmation code input type lacks verbatim-capture provenance.

**Severity:** warning · **Confidence:** high · **Effort:** trivial · **~5 min**

**Affected:** `type:ConfCode_verify_input`

**Evidence:**

```json
ConfCode_verify_input has direction input but userUtteranceSubstring is false and no format description.
```

**Fix:** Set userUtteranceSubstring: true on ConfCode_verify_input and add description: '6-character code spoken verbatim by the caller.'

*Source: 09b-type-provenance-and-copying.md*

---

### 🟡 [Tools] Overlapping outputInstructions all use when True, causing redundant always-on guidance and a typo.

**Severity:** warning · **Confidence:** high · **Effort:** small · **~20 min**

**Affected:** `tool:Appoint_create`, `tool:appointment_verify`

**Evidence:**

```json
Appoint_create has four outputInstructions with when True including 'do not continue unless the status i Success'; appointment_verify has five similar entries.
```

**Fix:** Consolidate to one or two outputInstructions per tool with clear success vs failure branches in the then text.

*Source: 04-integrating-knowledge-bases.md / §outputInstructions*

---

### 🟡 [Tools] Tool names are inconsistent and not action-oriented.

**Severity:** warning · **Confidence:** high · **Effort:** small · **~15 min**

**Evidence:**

```json
Appoint_create vs appointment_verify — mixed casing and prefix patterns; descriptions are minimal ('use this tool to verify an appointment').
```

**Fix:** Rename to create_appointment and verify_appointment with one-sentence descriptions of when to call and what is returned.

*Source: quick-guide.md / §Tools*

---

### 🟡 [Configuration] Start context first_name is referenced in role but not consumed by any tool via External source.

**Severity:** warning · **Confidence:** high · **Effort:** small · **~25 min**

**Affected:** `startContext:InputData`

**Evidence:**

```json
InputData defines first_name, last_name, phone_number; role greets with first_name; no tool input uses source External.
```

**Fix:** Either wire phone_number via External with fallbackToUser on Appoint_create, or remove unused start-context fields and greeting logic.

*Source: quick-guide.md / §Start Context checklist*

---

### 🟡 [Tools] Neither data action declares business error types; verify relies on 'Not Found' string values in output fields.

**Severity:** warning · **Confidence:** high · **Effort:** medium · **~45 min**

**Evidence:**

```json
errors: null on both tools; verify outputInstructions branch on GuestName = 'Not Found'.
```

**Fix:** Add errors[] with AppointmentNotFound on verify and BookingFailed on create; return record_found boolean from backend instead of sentinel strings.

*Source: quick-guide.md / §Tools*

---

### 🟡 [Agent] Dummy example confirmation code in tool text may be copied into live bookings.

**Severity:** warning · **Confidence:** high · **Effort:** trivial · **~5 min**

**Evidence:**

```json
Appoint_create description and inputInstructions include example 'MIKE01'.
```

**Fix:** Replace with format template: '6 uppercase alphanumeric characters' without a concrete example.

*Source: 09e-prompt-noise-and-format-examples.md*

---

### 🟡 [Tools] Create tool description duplicates collection steps already in inputInstructions.

**Severity:** warning · **Confidence:** high · **Effort:** trivial · **~10 min**

**Evidence:**

```json
Appoint_create description repeats the same collect-name/time/phone/generate-code text as inputInstructions[0].
```

**Fix:** Keep collection steps only in inputInstructions; shorten description to business purpose and return shape.

*Source: 09d-instruction-locality.md*

---

## Info (consider improving)

### 🔵 [Configuration] Comfort statement is enabled for tool wait turns.

**Severity:** info · **Type:** praise · **Confidence:** high

**Evidence:**

```json
settings.comfortStatement.enabled: true
```

**Fix:** Keep enabled; ensure wording stays short per Configuration guidance.

*Source: quick-guide.md*

---

### 🔵 [Agent] Role includes helpful business-location disambiguation for first-person questions.

**Severity:** info · **Type:** praise · **Confidence:** high

**Evidence:**

```json
role explains interpreting 'you' as the RMV office, not the virtual agent.
```

**Fix:** Retain this pattern; it reduces common voice misinterpretation.

*Source: quick-guide.md*

---

### 🔵 [Configuration] Escalation, UserExit, and Guardrails events are configured with custom messages.

**Severity:** info · **Type:** opportunity · **Confidence:** high

**Evidence:**

```json
events[] includes all three types with violationThreshold 3.
```

**Fix:** No change required; consider pairing escalation instructions with built-in escalate_to_human_agent per chapter 08.

*Source: 08-escalating-to-a-human-agent.md*

---

## Praise (working well)

### 🟡 [Agent] Role states explicit capabilities and exclusions including rescheduling.

**Severity:** warning · **Type:** praise · **Confidence:** high

**Evidence:**

```json
role lists appointment scheduling, verification, and excludes rescheduling and off-topic requests.
```

**Fix:** Keep; strengthen with positive grounding for knowledge once KB is attached.

*Source: quick-guide.md*

---

### 🟡 [Agent] One-question-per-turn guideline supports voice-friendly collection.

**Severity:** warning · **Type:** praise · **Confidence:** high

**Evidence:**

```json
instructions: 'Ask for one piece of information per turn.'
```

**Fix:** Keep; aligns with voice best practices.

*Source: quick-guide.md*

---

### 🟡 [Tools] Create tool output is compact (Status only).

**Severity:** warning · **Type:** praise · **Confidence:** high

**Evidence:**

```json
BookingResponse contains only Status string.
```

**Fix:** Extend output with ConfCode once backend generates it.

*Source: 09a-narrow-tool-types.md*

---

## Change Suggestions

| # | Priority | Suggestion | Category | Effort | Est. min | Auto |
|---|----------|-----------|----------|--------|----------|------|
| CS-001 | 1 | Move confirmation code generation to the data action: remove ConfCode user input, return ConfCode in BookingResponse, and speak it from tool outputInstructions. | Tools | medium | 45 | — |
| CS-002 | 2 | Fix tool name drift: rename tools to create_appointment / verify_appointment and update all instructions to match. | Agent | small | 15 | — |
| CS-003 | 3 | Add a KnowledgeSetting tool for RMV business FAQs or remove knowledge promises from guardrails. | Knowledge | medium | 60 | — |
| CS-004 | 4 | Relocate guardrail behavior rules to role/guidelines and tool outputInstructions; keep guardrails for input blocking only. | Guardrails | small | 20 | — |
| CS-005 | 5 | Strip procedural greeting script from role; move tool flows from global instructions to per-tool instructions. | Agent | medium | 55 | — |

## Test Coverage

**Status:** ⚠️ No existing tests

**Suggested tests:** 5

**Gaps:**

- No local evaluation scenarios under .ava-lifecycle
- No test for successful booking with backend-generated ConfCode
- No test for invalid/not-found confirmation code
- No test for cancel/reschedule escalation path
- No test for business FAQ routing once knowledge is added
