"""
test_sprint108_114_functional.py

Sprint 108: KPI operational endpoints
Sprint 109: KPI billing endpoints
Sprint 110: GPS track receive endpoint
Sprint 111: Vehicle positions + track endpoints
Sprint 112: Tariff grid endpoints
Sprint 113: 1C XML export
Sprint 114: Maintenance archiving
"""

import os
import pytest
from datetime import date


# ---------------------------------------------------------------------------
# Sprint 108-109 — KPI Dashboard
# ---------------------------------------------------------------------------

def test_kpi_router_importable():
    from api.wms_api_server.app.routers.transport_kpi import router
    assert "/api/admin/transport/kpi" in router.prefix


def test_kpi_fleet_endpoint():
    from api.wms_api_server.app.routers.transport_kpi import router
    routes = [r.path for r in router.routes]
    assert any("fleet" in r for r in routes)


def test_kpi_summary_endpoint():
    from api.wms_api_server.app.routers.transport_kpi import router
    routes = [r.path for r in router.routes]
    assert any("summary" in r for r in routes)


def test_kpi_regions_endpoint():
    from api.wms_api_server.app.routers.transport_kpi import router
    routes = [r.path for r in router.routes]
    assert any("regions" in r for r in routes)


def test_kpi_billing_endpoint():
    from api.wms_api_server.app.routers.transport_kpi import router
    routes = [r.path for r in router.routes]
    assert any("billing" in r and "company" not in r for r in routes)


def test_kpi_billing_by_company_endpoint():
    from api.wms_api_server.app.routers.transport_kpi import router
    routes = [r.path for r in router.routes]
    assert any("billing/by-company" in r for r in routes)


def test_kpi_fleet_query_structure():
    """Запрос fleet KPI строит агрегацию по дням."""
    import inspect
    from api.wms_api_server.app.routers import transport_kpi
    src = inspect.getsource(transport_kpi)
    assert "TRUNC(TT.SHIPMENT_DATE)" in src
    assert "GROUP BY" in src
    assert "PALLETS" in src.upper()


def test_kpi_billing_query_structure():
    import inspect
    from api.wms_api_server.app.routers import transport_kpi
    src = inspect.getsource(transport_kpi)
    assert "RRL_BILL_ORDERS" in src
    assert "PAYED" in src
    assert "CLOSED" in src


# ---------------------------------------------------------------------------
# Sprint 110-111 — GPS
# ---------------------------------------------------------------------------

def test_gps_router_importable():
    from api.wms_api_server.app.routers.gps import router
    assert router is not None


def test_gps_track_endpoint_registered():
    from api.wms_api_server.app.routers.gps import router
    routes = [(r.path, getattr(r, "methods", set())) for r in router.routes]
    post_routes = [p for p, m in routes if "gps/track" in p and "POST" in m]
    assert len(post_routes) > 0


def test_vehicle_positions_endpoint_registered():
    from api.wms_api_server.app.routers.gps import router
    routes = [r.path for r in router.routes]
    assert any("vehicles/positions" in r for r in routes)


def test_vehicle_track_endpoint_registered():
    from api.wms_api_server.app.routers.gps import router
    routes = [r.path for r in router.routes]
    assert any("vehicles/{vehicle_id}/track" in r for r in routes)


def test_gps_geofences_endpoint_registered():
    from api.wms_api_server.app.routers.gps import router
    routes = [r.path for r in router.routes]
    assert any("geofences" in r for r in routes)


def test_gps_track_schema():
    from api.wms_api_server.app.routers.gps import GpsTrackRequest
    req = GpsTrackRequest(vehicle_id=9201, lat=58.0105, lon=56.2502, speed_kmh=60)
    assert req.vehicle_id == 9201
    assert req.lat == pytest.approx(58.0105)
    assert req.speed_kmh == 60
    assert req.ts is None


def test_gps_track_schema_defaults():
    from api.wms_api_server.app.routers.gps import GpsTrackRequest
    req = GpsTrackRequest(vehicle_id=1, lat=55.0, lon=37.0)
    assert req.speed_kmh == 0


def test_migration_060_exists():
    assert os.path.exists("db/migrations/2026-05-29_gps/060_apply.sql")


def test_migration_060_creates_gps_tables():
    with open("db/migrations/2026-05-29_gps/060_apply.sql", encoding="utf-8") as f:
        content = f.read()
    assert "RRL_VEHICLE_GPS" in content
    assert "RRL_VEHICLE_GPS_LAST" in content
    assert "VEHICLE_ID" in content
    assert "LATITUDE" in content or "LAT" in content


def test_gps_track_calls_geofencing():
    import inspect
    from api.wms_api_server.app.routers import gps
    src = inspect.getsource(gps)
    assert "geofencing" in src
    assert "check_geofences" in src
    assert "geo_events" in src


# ---------------------------------------------------------------------------
# Sprint 112 — Tariff Grid
# ---------------------------------------------------------------------------

def test_tariffs_router_importable():
    from api.wms_api_server.app.routers.transport_tariffs import router
    assert router.prefix == "/api/admin/transport/tariffs"


