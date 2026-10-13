#!/Users/michael.debiase/.local/share/uv/tools/ava-mcp/bin/python3
"""Create live Custom REST Data Actions → Supabase RPC for miked_mv_front_door.

Requires:
  - GENESYS_CLIENT_ID / GENESYS_CLIENT_SECRET (or AVA_*), AVA_HABITAT=prod
  - SUPABASE_URL + SUPABASE_SECRET_KEY in .env.motor-vehicle (motor_vehicle project)

Uses inline apikey on each action so the shared Web Services integration is not
re-pointed away from EOHHS demo credentials.

Example:
  ./scripts/wire-genesys-supabase-mv-data-actions.py
  ./scripts/wire-genesys-supabase-mv-data-actions.py --replace
"""
from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
AVA_MCP_SITE = Path.home() / ".local/share/uv/tools/ava-mcp/lib/python3.12/site-packages"
if AVA_MCP_SITE.is_dir():
    sys.path.insert(0, str(AVA_MCP_SITE))

from api_utils import request as http  # noqa: E402
from auth_utils import public_headers  # noqa: E402
from config import Config  # noqa: E402
from constants import INTEGRATION_TYPE_ID  # noqa: E402
from tools.data_actions import draft  # noqa: E402
from tools.data_actions.integration import actions_base  # noqa: E402

DEFAULT_WSDA_INTEGRATION_ID = os.environ.get(
    "MIKED_MV_WSDA_INTEGRATION_ID", "19717556-e7eb-4db8-884e-b07c6f50d927"
)
REGISTRY_PATH = ROOT / ".ava-lifecycle/miked-mv-front-door/data-actions-registry.md"
SCHEMAS_PATH = ROOT / ".ava-lifecycle/miked-mv-front-door/supabase-action-schemas.json"
ENV_MV = ROOT / ".env.motor-vehicle"

ACTIONS: list[dict[str, str]] = [
    {"name": "miked_mv_resident_verify", "rpc": "miked_mv_resident_verify"},
    {"name": "miked_mv_get_profile", "rpc": "miked_mv_get_profile"},
    {"name": "miked_mv_registration_renew", "rpc": "miked_mv_registration_renew"},
    {"name": "miked_mv_license_book_appointment", "rpc": "miked_mv_license_book_appointment"},
    {"name": "miked_mv_handoff_create", "rpc": "miked_mv_handoff_create"},
]

# Do NOT auto-delete. Pass explicit IDs only when the author confirms (see org-retirement log).
DEFAULT_SLOT_FREE_IDS: list[str] = []


def supabase_rpc_json(
    supabase_host: str, apikey: str, rpc: str, body: dict[str, Any]
) -> dict[str, Any]:
    import urllib.error
    import urllib.request

    url = f"{supabase_host}/rest/v1/rpc/{rpc}"
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers={"apikey": apikey, "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            raw = resp.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        err_body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Supabase RPC {rpc} failed HTTP {exc.code}: {err_body}") from exc
    return json.loads(raw)


def load_motor_vehicle_env() -> tuple[str, str]:
    path = ENV_MV
    if not path.is_file():
        raise SystemExit(f"Missing {path}. Copy from .env.motor-vehicle.example and set secrets.")
    url = ""
    key = ""
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("SUPABASE_URL="):
            url = line.split("=", 1)[1].strip().strip('"').strip("'")
        if line.startswith("SUPABASE_SECRET_KEY="):
            key = line.split("=", 1)[1].strip().strip('"').strip("'")
    if not url or "mdwdkiwtawqcoxdlrvbd" not in url:
        raise SystemExit("SUPABASE_URL in .env.motor-vehicle must be motor_vehicle (mdwdkiwtawqcoxdlrvbd).")
    if not key or key in ("sb_secret_...",) or "your" in key:
        raise SystemExit("Set SUPABASE_SECRET_KEY in .env.motor-vehicle.")
    if key.startswith("sb_publishable_"):
        raise SystemExit("Use sb_secret_… in .env.motor-vehicle, not publishable key.")
    return url.rstrip("/"), key


def load_genesys_from_mcp_json() -> None:
    if os.environ.get("GENESYS_CLIENT_ID") and os.environ.get("GENESYS_CLIENT_SECRET"):
        return
    mcp_path = ROOT / ".cursor/mcp.json"
    if not mcp_path.is_file():
        return
    data = json.loads(mcp_path.read_text())
    env = data.get("mcpServers", {}).get("ava-harness", {}).get("env", {})
    for key in ("GENESYS_CLIENT_ID", "GENESYS_CLIENT_SECRET", "AVA_HABITAT"):
        if key in env and not os.environ.get(key):
            os.environ[key] = env[key]


def build_response_config(output_schema: dict[str, Any]) -> dict[str, Any]:
    _ = output_schema
    return {
        "translationMap": {"rawResult": "$"},
        "translationMapDefaults": {"rawResult": "{}"},
        "successTemplate": "${rawResult}",
    }


