# ServiceNow demo tickets — DOL claim status (SNOW 212585)

AVA tool: **`lookup_claim_status`** → Data Action **`ServiceNow Get Ticket by Incident No (Copy)`**  
**Action ID:** `custom_-_97d05ed0-dd93-4176-833e-c6856c5f7154`  
**Category:** `SNOW 212585`

## Data Action contract

**Input (required)**

| Field | Type | AVA behavior |
|-------|------|----------------|
| `sn_number` | string | Incident / claim number. Residents may say digits only; AVA should prefix **`INC`** when missing (same as legacy DLI). Example: resident says `0010123` → send `INC0010123`. |

**Output (array of objects — use first row)**

| Field | Required | Used by AVA |
|-------|----------|-------------|
| `number` | yes | Reference back to resident |
| `incident_state` | yes | Plain-language **claim status** (map state to friendly wording) |
| `short_description` | no | One-line summary (do not read verbatim) |
| `description` | no | Longer narrative for “what happened / next steps” when asked |
| `priority` | no | Optional (“high priority review”) when helpful |

If the array is **empty** or the call fails → treat as not found; ask resident to verify the claim number.

## Pair with ID&V demo

After **`dol_resident_verify_miked`** succeeds for **Linus Turing** (`1988-06-23`), the demo should return **`dol_claim_reference`: `INC0010009`**.  
Create (or reuse) a ServiceNow incident with **`number` = `INC0010009`** so claim status and verify tell a consistent story.

**Messenger symptom:** verify returns **`INC0010123`** but lookup returns **`[]`** → org verify template is still on **0123**, and ServiceNow has no matching row (or only **0009**). Align both actions to the same incident number.

## Example incidents to create in ServiceNow

### 1 — Missing payment (matches “I haven’t received a check”)

| Field | Suggested value |
|-------|-----------------|
| **number** | `INC0010009` |
| **incident_state** | `In Progress` (or your instance’s equivalent open state) |
| **short_description** | `Missing unemployment payment — week ending 2026-09-06` |
| **description** | `Claimant reports no payment received for the week ending September 6, 2026. Payment batch review in progress. No determination of eligibility changed.` |
| **priority** | `3 - Moderate` |

**What the AVA should say (example):** Your claim is open and being reviewed for a missing payment for the week of September 6; the payment team is still working on it—not a final denial.

### 2 — Identity / in-person verification (optional second ticket)

| Field | Suggested value |
|-------|-----------------|
| **number** | `INC0010456` |
| **incident_state** | `On Hold` |
| **short_description** | `Identity verification required — in-person appointment` |
| **description** | `Claim processing paused until identity verification is completed at a local office. Resident may schedule an identity verification appointment.` |
| **priority** | `4 - Low` |

### 3 — Not found (negative test)

Use any **`number`** that does not exist (e.g. `INC0099999`) to test “claim not found” handling.

## incident_state cheat sheet (wording for voice)

Map your instance’s states; avoid reading raw codes:

| ServiceNow-style state | Resident-friendly phrase |
|------------------------|---------------------------|
| New / In Progress | Your claim is active and being worked. |
| On Hold | Your claim is on hold—usually waiting for information or verification. |
| Resolved / Closed | Your claim shows as completed or closed for this issue. |
| Canceled | This claim request was canceled. |

## Fields you do *not* need on the ticket for this demo

The Data Action schema does not return assignee, work notes, or payment amount. Do not promise dollar amounts unless you extend the integration or add custom fields to the action output mapping.
