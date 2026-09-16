#!/Users/michael.debiase/.local/share/uv/tools/ava-mcp/bin/python3
"""Create live Custom REST Data Actions → Supabase RPC for the EOHHS demo.

Requires:
  - GENESYS_CLIENT_ID / GENESYS_CLIENT_SECRET (or AVA_*), AVA_HABITAT=prod
  - SUPABASE_SECRET_KEY in repo .env (same project as SUPABASE_URL)

Uses the ava-mcp Python package (same as the AVA harness MCP server).

Example:
  ./scripts/wire-genesys-supabase-data-actions.py --replace
"""
from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
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
from contracts.hedwig_contracts import GetDataActionSchemaRequest  # noqa: E402
from tools.data_actions import draft  # noqa: E402
from tools.data_actions.integration import (  # noqa: E402
    actions_base,
    get_integration_by_name,
    integrations_base,
)
from tools.hedwig_public import get_data_action_schema  # noqa: E402

SUPABASE_HOST = "https://njjkupupxvfvymelcjpg.supabase.co"
INTEGRATION_NAME = "EOHHS_Supabase_miked"
# Enabled org integration (custom-rest-actions). Override with EOHHS_WSDA_INTEGRATION_ID.
DEFAULT_WSDA_INTEGRATION_ID = os.environ.get(
    "EOHHS_WSDA_INTEGRATION_ID", "19717556-e7eb-4db8-884e-b07c6f50d927"
)
REGISTRY_PATH = ROOT / ".ava-lifecycle/eohhs-ma-front-door/data-actions-registry.md"
DESIGN_ARTIFACT = ROOT / ".ava-lifecycle/eohhs-ma-front-door/design-artifact.json"
SCHEMAS_PATH = ROOT / ".ava-lifecycle/eohhs-ma-front-door/supabase-action-schemas.json"

ACTIONS: list[dict[str, str]] = [
    {
        "name": "eohhs_resident_verify_miked",
        "rpc": "resident_verify",
        "old_id": "custom_-_e7e7c05d-3432-4a71-b90a-e534d80ac5ea",
    },
    {
        "name": "eohhs_dta_case_status_miked",
        "rpc": "dta_case_status",
        "old_id": "custom_-_988e6409-cf34-4d74-b0fb-456ecc7b9395",
    },
    {
        "name": "eohhs_dta_register_document_miked",
        "rpc": "dta_register_document",
        "old_id": "custom_-_ebb905ca-4f7b-49f1-984f-8d2f7e06a524",
    },
    {
        "name": "eohhs_masshealth_complete_screening_miked",
        "rpc": "masshealth_complete_screening",
        "old_id": "custom_-_cf6faa3e-165f-4d24-bc92-069a0d949552",
    },
    {
        "name": "eohhs_escalation_create_handoff_miked",
        "rpc": "escalation_create_handoff",
        "old_id": "custom_-_b0d5536a-b5e2-4a98-a517-d8b454f5ea91",
    },
]


def load_supabase_apikey() -> str:
    env_path = ROOT / ".env"
    if env_path.is_file():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("SUPABASE_SECRET_KEY="):
                val = line.split("=", 1)[1].strip().strip('"').strip("'")
                if val and "your" not in val and val != "sb_secret_...":
                    return val
    raise SystemExit("Set SUPABASE_SECRET_KEY in .env (see .env.example).")


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
    # Pass through PostgREST JSON body; per-field ${field} templates double-encode strings.
    _ = output_schema
    return {
        "translationMap": {"rawResult": "$"},
        "translationMapDefaults": {"rawResult": "{}"},
        "successTemplate": "${rawResult}",
    }


def build_request_config(rpc: str, *, inline_apikey: str | None = None) -> dict[str, Any]:
    apikey_header = inline_apikey if inline_apikey else "${credentials.apikey}"
    return {
        "requestUrlTemplate": f"{SUPABASE_HOST}/rest/v1/rpc/{rpc}",
        "requestType": "POST",
        "headers": {
            "Content-Type": "application/json",
            "apikey": apikey_header,
        },
        "requestTemplate": "${input.rawRequest}",
    }


