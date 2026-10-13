#!/usr/bin/env python3
"""Ensure External Contact by eMail - MikeD - Full exposes contact id for Architect.

Genesys Cloud wrapper actions use schema URIs (not inline successSchema). The published
schema already allows extra contact fields via additionalProperties; runtime returns id.
This script opens a draft and republishes so draft/test/publish pipeline stays clean.

If you need an explicit `id` property in the draft schema, add it in Admin UI on the
draft success schema (API schema PUT is not supported for this action type).
"""
from __future__ import annotations

import asyncio
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

ACTION_ID = "custom_-_816547b6-db32-410d-8aae-9f6824846583"
ACTION_NAME = "External Contact by eMail - MikeD - Full"
DRAFT_SCHEMA = (
    f"https://api.mypurecloud.com/api/v2/integrations/actions/{ACTION_ID}"
    "/draft/schemas/successschema.json"
)


def load_genesys_env() -> None:
    if os.environ.get("GENESYS_CLIENT_ID") and os.environ.get("GENESYS_CLIENT_SECRET"):
        return
    mcp_path = ROOT / ".cursor/mcp.json"
    if not mcp_path.is_file():
        return
    env = json.loads(mcp_path.read_text()).get("mcpServers", {}).get("ava-harness", {}).get("env", {})
    for key in ("GENESYS_CLIENT_ID", "GENESYS_CLIENT_SECRET", "AVA_HABITAT"):
        if key in env and not os.environ.get(key):
            os.environ[key] = env[key]


async def main() -> None:
    load_genesys_env()
    os.environ.setdefault("AVA_HABITAT", "prod")
    config = Config()
    hdrs = await public_headers(config)
    try:
        await draft.delete_action_draft(config, ACTION_ID)
    except Exception:
        pass
    await draft.create_action_draft(config, ACTION_ID)
    schema = await http("GET", DRAFT_SCHEMA, "HedwigPublic", headers=hdrs)
    props = schema["properties"]["contacts"]["items"].setdefault("properties", {})
    if "id" not in props:
        props["id"] = {"type": "string"}
        print(
            "Note: add contacts[].id in Admin on draft success schema if Architect rejects contacts.id"
        )
    test = await draft.test_action_draft(
        config, ACTION_ID, {"workEmail": "diane.martin@miked.demo"}
    )
    final = (test.get("finalResult") or {}).get("contacts") or []
    if final and final[0].get("id"):
        print(f"Draft test returned contact id: {final[0]['id']}")
    else:
        print("Warning: draft test missing contacts[0].id", json.dumps(test, indent=2)[:1500])
    refreshed = await draft.get_action_draft(config, ACTION_ID)
    await draft.publish_action_draft(config, ACTION_ID, refreshed["version"])
    print(f"Published {ACTION_NAME} (republish complete). Map contacts.id in Architect hydrate.")


if __name__ == "__main__":
    asyncio.run(main())
