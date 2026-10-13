# AVA Analysis Report — miked_mv_front_door

*Generated: 2026-10-13 16:45 UTC*  
*Target: `/Users/michael.debiase/Genesys/AXL/sc12/.ava-lifecycle/miked-mv-front-door/design-artifact.json`*

> ⚠️ **Needs work** — 0 errors · 5 warnings · 5 info · 7 praise

| Field | Value |
|-------|-------|
| Agent ID | `0490c8a0-4830-4c57-981b-0623f5a5a466` |
| Channel | voice |
| Version | 24.0 |
| Scope | full |
| Source | design_artifact |
| Tools / Types / Guardrails / Instructions | 7 / 28 / 4 / 7 |
| Features | Events: Guardrails, UserExit, Escalation · Knowledge ✓ · Start context ✓ · End context ✓ |
| Chapters consulted | quick-guide, 03-executing-multi-step-flows, 05-developing-an-agent-for-voice, 07-keeping-the-agent-on-topic-scope-containment-and-guardrails, 08-escalating-to-a-human-agent, 09a-narrow-tool-types, 09c-structural-flow-gates, 09d-instruction-locality |

## Executive Summary

Author focus confirmed: _publish-definition.json refreshed 2026-10-13 with seven instructions and gc_version 24.0 matches design-artifact.json and get_latest_published_version — the prior publish-snapshot drift finding is cleared. ProductionReady 24.0 has zero schema errors; mv-v1-extended eval-run-2026-10-13-005 is 10/10 including linus-handoff Escalation. Remaining items are structural authoring improvements (User-sourced plate and confirmation-code params, behavioral escalation guardrail, umbrella global instruction) and optional test hardening — not publish blockers. Minor info-only drift remains between design-artifact inputValidation/prose and live org on generate_confirmation_code and renew_registration wording.

**Top priorities:**

1. Hardcode generate_confirmation_code params in backend instead of User inputs
2. Revisit renew plate ToolOutput binding when Sage allows
3. Replace behavioral Escalation guardrail with tool/session gates

**Estimated total effort:** ~90 min

## Errors (must fix before publishing)

_None._

## Warnings (should fix)

### 🟡 [Tools] renew_registration still binds p_plate_number as User-sourced ProfilePlateNumber instead of a ToolOutput chain from get_profile registrations.

**Severity:** warning · **Confidence:** high · **Effort:** medium

**Affected:** `tool:renew_registration`

**Evidence:**

```json
renew_registration.inputs[1]: source User, type ProfilePlateNumber; pre-instructions prose says to copy plate from get_profile.
```

**Fix:** Prefer RegistrationItem.plate_number mapped from ResidentProfileResult via ToolOutput; if Sage rejects that mapping, keep ProfilePlateNumber but add inputValidation on renew_registration once publish preserves it.

**Impact:** UX: degraded

*Source: 09c-structural-flow-gates.md*

---

### 🟡 [Tools] generate_confirmation_code exposes length and characters as required User inputs the agent must supply every booking.

**Severity:** warning · **Confidence:** high · **Effort:** small

**Affected:** `tool:generate_confirmation_code`

**Evidence:**

```json
inputs length (SecurityCodeLength) and characters (SecurityCodeCharacters) source User; pre-instructions say always pass 6 and 0123456789.
```

**Fix:** Hardcode length 6 and charset in the data action contract; remove agent-facing inputs or mark dependencyOnly with fixed External defaults if the platform allows.

*Source: quick-guide*

---

### 🟡 [Guardrails] Custom guardrail blocks Escalation when verify_resident has not succeeded — this steers agent behavior rather than blocking a customer input pattern.

**Severity:** warning · **Confidence:** medium · **Effort:** small

**Affected:** `guardrail[3]`

**Evidence:**

```json
guardrails.custom[3]: Block Escalation to a live representative when verify_resident has not succeeded...
```

