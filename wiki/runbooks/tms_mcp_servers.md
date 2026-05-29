# TMS MCP Servers

Purpose: reduce context usage for TMS agents by exposing compact, project-local MCP tools for wiki recall, repository search, Oracle schema checks, Playwright browser work, and routing/Docker status.

## Servers

| Server | Command | Main tools |
|---|---|---|
| `tms-wiki` | `python tools/mcp/tms_mcp_server.py --server wiki` | `wiki_search`, `wiki_read`, `wiki_recent_log` |
| `tms-repo` | `python tools/mcp/tms_mcp_server.py --server repo` | `repo_search`, `repo_files`, `repo_read` |
| `tms-oracle` | `python tools/mcp/tms_mcp_server.py --server oracle` | `oracle_table_columns`, `oracle_find_column`, `oracle_readonly_query` |
| `tms-playwright` | `node admin/wms_admin_frontend/node_modules/playwright-core/lib/entry/mcp.js` | Official Playwright MCP tools |
| `tms-docker-routing` | `python tools/mcp/tms_mcp_server.py --server docker` | `routing_status`, `docker_compose_ps`, `docker_compose_config` |

## Config

Examples are stored in:

- `config/mcp.codex.toml.example`
- `config/mcp.claude.json.example`

For Codex, copy the `[mcp_servers.*]` sections into `%USERPROFILE%\.codex\config.toml` on Windows or `~/.codex/config.toml` on Linux-like systems, then restart Codex. Running sessions do not hot-load newly added MCP tools.

For Claude Code, merge `config/mcp.claude.json.example` into the local Claude MCP configuration.

## Verification

Basic local smoke:

```powershell
python scripts\test_mcp_servers.py --skip-oracle --skip-docker
```

Full live smoke, when Oracle and routing containers are available:

```powershell
python scripts\test_mcp_servers.py
```

`tms-oracle` is read-only by design: it exposes metadata and bounded `SELECT/WITH` queries only. It uses `WMS_ORACLE_USER`, `WMS_ORACLE_PASSWORD`, and `WMS_ORACLE_DSN`, with local defaults matching the dev environment.
