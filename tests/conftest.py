from __future__ import annotations

import os


def pytest_sessionfinish(session, exitstatus):  # type: ignore[no-untyped-def]
    if os.environ.get("TMS_FAIL_ON_SKIPS") != "1":
        return
    skipped = session.config.pluginmanager.get_plugin("terminalreporter").stats.get("skipped", [])
    if skipped:
        session.exitstatus = 1
