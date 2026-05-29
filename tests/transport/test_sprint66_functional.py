"""Sprint 66: VERIFY_PERC column in trip detail table (TaskStTableRow)"""
import pytest


def test_verify_perc_column_in_header():
    """Header has % column in task-tab trip detail table."""
    import subprocess, re
    src = open(
        "admin/wms_admin_frontend/src/components/TransportDispatchPage.tsx",
        encoding="utf-8",
    ).read()
    # Find the tasks-tab trip-detail thead block
    block = re.search(
        r"dispatch-trip-sts-wrap.*?</thead>",
        src,
        re.DOTALL,
    )
    assert block, "dispatch-trip-sts-wrap block not found"
    assert "% сборки" in block.group(0), "% column header missing"


def test_verify_perc_cell_in_task_st_row():
    """TaskStTableRow renders VerifyBar for VERIFY_PERC."""
    src = open(
        "admin/wms_admin_frontend/src/components/TransportDispatchPage.tsx",
        encoding="utf-8",
    ).read()
    # After the weight cell in TaskStTableRow, VerifyBar must appear
    idx = src.index("function TaskStTableRow")
    snippet = src[idx : idx + 3000]
    assert "VERIFY_PERC" in snippet, "VERIFY_PERC not referenced in TaskStTableRow"
    assert "VerifyBar" in snippet, "VerifyBar not used in TaskStTableRow"


def test_colspan_updated():
    """Empty-state colspan matches column count (12)."""
    src = open(
        "admin/wms_admin_frontend/src/components/TransportDispatchPage.tsx",
        encoding="utf-8",
    ).read()
    assert 'colSpan={12}' in src, "colSpan should be 12 in tasks-tab trip table"


def test_typescript_compiles():
    from tests.support.frontend_checks import run_tsc_no_emit
    r = run_tsc_no_emit()
    assert r.returncode == 0, f"TypeScript errors:\n{r.stdout}\n{r.stderr}"