def build_request_config(supabase_host: str, rpc: str, apikey: str) -> dict[str, Any]:
    return {
        "requestUrlTemplate": f"{supabase_host}/rest/v1/rpc/{rpc}",
        "requestType": "POST",
        "headers": {
            "Content-Type": "application/json",
            "apikey": apikey,
        },
        "requestTemplate": "${input.rawRequest}",
    }


async def delete_action(config: Config, action_id: str) -> None:
    hdrs = await public_headers(config)
    try:
        await draft.delete_action_draft(config, action_id)
    except Exception:
        pass
    try:
        await http(
            "DELETE",
            f"{actions_base(config)}/{action_id}",
            "HedwigPublic",
            headers=hdrs,
        )
    except Exception as exc:  # noqa: BLE001
        print(f"  warning: could not delete {action_id}: {exc}", file=sys.stderr)


def draft_test_ok(result: dict[str, Any]) -> tuple[bool, str]:
    if not result:
        return False, "empty test result"
    ops = result.get("operations") or []
    for step in ops:
        name = step.get("name") or "?"
        if step.get("success") is False:
            return False, f"{name}: {json.dumps(step.get('result', step))[:1200]}"
    if result.get("finalResult") is not None or result.get("success") is True:
        return True, "ok"
    return False, json.dumps(result)[:1200]


async def create_live_action(
    config: Config,
    *,
    integration_id: str,
    supabase_host: str,
    apikey: str,
    name: str,
    rpc: str,
    input_schema: dict[str, Any],
    output_schema: dict[str, Any],
    test_input: dict[str, Any],
) -> tuple[str, dict[str, Any] | None]:
    config_payload = {
        "request": build_request_config(supabase_host, rpc, apikey),
        "response": build_response_config(output_schema),
    }
    opened = await draft.create_draft(
        config,
        name=name,
        category="MIKED-MV-Supabase-RPC",
        integration_id=integration_id,
        integration_type_id=INTEGRATION_TYPE_ID,
        input_schema=input_schema,
        output_schema=output_schema,
        config_payload=config_payload,
        secure=False,
        description=f"Live Supabase RPC {rpc} for miked_mv_front_door (motor_vehicle project).",
    )
    action_id = str(opened["id"])
    test_result = await draft.test_action_draft(config, action_id, test_input)
    ok, reason = draft_test_ok(test_result if isinstance(test_result, dict) else {})
    if not ok:
        await draft.delete_action_draft(config, action_id)
        await delete_action(config, action_id)
        raise RuntimeError(f"draft test failed for {name}: {reason}")

    refreshed = await draft.get_action_draft(config, action_id)
    await draft.publish_action_draft(config, action_id, refreshed["version"])
    final = test_result.get("finalResult") if isinstance(test_result, dict) else None
    return action_id, final if isinstance(final, dict) else None


def load_local_schemas(name: str) -> tuple[dict, dict]:
    data = json.loads(SCHEMAS_PATH.read_text())
    block = data[name]
    return block["inputSchema"], block["outputSchema"]


def load_registry_ids() -> dict[str, str]:
    if not REGISTRY_PATH.is_file():
        return {}
    out: dict[str, str] = {}
    for line in REGISTRY_PATH.read_text().splitlines():
        if not line.startswith("| `miked_mv_"):
            continue
        parts = [p.strip() for p in line.split("|")]
        if len(parts) < 3:
            continue
        name = parts[1].strip("`")
        action_id = parts[2].strip("`")
        if action_id.startswith("custom_-_"):
            out[name] = action_id
    return out


def build_test_inputs(token: str) -> dict[str, dict[str, Any]]:
    wire_code = f"MAWIRE{int(time.time()) % 1000000000:09d}"
    return {
        "miked_mv_resident_verify": {
            "p_state_code": "MA",
            "p_first_name": "Kimberly",
            "p_last_name": "Green",
            "p_date_of_birth": "1966-01-10",
            "p_phone_last4": "3738",
            "p_channel": "wire-script",
            "p_conversation_id": "miked-mv-wire-test",
        },
        "miked_mv_get_profile": {"p_session_token": token},
        "miked_mv_registration_renew": {
            "p_session_token": token,
            "p_plate_number": "4EF482",
        },
        "miked_mv_license_book_appointment": {
            "p_session_token": token,
            "p_purpose": "REAL ID license renewal",
            "p_service_center": "Boston RMV Service Center",
            "p_scheduled_at": "2026-10-15T14:00:00-04:00",
            "p_confirmation_code": wire_code,
        },
        "miked_mv_handoff_create": {
            "p_session_token": token,
            "p_intent_summary": "Wire script live integration test handoff.",
            "p_channel": "voice",
            "p_conversation_id": "miked-mv-wire-test",
            "p_fields_json": '{"topic":"license_renewal","demo":true}',
        },
    }