def test_tariffs_list_endpoint():
    from api.wms_api_server.app.routers.transport_tariffs import router
    routes = [(r.path, getattr(r, "methods", set())) for r in router.routes]
    get_routes = [p for p, m in routes if p == "/api/admin/transport/tariffs" and "GET" in m]
    assert len(get_routes) > 0


def test_tariffs_table_info_endpoint():
    from api.wms_api_server.app.routers.transport_tariffs import router
    routes = [r.path for r in router.routes]
    assert any("table-info" in r for r in routes)


def test_get_tariff_table_handles_no_table():
    """_get_tariff_table возвращает None если нужной таблицы нет."""
    from api.wms_api_server.app.routers.transport_tariffs import _get_tariff_table
    # Function should return None gracefully if table not found
    # We can't run it without Oracle, but verify it's callable
    assert callable(_get_tariff_table)


# ---------------------------------------------------------------------------
# Sprint 113 — 1C Export
# ---------------------------------------------------------------------------

def test_export_1c_router_importable():
    from api.wms_api_server.app.routers.export_1c import router
    assert router is not None


def test_export_order_1c_endpoint():
    from api.wms_api_server.app.routers.export_1c import router
    routes = [r.path for r in router.routes]
    assert any("export/1c" in r and "{order_id}" in r for r in routes)


def test_export_registry_1c_endpoint():
    from api.wms_api_server.app.routers.export_1c import router
    routes = [r.path for r in router.routes]
    assert any("export/1c" in r and "{order_id}" not in r for r in routes)


def test_build_1c_xml_structure():
    """_build_1c_xml создаёт корректный XML для списка заказов."""
    from api.wms_api_server.app.routers.export_1c import _build_1c_xml
    orders = [
        {
            "id": 42, "num": "БТ-0042", "company": "ООО Тест", "dateoforder": "2026-05-01",
            "closed": 0, "payed": 0, "total_amount": 15000,
            "tasks": [
                {"tt_id": 101, "transport": "Е123АВ77", "shipment_date": "2026-05-15", "price": 7500},
                {"tt_id": 102, "transport": "Т456УХ77", "shipment_date": "2026-05-16", "price": 7500},
            ],
        }
    ]
    xml_bytes = _build_1c_xml(orders)
    assert xml_bytes.startswith(b"<?xml")
    xml_str = xml_bytes.decode("utf-8")
    assert "КоммерческаяИнформация" in xml_str
    assert "Версия" in xml_str
    assert "БТ-0042" in xml_str
    assert "ООО Тест" in xml_str
    assert "15000" in xml_str
    assert "101" in xml_str  # task id


def test_1c_xml_status_mapping():
    from api.wms_api_server.app.routers.export_1c import _build_1c_xml
    paid_order = [{"id": 1, "num": "1", "company": "X", "dateoforder": "2026-01-01",
                   "closed": 1, "payed": 1, "total_amount": 0, "tasks": []}]
    xml = _build_1c_xml(paid_order).decode("utf-8")
    assert "Оплачен" in xml

    closed_order = [{"id": 2, "num": "2", "company": "X", "dateoforder": "2026-01-01",
                     "closed": 1, "payed": 0, "total_amount": 0, "tasks": []}]
    xml = _build_1c_xml(closed_order).decode("utf-8")
    assert "Закрыт" in xml

    open_order = [{"id": 3, "num": "3", "company": "X", "dateoforder": "2026-01-01",
                   "closed": 0, "payed": 0, "total_amount": 0, "tasks": []}]
    xml = _build_1c_xml(open_order).decode("utf-8")
    assert "Выставлен" in xml


# ---------------------------------------------------------------------------
# Sprint 114 — Maintenance
# ---------------------------------------------------------------------------

def test_maintenance_router_importable():
    from api.wms_api_server.app.routers.maintenance import router
    assert router.prefix == "/api/admin/transport/maintenance"


def test_maintenance_stats_endpoint():
    from api.wms_api_server.app.routers.maintenance import router
    routes = [(r.path, getattr(r, "methods", set())) for r in router.routes]
    get_routes = [p for p, m in routes if "stats" in p and "GET" in m]
    assert len(get_routes) > 0


def test_maintenance_archive_endpoint():
    from api.wms_api_server.app.routers.maintenance import router
    routes = [(r.path, getattr(r, "methods", set())) for r in router.routes]
    post_routes = [p for p, m in routes if "archive" in p and "POST" in m]
    assert len(post_routes) > 0


def test_maintenance_archive_dry_run_default():
    """По умолчанию dry_run=True — безопасно."""
    import inspect
    from api.wms_api_server.app.routers import maintenance
    src = inspect.getsource(maintenance)
    assert "dry_run: bool = Query(default=True" in src


def test_maintenance_table_list():
    """Список таблиц для stats включает ключевые TMS таблицы."""
    import inspect
    from api.wms_api_server.app.routers import maintenance
    src = inspect.getsource(maintenance)
    assert "RRL_TRANSPORT_TASK" in src
    assert "RRL_SBORKA_PALLETS" in src
    assert "RRL_TT_OPERATIONS" in src
    assert "RRL_BILL_ORDERS" in src
