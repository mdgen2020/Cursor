#!/usr/bin/env python3
"""Fetch published Genesys data action config (read-only)."""
from __future__ import annotations

import asyncio
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path.home() / ".local/share/uv/tools/ava-mcp/lib/python3.12/site-packages"))

from config import Config  # noqa: E402
from api_utils import request as http  # noqa: E402
from auth_utils import public_headers  # noqa: E402
from tools.data_actions.integration import action_url  # noqa: E402

_wire = ROOT / "scripts/wire-genesys-supabase-mv-data-actions.py"
_spec = importlib.util.spec_from_file_location("wire_mv", _wire)
wire_mv = importlib.util.module_from_spec(_spec)
assert _spec and _spec.loader
_spec.loader.exec_module(wire_mv)


async def main() -> None:
    wire_mv.load_genesys_from_mcp_json()
    config = Config()
    hdrs = await public_headers(config)
    ids = sys.argv[1:] or [
        "custom_-_3d6ab822-2248-4118-b55e-4adb377514af",
        "custom_-_d57c9f4b-5a28-4de0-b52d-16cd16b12c02",
    ]
    for aid in ids:
        data = await http("GET", action_url(config, aid), "HedwigPublic", headers=hdrs)
        cfg = (data or {}).get("config") or {}
        req = cfg.get("request") or {}
        print("\n===", aid, (data or {}).get("name"), "===")
        print("requestUrlTemplate:", req.get("requestUrlTemplate"))
        print("headers keys:", list((req.get("headers") or {}).keys()))
        contract = (data or {}).get("contract") or {}
        out = contract.get("output") or {}
        print("successSchema required:", (out.get("successSchema") or {}).get("required"))


if __name__ == "__main__":
    asyncio.run(main())
