from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_osrm_and_valhalla_compose_files_exist():
    assert (ROOT / "docker-compose.osrm.yml").exists()
    assert (ROOT / "docker-compose.valhalla.yml").exists()
    assert "osrm/osrm-backend:latest" in (ROOT / "docker-compose.osrm.yml").read_text(encoding="utf-8")
    assert "ghcr.io/gis-ops/docker-valhalla/valhalla:latest" in (ROOT / "docker-compose.valhalla.yml").read_text(encoding="utf-8")


def test_osrm_provider_uses_real_osrm_route_health_probe():
    source = (ROOT / "api/wms_api_server/app/services/routing.py").read_text(encoding="utf-8")
    assert "/route/v1/driving/" in source
    assert f"{'{'}OSRM_URL{'}'}/health" not in source


def test_routing_status_exposes_provider_availability_flags():
    source = (ROOT / "api/wms_api_server/app/services/transport_service.py").read_text(encoding="utf-8")
    for token in (
        '"active_provider"',
        '"osrm_available"',
        '"valhalla_available"',
        '"haversine_available"',
    ):
        assert token in source


def test_routing_smoke_script_validates_compose_and_live_endpoints():
    source = (ROOT / "scripts/tms2-routing-smoke.ps1").read_text(encoding="utf-8")
    assert "docker compose -f docker-compose.osrm.yml config" in source
    assert "docker compose -f docker-compose.valhalla.yml config" in source
    assert "/route/v1/driving/" in source
    assert "/status" in source


def test_routing_data_prep_script_exists_and_builds_osrm():
    source = (ROOT / "scripts/tms2-routing-data-prep.ps1").read_text(encoding="utf-8")
    assert "curl.exe -L --fail" in source
    assert "osrm-extract" in source
    assert "osrm-partition" in source
    assert "osrm-customize" in source
    assert "VALHALLA_FORCE_REBUILD" in source
