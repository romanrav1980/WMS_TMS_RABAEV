"""Sprint 77: Export trip STs to CSV."""
import pytest


def test_export_function_defined():
    src = open(
        "admin/wms_admin_frontend/src/components/TransportDispatchPage.tsx",
        encoding="utf-8",
    ).read()
    assert "function exportTaskStsCsv" in src


def test_export_button_in_toolbar():
    src = open(
        "admin/wms_admin_frontend/src/components/TransportDispatchPage.tsx",
        encoding="utf-8",
    ).read()
    assert "dispatch-trip-csv-btn" in src
    assert "exportTaskStsCsv" in src


def test_export_uses_filtered_sts():
    src = open(
        "admin/wms_admin_frontend/src/components/TransportDispatchPage.tsx",
        encoding="utf-8",
    ).read()
    # The button must use filteredTaskSts (respects the inline filter)
    idx = src.index("Sprint 77 — export trip STs")
    snippet = src[idx : idx + 200]
    assert "filteredTaskSts" in snippet, "export should use filtered STs"


def test_export_css_defined():
    css = open(
        "admin/wms_admin_frontend/src/styles.css",
        encoding="utf-8",
    ).read()
    assert ".dispatch-trip-csv-btn" in css


def test_typescript_compiles():
    from tests.support.frontend_checks import run_tsc_no_emit
    r = run_tsc_no_emit()
    assert r.returncode == 0, f"TypeScript errors:\n{r.stdout}\n{r.stderr}"
