"""Sprint 76: VOLUME_M3 column in trip detail table (TaskStTableRow)."""
import pytest


def test_volume_column_in_header():
    src = open(
        "admin/wms_admin_frontend/src/components/TransportDispatchPage.tsx",
        encoding="utf-8",
    ).read()
    idx = src.index("dispatch-trip-sts-wrap")
    snippet = src[idx : idx + 800]
    assert "Объём" in snippet, "Объём header missing"


def test_volume_cell_in_task_st_row():
    src = open(
        "admin/wms_admin_frontend/src/components/TransportDispatchPage.tsx",
        encoding="utf-8",
    ).read()
    idx = src.index("function TaskStTableRow")
    snippet = src[idx : idx + 3500]
    assert "VOLUME_M3" in snippet, "VOLUME_M3 not in TaskStTableRow"
    assert "toFixed(2)" in snippet, "volume not formatted to 2 decimals"


def test_colspan_13():
    src = open(
        "admin/wms_admin_frontend/src/components/TransportDispatchPage.tsx",
        encoding="utf-8",
    ).read()
    assert 'colSpan={13}' in src, "colSpan should be 13 after adding volume"


def test_typescript_compiles():
    import subprocess
    r = subprocess.run(
        ["npx", "tsc", "--noEmit"],
        cwd="admin/wms_admin_frontend",
        capture_output=True,
        text=True,
    )
    assert r.returncode == 0, f"TypeScript errors:\n{r.stdout}\n{r.stderr}"
