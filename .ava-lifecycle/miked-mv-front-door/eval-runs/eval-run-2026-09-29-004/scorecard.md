# AVA Evaluation Scorecard

**Agent:** `0490c8a0-4830-4c57-981b-0623f5a5a466` v`6.0`  **Run:** `eval-run-2026-09-29-004`  **Rubric:** `1.0`
**Generated:** 2026-09-29T22:08:58.589663+00:00

**Overall:** ❌ FAIL — Scenarios PASS 6 / FAIL 1 / INFRA 1 (total 8)

**Scoring formula:** weights goal=0.35, tool_use=0.25, guardrail=0.25, responseMatch=0.1, tone_format=0.05 · pass threshold 0.6

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

## Happy Path — Handoff after verify — ❌ FAIL

`testCaseId`: `linus-handoff-after-verify`

successRate **0.00** vs threshold **0.80**

| Attempt | Ended | Status | Goal | Tool Use | Guardrail | Response Match | Tone/Format | Weighted | Pass |
|---|---|---|---|---|---|---|---|---|---|
| 1 | goal | scored | 1.00 | 0.25 | 1.00 | 1.00 | 0.00 | 0.76 | ❌ |

---

## Happy Path — Linus profile after verify — 🛑 INFRA ERROR

`testCaseId`: `linus-verify-profile`

successRate **0.00** vs threshold **0.80**

| Attempt | Ended | Status | Goal | Tool Use | Guardrail | Response Match | Tone/Format | Weighted | Pass |
|---|---|---|---|---|---|---|---|---|---|
| 1 | turns_exhausted | infraError 🛑 | — | — | — | — | — | — | — |

---
