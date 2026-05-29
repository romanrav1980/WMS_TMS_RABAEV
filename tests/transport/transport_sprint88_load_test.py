"""Cross-platform no-mutation load gate for Sprint 88.

Run from the repository root with Python on Windows or Linux-like systems.
It measures the dispatcher read context for the sprint feature without requiring
Locust or mutating Oracle data.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from support.transport_load_runner import run_read_gate  # noqa: E402


if __name__ == "__main__":
    raise SystemExit(run_read_gate(88, include_task_sts=True))