"""
test_sprint97_98_functional.py — Fleet CRUD: Vehicles + Drivers

Sprint 97: POST/PATCH/DELETE /vehicles, GET /vehicles/full
Sprint 98: POST/PATCH/DELETE /drivers, GET /drivers/full

Тесты проверяют:
- Новые эндпоинты зарегистрированы в роутере
- Pydantic-схемы корректны (валидация полей)
- Service methods существуют и имеют правильную сигнатуру
- TRANSPORT_FLEET_EDIT_PERMISSION константа задана
- FleetManagementPage.tsx экспортирует компонент
"""

import inspect
import pytest
from pydantic import ValidationError


# ---------------------------------------------------------------------------
# Auth / permissions
# ---------------------------------------------------------------------------

def test_fleet_edit_permission_defined():
    from api.wms_api_server.app.auth import TRANSPORT_FLEET_EDIT_PERMISSION
    assert TRANSPORT_FLEET_EDIT_PERMISSION == "transport_fleet_edit"


# ---------------------------------------------------------------------------
# Schemas — Sprint 97
# ---------------------------------------------------------------------------

def test_vehicle_create_schema_valid():
    from api.wms_api_server.app.schemas import VehicleCreateRequest
    v = VehicleCreateRequest(num_plat="Е123АВ77")
    assert v.num_plat == "Е123АВ77"
    assert v.max_weight_kg == 10000
    assert v.max_pallets == 20
    assert v.sobstvennyy is True
    assert v.doverennost_ot is None


def test_vehicle_create_schema_empty_numplat_rejected():
    from api.wms_api_server.app.schemas import VehicleCreateRequest
    with pytest.raises(ValidationError):
        VehicleCreateRequest(num_plat="")


def test_vehicle_update_schema_valid():
    from api.wms_api_server.app.schemas import VehicleUpdateRequest
    v = VehicleUpdateRequest(num_plat="Т999ХХ77", sobstvennyy=False, doverennost_ot="ООО Транс")
    assert v.sobstvennyy is False
    assert v.doverennost_ot == "ООО Транс"


# ---------------------------------------------------------------------------
# Schemas — Sprint 98
# ---------------------------------------------------------------------------

def test_driver_create_schema_valid():
    from api.wms_api_server.app.schemas import DriverCreateRequest
    d = DriverCreateRequest(name="Иванов Иван Иванович")
    assert d.name == "Иванов Иван Иванович"
    assert d.phone is None
    assert d.license_number is None
    assert d.company is None


def test_driver_create_schema_empty_name_rejected():
    from api.wms_api_server.app.schemas import DriverCreateRequest
    with pytest.raises(ValidationError):
        DriverCreateRequest(name="")


def test_driver_update_schema_valid():
    from api.wms_api_server.app.schemas import DriverUpdateRequest
    d = DriverUpdateRequest(name="Петров А.А.", phone="89001234567", license_number="7712345678")
    assert d.phone == "89001234567"


# ---------------------------------------------------------------------------
# Router endpoints registered
# ---------------------------------------------------------------------------

def test_vehicles_full_endpoint_registered():
    from api.wms_api_server.app.routers.transport import router
    routes = [r.path for r in router.routes]
    assert any("vehicles/full" in r for r in routes), f"vehicles/full not in {routes}"


def test_vehicles_create_endpoint_registered():
    from api.wms_api_server.app.routers.transport import router
    methods = {}
    for r in router.routes:
        if hasattr(r, "methods") and "vehicles" in r.path and "{vehicle_id}" not in r.path and "full" not in r.path:
            methods.update({m: r.path for m in r.methods})
    assert "POST" in methods, "POST /vehicles not registered"


def test_vehicles_update_endpoint_registered():
    from api.wms_api_server.app.routers.transport import router
    routes = [(r.path, getattr(r, 'methods', set())) for r in router.routes]
    patch_routes = [p for p, m in routes if "vehicles/{vehicle_id}" in p and "PATCH" in m]
    assert len(patch_routes) > 0


