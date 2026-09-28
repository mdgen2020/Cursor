# AVA Analysis Report — miked_RMV_appointment

*Generated: 2026-09-14 19:45 UTC*  
*Target: `a9e0db74-1d91-4646-b509-3940f4cd90e3`*

> ⚠️ **Needs work** — 0 errors · 6 warnings · 5 info · 7 praise

| Field | Value |
|-------|-------|
| Agent ID | `a9e0db74-1d91-4646-b509-3940f4cd90e3` |
| Version | 29.0 |
| Scope | full |
| Source | saved_draft |
| Tools / Types / Guardrails / Instructions | 4 / 16 / 2 / 2 |
| Features | Events: Guardrails, UserExit, Escalation · Knowledge ✓ · Start context ✓ |
| Chapters consulted | quick-guide.md, 03-executing-multi-step-flows.md, 04-integrating-knowledge-bases.md, 05-developing-an-agent-for-voice.md, 07-keeping-the-agent-on-topic-scope-containment-and-guardrails.md, 08-escalating-to-a-human-agent.md, 09a-narrow-tool-types.md, 09b-type-provenance-and-copying.md, 09c-structural-flow-gates.md, 09d-instruction-locality.md, 09e-prompt-noise-and-format-examples.md |

## Executive Summary

Version 29.0 (Draft) is a major improvement over the stale v20 ProductionReady baseline: CS-style fixes for errors[] typing, ToolOutput-gated confirmation codes, KB routing, and 404 AppointmentNotFound on verify_appointment are present and match preview-confirmed behavior. No blocking schema or error-severity findings remain. Remaining work is reliability polish (hardcode code-generator params), type provenance for verification codes, role/noise trimming, voice-safe formatting if deployed on voice, and local turn-based evaluation before TestReady publish.

**Top priorities:**

1. Add automated scenarios for booking, verify success, verify 404, KB, transfer, and guardrails
2. Hardcode security code generator parameters in the data action
3. Add userUtteranceSubstring on ConfCode_verify_input
4. Shorten role and relocate greeting/procedural copy
5. Add voice-safe global formatting guidelines if this AVA serves voice

**Estimated total effort:** ~155 min

## Errors (must fix before publishing)

_None._

## Warnings (should fix)

### 🟡 [Agent] Role mixes identity, scope, and procedural greeting scripts that belong in Guidelines or Architect.

**Severity:** warning · **Confidence:** high · **Effort:** small · **~30 min**

**Affected:** `role`

**Evidence:**

```json
role contains step-by-step greetings (Hello first_name, then offer scheduling vs verify), bullet-style confirmation-code rules, and location/hours disambiguation prose spanning ~40 lines.
```

**Fix:** Shorten role to brand, capabilities, exclusions, and customer term; move greeting and first_name handling to a single guidelines entry or start-context-driven opener.

*Source: 09d-instruction-locality.md / §Misplaced instructions / AP:misplaced-in-role*

---

### 🟡 [Tools] Static security-code generator parameters are exposed as user-sourced tool inputs.

**Severity:** warning · **Confidence:** high · **Effort:** medium · **~45 min**

**Affected:** `tool:generate_confirmation_code`

**Evidence:**

```json
generate_confirmation_code requires length and characters with source User; inputInstructions tell the model to always pass 6 and 0123456789.
```

**Fix:** Hardcode length and character set in the miked_SecurityCodeGenerator data action (or a wrapper function) and remove those inputs from the AVA tool surface.

**Impact:** UX: degraded

*Source: quick-guide*

---

### 🟡 [Types] Verification confirmation code input lacks verbatim-capture provenance.

**Severity:** warning · **Confidence:** high · **Effort:** trivial · **~10 min**

**Affected:** `type:ConfCode_verify_input`

**Evidence:**

```json
ConfCode_verify_input is direction input with userUtteranceSubstring false and empty description.
```

**Fix:** Set userUtteranceSubstring true and describe as a 6-digit code spoken by the customer; avoid applying substring to ApptDetails_1 (free-form date/time).

*Source: 09b-type-provenance-and-copying.md / §Generic string types instead of semantic aliases*

---

### 🟡 [Agent] Customer terminology is inconsistent (user vs customer vs guest).

**Severity:** warning · **Confidence:** high · **Effort:** small · **~15 min**

**Evidence:**

