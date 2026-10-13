"""Expose Genesys Archy CLI commands as MCP tools for Cursor."""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from typing import Any

from mcp.server.mcpserver import MCPServer

ARCHY_BIN = os.environ.get("ARCHY_BIN", "archy")
DEFAULT_TIMEOUT_SEC = int(os.environ.get("ARCHY_MCP_TIMEOUT_SEC", "600"))

server = MCPServer(
    name="archy",
    instructions=(
        "Genesys Cloud Architect Scripting (Archy). Uses OAuth from ~/.archy_config "
        "unless overridden per call. Exit codes follow Archy docs (e.g. doesFlowExist: "
        "0=no, 1=yes)."
    ),
    log_level=os.environ.get("ARCHY_MCP_LOG_LEVEL", "WARNING"),
)


def _run_archy(args: list[str], timeout_sec: int | None = None) -> dict[str, Any]:
    timeout = timeout_sec or DEFAULT_TIMEOUT_SEC
    cmd = [ARCHY_BIN, *args]
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except FileNotFoundError as exc:
        return {
            "ok": False,
            "error": f"Archy not found at {ARCHY_BIN!r}. Install Archy or set ARCHY_BIN.",
            "detail": str(exc),
        }
    except subprocess.TimeoutExpired:
        return {
            "ok": False,
            "error": f"Archy timed out after {timeout}s",
            "command": cmd,
        }

    return {
        "ok": proc.returncode not in (124, 125),
        "exit_code": proc.returncode,
        "stdout": proc.stdout.strip(),
        "stderr": proc.stderr.strip(),
        "command": cmd,
    }


def _optional_auth_args(
    client_id: str | None,
    client_secret: str | None,
    location: str | None,
) -> list[str]:
    out: list[str] = []
    if client_id:
        out.extend(["--clientId", client_id])
    if client_secret:
        out.extend(["--clientSecret", client_secret])
    if location:
        out.extend(["--location", location])
    return out


@server.tool()
def archy_dump() -> str:
    """Print Archy default configuration (redact secrets locally before sharing)."""
    return json.dumps(_run_archy(["dump"]), indent=2)


@server.tool()
def archy_does_flow_exist(
    flow_name: str,
    flow_type: str,
    location: str | None = None,
) -> str:
    """Check whether a flow exists. Archy exit_code 0=no, 1=yes."""
    args = [
        "doesFlowExist",
        "--flowName",
        flow_name,
        "--flowType",
        flow_type,
        *_optional_auth_args(None, None, location),
    ]
    result = _run_archy(args)
    if result.get("exit_code") == 0:
        result["exists"] = False
    elif result.get("exit_code") == 1:
        result["exists"] = True
    return json.dumps(result, indent=2)


@server.tool()
def archy_is_published(
    flow_name: str,
    flow_type: str,
    location: str | None = None,
) -> str:
    """Whether the flow has a published version. exit_code 0=no, 1=yes."""
    args = [
        "isPublished",
        "--flowName",
        flow_name,
        "--flowType",
        flow_type,
        *_optional_auth_args(None, None, location),
    ]
    result = _run_archy(args)
    if result.get("exit_code") == 0:
        result["published"] = False
    elif result.get("exit_code") == 1:
        result["published"] = True
    return json.dumps(result, indent=2)


@server.tool()
def archy_export_flow(
    flow_name: str | None = None,
    flow_type: str | None = None,
    flow_id: str | None = None,
    flow_version: str = "latest",
    export_type: str = "architect",
    output_dir: str | None = None,
    export_file_name: str | None = None,
    force: bool = False,
    location: str | None = None,
) -> str:
    """
    Export an Architect flow to disk (i3 or yaml). Returns stdout path from Archy.
    Provide flow_id OR (flow_name + flow_type).
    """
    if not flow_id and not (flow_name and flow_type):
        return json.dumps(
            {"ok": False, "error": "Provide flow_id or both flow_name and flow_type."},
            indent=2,
        )
    args = ["export", "--flowVersion", flow_version, "--exportType", export_type]
    if flow_id:
        args.extend(["--flowId", flow_id])
    else:
        args.extend(["--flowName", flow_name or "", "--flowType", flow_type or ""])
    if output_dir:
        args.extend(["--outputDir", str(Path(output_dir).expanduser().resolve())])
    if export_file_name:
        args.extend(["--exportFileName", export_file_name])
    if force:
        args.append("--force")
    args.extend(_optional_auth_args(None, None, location))
    return json.dumps(_run_archy(args), indent=2)


