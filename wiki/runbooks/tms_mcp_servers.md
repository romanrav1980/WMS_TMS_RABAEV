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

## Windows sandbox recovery — 2026-10-07

`exec_command` failed with `helper_unknown_error: setup refresh had errors`. The sandbox log identified `deny ACE failed on C:\projects\TMS\.git: open deny ACL target for update`. The directory owner was `CodexSandboxOffline`, rather than the project owner `roma`.

Saved the directory's original SDDL to `tmp/sandbox_repair/git-directory-acl-before.txt` and restored only the `.git` directory owner to `roma` through a UAC-elevated PowerShell script. Existing access rules were preserved. No recursive ownership changes or sandbox disabling were used. The next ordinary sandboxed command succeeded, including `python scripts/test_mcp_servers.py --skip-docker` (wiki, repo, Oracle all OK). Python 3.13.3, Node 22.15.0, .NET SDK 9.0.312 and Git 2.49.0 were available.

Live read-only Oracle checks confirmed Oracle 19c Enterprise Edition, DB `ORCL`, service `orcl`, schema/user `RABAEV`. This differs from the historical 11g-family recommendation in [[concepts/oracle_environment]]. The schema contained 59 invalid objects (51 functions, seven package bodies, one view), including `RRL_CUSTOMER_ORDER_API` body and `RRL_V_AVAILABLE_STS`; connectivity does not prove those paths are operational. No Oracle objects were changed. Docker/routing, API startup and migration execution were not checked by this recovery.
