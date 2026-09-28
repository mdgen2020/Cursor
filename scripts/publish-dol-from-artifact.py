#!/usr/bin/env python3
"""Create + TestReady-publish DOL_Front_Door_miked from design-artifact.json."""
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

from config import Config  # noqa: E402
from contracts.sage_contracts import CreateVersionRequest  # noqa: E402
from sage.common.contracts.version_definition import VersionDefinition  # noqa: E402
from tools import sage_public  # noqa: E402

DESIGN = ROOT / ".ava-lifecycle/dol-front-door-miked/design-artifact.json"


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


def build_definition(artifact: dict) -> VersionDefinition:
    return VersionDefinition.model_validate(
        {
            "role": artifact["role"],
            "instructions": artifact["instructions"],
            "guardrails": artifact.get("guardrails"),
            "tools": artifact["tools"],
            "types": artifact["types"],
            "events": artifact["events"],
            "settings": artifact.get("settings"),
        }
    )


async def main() -> None:
    load_genesys_env()
    artifact = json.loads(DESIGN.read_text())
    agent_id = artifact["_meta"]["agent_id"]
    definition = build_definition(artifact)
    config = Config()
    created = await sage_public.create_version(
        config, CreateVersionRequest(agentId=agent_id, definition=definition)
    )
    print(f"Created version {created.version} status={created.status}")
    job = await sage_public.publish_version(config, agent_id, created.version, test_only=True)
    print(json.dumps(job, indent=2))
    if job.get("status") == "Succeeded":
        artifact["_meta"]["gc_version"] = created.version
        artifact["_meta"]["local_status"] = "test-ready"
        artifact["_meta"]["last_synced_at"] = __import__("datetime").datetime.now(
            __import__("datetime").timezone.utc
        ).strftime("%Y-%m-%dT%H:%M:%SZ")
        DESIGN.write_text(json.dumps(artifact, indent=2) + "\n")
        sage_path = ROOT / ".ava-lifecycle/dol-front-door-miked/sage-agent.json"
        sage = json.loads(sage_path.read_text())
        sage["version"] = created.version
        sage["_meta"]["gc_version"] = created.version
        sage["_meta"]["last_synced_at"] = artifact["_meta"]["last_synced_at"]
        sage["publish_status"] = "TestReady"
        sage_path.write_text(json.dumps(sage, indent=2) + "\n")
        idx_path = ROOT / ".ava-lifecycle/index.json"
        idx = json.loads(idx_path.read_text())
        for entry in idx.get("avas", []):
            if entry.get("slug") == "dol-front-door-miked":
                entry["gc_version"] = created.version
                entry["local_status"] = "test-ready"
                entry["last_updated"] = artifact["_meta"]["last_synced_at"]
        idx_path.write_text(json.dumps(idx, indent=2) + "\n")


if __name__ == "__main__":
    asyncio.run(main())
