"""
test_sprint115_119_functional.py

Sprint 115-117: Attention Model VRP
Sprint 118-119: Geofencing
"""

import os
import pytest
import math


# ---------------------------------------------------------------------------
# Sprint 115 — Dataset collection script
# ---------------------------------------------------------------------------

def test_collect_dataset_script_exists():
    assert os.path.exists("scripts/attention_model/collect_dataset.py")


def test_collect_dataset_imports_oracle():
    with open("scripts/attention_model/collect_dataset.py", encoding="utf-8") as f:
        content = f.read()
    assert "OracleGateway" in content
    assert "TRANSTASK_ID" in content or "SHIPMENT_DATE" in content


def test_collect_dataset_has_minimum_warning():
    with open("scripts/attention_model/collect_dataset.py", encoding="utf-8") as f:
        content = f.read()
    assert "1000" in content  # minimum trip count warning


# ---------------------------------------------------------------------------
# Sprint 116 — AM training script + solver
# ---------------------------------------------------------------------------

def test_train_am_script_exists():
    assert os.path.exists("scripts/attention_model/train_am.py")


def test_train_am_has_encoder_decoder():
    with open("scripts/attention_model/train_am.py", encoding="utf-8") as f:
        content = f.read()
    assert "AMEncoder" in content
    assert "AMDecoder" in content
    assert "TransformerEncoder" in content


def test_train_am_saves_checkpoint():
    with open("scripts/attention_model/train_am.py", encoding="utf-8") as f:
        content = f.read()
    assert "torch.save" in content
    assert "am_vrp.pt" in content


def test_am_solver_importable():
    from api.wms_api_server.app.services.am_solver import is_available, solve_am
    assert callable(is_available)
    assert callable(solve_am)


def test_am_solver_without_model():
    """solve_am возвращает None если нет модели (без torch или файла)."""
    from api.wms_api_server.app.services.am_solver import is_available, solve_am
    if not is_available():
        result = solve_am([58.0, 58.1, 58.2], [56.0, 56.1, 56.2], [5, 10, 3])
        assert result is None, "Expected None when model not available"


def test_am_solver_is_available_returns_bool():
    from api.wms_api_server.app.services.am_solver import is_available
    result = is_available()
    assert isinstance(result, bool)


def test_am_solver_handles_import_error():
    """Если torch не установлен — is_available() возвращает False без ошибок."""
    from api.wms_api_server.app.services import am_solver
    import sys
    original = sys.modules.get("torch")
    sys.modules["torch"] = None  # type: ignore[assignment]
    try:
        # Re-test is_available with torch blocked
        result = am_solver.is_available()
        assert result is False
    finally:
        if original is None:
            sys.modules.pop("torch", None)
        else:
            sys.modules["torch"] = original


# ---------------------------------------------------------------------------
# Sprint 117 — UI integration
# ---------------------------------------------------------------------------

def test_attention_model_option_in_planner():
    with open("admin/wms_admin_frontend/src/components/TransportPlannerPage.tsx", encoding="utf-8") as f:
        content = f.read()
    assert "attention_model" in content


def test_am_solver_dispatch_in_transport_service():
    import inspect
    from api.wms_api_server.app.services import transport_service
    src = inspect.getsource(transport_service)
    assert "attention_model" in src
    assert "am_solver" in src
    assert "solve_am" in src


def test_am_fallback_to_auto():
    """Если AM недоступен — solver переключается на 'auto'."""
    import inspect
    from api.wms_api_server.app.services import transport_service
    src = inspect.getsource(transport_service)
    assert 'solver = "auto"' in src  # fallback line


# ---------------------------------------------------------------------------
# Sprint 118 — Geofencing detection
# ---------------------------------------------------------------------------

def test_geofencing_module_importable():
    from api.wms_api_server.app.services.geofencing import check_geofences, haversine_m
    assert callable(check_geofences)
    assert callable(haversine_m)


