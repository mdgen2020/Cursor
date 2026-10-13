# AVA Evaluation Scorecard

**Agent:** `0490c8a0-4830-4c57-981b-0623f5a5a466` v`7.0`  **Run:** `eval-run-2026-09-29-005`  **Rubric:** `1.0`
**Generated:** 2026-09-29T22:10:15.617311+00:00

**Overall:** ❌ FAIL — Scenarios PASS 1 / FAIL 1 / INFRA 0 (total 2)

**Scoring formula:** weights goal=0.35, tool_use=0.25, guardrail=0.25, responseMatch=0.1, tone_format=0.05 · pass threshold 0.6

---

## Happy Path — Handoff after verify — ❌ FAIL

`testCaseId`: `linus-handoff-after-verify`

successRate **0.00** vs threshold **0.80**

| Attempt | Ended | Status | Goal | Tool Use | Guardrail | Response Match | Tone/Format | Weighted | Pass |
|---|---|---|---|---|---|---|---|---|---|
| 1 | terminal | scored | 0.00 | 1.00 | 1.00 | 1.00 | 0.00 | 0.60 | ❌ |

---

## Happy Path — Linus profile after verify — ✅ PASS

`testCaseId`: `linus-verify-profile`

successRate **1.00** vs threshold **0.80**

| Attempt | Ended | Status | Goal | Tool Use | Guardrail | Response Match | Tone/Format | Weighted | Pass |
|---|---|---|---|---|---|---|---|---|---|
| 1 | goal | scored | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | ✅ |

---
