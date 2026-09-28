# Upload RMV knowledge to Miked_SharePT

## What to upload

Upload **all `.md` files** in the `knowledge/` folder to the SharePoint library connected to your Genesys Knowledge Fabric source **Miked_SharePT**.

**Do not upload** `knowledge-sources.md` — that file is for local authoring lineage only.

## Recommended upload layout

Upload each card as its own file (9 files total). One intent per file gives Knowledge Fabric the cleanest retrieval chunks.

## After upload

1. Wait for Knowledge Fabric to sync the SharePoint source (timing depends on your org configuration).
2. In Genesys Cloud Admin, create a **Knowledge Configuration** bound to **Miked_SharePT** if one does not exist yet:
   - Generation mode: Answer generation (or Search with context, per your standard)
   - Generation language: `en-US`
3. Tell me when sync is complete and share the **Knowledge Configuration name** (or confirm you want it named `Miked_SharePT_Setting`).

I will then perform **Option A**:
- Attach a `KnowledgeSetting` tool to `miked_RMV_appointment`
- Tighten guardrails/role so FAQ scope matches scheduling + verification
- Publish a new AVA version

## Source disclaimer

Cards were authored from public Mass.gov / myRMV information as of 2026-09-09. Review and update before production use.
