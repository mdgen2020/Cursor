# Connect Archy to Cursor (MCP)

Genesys **Archy** (`archy` on your Mac) talks to Architect via the Platform API. Cursor does not ship an Archy plugin; you add a small **MCP server** that shells out to `archy`.

## Quick path

1. Confirm Archy works: `archy version` and `archy dump` (credentials in `~/.archy_config`).
2. Install the repo wrapper: `cd scripts/archy-mcp && uv sync`
3. Register MCP in `.cursor/mcp.json` — see [scripts/archy-mcp/README.md](../../scripts/archy-mcp/README.md).
4. Reload MCP in Cursor; start a new agent chat so **archy** tools appear.

## Archy vs ava-harness

| MCP | What it controls |
|-----|------------------|
| **ava-harness** | AVA versions, Cicero tests, knowledge, data-action schemas |
| **archy** (this wrapper) | Architect flows — export, validate, publish from YAML |

For **Massachusetts RMV voice**, both matter: publish **AVA 7.0** (harness) and **bot + inbound flows** (Archy or `.i3` import in UI).

## First-time Archy auth

If `archy export` fails with auth errors:

```bash
archy configure -k location -a 'mypurecloud.com'
archy configure -k clientId -a '<OAuth client id>'
archy configure -k clientSecret -a '<secret>'
archy refresh
```

Use an OAuth client with permissions for Architect / flows in your division.

## Alternative: no MCP

Agents can run `/opt/homebrew/bin/archy ...` via Shell when you approve network commands. MCP is optional convenience.
