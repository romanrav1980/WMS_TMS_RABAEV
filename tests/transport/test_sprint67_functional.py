"""Sprint 67: Amber row for unready STs in trip detail table."""
import pytest


def test_unready_class_applied_in_task_st_row():
    src = open(
        "admin/wms_admin_frontend/src/components/TransportDispatchPage.tsx",
        encoding="utf-8",
    ).read()
    idx = src.index("function TaskStTableRow")
    snippet = src[idx : idx + 3500]
    assert "dispatch-gr-unready" in snippet, "unready CSS class not applied in TaskStTableRow"
    assert "VERIFY_PERC < 100" in snippet, "unready condition not checked"


def test_unready_css_defined():
    css = open(
        "admin/wms_admin_frontend/src/styles.css",
        encoding="utf-8",
    ).read()
    assert ".dispatch-gr-unready" in css, "unready CSS class not defined in styles.css"


def test_typescript_compiles():
    from tests.support.frontend_checks import run_tsc_no_emit
    r = run_tsc_no_emit()
    assert r.returncode == 0, f"TypeScript errors:\n{r.stdout}\n{r.stderr}"
