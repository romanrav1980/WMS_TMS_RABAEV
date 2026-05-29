from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[2]

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


def json_default(value: object) -> str:
    return str(value)


def read_text(path: Path, max_chars: int | None = None) -> str:
    text = path.read_text(encoding="utf-8", errors="replace")
    if max_chars is not None and len(text) > max_chars:
        return text[:max_chars] + "\n...[truncated]"
    return text


def safe_path(raw_path: str) -> Path:
    path = (ROOT / raw_path).resolve()
    if ROOT not in path.parents and path != ROOT:
        raise ValueError(f"path is outside repository: {raw_path}")
    if not path.exists():
        raise FileNotFoundError(raw_path)
    return path


def as_text(value: object) -> list[dict[str, str]]:
    if isinstance(value, str):
        text = value
    else:
        text = json.dumps(value, ensure_ascii=False, indent=2, default=json_default)
    return [{"type": "text", "text": text}]


def schema(properties: dict[str, Any], required: list[str] | None = None) -> dict[str, Any]:
    return {
        "type": "object",
        "properties": properties,
        "required": required or [],
        "additionalProperties": False,
    }


class Tool:
    def __init__(self, name: str, description: str, input_schema: dict[str, Any], handler: Callable[[dict[str, Any]], object]):
        self.name = name
        self.description = description
        self.input_schema = input_schema
        self.handler = handler

    def descriptor(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "inputSchema": self.input_schema,
        }


class StdioMcpServer:
    def __init__(self, name: str, tools: list[Tool]):
        self.name = name
        self.tools = {tool.name: tool for tool in tools}

    def send(self, payload: dict[str, Any]) -> None:
        sys.stdout.write(json.dumps(payload, ensure_ascii=False, default=json_default) + "\n")
        sys.stdout.flush()

    def result(self, request_id: object, value: object) -> None:
        self.send({"jsonrpc": "2.0", "id": request_id, "result": value})

    def error(self, request_id: object, code: int, message: str) -> None:
        self.send({"jsonrpc": "2.0", "id": request_id, "error": {"code": code, "message": message}})

    def handle(self, message: dict[str, Any]) -> None:
        method = message.get("method")
        request_id = message.get("id")
        if method == "initialize":
            self.result(
                request_id,
                {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": self.name, "version": "0.1.0"},
                },
            )
        elif method == "tools/list":
            self.result(request_id, {"tools": [tool.descriptor() for tool in self.tools.values()]})
        elif method == "tools/call":
            params = message.get("params") or {}
            tool_name = params.get("name")
            args = params.get("arguments") or {}
            tool = self.tools.get(tool_name)
            if not tool:
                self.error(request_id, -32602, f"unknown tool: {tool_name}")
                return
            try:
                value = tool.handler(args)
                self.result(request_id, {"content": as_text(value), "isError": False})
            except Exception as exc:  # noqa: BLE001
                self.result(request_id, {"content": as_text(f"{type(exc).__name__}: {exc}"), "isError": True})
        elif method and request_id is not None:
            self.error(request_id, -32601, f"unsupported method: {method}")

    def serve(self) -> None:
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            try:
                self.handle(json.loads(line))
            except Exception as exc:  # noqa: BLE001
                self.error(None, -32700, f"invalid message: {exc}")


def markdown_files() -> list[Path]:
    roots = [ROOT / "wiki", ROOT / "AGENTS.md", ROOT / "CLAUDE.md"]
    files: list[Path] = []
    for item in roots:
        if item.is_file():
            files.append(item)
        elif item.is_dir():
            files.extend(item.rglob("*.md"))
    return [path for path in files if ".git" not in path.parts]


def wiki_search(args: dict[str, Any]) -> object:
    query = str(args["query"]).strip()
    limit = int(args.get("limit") or 8)
    terms = [term.lower() for term in re.findall(r"[\wА-Яа-яЁё-]+", query) if len(term) > 1]
    results = []
    for path in markdown_files():
        text = read_text(path)
        lower = text.lower()
        score = sum(lower.count(term) for term in terms)
        if score <= 0:
            continue
        first = min((lower.find(term) for term in terms if lower.find(term) >= 0), default=0)
        start = max(0, first - 220)
        end = min(len(text), first + 420)
        results.append(
            {
                "path": str(path.relative_to(ROOT)).replace("\\", "/"),
                "score": score,
                "snippet": text[start:end].replace("\n", " ").strip(),
            }
        )
    return sorted(results, key=lambda item: item["score"], reverse=True)[:limit]


