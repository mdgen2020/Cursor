# Incident — data actions deleted during MV wire (2026-09-29)

**Cause:** `wire-genesys-supabase-mv-data-actions.py --free-slots` deleted four actions to work around the org **500 data-action cap**. Those actions were **active demos**, not obsolete. That was wrong without explicit author approval.

## Deleted actions (restore in Admin or recreate)

| Name | Former ID | Category (last known) |
|------|-----------|------------------------|
| `miked_get_demo_rule_V2` | `custom_-_3db4c3ed-afaf-4eba-8ea8-488f1c328d28` | Eddie_Genesys Cloud Data Actions |
| `miked_get_demo_account_v2` | `custom_-_d1e16ef4-dfa9-43e5-bc85-0db2cf9af6bd` | Eddie_Genesys Cloud Data Actions |
| `miked_ClearLicenseRow` | `custom_-_53c000d0-59ff-49ac-bf5c-2c215dbd0985` | PureCloud Data Actions |
| `miked_ClearRegistrationRow` | `custom_-_f66efa26-5194-445c-a2cf-98cd28436c32` | PureCloud Data Actions |

**This repo has no JSON exports** for these four. Recovery options:

1. **Genesys Admin → Integrations → Actions** — recreate with same names; update any AVA/flow that referenced the old IDs.
2. **Search org** for stale `custom_-_…` references: Architect flows, AVA tool targets, bot flows.
3. **Audit trail** (if enabled in org) for deleted integration action definitions.

## MV actions created (unchanged — keep)

See [`.ava-lifecycle/miked-mv-front-door/data-actions-registry.md`](../../.ava-lifecycle/miked-mv-front-door/data-actions-registry.md).

## Script change

`--free-slots` no longer deletes anything by default. To delete specific IDs in future, pass a confirmed list via code/env only after author sign-off — do not assume “demo cleanup” names.

## Finding broken demos

- AVA **Preview / Test** → tool call fails (404 action or wrong ID).
- **Architect** → Data Action steps red / missing action.
- **Admin → Integrations → Actions** → search each name above; if missing, that demo path is broken until recreated.

If you export recreated actions to `.ava-lifecycle/…/data_actions/*.json`, commit them so this does not happen again.
