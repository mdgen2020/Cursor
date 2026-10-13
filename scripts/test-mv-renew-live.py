#!/usr/bin/env python3
"""Test live Genesys miked_mv_registration_renew (draft-from-published test only)."""
from __future__ import annotations

import asyncio
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path.home() / ".local/share/uv/tools/ava-mcp/lib/python3.12/site-packages"))

from config import Config  # noqa: E402
from tools.data_actions import draft  # noqa: E402

_wire = ROOT / "scripts/wire-genesys-supabase-mv-data-actions.py"
_spec = importlib.util.spec_from_file_location("wire_mv", _wire)
wire_mv = importlib.util.module_from_spec(_spec)
assert _spec and _spec.loader
_spec.loader.exec_module(wire_mv)

RENEW_ID = "custom_-_d57c9f4b-5a28-4de0-b52d-16cd16b12c02"


async def main() -> None:
    wire_mv.load_genesys_from_mcp_json()
    host, key = wire_mv.load_motor_vehicle_env()
    tests = wire_mv.build_test_inputs("")
    verify = wire_mv.supabase_rpc_json(host, key, "miked_mv_resident_verify", tests["miked_mv_resident_verify"])
    token = verify.get("session_token")
    if not token:
        raise SystemExit(f"verify failed: {verify}")
    print("Supabase verify OK, token prefix:", token[:12])

    renew_input = wire_mv.build_test_inputs(token)["miked_mv_registration_renew"]
    print("Renew input:", renew_input)

    try:
        direct = wire_mv.supabase_rpc_json(host, key, "miked_mv_registration_renew", renew_input)
        print("Supabase renew OK:", json.dumps(direct, indent=2)[:800])
    except RuntimeError as exc:
        print("Supabase renew FAILED:", exc)
        sys.exit(1)

    config = Config()
    action_id = sys.argv[1] if len(sys.argv) > 1 else RENEW_ID
    print(f"\nGenesys test via draft-from-published: {action_id}")
    try:
        await draft.create_action_draft(config, action_id)
        result = await draft.test_action_draft(config, action_id, renew_input)
        print(json.dumps(result, indent=2)[:4000])
        ok, reason = wire_mv.draft_test_ok(result if isinstance(result, dict) else {})
        print("Genesys test:", "OK" if ok else "FAIL", reason)
        if not ok:
            sys.exit(2)
    finally:
        try:
            await draft.delete_action_draft(config, action_id)
        except Exception:
            pass


if __name__ == "__main__":
    asyncio.run(main())