def wiki_read(args: dict[str, Any]) -> object:
    path = safe_path(str(args["path"]))
    if path.suffix.lower() != ".md":
        raise ValueError("wiki_read only reads markdown files")
    return {"path": str(path.relative_to(ROOT)).replace("\\", "/"), "text": read_text(path, int(args.get("max_chars") or 12000))}


def wiki_recent_log(args: dict[str, Any]) -> object:
    limit = int(args.get("limit") or 5)
    text = read_text(ROOT / "wiki" / "log.md")
    sections = re.split(r"(?m)^## ", text)
    entries = ["## " + section.strip() for section in sections[1:] if section.strip()]
    return entries[-limit:]


def repo_search(args: dict[str, Any]) -> object:
    query = str(args["query"])
    limit = int(args.get("limit") or 50)
    glob = args.get("glob")
    command = ["rg", "-n", "--hidden", "-S", query, str(ROOT)]
    if glob:
        command.extend(["-g", str(glob)])
    command.extend(["-g", "!.git", "-g", "!node_modules", "-g", "!runtime", "-g", "!*.png", "-g", "!*.jpg"])
    proc = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=20)
    lines = [line for line in proc.stdout.splitlines() if line.strip()]
    return {"matches": lines[:limit], "truncated": len(lines) > limit, "returncode": proc.returncode}


def repo_files(args: dict[str, Any]) -> object:
    pattern = str(args.get("pattern") or "")
    limit = int(args.get("limit") or 200)
    proc = subprocess.run(["rg", "--files"], cwd=ROOT, capture_output=True, text=True, timeout=20)
    files = [line.replace("\\", "/") for line in (proc.stdout or "").splitlines()]
    if pattern:
        needle = pattern.lower()
        files = [file for file in files if needle in file.lower()]
    return files[:limit]


def repo_read(args: dict[str, Any]) -> object:
    path = safe_path(str(args["path"]))
    start = int(args.get("start_line") or 1)
    end = args.get("end_line")
    end_line = int(end) if end else start + int(args.get("line_count") or 120) - 1
    lines = read_text(path).splitlines()
    selected = lines[max(0, start - 1) : min(len(lines), end_line)]
    return {
        "path": str(path.relative_to(ROOT)).replace("\\", "/"),
        "start_line": start,
        "end_line": start + len(selected) - 1,
        "text": "\n".join(f"{idx + start}: {line}" for idx, line in enumerate(selected)),
    }


def oracle_connection():
    try:
        import oracledb  # type: ignore
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError("python-oracledb is not installed") from exc
    return oracledb.connect(
        user=os.getenv("WMS_ORACLE_USER", "RABAEV"),
        password=os.getenv("WMS_ORACLE_PASSWORD", "RABAEVWMS"),
        dsn=os.getenv("WMS_ORACLE_DSN", "127.0.0.1:1521/orcl"),
    )


def oracle_table_columns(args: dict[str, Any]) -> object:
    table = str(args["table"]).upper()
    owner = str(args.get("owner") or "RABAEV").upper()
    with oracle_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT column_id, column_name, data_type, data_length, data_precision, data_scale, nullable
                 FROM all_tab_columns
                 WHERE owner = :p_owner AND table_name = :p_table
                 ORDER BY column_id
                """,
                p_owner=owner,
                p_table=table,
            )
            return [
                {
                    "column_id": row[0],
                    "column_name": row[1],
                    "data_type": row[2],
                    "data_length": row[3],
                    "data_precision": row[4],
                    "data_scale": row[5],
                    "nullable": row[6],
                }
                for row in cur.fetchall()
            ]


def oracle_find_column(args: dict[str, Any]) -> object:
    column = str(args["column"]).upper()
    owner = str(args.get("owner") or "RABAEV").upper()
    with oracle_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT owner, table_name, column_name, data_type
                 FROM all_tab_columns
                 WHERE owner = :p_owner AND column_name LIKE :p_column
                 ORDER BY table_name, column_id
                """,
                p_owner=owner,
                p_column=column,
            )
            return [
                {"owner": row[0], "table_name": row[1], "column_name": row[2], "data_type": row[3]}
                for row in cur.fetchall()
            ]


def oracle_readonly_query(args: dict[str, Any]) -> object:
    sql = str(args["sql"]).strip()
    if not re.match(r"^(select|with)\b", sql, re.I) or ";" in sql:
        raise ValueError("only one read-only SELECT/WITH statement without semicolon is allowed")
    limit = min(int(args.get("limit") or 50), 200)
    with oracle_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
            columns = [item[0] for item in cur.description or []]
            rows = cur.fetchmany(limit)
            return {"columns": columns, "rows": [dict(zip(columns, row)) for row in rows], "limit": limit}


