#!/Users/michael.debiase/.local/share/uv/tools/ava-mcp/bin/python3
"""Patch miked_mv_registration_renew Hedwig contract for p_quote_only (no action delete)."""
from __future__ import annotations

import asyncio
import copy
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
from tools.data_actions.integration import action_url  # noqa: E402

_wire = ROOT / "scripts/wire-genesys-supabase-mv-data-actions.py"
_spec = importlib.util.spec_from_file_location("wire_mv", _wire)
wire_mv = importlib.util.module_from_spec(_spec)
assert _spec and _spec.loader
_spec.loader.exec_module(wire_mv)

ACTION_ID = "custom_-_49351070-1d64-4b84-90b9-f1ea2a492d06"
SCHEMAS_PATH = ROOT / ".ava-lifecycle/miked-mv-front-door/supabase-action-schemas.json"


async def main() -> None:
    wire_mv.load_genesys_from_mcp_json()
    os.environ.setdefault("AVA_HABITAT", "prod")
    config = Config()
    hdrs = await public_headers(config)
    schemas = json.loads(SCHEMAS_PATH.read_text())["miked_mv_registration_renew"]

    action = await http("GET", action_url(config, ACTION_ID), "HedwigPublic", headers=hdrs)
    contract = copy.deepcopy(action.get("contract") or {})
    contract["input"] = {"inputSchema": schemas["inputSchema"]}
    contract["output"] = {"successSchema": schemas["outputSchema"]}
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
            "p_conversation_id": "patch-renew-quote",
        },
    )
    quote = wire_mv.supabase_rpc_json(
        supabase_host,
        apikey,
        "miked_mv_registration_renew",
        {
            "p_session_token": verify["session_token"],
            "p_plate_number": "LS8823",
            "p_quote_only": True,
        },
    )
    if quote.get("status") != "quote" or quote.get("amount_dollars") is None:
        raise SystemExit(f"Quote RPC failed: {json.dumps(quote)}")
    print(f"Live quote amount_dollars={quote['amount_dollars']} status={quote['status']}")
    print(f"Patched {ACTION_ID} contract for p_quote_only.")


if __name__ == "__main__":
    asyncio.run(main())