@server.tool()
def archy_validate_flow(
    flow_name: str | None = None,
    flow_type: str | None = None,
    flow_id: str | None = None,
    location: str | None = None,
) -> str:
    """
    Validate a flow in the org. exit_code 0=ok, 1=warnings, 123=errors.
    Provide flow_id OR (flow_name + flow_type).
    """
    if not flow_id and not (flow_name and flow_type):
        return json.dumps(
            {"ok": False, "error": "Provide flow_id or both flow_name and flow_type."},
            indent=2,
        )
    args = ["validate"]
    if flow_id:
        args.extend(["--flowId", flow_id])
    else:
        args.extend(["--flowName", flow_name or "", "--flowType", flow_type or ""])
    args.extend(_optional_auth_args(None, None, location))
    return json.dumps(_run_archy(args), indent=2)


@server.tool()
def archy_create_yaml(
    yaml_file: str,
    confirm: bool = False,
    location: str | None = None,
) -> str:
    """
    Create a new Architect flow from Archy YAML. Requires confirm=true (live org change).
    """
    if not confirm:
        return json.dumps(
            {"ok": False, "error": "Refusing to create without confirm=true."},
            indent=2,
        )
    path = Path(yaml_file).expanduser().resolve()
    if not path.is_file():
        return json.dumps({"ok": False, "error": f"File not found: {path}"}, indent=2)
    args = ["create", "--file", str(path), *_optional_auth_args(None, None, location)]
    return json.dumps(_run_archy(args), indent=2)


@server.tool()
def archy_validate_yaml(
    yaml_file: str,
    location: str | None = None,
) -> str:
    """Validate an Archy YAML file (schema + org entity lookups)."""
    path = Path(yaml_file).expanduser().resolve()
    if not path.is_file():
        return json.dumps({"ok": False, "error": f"File not found: {path}"}, indent=2)
    args = ["validateYaml", "--file", str(path), *_optional_auth_args(None, None, location)]
    return json.dumps(_run_archy(args), indent=2)


@server.tool()
def archy_publish_yaml(
    yaml_file: str,
    confirm: bool = False,
    location: str | None = None,
) -> str:
    """
    Publish a flow from Archy YAML. Requires confirm=true (live org change).
    """
    if not confirm:
        return json.dumps(
            {
                "ok": False,
                "error": "Refusing to publish without confirm=true.",
            },
            indent=2,
        )
    path = Path(yaml_file).expanduser().resolve()
    if not path.is_file():
        return json.dumps({"ok": False, "error": f"File not found: {path}"}, indent=2)
    args = ["publish", "--file", str(path), *_optional_auth_args(None, None, location)]
    return json.dumps(_run_archy(args), indent=2)


@server.tool()
def archy_update_yaml(
    yaml_file: str,
    confirm: bool = False,
    location: str | None = None,
) -> str:
    """
    Update (new version + check in) from Archy YAML. Requires confirm=true.
    """
    if not confirm:
        return json.dumps(
            {
                "ok": False,
                "error": "Refusing to update without confirm=true.",
            },
            indent=2,
        )
    path = Path(yaml_file).expanduser().resolve()
    if not path.is_file():
        return json.dumps({"ok": False, "error": f"File not found: {path}"}, indent=2)
    args = ["update", "--file", str(path), *_optional_auth_args(None, None, location)]
    return json.dumps(_run_archy(args), indent=2)


def main() -> None:
    server.run()


if __name__ == "__main__":
    main()
