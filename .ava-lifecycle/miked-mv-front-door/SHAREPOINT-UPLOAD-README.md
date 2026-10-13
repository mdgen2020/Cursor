# Upload MV knowledge to Miked_SharePT

## What to upload

Upload these files from [`knowledge/`](knowledge/) to the SharePoint library for **`Miked_SharePT`** (`93cb697a-ec20-4ad5-8740-80498e098fd9`):

- `faqs.md`
- `policies.md`
- `sops.md`

**Do not upload** `knowledge-sources.md`, `transcripts/`, or repo-only docs.

Optional: upload as three separate files (recommended for chunking) or split `faqs.md` into one file per `---` block if your library prefers single-intent files.

## After upload

1. Run **Incremental** Knowledge Fabric sync for **Miked_SharePT** (not Full — other demos share this library).
2. Confirm sync **Completed** and ingestion **Complete**.
3. AVA **`miked_mv_front_door`** uses Knowledge setting **`miked_mv_KB`** (`048d8a14-e178-4301-beb6-499a71dacb09`).

## Zip helper

From repo root:

```bash
cd .ava-lifecycle/miked-mv-front-door/knowledge && zip -r ../miked_mv_kb_v1-upload.zip faqs.md policies.md sops.md
```
