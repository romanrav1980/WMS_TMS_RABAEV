from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SERVER = ROOT / "tools" / "mcp" / "tms_mcp_server.py"


def rpc(proc: subprocess.Popen[str], payload: dict) -> dict:
    assert proc.stdin is not None
    assert proc.stdout is not None
    proc.stdin.write(json.dumps(payload, ensure_ascii=False) + "\n")
    proc.stdin.flush()
    line = proc.stdout.readline()
    if not line:
        raise RuntimeError("MCP server closed stdout")
    return json.loads(line)


def check_server(kind: str) -> None:
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    proc = subprocess.Popen(
        [sys.executable, str(SERVER), "--server", kind],
        cwd=ROOT,
        env=env,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
    )
    try:
        init = rpc(proc, {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}})
        if "result" not in init:
            raise RuntimeError(f"initialize failed: {init}")
        tools = rpc(proc, {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}})
        names = [tool["name"] for tool in tools["result"]["tools"]]
        if not names:
            raise RuntimeError(f"no tools listed for {kind}")
        smoke_tool, smoke_args = {
            "wiki": ("wiki_search", {"query": "TMS-2 Sprint 60", "limit": 2}),
            "repo": ("repo_files", {"pattern": "TransportDispatchPage", "limit": 5}),
            "oracle": ("oracle_table_columns", {"table": "RRL_TRANSPORT_TASK"}),
            "docker": ("routing_status", {}),
        }[kind]
        call = rpc(
            proc,
            {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {"name": smoke_tool, "arguments": smoke_args},
            },
        )
        result = call.get("result") or {}
        if result.get("isError"):
            raise RuntimeError(f"{kind}.{smoke_tool} returned MCP error: {result}")
        print(f"{kind}: OK tools={', '.join(names)}")
    finally:
        proc.kill()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-oracle", action="store_true", help="Skip live Oracle smoke.")
    parser.add_argument("--skip-docker", action="store_true", help="Skip live routing smoke.")
    args = parser.parse_args()

    kinds = ["wiki", "repo"]
    if not args.skip_oracle:
        kinds.append("oracle")
    if not args.skip_docker:
        kinds.append("docker")
    for kind in kinds:
        check_server(kind)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
