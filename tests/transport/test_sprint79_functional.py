"""Sprint 79: ТК column in tasks-tab trips table (§3.8.1 ТЗ)."""
import pytest


def test_tk_name_in_header():
    src = open(
        "admin/wms_admin_frontend/src/components/TransportDispatchPage.tsx",
        encoding="utf-8",
    ).read()
    assert '"TK_NAME:ТК"' in src, "TK_NAME column not in header array"


def test_tk_name_in_row():
    src = open(
        "admin/wms_admin_frontend/src/components/TransportDispatchPage.tsx",
        encoding="utf-8",
    ).read()
    # In the tasks-tab trips table row
    assert "task.TK_NAME" in src


def test_colspan_15():
    src = open(
        "admin/wms_admin_frontend/src/components/TransportDispatchPage.tsx",
        encoding="utf-8",
    ).read()
    assert 'colSpan={15}' in src, "colSpan should be 15 after adding ТК"


def test_typescript_compiles():
    from tests.support.frontend_checks import run_tsc_no_emit
    r = run_tsc_no_emit()
    assert r.returncode == 0, f"TypeScript errors:\n{r.stdout}\n{r.stderr}"
