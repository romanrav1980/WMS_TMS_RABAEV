"""Sprint 75: V= (volume m³) added to trip summary in header."""
import pytest


def test_trip_volume_computed():
    src = open(
        "admin/wms_admin_frontend/src/components/TransportDispatchPage.tsx",
        encoding="utf-8",
    ).read()
    assert "tripV" in src, "tripV not computed"
    assert "VOLUME_M3" in src[src.index("tripV"):src.index("tripV") + 80]


def test_trip_volume_displayed_in_header():
    src = open(
        "admin/wms_admin_frontend/src/components/TransportDispatchPage.tsx",
        encoding="utf-8",
    ).read()
    assert "tripV.toFixed(2)" in src, "tripV not shown in header"
    assert src.count("tripV.toFixed(2)") >= 2, "tripV not shown in both tabs"


def test_typescript_compiles():
    from tests.support.frontend_checks import run_tsc_no_emit
    r = run_tsc_no_emit()
    assert r.returncode == 0, f"TypeScript errors:\n{r.stdout}\n{r.stderr}"
