from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import queue
import subprocess
import sys
import threading

ROOT = Path(__file__).resolve().parents[1]
SERVER = ROOT / 'tools' / 'mcp' / 'tms_mcp_server.py'


def rpc(proc: subprocess.Popen[str], payload: dict, timeout: float = 30) -> dict:
    assert proc.stdin is not None and proc.stdout is not None
    proc.stdin.write(json.dumps(payload, ensure_ascii=False) + '\n')
    proc.stdin.flush()
    received: queue.Queue[str] = queue.Queue(maxsize=1)
    threading.Thread(target=lambda: received.put(proc.stdout.readline()), daemon=True).start()
    try:
        line = received.get(timeout=timeout)
    except queue.Empty as exc:
        raise TimeoutError(f'MCP request timed out after {timeout}s') from exc
    if not line:
        raise RuntimeError('MCP server closed stdout')
    reply = json.loads(line)
    if reply.get('id') != payload['id'] or 'error' in reply:
        raise RuntimeError(f'Unexpected MCP response: {reply}')
    return reply


def routing_health(result: dict) -> dict[str, bool]:
    return {name: isinstance(result.get(name), dict)
            and result[name].get('status') == 200 and not result[name].get('error')
            for name in ('osrm', 'valhalla')}


def check_server(kind: str, timeout: float = 30) -> dict:
    env = os.environ.copy()
    env['PYTHONIOENCODING'] = 'utf-8'
    command = [sys.executable, str(SERVER), '--server', kind]
    if kind == 'playwright':
        entry = ROOT / 'admin/wms_admin_frontend/node_modules/playwright-core/lib/entry/mcp.js'
        if not entry.is_file():
            raise FileNotFoundError('Install frontend dependencies before Playwright MCP smoke')
        command = ['node', str(entry), '--headless', '--isolated']
    proc = subprocess.Popen(command, cwd=ROOT,
                            env=env, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                            stderr=subprocess.DEVNULL, text=True, encoding='utf-8')
    try:
        init = rpc(proc, {'jsonrpc': '2.0', 'id': 1, 'method': 'initialize', 'params': {'protocolVersion': '2024-11-05', 'capabilities': {}, 'clientInfo': {'name': 'nicora-tooling-smoke', 'version': '1.0.0'}}}, timeout)
        if 'result' not in init:
            raise RuntimeError(f'initialize failed for {kind}')
        assert proc.stdin is not None
        proc.stdin.write(json.dumps({'jsonrpc': '2.0', 'method': 'notifications/initialized'}) + '\n')
        proc.stdin.flush()
        listing = rpc(proc, {'jsonrpc': '2.0', 'id': 2, 'method': 'tools/list', 'params': {}}, timeout)
        names = {item['name'] for item in listing.get('result', {}).get('tools', [])}
        tool, arguments = {
            'wiki': ('wiki_read', {'path': 'wiki/requirements/nikora_delivery_v55/README.md', 'max_chars': 800}),
            'repo': ('repo_files', {'pattern': 'TransportDispatchPage', 'limit': 5}),
            'oracle': ('oracle_readonly_query', {'sql': "SELECT USER AS SESSION_USER, SYS_CONTEXT('USERENV','DB_NAME') AS DB_NAME FROM DUAL", 'limit': 1}),
            'docker': ('routing_status', {}),
            'playwright': ('browser_tabs', {'action': 'list'}),
        }[kind]
        if tool not in names:
            raise RuntimeError(f'{kind}: expected tool {tool} is not registered')
        reply = rpc(proc, {'jsonrpc': '2.0', 'id': 3, 'method': 'tools/call',
                           'params': {'name': tool, 'arguments': arguments}}, timeout)
        result = reply.get('result') or {}
        if result.get('isError'):
            raise RuntimeError(f'{kind}.{tool} failed: {result}')
        text = next((block['text'] for block in result.get('content', []) if block.get('type') == 'text'), '')
        if not text:
            raise RuntimeError(f'{kind}.{tool} returned no evidence')
        report = {'mcp': 'ok', 'tool': tool}
        if kind == 'docker':
            report['endpoints'] = routing_health(json.loads(text))
        elif kind == 'oracle':
            rows = json.loads(text).get('rows', [])
            if not rows:
                raise RuntimeError('Oracle DUAL query returned no row')
            report['connection'] = rows[0]
        return report
    finally:
        if proc.stdin:
            proc.stdin.close()
        try:
            proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=5)
        for pipe in (proc.stdin, proc.stdout):
            if pipe and not pipe.closed:
                pipe.close()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--skip-oracle', action='store_true')
    parser.add_argument('--skip-docker', action='store_true')
    parser.add_argument('--skip-playwright', action='store_true')
    parser.add_argument('--require-routing', action='store_true', help='Fail if OSRM/Valhalla are unavailable, not just MCP.')
    parser.add_argument('--timeout', type=float, default=30)
    parser.add_argument('--report', type=Path, help='Save actual health results as JSON.')
    args = parser.parse_args()
    if args.timeout <= 0 or (args.require_routing and args.skip_docker):
        parser.error('timeout must be positive; require-routing cannot skip docker')
    kinds = ['wiki', 'repo'] + ([] if args.skip_oracle else ['oracle']) + ([] if args.skip_docker else ['docker']) + ([] if args.skip_playwright else ['playwright'])
    reports = {}
    failed = False
    for kind in kinds:
        try:
            reports[kind] = check_server(kind, args.timeout)
            print(f'{kind}: MCP OK')
            if kind == 'docker':
                health = reports[kind]['endpoints']
                print('routing endpoints: ' + ', '.join(f'{name}={"reachable" if ok else "unavailable"}' for name, ok in health.items()))
                if args.require_routing and not all(health.values()):
                    failed = True
        except Exception as exc:
            failed = True
            reports[kind] = {'mcp': 'failed', 'error': str(exc)}
            print(f'{kind}: FAILED {type(exc).__name__}: {exc}')
    output = {'servers': reports, 'require_routing': args.require_routing,
              'skipped': [name for name, skip in [('oracle', args.skip_oracle), ('docker', args.skip_docker), ('playwright', args.skip_playwright)] if skip],
              'passed': not failed}
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(output, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return int(failed)


if __name__ == '__main__':
    raise SystemExit(main())
