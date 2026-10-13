#!/Users/michael.debiase/.local/share/uv/tools/ava-mcp/bin/python3
"""Patch miked_mv_get_profile Hedwig success schema to include renewal_fee_dollars (no action delete)."""
from __future__ import annotations

import asyncio
import importlib.util
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AVA_MCP_SITE = Path.home() / ".local/share/uv/tools/ava-mcp/lib/python3.12/site-packages"
if AVA_MCP_SITE.is_dir():
    sys.path.insert(0, str(AVA_MCP_SITE))

from api_utils import request as http  # noqa: E402
from auth_utils import public_headers  # noqa: E402
from config import Config  # noqa: E402
from tools.data_actions import draft  # noqa: E402
from tools.data_actions.integration import action_url  # noqa: E402

_wire = ROOT / "scripts/wire-genesys-supabase-mv-data-actions.py"
_spec = importlib.util.spec_from_file_location("wire_mv", _wire)
wire_mv = importlib.util.module_from_spec(_spec)
assert _spec and _spec.loader
_spec.loader.exec_module(wire_mv)

ACTION_ID = "custom_-_d0a7dee0-98b5-4c3d-b482-e441701f1d39"
SCHEMAS_PATH = ROOT / ".ava-lifecycle/miked-mv-front-door/supabase-action-schemas.json"


def draft_success_schema_url(action_id: str) -> str:
    return (
        f"https://api.mypurecloud.com/api/v2/integrations/actions/{action_id}"
        "/draft/schemas/successschema.json"
    )


async def main() -> None:
    wire_mv.load_genesys_from_mcp_json()
    os.environ.setdefault("AVA_HABITAT", "prod")
    config = Config()
    hdrs = await public_headers(config)

    expected_out = json.loads(SCHEMAS_PATH.read_text())["miked_mv_get_profile"]["outputSchema"]
    reg_items = expected_out["properties"]["registrations"]["items"]["properties"]

    import copy

    action = await http("GET", action_url(config, ACTION_ID), "HedwigPublic", headers=hdrs)
    contract = copy.deepcopy(action.get("contract") or {})
    contract.setdefault("output", {})["successSchema"] = expected_out
    await http(
        "PATCH",
        action_url(config, ACTION_ID),
        "HedwigPublic",
        headers=hdrs,
        json={"contract": contract, "version": action.get("version")},
    )

    supabase_host, apikey = wire_mv.load_motor_vehicle_env()
    verify = wire_mv.supabase_rpc_json(
        supabase_host,
        apikey,
        "miked_mv_resident_verify",
        {
            "p_state_code": "MA",
            "p_first_name": "Linus",
            "p_last_name": "Smith",
            "p_date_of_birth": "1988-06-23",
            "p_channel": "patch-script",
            "p_conversation_id": "patch-get-profile-fee",
        },
    )
    token = verify["session_token"]
    live = wire_mv.supabase_rpc_json(
        supabase_host, apikey, "miked_mv_get_profile", {"p_session_token": token}
    )
    regs = live.get("registrations") or []
    fee = regs[0].get("renewal_fee_dollars") if regs else None
    if fee is None:
        raise SystemExit(f"Live RPC missing renewal_fee_dollars: {json.dumps(live)[:2000]}")
    print(f"Live Supabase renewal_fee_dollars={fee}")
    print(f"Patched {ACTION_ID} contract with renewal_fee_dollars on registrations.")


if __name__ == "__main__":
    asyncio.run(main())