def write_registry(id_map: dict[str, str], supabase_host: str) -> None:
    lines = [
        "# MV Data Actions (Genesys Cloud) — `miked_mv_*`",
        "",
        f"Live **Custom REST** → Supabase RPC (`motor_vehicle` — `{supabase_host}`).",
        "",
        "Wire script: `scripts/wire-genesys-supabase-mv-data-actions.py`",
        "",
        "Integration (shared Web Services): "
        f"`{DEFAULT_WSDA_INTEGRATION_ID}` — **inline apikey** per action (does not change EOHHS integration secret).",
        "",
        "| Name | Action ID | RPC |",
        "|------|-----------|-----|",
    ]
    for row in ACTIONS:
        name = row["name"]
        lines.append(f"| `{name}` | `{id_map[name]}` | `{row['rpc']}` |")
    lines.extend(
        [
            "",
            "After wiring, attach these IDs in `miked_mv_front_door` tool targets and publish a new AVA version.",
            "",
        ]
    )
    REGISTRY_PATH.write_text("\n".join(lines) + "\n")


async def free_action_slots(config: Config, action_ids: list[str]) -> None:
    for action_id in action_ids:
        print(f"  freeing slot: delete {action_id}")
        await delete_action(config, action_id)


async def run(replace: bool, free_slots: bool, skip_verify: bool, only: list[str] | None) -> None:
    load_genesys_from_mcp_json()
    os.environ.setdefault("AVA_HABITAT", "prod")
    supabase_host, apikey = load_motor_vehicle_env()
    config = Config()
    integration_id = DEFAULT_WSDA_INTEGRATION_ID
    print(f"Supabase: {supabase_host}")
    print(f"Using Web Services integration: {integration_id} (inline apikey on each MV action)")

    if free_slots:
        print("Freeing data action slots (org 500 cap)...")
        await free_action_slots(config, DEFAULT_SLOT_FREE_IDS)

    old_ids = load_registry_ids() if replace else {}
    id_map: dict[str, str] = {}

    verify_in, verify_out = load_local_schemas("miked_mv_resident_verify")
    verify_final: dict[str, Any] | None = None

    if skip_verify:
        reg_ids = load_registry_ids()
        if "miked_mv_resident_verify" in reg_ids:
            id_map["miked_mv_resident_verify"] = reg_ids["miked_mv_resident_verify"]
            print(f"  miked_mv_resident_verify (existing) -> {reg_ids['miked_mv_resident_verify']}")
        else:
            skip_verify = False

    if not skip_verify or "miked_mv_resident_verify" not in id_map:
        if replace and "miked_mv_resident_verify" in old_ids:
            await delete_action(config, old_ids["miked_mv_resident_verify"])
        tests = build_test_inputs("")
        verify_id, verify_final = await create_live_action(
            config,
            integration_id=integration_id,
            supabase_host=supabase_host,
            apikey=apikey,
            name="miked_mv_resident_verify",
            rpc="miked_mv_resident_verify",
            input_schema=verify_in,
            output_schema=verify_out,
            test_input=tests["miked_mv_resident_verify"],
        )
        print(f"  miked_mv_resident_verify -> {verify_id}")
        id_map["miked_mv_resident_verify"] = verify_id

    if verify_final is None:
        tests = build_test_inputs("")
        verify_final = supabase_rpc_json(
            supabase_host,
            apikey,
            "miked_mv_resident_verify",
            tests["miked_mv_resident_verify"],
        )

    token = (verify_final or {}).get("session_token") or ""
    if not token:
        raise RuntimeError("Could not obtain session_token from live verify test")
    tests = build_test_inputs(token)

    start_idx = 1 if "miked_mv_resident_verify" in id_map else 0
    todo = ACTIONS[start_idx:]
    if only:
        only_set = set(only)
        todo = [r for r in todo if r["name"] in only_set]
    for row in todo:
        name = row["name"]
        if replace and name in old_ids:
            await delete_action(config, old_ids[name])
        input_schema, output_schema = load_local_schemas(name)
        new_id, _ = await create_live_action(
            config,
            integration_id=integration_id,
            supabase_host=supabase_host,
            apikey=apikey,
            name=name,
            rpc=row["rpc"],
            input_schema=input_schema,
            output_schema=output_schema,
            test_input=tests[name],
        )
        id_map[name] = new_id
        print(f"  {name} -> {new_id}")

    merged = {**load_registry_ids(), **id_map}
    write_registry(merged, supabase_host)
    print(f"\nUpdated {REGISTRY_PATH.relative_to(ROOT)}")
    print("Next: ava-design / build miked_mv_front_door with these target IDs.")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--replace",
        action="store_true",
        help="Delete actions listed in data-actions-registry.md before recreating",
    )
    parser.add_argument(
        "--free-slots",
        action="store_true",
        help="Delete obsolete demo data actions to free org quota before creating MV actions",
    )
    parser.add_argument(
        "--skip-verify",
        action="store_true",
        help="Keep existing miked_mv_resident_verify; wire remaining actions only",
    )
    parser.add_argument(
        "--only",
        action="append",
        metavar="ACTION_NAME",
        help="Wire only this action (repeatable), e.g. --only miked_mv_handoff_create",
    )
    args = parser.parse_args()
    asyncio.run(
        run(
            replace=args.replace,
            free_slots=args.free_slots,
            skip_verify=args.skip_verify,
            only=args.only,
        )
    )


if __name__ == "__main__":
    main()
