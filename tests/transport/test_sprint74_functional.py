"""Sprint 74: Collapse/expand trip detail STs section."""
import pytest


def test_collapse_state_defined():
    src = open(
        "admin/wms_admin_frontend/src/components/TransportDispatchPage.tsx",
        encoding="utf-8",
    ).read()
    assert "tripDetailCollapsed" in src, "tripDetailCollapsed state missing"
    assert "setTripDetailCollapsed" in src


def test_collapse_button_present():
    src = open(
        "admin/wms_admin_frontend/src/components/TransportDispatchPage.tsx",
        encoding="utf-8",
    ).read()
    assert "dispatch-trip-collapse-btn" in src
    assert "Sprint 74" in src


def test_collapse_wraps_sts_section():
    src = open(
        "admin/wms_admin_frontend/src/components/TransportDispatchPage.tsx",
        encoding="utf-8",
    ).read()
    idx = src.index("Sprint 74 — collapsible STs section")
    snippet = src[idx : idx + 200]
    assert "tripDetailCollapsed" in snippet, "collapse guard not wrapping STs section"


def test_collapse_css_defined():
    css = open(
        "admin/wms_admin_frontend/src/styles.css",
        encoding="utf-8",
    ).read()
    assert ".dispatch-trip-collapse-btn" in css


def test_typescript_compiles():
    from tests.support.frontend_checks import run_tsc_no_emit
    r = run_tsc_no_emit()
    assert r.returncode == 0, f"TypeScript errors:\n{r.stdout}\n{r.stderr}"
