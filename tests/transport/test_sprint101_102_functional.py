"""
test_sprint101_102_functional.py

Sprint 101: SSE VRP cancel — VrpJobStore, job lifecycle, endpoints
Sprint 102: @tanstack/react-virtual — package.json + code references
"""

import pytest


# ---------------------------------------------------------------------------
# Sprint 101 — VRP Job Store
# ---------------------------------------------------------------------------

def test_vrp_job_store_importable():
    from api.wms_api_server.app.services.vrp_job_store import vrp_job_store, VrpJobStore, VrpJob
    assert isinstance(vrp_job_store, VrpJobStore)


def test_vrp_job_create():
    from api.wms_api_server.app.services.vrp_job_store import VrpJobStore
    store = VrpJobStore()
    job = store.create()
    assert job.job_id
    assert len(job.job_id) == 36  # UUID4 format
    assert not job.done
    assert not job.cancel_event.is_set()


def test_vrp_job_get():
    from api.wms_api_server.app.services.vrp_job_store import VrpJobStore
    store = VrpJobStore()
    job = store.create()
    retrieved = store.get(job.job_id)
    assert retrieved is job


def test_vrp_job_get_nonexistent():
    from api.wms_api_server.app.services.vrp_job_store import VrpJobStore
    store = VrpJobStore()
    assert store.get("nonexistent-uuid") is None


def test_vrp_job_cancel():
    from api.wms_api_server.app.services.vrp_job_store import VrpJobStore
    store = VrpJobStore()
    job = store.create()
    result = store.cancel(job.job_id)
    assert result is True
    assert job.done is True
    assert job.cancel_event.is_set()
    # Events contain cancelled
    assert any(e.get("type") == "cancelled" for e in job.events)


def test_vrp_job_cancel_already_done():
    from api.wms_api_server.app.services.vrp_job_store import VrpJobStore
    store = VrpJobStore()
    job = store.create()
    job.done = True
    result = store.cancel(job.job_id)
    assert result is False


def test_vrp_job_cancel_nonexistent():
    from api.wms_api_server.app.services.vrp_job_store import VrpJobStore
    store = VrpJobStore()
    result = store.cancel("nonexistent")
    assert result is False


def test_vrp_job_put_event():
    from api.wms_api_server.app.services.vrp_job_store import VrpJob
    import threading
    job = VrpJob(job_id="test-job")
    job.put_event({"type": "progress", "pct": 10})
    job.put_event({"type": "progress", "pct": 50})
    assert len(job.events) == 2
    assert job.events[0]["type"] == "progress"
    assert job.events[1]["pct"] == 50


def test_vrp_job_cleanup():
    from api.wms_api_server.app.services.vrp_job_store import VrpJobStore
    store = VrpJobStore()
    j1 = store.create()
    j2 = store.create()
    j1.done = True
    store.cleanup_done()
    assert store.get(j1.job_id) is None
    assert store.get(j2.job_id) is j2


# Router endpoints
def test_solve_vrp_returns_job_id():
    """POST /planner/solve endpoint now returns {job_id, stream_url} shape."""
    import inspect
    import api.wms_api_server.app.routers.transport as t
    src = inspect.getsource(t)
    assert "job_id" in src
    assert "vrp_job_store" in src
    assert "stream_url" in src


def test_cancel_vrp_endpoint_registered():
    from api.wms_api_server.app.routers.transport import router
    routes = [(r.path, getattr(r, "methods", set())) for r in router.routes]
    del_routes = [p for p, m in routes if "planner/solve/{job_id}" in p and "DELETE" in m]
    assert len(del_routes) > 0


def test_stream_vrp_endpoint_registered():
    from api.wms_api_server.app.routers.transport import router
    routes = [r.path for r in router.routes]
    assert any("planner/solve/{job_id}/stream" in r for r in routes)


def test_solve_vrp_timeout_logic_present():
    import inspect
    import api.wms_api_server.app.routers.transport as t
    src = inspect.getsource(t)
    assert "timeout" in src.lower()
    assert "daemon=True" in src or "threading.Thread" in src


# ---------------------------------------------------------------------------
# Sprint 102 — react-virtual
# ---------------------------------------------------------------------------

def test_react_virtual_in_package_json():
    import json
    with open("admin/wms_admin_frontend/package.json", encoding="utf-8") as f:
        pkg = json.load(f)
    deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
    assert "@tanstack/react-virtual" in deps, f"@tanstack/react-virtual not in deps: {list(deps.keys())}"


def test_react_virtual_imported_in_dispatch_page():
    with open("admin/wms_admin_frontend/src/components/TransportDispatchPage.tsx", encoding="utf-8") as f:
        content = f.read()
    assert "@tanstack/react-virtual" in content
    assert "useVirtualizer" in content


def test_pagination_removed_from_dispatch_page():
    """Пагинация заменена виртуализацией — старые кнопки ◄◄ ►► должны отсутствовать."""
    with open("admin/wms_admin_frontend/src/components/TransportDispatchPage.tsx", encoding="utf-8") as f:
        content = f.read()
    # Old pagination buttons removed
    assert 'onClick={() => setStPage(0)}' not in content, "Old pagination buttons still present"
    assert 'dispatch-page-btn' not in content or 'virtual-info' in content


def test_virtualizer_config_in_dispatch_page():
    with open("admin/wms_admin_frontend/src/components/TransportDispatchPage.tsx", encoding="utf-8") as f:
        content = f.read()
    assert "stRowVirtualizer" in content
    assert "getVirtualItems" in content
    assert "getTotalSize" in content


def test_virtual_padding_spacers_in_dispatch_page():
    with open("admin/wms_admin_frontend/src/components/TransportDispatchPage.tsx", encoding="utf-8") as f:
        content = f.read()
    assert "stVirtualTopPad" in content
    assert "stVirtualBottomPad" in content


def test_overscan_configured():
    with open("admin/wms_admin_frontend/src/components/TransportDispatchPage.tsx", encoding="utf-8") as f:
        content = f.read()
    assert "overscan" in content