**Fix:** Rely on verify_resident pre-instructions plus create_handoff session_token gate; reserve guardrails.custom for jailbreak/PII/social-engineering inputs only.

*Source: 07-keeping-the-agent-on-topic-scope-containment-and-guardrails.md*

---

### 🟡 [Agent] Global instruction delegates all tool routing to a single umbrella line instead of tool-local pre-instructions only.

**Severity:** warning · **Confidence:** high · **Effort:** trivial

**Affected:** `instruction[3]`

**Evidence:**

```json
instructions[3]: Follow each tool's input and output instructions for identity verification, profile lookup...
```

**Fix:** Delete or shorten to channel-neutral tone only; verify_resident, create_handoff, and renew_registration pre-instructions already carry routing.

*Source: 09d-instruction-locality.md / AP:misplaced-instructions*

---

### 🟡 [Platform] No layer-1 assertion that OutputData handoff.genesys_external_contact_id is populated after create_handoff.

**Severity:** warning · **Confidence:** medium · **Effort:** medium

**Evidence:**

```json
OutputData maps handoff.genesys_external_contact_id from HandoffCreateResult; rubric ho-endcontext is LLM-judged only.
```

**Fix:** Add validate_trajectory or end-context fixture check in test/eval when mocks return genesys_external_contact_id.

*Source: quick-guide*

---

## Info (consider improving)

### 🔵 [Platform] Author attempted ToolOutput plate binding from get_profile; Sage rejected mapping — prose + ProfilePlateNumber is the documented workaround.

**Severity:** info · **Type:** opportunity · **Confidence:** high

**Evidence:**

```json
renew_registration remains User-sourced with extensive pre-instructions.
```

**Fix:** Track Sage ticket; revisit ToolOutput when platform accepts nested registration plate mapping.

*Source: quick-guide*

---

### 🔵 [Platform] inputValidation on generate_confirmation_code is present in design-artifact.json but stripped on ProductionReady 24.0 and omitted from _publish-definition.json.

**Severity:** info · **Type:** opportunity · **Confidence:** high

**Evidence:**

```json
design-artifact generate_confirmation_code.inputValidation is Structured length/characters; get_latest_published_version and _publish-definition show inputValidation null.
```

**Fix:** After Sage preserves validation at publish, re-add Structured validation referencing only length and characters.

*Source: 03-executing-multi-step-flows.md*

---

### 🔵 [Schema] Minor prose drift: live 24.0 renew_registration pre-instructions mention ToolOutput binding; design-artifact and _publish-definition use set p_plate_number wording (same User binding).

**Severity:** info · **Confidence:** high

**Evidence:**

```json
get_latest_published_version renew inputInstructions[1] references bind via ToolOutput when available; design-artifact line 872 says set p_plate_number to compact plate from registrations.
```

**Fix:** Optional: align design-artifact wording with live after next publish, or republish from design when you intentionally change copy.

*Source: quick-guide*

---

### 🔵 [Configuration] 781 voice demo may show ANI-linked external contact until Architect hydrates from create_handoff CustEmail.

**Severity:** info · **Type:** opportunity · **Confidence:** high

**Evidence:**

```json
demo-personas.md 781 voice caveat.
```

**Fix:** Demo script: call from Linus-linked mobile or run Hydrate external contact after handoff; document for presenters.

*Source: quick-guide*

---

### 🔵 [Types] InputPlateNumber is declared but renew_registration uses ProfilePlateNumber instead.

**Severity:** info · **Confidence:** high · **Effort:** trivial

**Evidence:**

```json
types[] includes InputPlateNumber; renew_registration input type is ProfilePlateNumber.
```

**Fix:** Remove InputPlateNumber or wire it for resident-spoken plates when profile unknown.

*Source: 09b-type-provenance-and-copying.md*

---

## Praise (working well)

### 🔵 [Platform] _publish-definition.json refreshed 2026-10-13: seven global instructions, gc_version 24.0, aligned with design-artifact.json and ProductionReady 24.0 (prior 21-instruction drift cleared).

