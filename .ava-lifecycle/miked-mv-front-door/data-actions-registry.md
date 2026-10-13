# MV Data Actions (Genesys Cloud) — `miked_mv_*`

Live **Custom REST** → Supabase RPC (`motor_vehicle` — `https://mdwdkiwtawqcoxdlrvbd.supabase.co`).

Wire script: `scripts/wire-genesys-supabase-mv-data-actions.py`

Integration (shared Web Services): `19717556-e7eb-4db8-884e-b07c6f50d927` — **inline apikey** per action (does not change EOHHS integration secret).

| Name | Action ID | RPC |
|------|-----------|-----|
| `miked_mv_resident_verify` | `custom_-_a245699c-3939-4de7-ac92-847f32c2e500` | `miked_mv_resident_verify` |
| `miked_mv_get_profile` | `custom_-_d0a7dee0-98b5-4c3d-b482-e441701f1d39` | `miked_mv_get_profile` |
| `miked_mv_registration_renew` | `custom_-_49351070-1d64-4b84-90b9-f1ea2a492d06` | `miked_mv_registration_renew` |
| `miked_mv_license_book_appointment` | `custom_-_419def6c-3dc9-44b6-82e1-a2d3fcc507af` | `miked_mv_license_book_appointment` |
| `miked_mv_handoff_create` | `custom_-_65ba764d-f804-40c6-9670-c8a01fc104f7` | `miked_mv_handoff_create` |

After wiring, attach these IDs in `miked_mv_front_door` tool targets and publish a new AVA version.

