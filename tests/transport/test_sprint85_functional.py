"""Sprint 85: Routes tab summary strip (Рейсов / Пал. / Вес / Отгружено)."""


def _src():
    return open(
        "admin/wms_admin_frontend/src/components/TransportDispatchPage.tsx",
        encoding="utf-8",
    ).read()


def _css():
    return open(
        "admin/wms_admin_frontend/src/styles.css",
        encoding="utf-8",
    ).read()


def test_routes_summary_jsx_present():
    src = _src()
    assert "dispatch-routes-summary" in src, "dispatch-routes-summary JSX missing"


def test_routes_summary_shows_trip_count():
    src = _src()
    idx = src.index("dispatch-routes-summary")
    snippet = src[idx : idx + 400]
    assert "searchedRouteTasks.length" in snippet


def test_routes_summary_computed_values():
    src = _src()
    assert "routeTotalPallets" in src
    assert "routeTotalWeight" in src
    assert "routeClosedCount" in src


def test_routes_summary_aggregates_correct_fields():
    src = _src()
    assert "PALLET_COUNT" in src
    idx = src.index("routeTotalPallets")
    snippet = src[idx : idx + 200]
    assert "PALLET_COUNT" in snippet


def test_routes_summary_css():
    css = _css()
    assert ".dispatch-routes-summary" in css
