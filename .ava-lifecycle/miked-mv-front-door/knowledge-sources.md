# Knowledge source lineage — `miked_mv_front_door`

| Field | Value |
|--------|--------|
| **Lifecycle slug** | `miked-mv-front-door` |
| **Knowledge source (reuse only)** | **`Miked_SharePT`** — SharePoint — `93cb697a-ec20-4ad5-8740-80498e098fd9` |
| **New sources** | **Not allowed** — org at source capacity |
| **Authoring mode** | Transform (200 fictitious RMV transcripts + v1 topic focus) |
| **v1 retrieval topics** | License renewal (Standard/REAL ID), registration renewal, REAL ID requirements |
| **Generation language (v1)** | `en-US` (Spanish AVA enabled; KB English-first per requirements) |

## Knowledge setting (AVA tool target)

| Setting name | ID | Source |
|--------------|-----|--------|
| **`miked_mv_KB`** | `048d8a14-e178-4301-beb6-499a71dacb09` | **`Miked_SharePT`** `93cb697a-ec20-4ad5-8740-80498e098fd9` |

Created 2026-09-29 — Answer generation, stateful search, `en-US`, no source filter.  
**`miked_mv_front_door`** knowledge tool → **`miked_mv_KB`** (not `MikeD_KB_Config`).

SharePoint library is shared; other settings on the same source may still retrieve MV cards after sync unless filtered in Admin.

## Upload path

1. Author cards under [`.ava-lifecycle/miked-mv-front-door/knowledge/`](knowledge/) (prefix files `mv-` to distinguish from DOL-only content in the same library if desired).
2. Copy into the **Miked_SharePT** SharePoint document library (same process as [miked-rmv-appointment `SHAREPOINT-UPLOAD-README.md`](../miked-rmv-appointment/SHAREPOINT-UPLOAD-README.md)).
3. **Incremental** Knowledge Fabric sync in Admin (do **not** Full replace — other demos share this source).
4. Confirm sync **Completed** / ingestion **Complete** before AVA TestReady.

## Cards authored (v1 — upload set)

| File | Intents |
|------|---------|
| [`knowledge/faqs.md`](knowledge/faqs.md) | License renewal, REAL ID definition/docs, registration renewal, inspection vs registration, mail delay, confirmation numbers, appointments |
| [`knowledge/policies.md`](knowledge/policies.md) | Identity verification; insurance for registration renewal |
| [`knowledge/sops.md`](knowledge/sops.md) | Self-service registration renew; book REAL ID / license appointment |

Do **not** upload this file or `transcripts/`.

## Lineage

Transcript corpus: [`transcripts/`](transcripts/) (headers = intent; citizen/agent dialogue).  
Content transformed for customer-safe FAQ/SOP/policy cards; aligned with v1 topics and public RMV patterns. Fictitious transcript disclaimer applies to training demos—not official RMV policy documents.