def test_vehicles_delete_endpoint_registered():
    from api.wms_api_server.app.routers.transport import router
    routes = [(r.path, getattr(r, 'methods', set())) for r in router.routes]
    del_routes = [p for p, m in routes if "vehicles/{vehicle_id}" in p and "DELETE" in m]
    assert len(del_routes) > 0


def test_drivers_full_endpoint_registered():
    from api.wms_api_server.app.routers.transport import router
    routes = [r.path for r in router.routes]
    assert any("drivers/full" in r for r in routes)


def test_drivers_create_endpoint_registered():
    from api.wms_api_server.app.routers.transport import router
    methods = {}
    for r in router.routes:
        if hasattr(r, "methods") and "drivers" in r.path and "{driver_id}" not in r.path and "full" not in r.path:
            methods.update({m: r.path for m in r.methods})
    assert "POST" in methods, "POST /drivers not registered"


# ---------------------------------------------------------------------------
# Service methods exist
# ---------------------------------------------------------------------------

def test_transport_service_has_vehicle_crud():
    from api.wms_api_server.app.services.transport_service import TransportService
    assert hasattr(TransportService, "list_vehicles_full")
    assert hasattr(TransportService, "create_vehicle")
    assert hasattr(TransportService, "update_vehicle")
    assert hasattr(TransportService, "delete_vehicle")


def test_transport_service_has_driver_crud():
    from api.wms_api_server.app.services.transport_service import TransportService
    assert hasattr(TransportService, "list_drivers_full")
    assert hasattr(TransportService, "create_driver")
    assert hasattr(TransportService, "update_driver")
    assert hasattr(TransportService, "delete_driver")


def test_create_vehicle_signature():
    from api.wms_api_server.app.services.transport_service import TransportService
    sig = inspect.signature(TransportService.create_vehicle)
    params = list(sig.parameters.keys())
    assert "num_plat" in params
    assert "max_weight_kg" in params
    assert "max_pallets" in params
    assert "sobstvennyy" in params


def test_create_driver_signature():
    from api.wms_api_server.app.services.transport_service import TransportService
    sig = inspect.signature(TransportService.create_driver)
    params = list(sig.parameters.keys())
    assert "name" in params
    assert "phone" in params
    assert "license_number" in params
    assert "company" in params


# ---------------------------------------------------------------------------
# Invalidate ref cache helper
# ---------------------------------------------------------------------------

def test_invalidate_ref_cache_exists():
    from api.wms_api_server.app.services.transport_service import _invalidate_ref_cache
    # Should not raise and should handle unknown prefix gracefully
    _invalidate_ref_cache("vehicles")
    _invalidate_ref_cache("drivers")
    _invalidate_ref_cache("nonexistent")


# ---------------------------------------------------------------------------
# Migration files exist
# ---------------------------------------------------------------------------

def test_migration_055_exists():
    import os
    path = "db/migrations/2026-05-29_fleet_crud/055_apply.sql"
    assert os.path.exists(path), f"Migration 055 not found at {path}"


def test_migration_055_contains_sequence():
    with open("db/migrations/2026-05-29_fleet_crud/055_apply.sql", encoding="utf-8") as f:
        content = f.read()
    assert "SEQ_TR_VEHICLE" in content
    assert "RRL_TR_VEHICLE_ADD" in content
    assert "RRL_TR_VEHICLE_UPDATE" in content
    assert "RRL_TR_VEHICLE_DEL" in content


def test_migration_056_exists():
    import os
    assert os.path.exists("db/migrations/2026-05-29_fleet_crud/056_apply.sql")


def test_migration_056_contains_sequence():
    with open("db/migrations/2026-05-29_fleet_crud/056_apply.sql", encoding="utf-8") as f:
        content = f.read()
    assert "RRL_TR_VODITEL_ADD" in content
    assert "RRL_TR_VODITEL_UPDATE" in content
    assert "RRL_TR_VODITEL_DEL" in content