async def ensure_supabase_integration(config: Config, apikey: str) -> tuple[str, bool]:
    """Returns (integration_id, use_inline_apikey)."""
    integration_id = DEFAULT_WSDA_INTEGRATION_ID
    hdrs = await public_headers(config)
    cur = await http(
        "GET",
        f"{integrations_base(config)}/{integration_id}/config/current",
        "IntegrationsPublic",
        headers=hdrs,
    )
    version = cur.get("version", 1)
    body = {
        "name": cur.get("name") or "Web Services Data Actions (1)",
        "version": version,
        "notes": cur.get("notes") or "",
        "advanced": cur.get("advanced") or {},
        "properties": {"apikey": {"value": apikey}},
        "requestUriTemplate": SUPABASE_HOST,
        "credentialType": "UserDefined",
    }
    try:
        await http(
            "PUT",
            f"{integrations_base(config)}/{integration_id}/config/current",
            "IntegrationsPublic",
            headers=hdrs,
            json=body,
        )
        return integration_id, False
    except Exception as exc:  # noqa: BLE001
        print(
            "WARN: Could not PUT User Defined apikey on integration (set manually in Admin → "
            f"Integrations → {integration_id} field `apikey`). Falling back to inline header for demo. "
            f"({exc})",
            file=sys.stderr,
        )
        return integration_id, True


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
    name: str,
    rpc: str,
    inline_apikey: str | None,
    input_schema: dict[str, Any],
    output_schema: dict[str, Any],
    test_input: dict[str, Any],
) -> tuple[str, dict[str, Any] | None]:
    config_payload = {
        "request": build_request_config(rpc, inline_apikey=inline_apikey),
        "response": build_response_config(output_schema),
    }
    opened = await draft.create_draft(
        config,
        name=name,
        category="EOHHS-Supabase-RPC",
        integration_id=integration_id,
        integration_type_id=INTEGRATION_TYPE_ID,
        input_schema=input_schema,
        output_schema=output_schema,
        config_payload=config_payload,
        secure=False,
        description=f"Live Supabase RPC {rpc} for EOHHS demo (_miked).",
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


def build_test_inputs(token: str, case_number: str) -> dict[str, dict[str, Any]]:
    return {
        "eohhs_resident_verify_miked": {
            "p_first_name": "Linus",
            "p_last_name": "Turing",
            "p_date_of_birth": "1988-06-23",
        },
        "eohhs_dta_case_status_miked": {
            "p_case_number": case_number,
            "p_session_token": token,
        },
        "eohhs_dta_register_document_miked": {
            "p_case_number": case_number,
            "p_session_token": token,
            "p_document_type": "proof_of_rent",
            "p_channel": "digital",
            "p_conversation_id": "wire-script-test",
        },
        "eohhs_masshealth_complete_screening_miked": {
            "p_session_token": token,
            "p_household_size": 1,
            "p_income_band": "low",
            "p_coverage_status": "none",
        },
        "eohhs_escalation_create_handoff_miked": {
            "p_session_token": token,
            "p_program": "SNAP",
            "p_summary": "Wire script live integration test handoff.",
            "p_channel": "voice",
            "p_conversation_id": "wire-script-test",
        },
    }


def update_design_artifact_tool_ids(id_map: dict[str, str]) -> None:
    if not DESIGN_ARTIFACT.is_file():
        return
    doc = json.loads(DESIGN_ARTIFACT.read_text())
    for tool in doc.get("tools") or []:
        target = tool.get("target") or {}
        name = target.get("name")
        if name and name in id_map:
            target["id"] = id_map[name]
    if "_meta" in doc:
        doc["_meta"]["note"] = (
            "Live Supabase Custom REST actions on integration EOHHS_Supabase_miked. "
            "Re-publish AVA after ID changes."
        )
    DESIGN_ARTIFACT.write_text(json.dumps(doc, indent=2) + "\n")


def write_registry(id_map: dict[str, str]) -> None:
    lines = [
        "# EOHHS Data Actions (Genesys Cloud) — `_miked`",
        "",
        "Live **Custom REST** → Supabase RPC (`EOHHS_Supabase_miked` integration).",
        "",
        "Docs: [`docs/demo/genesys-data-actions-supabase.md`](../../docs/demo/genesys-data-actions-supabase.md)",
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
            "After wiring, publish a new AVA version if tool `target.id` values changed.",
            "",
        ]
    )
    REGISTRY_PATH.write_text("\n".join(lines) + "\n")


def load_local_schemas(name: str) -> tuple[dict, dict]:
    data = json.loads(SCHEMAS_PATH.read_text())
    block = data[name]
    return block["inputSchema"], block["outputSchema"]


async def fetch_schemas(config: Config, row: dict[str, str]) -> tuple[dict, dict]:
    try:
        got = await get_data_action_schema(
            config, GetDataActionSchemaRequest(data_action_id=row["old_id"])
        )
        return got["inputSchema"], got["outputSchema"]
    except Exception:
        return load_local_schemas(row["name"])


async def run(replace: bool) -> None:
    load_genesys_from_mcp_json()
    os.environ.setdefault("AVA_HABITAT", "prod")
    apikey = load_supabase_apikey()
    config = Config()

    integration_id, inline = await ensure_supabase_integration(config, apikey)
    inline_key = apikey if inline else None
    print(f"Using Web Services integration: {integration_id}")

    verify_schema_in, verify_schema_out = await fetch_schemas(config, ACTIONS[0])
    verify_test = build_test_inputs("", "")["eohhs_resident_verify_miked"]
    if replace:
        await delete_action(config, ACTIONS[0]["old_id"])

    verify_id, verify_final = await create_live_action(
        config,
        integration_id=integration_id,
        name=ACTIONS[0]["name"],
        rpc=ACTIONS[0]["rpc"],
        inline_apikey=inline_key,
        input_schema=verify_schema_in,
        output_schema=verify_schema_out,
        test_input=verify_test,
    )
    print(f"  {ACTIONS[0]['name']} -> {verify_id}")

    token = (verify_final or {}).get("session_token") or ""
    case_number = (verify_final or {}).get("snap_case_number") or "SNAP-MA-100234"
    if not token:
        raise RuntimeError("Could not obtain session_token from live verify test")

    id_map = {ACTIONS[0]["name"]: verify_id}
    tests = build_test_inputs(token, case_number)

    for row in ACTIONS[1:]:
        input_schema, output_schema = await fetch_schemas(config, row)
        if replace:
            await delete_action(config, row["old_id"])
        new_id, _ = await create_live_action(
            config,
            integration_id=integration_id,
            name=row["name"],
            rpc=row["rpc"],
            inline_apikey=inline_key,
            input_schema=input_schema,
            output_schema=output_schema,
            test_input=tests[row["name"]],
        )
        id_map[row["name"]] = new_id
        print(f"  {row['name']} -> {new_id}")

    write_registry(id_map)
    update_design_artifact_tool_ids(id_map)
    print("\nUpdated registry and design-artifact.json tool target IDs.")
    print("Next: create_version + publish_version (TestReady) on the EOHHS AVA.")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--replace",
        action="store_true",
        help="Delete previous mock action IDs before creating live REST actions",
    )
    args = parser.parse_args()
    asyncio.run(run(replace=args.replace))


if __name__ == "__main__":
    main()
