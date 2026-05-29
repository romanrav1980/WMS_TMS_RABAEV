"""Sprint 73: Логист column in tasks-tab trips table."""
import pytest


def test_logist_in_header():
    src = open(
        "admin/wms_admin_frontend/src/components/TransportDispatchPage.tsx",
        encoding="utf-8",
    ).read()
    # The header array for tasks-tab trips table must include LOGIST
    idx = src.index('"LOGIST:Логист"')
    assert idx > 0, "LOGIST column not in header array"


def test_logist_in_row():
    src = open(
        "admin/wms_admin_frontend/src/components/TransportDispatchPage.tsx",
        encoding="utf-8",
    ).read()
    assert "task.LOGIST" in src, "task.LOGIST not rendered in row"


def test_colspan_updated_for_logist_column():
    src = open(
        "admin/wms_admin_frontend/src/components/TransportDispatchPage.tsx",
        encoding="utf-8",
    ).read()
    # The tasks-tab trips table empty-state has LOGIST included, so colspan is 15.
    assert 'colSpan={15}' in src, "colSpan not updated for LOGIST column"


def test_typescript_compiles():
    from tests.support.frontend_checks import run_tsc_no_emit
    r = run_tsc_no_emit()
    assert r.returncode == 0, f"TypeScript errors:\n{r.stdout}\n{r.stderr}"
