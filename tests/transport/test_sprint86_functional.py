"""Sprint 86: CSV export for routes tab trips table."""


def _src():
    return open(
        "admin/wms_admin_frontend/src/components/TransportDispatchPage.tsx",
        encoding="utf-8",
    ).read()


def test_export_routes_csv_function_exists():
    src = _src()
    assert "function exportRoutesCsv" in src


def test_export_routes_csv_header_fields():
    src = _src()
    idx = src.index("function exportRoutesCsv")
    snippet = src[idx : idx + 800]
    assert "Дата" in snippet
    assert "Машина" in snippet
    assert "Паллет" in snippet or "Пал." in snippet
    assert "Статус" in snippet


def test_csv_button_in_routes_toolbar():
    src = _src()
    idx = src.index("dispatch-routes-table-wrap")
    # button must be in toolbar which is before the table
    toolbar_region = src[max(0, idx - 2000) : idx]
    assert "exportRoutesCsv" in toolbar_region


def test_csv_button_disabled_when_empty():
    src = _src()
    idx = src.index("exportRoutesCsv")
    snippet = src[max(0, idx - 200) : idx + 200]
    assert "searchedRouteTasks.length === 0" in snippet or "disabled" in snippet


def test_csv_filename_contains_date():
    src = _src()
    idx = src.index("function exportRoutesCsv")
    snippet = src[idx : idx + 1200]
    assert "routes-" in snippet
    assert ".csv" in snippet