```json
Role and guidelines say user; tool copy says customer and guest; start context uses first_name without a defined customer term in role.
```

**Fix:** Pick one term (e.g. customer) in role and align tool pre-instructions and output templates.

*Source: quick-guide*

---

### 🟡 [Configuration] Voice-oriented deployments lack explicit plain-spoken formatting rules while role uses list-like lines.

**Severity:** warning · **Confidence:** high · **Effort:** small · **~20 min**

**Evidence:**

```json
instructions[] only cover one-question-per-turn and tone; role includes hyphen-prefixed confirmation-code bullets; no no-markdown / spoken-number guidance.
```

**Fix:** Add channel-appropriate guidelines (plain prose, no bullets in replies, speak confirmation codes digit-by-digit) or publish a voice-specific version.

*Source: 05-developing-an-agent-for-voice.md / §Dynamic instructions*

---

### 🟡 [Types] Several booking and output types have empty descriptions, reducing capture quality.

**Severity:** warning · **Confidence:** high · **Effort:** small · **~25 min**

**Evidence:**

```json
PhoneNumber_1, ConfCode_verify_input, confcode_output, and BookingResponse have null or empty descriptions.
```

**Fix:** Add concise semantic descriptions and format hints (phone E.164 or spoken template, appointment date/time expectations).

*Source: 09e-prompt-noise-and-format-examples.md / §Dummy values in format templates*

---

## Info (consider improving)

### 🔵 [Agent] Minor typo: double period after Motor Vehicles in role opening.

**Severity:** info · **Confidence:** high · **Effort:** trivial · **~2 min**

**Evidence:**

```json
Massachusetts Registry of Motor Vehicles..
```

**Fix:** Remove the extra period.

*Source: quick-guide*

---

### 🔵 [Tools] Prose ordering for generate_confirmation_code before create_appointment duplicates the type graph gate.

**Severity:** info · **Confidence:** high · **Effort:** trivial · **~5 min**

**Evidence:**

```json
create_appointment ConfCode is ToolOutput SecurityCodeResult with mapping to securityCode; inputInstructions still say First call generate_confirmation_code.
```

**Fix:** Keep one short reminder in create_appointment pre-instructions; remove redundant CRITICAL-style ordering from global prose if added later.

*Source: 09c-structural-flow-gates.md*

---

### 🔵 [Types] Duplicate phone aliases (PhoneNumber for start context vs PhoneNumber_1 for booking).

**Severity:** info · **Confidence:** high · **Effort:** small · **~15 min**

**Evidence:**

```json
InputData.phone_number uses PhoneNumber; create_appointment uses PhoneNumber_1.
```

**Fix:** Reuse one semantic input alias or document why booking phone is independent from start-context phone.

*Source: quick-guide*

---

### 🔵 [Configuration] Start-context alias types FirstName, LastName, PhoneNumber omit direction input on the alias entries.

**Severity:** info · **Confidence:** high · **Effort:** small · **~10 min**

**Evidence:**

```json
types FirstName/LastName/PhoneNumber have direction null while used on InputData properties.
```

**Fix:** Set direction input on start-context alias types per Start Context checklist for consistency with tool inputs.

*Source: quick-guide*

---

### 🔵 [Platform] ProductionReady remains v20.0 while draft v29.0 carries substantive fixes; plan TestReady publish after evaluation.

**Severity:** info · **Type:** opportunity · **Confidence:** high · **Effort:** medium · **~60 min**

**Evidence:**

```json
get_ava latestProductionReadyVersion 20.0 vs analyzed saved version 29.0 Draft.
```

**Fix:** Run scenario evaluation on v29, publish TestReady, then promote after Architect validation.

*Source: quick-guide*

---

## Praise (working well)

### 🔵 [Tools] Booking flow enforces confirmation-code provenance via ToolOutput typing.

**Severity:** info · **Type:** praise · **Confidence:** high

**Evidence:**

```json
create_appointment ConfCode source ToolOutput type SecurityCodeResult mapping [SecurityCodeResult, securityCode].
```

**Fix:** No change required; preserve this pattern when refactoring code generation.

*Source: 03-executing-multi-step-flows.md / §Chained token collection*

---

### 🔵 [Tools] HTTP error types use errors[] with plain-language names and actionable defaultInstruction text.

**Severity:** info · **Type:** praise · **Confidence:** high

