"""Offline NICORA quality gate; no Oracle mutations or live service requirements."""
from __future__ import annotations
import argparse
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def run(command: list[str], cwd: Path = ROOT) -> None:
    print('+ ' + ' '.join(command), flush=True)
    subprocess.run(command, cwd=cwd, check=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--skip-typecheck', action='store_true', help='Partial gate only; not a complete quality pass.')
    args = parser.parse_args()
    run([sys.executable, 'scripts/check_architecture.py'])
    run([sys.executable, '-m', 'pytest', 'tests/architecture', 'tests/tooling', '-q',
         '-o', 'cache_dir=tmp/nicora_quality/pytest-cache'])
    if args.skip_typecheck:
        print('PARTIAL: frontend type checks explicitly skipped.')
    else:
        for project in ('admin/wms_admin_frontend', 'terminal/wms_terminal_web'):
            run(['node', str(ROOT / project / 'node_modules/typescript/bin/tsc'), '--noEmit'], ROOT / project)
        print('NICORA quality gate: PASS')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
