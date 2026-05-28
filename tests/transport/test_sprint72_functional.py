"""Sprint 72: Inline filter within trip detail STs table."""
import pytest


def test_trip_st_filter_state():
    src = open(
        "admin/wms_admin_frontend/src/components/TransportDispatchPage.tsx",
        encoding="utf-8",
    ).read()
    assert "tripStFilter" in src, "tripStFilter state missing"
    assert "filteredTaskSts" in src, "filteredTaskSts computed var missing"


def test_filtered_task_sts_logic():
    src = open(
        "admin/wms_admin_frontend/src/components/TransportDispatchPage.tsx",
        encoding="utf-8",
    ).read()
    idx = src.index("Sprint 72 — filter within trip detail")
    snippet = src[idx : idx + 400]
    assert "tripStFilter" in snippet
    assert "toLowerCase()" in snippet, "case-insensitive filter missing"


def test_filter_input_in_toolbar():
    src = open(
        "admin/wms_admin_frontend/src/components/TransportDispatchPage.tsx",
        encoding="utf-8",
    ).read()
    assert "dispatch-trip-filter-input" in src, "filter input class missing"
    assert "Фильтр по СТ/адресу" in src, "filter placeholder missing"


def test_filter_css_defined():
    css = open(
        "admin/wms_admin_frontend/src/styles.css",
        encoding="utf-8",
    ).read()
    assert ".dispatch-trip-filter-input" in css


def test_typescript_compiles():
    import subprocess
    r = subprocess.run(
        ["npx", "tsc", "--noEmit"],
        cwd="admin/wms_admin_frontend",
        capture_output=True,
        text=True,
    )
    assert r.returncode == 0, f"TypeScript errors:\n{r.stdout}\n{r.stderr}"
