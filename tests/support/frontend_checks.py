from __future__ import annotations

import os
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
FRONTEND_DIR = ROOT / "admin" / "wms_admin_frontend"


def tsc_command() -> list[str]:
    """Return a cross-platform local TypeScript compiler command."""
    if os.name == "nt":
        return ["cmd", "/c", r"node_modules\.bin\tsc.cmd", "--noEmit"]
    return [str(FRONTEND_DIR / "node_modules" / ".bin" / "tsc"), "--noEmit"]


def run_tsc_no_emit() -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        tsc_command(),
        cwd=FRONTEND_DIR,
        capture_output=True,
        text=True,
    )
