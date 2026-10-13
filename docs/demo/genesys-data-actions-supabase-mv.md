# Genesys Data Actions → Supabase RPC (miked_mv_front_door)

Live actions POST to:

`https://mdwdkiwtawqcoxdlrvbd.supabase.co/rest/v1/rpc/<function_name>`

## Local credentials

Use **`.env.motor-vehicle`** (not repo `.env`). See [`.env.motor-vehicle.example`](../../.env.motor-vehicle.example).

## Wire script

```bash
./scripts/wire-genesys-supabase-mv-data-actions.py
./scripts/wire-genesys-supabase-mv-data-actions.py --replace --free-slots
./scripts/wire-genesys-supabase-mv-data-actions.py --skip-verify --only miked_mv_handoff_create
```

Each action uses an **inline `apikey` header** so the shared Web Services integration secret is not switched away from EOHHS.

Registry: [`.ava-lifecycle/miked-mv-front-door/data-actions-registry.md`](../../.ava-lifecycle/miked-mv-front-door/data-actions-registry.md)

## Org quota

Genesys orgs cap custom data actions at **500**. If create fails with `Maximum action count`, **do not delete actions without explicit approval**. Free slots manually in Admin, or ask which demos may be retired. See [genesys-org-retirement-log-mv-wire-incident.md](genesys-org-retirement-log-mv-wire-incident.md) for actions removed in error on 2026-09-29.

## Handoff fields

`miked_mv_handoff_create` accepts **`p_fields_json`** (stringified JSON object), not nested objects — Genesys request bodies must be flat key-value pairs.