**Severity:** info · **Type:** praise · **Confidence:** high

**Evidence:**

```json
_meta.synced_at 2026-10-13T16:37:50Z, instruction_count 7; byte-level match on role, instructions, guardrails, and tool names vs design-artifact.
```

**Fix:** Refresh this snapshot after each ProductionReady publish.

*Source: quick-guide*

---

### 🔵 [Agent] Global instructions reduced to seven channel-neutral lines; tool-specific verify, handoff, and renewal rules live on tools.

**Severity:** info · **Type:** praise · **Confidence:** high

**Evidence:**

```json
instructions.length === 7 on ProductionReady 24.0.
```

**Fix:** Maintain locality on future edits.

*Source: 09d-instruction-locality.md*

---

### 🔵 [Types] ResidentProfileResult includes DriverLicenseResult for REAL ID and license readback after 23.0+.

**Severity:** info · **Type:** praise · **Confidence:** high

**Evidence:**

```json
types ResidentProfileResult.properties driver_license -> DriverLicenseResult; get_profile outputInstructions reference driver_license.
```

**Fix:** Keep profile summaries tied to tool output only.

*Source: quick-guide*

---

### 🔵 [Configuration] Two-turn handoff pattern documented: create_handoff then Escalation-only on agreement; custom Escalation message configured.

**Severity:** info · **Type:** praise · **Confidence:** high

**Evidence:**

```json
instructions[4], create_handoff pre/output instructions, events Escalation message; linus-handoff-after-verify passes on eval-run-2026-10-13-005.
```

**Fix:** Keep scripted yes turn in regression set.

*Source: 08-escalating-to-a-human-agent.md*

---

### 🔵 [Types] Session token uses SessionTokenValue with undisclosed output masking.

**Severity:** info · **Type:** praise · **Confidence:** high

**Evidence:**

```json
SessionTokenValue undisclosed true; verify_resident outputInstructions forbid reading token.
```

**Fix:** Continue omitting secrets from speakable fields.

*Source: 09a-narrow-tool-types.md*

---

### 🔵 [Configuration] OutputData maps handoff contact email, intent, license/plate, appointments, and genesys_external_contact_id for Architect.

**Severity:** info · **Type:** praise · **Confidence:** high

**Evidence:**

```json
OutputData properties include handoff.genesys_external_contact_id mapping HandoffCreateResult.
```

**Fix:** Validate in Architect smoke after eval extends assertions.

*Source: 08-escalating-to-a-human-agent.md*

---

### 🔵 [Platform] mv-v1-extended eval on ProductionReady 24.0 passed 10/10 (eval-run-2026-10-13-005).

**Severity:** info · **Type:** praise · **Confidence:** high

**Evidence:**

```json
scorecard summary total 10 passed 10 failed 0 version 24.0.
```

**Fix:** Re-run extended set after substantive definition changes.

*Source: quick-guide*

---

## Change Suggestions

| # | Priority | Suggestion | Category | Effort | Est. min | Auto |
|---|----------|-----------|----------|--------|----------|------|
| — | 1 | Hardcode confirmation code length/charset in backend and drop User inputs on generate_confirmation_code. | Tools | small | — | — |
| — | 2 | Revisit renew_registration plate binding when Sage accepts ToolOutput from get_profile. | Tools | medium | — | — |
| — | 3 | Move verify-before-escalation policy from custom guardrail into verify_resident/create_handoff pre-instructions only. | Guardrails | small | — | — |
| — | 4 | Add layer-1 or fixture assert for handoff.genesys_external_contact_id after create_handoff. | Platform | medium | — | — |

## Test Coverage

**Status:** ✅ Existing tests found

**Test set:** `mv-v1-extended`

**Suggested tests:** 1

**Gaps:**

- No structural assert on handoff.genesys_external_contact_id
- No automated 781 Architect hydrate external contact smoke