**Evidence:**

```json
AppointmentNotFound (404), BookingFailed (400), ServiceUnavailable (500) on verify/create/generate tools.
```

**Fix:** Keep defaultInstruction copy; optionally add tool-level error instruction overrides only if preview tone needs tuning.

*Source: quick-guide*

---

### 🔵 [Tools] 404 / AppointmentNotFound path aligns with preview-confirmed behavior (regression vs v20 critique).

**Severity:** info · **Type:** praise · **Confidence:** high

**Evidence:**

```json
verify_appointment errors include AppointmentNotFound statusCodes [404] with defaultInstruction to re-collect code; author confirmed working in preview for v29.
```

**Fix:** Add automated verify-not-found scenario to lock this behavior.

*Source: 07-keeping-the-agent-on-topic-scope-containment-and-guardrails.md*

---

### 🔵 [Knowledge] search_rmv_knowledge has strong when-to-use / when-not-to-use routing versus booking tools.

**Severity:** info · **Type:** praise · **Confidence:** high

**Evidence:**

```json
Five inputInstructions disambiguate KB vs create_appointment vs verify_appointment and cancel/reschedule transfer.
```

**Fix:** No change required.

*Source: 04-integrating-knowledge-bases.md*

---

### 🔵 [Guardrails] Custom guardrails target blocked customer inputs (jailbreak, professional advice), not tone.

**Severity:** info · **Type:** praise · **Confidence:** high

**Evidence:**

```json
guardrails.custom entries begin with Block attempts / Block requests.
```

**Fix:** No change required.

*Source: 07-keeping-the-agent-on-topic-scope-containment-and-guardrails.md*

---

### 🔵 [Agent] Role states explicit capabilities and exclusions including cancel/reschedule handoff.

**Severity:** info · **Type:** praise · **Confidence:** high

**Evidence:**

```json
Explicit can/cannot lists and confirmation-code anti-hallucination rules in role.
```

**Fix:** Trim verbosity without removing exclusions.

*Source: quick-guide*

---

### 🔵 [Schema] Tool discriminators and error contract match current VersionDefinition conventions.

**Severity:** info · **Type:** praise · **Confidence:** high

**Evidence:**

```json
type DataAction and KnowledgeSetting; errors[] present; no errorTypes, kind, or supportedLanguages fields.
```

**Fix:** No change required.

*Source: cookbook.md*

---

## Change Suggestions

| # | Priority | Suggestion | Category | Effort | Est. min | Auto |
|---|----------|-----------|----------|--------|----------|------|
| CS-EVAL-1 | 1 | Author turn-based scenarios under .ava-lifecycle/miked-rmv-appointment covering book success, verify success, verify 404/AppointmentNotFound, BookingFailed, KB FAQ, cancel/reschedule transfer, and guardrail jailbreak. | Platform | medium | 90 | — |
| CS-TOOL-1 | 2 | Remove length/characters from generate_confirmation_code AVA inputs; hardcode defaults in miked_SecurityCodeGenerator data action. | Tools | medium | 45 | — |
| CS-TYPE-1 | 3 | Enable userUtteranceSubstring and a clear description on ConfCode_verify_input for 6-digit verification capture. | Types | trivial | 10 | — |
| CS-ROLE-1 | 4 | Condense role to scope and identity; move greeting/first_name and confirmation-code bullets into guidelines or tool-local instructions. | Agent | small | 30 | — |
| CS-TYPE-2 | 5 | Fill empty type descriptions for PhoneNumber_1, GuestName_1, ApptDetails_1, confcode_output, and BookingResponse; unify customer terminology. | Types | small | 25 | — |

## Test Coverage

**Status:** ⚠️ No existing tests

**Suggested tests:** 9

**Gaps:**

- No scenarios directory or test set under .ava-lifecycle/miked-rmv-appointment
- End-to-end book flow with generate_confirmation_code → create_appointment
- verify_appointment success path with read-back of GuestName/ApptDetails/PhoneNumber
- verify_appointment AppointmentNotFound / 404 recovery (preview-validated but not scripted)
- BookingFailed (400) retry offer
- ServiceUnavailable escalation on appointment tools
- search_rmv_knowledge FAQ vs booking disambiguation
- Cancel/reschedule transfer without calling booking tools
- Custom guardrail jailbreak block