def http_probe(url: str, timeout: int = 5) -> dict[str, Any]:
    started = Request(url, headers={"User-Agent": "tms-mcp-routing/0.1"})
    with urlopen(started, timeout=timeout) as response:
        body = response.read(240).decode("utf-8", errors="replace")
        return {"url": url, "status": response.status, "body_prefix": body}


def docker_routing_status(args: dict[str, Any]) -> object:
    osrm_url = str(args.get("osrm_url") or "http://127.0.0.1:5000/route/v1/driving/60.5975,56.8389;60.6122,56.8519?overview=false")
    valhalla_url = str(args.get("valhalla_url") or "http://127.0.0.1:8002/status")
    result: dict[str, Any] = {}
    for name, url in (("osrm", osrm_url), ("valhalla", valhalla_url)):
        try:
            result[name] = http_probe(url)
        except Exception as exc:  # noqa: BLE001
            result[name] = {"url": url, "error": f"{type(exc).__name__}: {exc}"}
    return result


def docker_compose_ps(args: dict[str, Any]) -> object:
    compose = str(args.get("compose") or "docker-compose.osrm.yml")
    safe_path(compose)
    proc = subprocess.run(["docker", "compose", "-f", compose, "ps"], cwd=ROOT, capture_output=True, text=True, timeout=20)
    return {"returncode": proc.returncode, "stdout": proc.stdout, "stderr": proc.stderr}


def docker_compose_config(args: dict[str, Any]) -> object:
    compose = str(args["compose"])
    safe_path(compose)
    proc = subprocess.run(["docker", "compose", "-f", compose, "config"], cwd=ROOT, capture_output=True, text=True, timeout=20)
    return {"returncode": proc.returncode, "stdout": proc.stdout[-12000:], "stderr": proc.stderr}


def build_tools(kind: str) -> list[Tool]:
    if kind == "wiki":
        return [
            Tool("wiki_search", "Search maintained wiki pages and agent onramp files.", schema({"query": {"type": "string"}, "limit": {"type": "integer"}}, ["query"]), wiki_search),
            Tool("wiki_read", "Read a markdown wiki/onramp page by repository-relative path.", schema({"path": {"type": "string"}, "max_chars": {"type": "integer"}}, ["path"]), wiki_read),
            Tool("wiki_recent_log", "Return recent sections from wiki/log.md.", schema({"limit": {"type": "integer"}}), wiki_recent_log),
        ]
    if kind == "repo":
        return [
            Tool("repo_search", "Search repository text with ripgrep and compact results.", schema({"query": {"type": "string"}, "glob": {"type": "string"}, "limit": {"type": "integer"}}, ["query"]), repo_search),
            Tool("repo_files", "List repository files, optionally filtered by a substring.", schema({"pattern": {"type": "string"}, "limit": {"type": "integer"}}), repo_files),
            Tool("repo_read", "Read a bounded line range from a repository file.", schema({"path": {"type": "string"}, "start_line": {"type": "integer"}, "end_line": {"type": "integer"}, "line_count": {"type": "integer"}}, ["path"]), repo_read),
        ]
    if kind == "oracle":
        return [
            Tool("oracle_table_columns", "Read Oracle table columns from ALL_TAB_COLUMNS.", schema({"table": {"type": "string"}, "owner": {"type": "string"}}, ["table"]), oracle_table_columns),
            Tool("oracle_find_column", "Find Oracle tables containing a column name or LIKE pattern.", schema({"column": {"type": "string"}, "owner": {"type": "string"}}, ["column"]), oracle_find_column),
            Tool("oracle_readonly_query", "Run a bounded read-only SELECT/WITH query.", schema({"sql": {"type": "string"}, "limit": {"type": "integer"}}, ["sql"]), oracle_readonly_query),
        ]
    if kind == "docker":
        return [
            Tool("routing_status", "Probe local OSRM and Valhalla routing endpoints.", schema({"osrm_url": {"type": "string"}, "valhalla_url": {"type": "string"}}), docker_routing_status),
            Tool("docker_compose_ps", "Run docker compose ps for a routing compose file.", schema({"compose": {"type": "string"}}), docker_compose_ps),
            Tool("docker_compose_config", "Validate and print compact docker compose config.", schema({"compose": {"type": "string"}}, ["compose"]), docker_compose_config),
        ]
    raise ValueError(f"unknown server kind: {kind}")


def main() -> int:
    parser = argparse.ArgumentParser(description="TMS project MCP stdio server.")
    parser.add_argument("--server", choices=["wiki", "repo", "oracle", "docker"], required=True)
    args = parser.parse_args()
    StdioMcpServer(f"tms-{args.server}", build_tools(args.server)).serve()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
