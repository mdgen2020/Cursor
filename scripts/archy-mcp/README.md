# Archy MCP (Cursor)

[Archy](https://developer.genesys.cloud/devapps/archy/) is Genesys **Architect Scripting** — a **CLI**, not an MCP server. This package wraps common Archy commands so Cursor agents can export, validate, and (with confirmation) publish flows.

## Prerequisites

1. **Archy installed** (`which archy` → e.g. `/opt/homebrew/bin/archy`).
2. **Archy configured** for your org (OAuth client credentials):

   ```bash
   archy setup    # first time
   # or
   archy configure -k clientId -a '<oauth-client-id>'
   archy configure -k clientSecret -a '<secret>'
   archy configure -k location -a 'mypurecloud.com'
   ```

   Settings live in `~/.archy_config`. The MCP server does **not** store secrets; it calls the `archy` binary, which reads that file.

3. **`uv`** on your PATH ([https://docs.astral.sh/uv/](https://docs.astral.sh/uv/)).

## Install (once per machine)

From repo root:

```bash
cd scripts/archy-mcp && uv sync
```

## Enable in Cursor

Add to **this project’s** `.cursor/mcp.json` (merge with existing servers):

```json
"archy": {
  "command": "uv",
  "args": [
    "run",
    "--directory",
    "scripts/archy-mcp",
    "archy-mcp"
  ],
  "env": {
    "FASTMCP_LOG_LEVEL": "ERROR",
    "ARCHY_BIN": "/opt/homebrew/bin/archy"
  },
  "disabled": false,
  "timeout": 120000
}
```

Use an **absolute** path for `--directory` if Cursor does not resolve it relative to the workspace.

Then **Cursor → Settings → MCP** → restart or refresh MCP. You should see a server named **archy** with tools like `archy_export_flow`, `archy_does_flow_exist`.

## Tools (summary)

| Tool | Purpose |
|------|---------|
| `archy_validate_yaml` | Validate Archy YAML before create/update |
| `archy_create_yaml` | Create flow from YAML (`confirm: true`) |
| `archy_does_flow_exist` | Is `miked_mv_VAbotflow` in the org? |
| `archy_is_published` | Published version? |
| `archy_export_flow` | Pull i3/yaml into `docs/demo/architect-exports/` |
| `archy_validate_flow` | Org-side validation |
| `archy_publish_yaml` / `archy_update_yaml` | **Live changes** — require `confirm: true` |
| `archy_dump` | Show Archy config (keep output private) |

## MV greenfield smoke (agent or terminal)

```bash
archy doesFlowExist --flowName "miked_mv_VAbotflow" --flowType bot
archy export --flowName "miked direct to queue" --flowType inboundcall \
  --outputDir "$(pwd)/docs/demo/architect-exports" --force
```

Flow types: `bot`, `inboundcall`, `digitalbot`, `inboundchat`, etc. (`archy export --help`).

## Without MCP

You can always run `archy` from the terminal or ask the agent to use the **Shell** tool — MCP just makes discovery and structured args easier.