def test_haversine_m_same_point():
    from api.wms_api_server.app.services.geofencing import haversine_m
    dist = haversine_m(58.0, 56.0, 58.0, 56.0)
    assert dist == pytest.approx(0.0, abs=0.01)


def test_haversine_m_known_distance():
    """Расстояние между двумя точками примерно 1 км."""
    from api.wms_api_server.app.services.geofencing import haversine_m
    # ~1 km difference in latitude at 58°N
    dist = haversine_m(58.0, 56.0, 58.009, 56.0)
    assert 900 < dist < 1100, f"Expected ~1000m, got {dist:.1f}m"


def test_haversine_m_perm_to_perm():
    """Пермь — две точки в пределах города (~5 км)."""
    from api.wms_api_server.app.services.geofencing import haversine_m
    # Пермь центр vs Пермь-2
    dist = haversine_m(58.0105, 56.2502, 58.0650, 56.2110)
    assert 3000 < dist < 8000, f"Expected 5-7 km within Perm, got {dist:.0f}m"


def test_haversine_m_not_negative():
    from api.wms_api_server.app.services.geofencing import haversine_m
    for lat1, lon1, lat2, lon2 in [(0, 0, 0, 0), (55.0, 37.0, 58.0, 56.0), (-33.0, 151.0, 48.8, 2.3)]:
        assert haversine_m(lat1, lon1, lat2, lon2) >= 0


def test_geofencing_state_structure():
    """_GEO_STATE хранит множества addr_id по vehicle_id."""
    from api.wms_api_server.app.services.geofencing import _GEO_STATE
    assert isinstance(_GEO_STATE, dict)


def test_migration_062_exists():
    assert os.path.exists("db/migrations/2026-05-29_geofencing/062_apply.sql")


def test_migration_062_adds_radius_column():
    with open("db/migrations/2026-05-29_geofencing/062_apply.sql", encoding="utf-8") as f:
        content = f.read()
    assert "GEO_FENCE_RADIUS_M" in content
    assert "200" in content  # default radius


def test_geofence_endpoints_in_gps_router():
    from api.wms_api_server.app.routers.gps import router
    routes = [r.path for r in router.routes]
    assert any("geofences" in r for r in routes)


# ---------------------------------------------------------------------------
# Sprint 119 — Auto-mark UNLOAD
# ---------------------------------------------------------------------------

def test_auto_mark_functions_exist():
    from api.wms_api_server.app.services.geofencing import (
        _auto_mark_unload_start,
        _auto_mark_unload_done,
    )
    assert callable(_auto_mark_unload_start)
    assert callable(_auto_mark_unload_done)


def test_auto_mark_called_on_enter_exit():
    """check_geofences вызывает auto-mark при enter/exit."""
    import inspect
    from api.wms_api_server.app.services import geofencing
    src = inspect.getsource(geofencing)
    assert "_auto_mark_unload_start" in src
    assert "_auto_mark_unload_done" in src
    assert '"enter"' in src
    assert '"exit"' in src


def test_auto_mark_uses_sysdate():
    """Oracle UPDATE использует SYSDATE для fact_start/fact_end."""
    import inspect
    from api.wms_api_server.app.services import geofencing
    src = inspect.getsource(geofencing)
    assert "SYSDATE" in src
    assert "FACT_START" in src
    assert "FACT_END" in src


def test_auto_mark_tags_gps_audit():
    """Авто-отмеченные операции помечаются [GPS-auto] в NOTE."""
    import inspect
    from api.wms_api_server.app.services import geofencing
    src = inspect.getsource(geofencing)
    assert "GPS-auto" in src


def test_geo_event_returned_in_gps_track():
    """POST /gps/track возвращает geo_events в ответе."""
    import inspect
    from api.wms_api_server.app.routers import gps
    src = inspect.getsource(gps)
    assert "geo_events" in src
    assert '"geo_events"' in src
