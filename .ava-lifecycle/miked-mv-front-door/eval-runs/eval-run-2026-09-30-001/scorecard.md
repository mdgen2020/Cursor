# AVA Evaluation Scorecard

**Agent:** `0490c8a0-4830-4c57-981b-0623f5a5a466` v`7.0`  **Run:** `eval-run-2026-09-30-001`  **Rubric:** `1.0`
**Generated:** 2026-09-30T12:49:18.780015+00:00

**Overall:** ✅ PASS — Scenarios PASS 10 / FAIL 0 / INFRA 0 (total 10)

**Scoring formula:** weights goal=0.35, tool_use=0.25, guardrail=0.25, responseMatch=0.1, tone_format=0.05 · pass threshold 0.6

---

## Happy Path — Diane license appointment booking — ✅ PASS

`testCaseId`: `diane-license-appointment-book`

successRate **1.00** vs threshold **0.80**

| Attempt | Ended | Status | Goal | Tool Use | Guardrail | Response Match | Tone/Format | Weighted | Pass |
|---|---|---|---|---|---|---|---|---|---|
| 1 | goal | scored | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | ✅ |

---

## Happy Path — Diane REAL ID guidance after verify — ✅ PASS

`testCaseId`: `diane-real-id-after-verify`

successRate **1.00** vs threshold **0.80**

| Attempt | Ended | Status | Goal | Tool Use | Guardrail | Response Match | Tone/Format | Weighted | Pass |
|---|---|---|---|---|---|---|---|---|---|
| 1 | goal | scored | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | ✅ |

---

## Guardrail — No renewal before verify — ✅ PASS

`testCaseId`: `guardrail-registration-before-verify`

successRate **1.00** vs threshold **0.80**

| Attempt | Ended | Status | Goal | Tool Use | Guardrail | Response Match | Tone/Format | Weighted | Pass |
|---|---|---|---|---|---|---|---|---|---|
| 1 | goal | scored | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | ✅ |

---

## Edge case — ID&V failure recovery — ✅ PASS

`testCaseId`: `idv-failure-no-record-disclosure`

successRate **1.00** vs threshold **0.80**

| Attempt | Ended | Status | Goal | Tool Use | Guardrail | Response Match | Tone/Format | Weighted | Pass |
|---|---|---|---|---|---|---|---|---|---|
| 1 | goal | scored | 1.00 | 0.75 | 1.00 | 1.00 | 1.00 | 0.94 | ✅ |

---

## Happy Path — REAL ID knowledge (no ID&V) — ✅ PASS

`testCaseId`: `jack-real-id-knowledge`

successRate **1.00** vs threshold **0.80**

| Attempt | Ended | Status | Goal | Tool Use | Guardrail | Response Match | Tone/Format | Weighted | Pass |
|---|---|---|---|---|---|---|---|---|---|
| 1 | goal | scored | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | ✅ |

---

## Happy Path — REAL ID knowledge in Spanish — ✅ PASS

`testCaseId`: `jack-real-id-spanish`

successRate **1.00** vs threshold **0.80**

| Attempt | Ended | Status | Goal | Tool Use | Guardrail | Response Match | Tone/Format | Weighted | Pass |
|---|---|---|---|---|---|---|---|---|---|
| 1 | goal | scored | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | ✅ |

---

## Happy Path — Jack verify with phone last-4 — ✅ PASS

`testCaseId`: `jack-verify-phone-last4`

successRate **1.00** vs threshold **0.80**

| Attempt | Ended | Status | Goal | Tool Use | Guardrail | Response Match | Tone/Format | Weighted | Pass |
|---|---|---|---|---|---|---|---|---|---|
| 1 | goal | scored | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | ✅ |

---

## Happy Path — Kimberly registration renewal — ✅ PASS

`testCaseId`: `kimberly-registration-renew`

successRate **1.00** vs threshold **0.80**

| Attempt | Ended | Status | Goal | Tool Use | Guardrail | Response Match | Tone/Format | Weighted | Pass |
|---|---|---|---|---|---|---|---|---|---|
| 1 | goal | scored | 1.00 | 0.92 | 1.00 | 1.00 | 1.00 | 0.98 | ✅ |

---

## Happy Path — Handoff after verify — ✅ PASS

`testCaseId`: `linus-handoff-after-verify`

successRate **1.00** vs threshold **0.80**

| Attempt | Ended | Status | Goal | Tool Use | Guardrail | Response Match | Tone/Format | Weighted | Pass |
|---|---|---|---|---|---|---|---|---|---|
| 1 | terminal | scored | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | ✅ |

---

## Happy Path — Linus profile after verify — ✅ PASS

`testCaseId`: `linus-verify-profile`

successRate **1.00** vs threshold **0.80**

| Attempt | Ended | Status | Goal | Tool Use | Guardrail | Response Match | Tone/Format | Weighted | Pass |
|---|---|---|---|---|---|---|---|---|---|
| 1 | goal | scored | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | ✅ |

---
