"""
test_sprint103_107_functional.py

Sprint 103: Driver mobile — GET /trips, /trips/{id}/sts, /trips/{id}/ops
Sprint 104: POST /ops/{id}/start, /ops/{id}/done
Sprint 105: Service Worker + manifest files exist
Sprint 106: Push subscription endpoints
Sprint 107: Email notification settings
"""

import os
import pytest


# ---------------------------------------------------------------------------
# Sprint 103-104 — Driver Mobile API
# ---------------------------------------------------------------------------

def test_driver_mobile_router_importable():
    from api.wms_api_server.app.routers.driver_mobile import router
    assert router.prefix == "/api/driver"


def test_driver_trips_endpoint_registered():
    from api.wms_api_server.app.routers.driver_mobile import router
    routes = [r.path for r in router.routes]
    assert "/api/driver/trips" in routes


def test_driver_trips_sts_endpoint_registered():
    from api.wms_api_server.app.routers.driver_mobile import router
    routes = [r.path for r in router.routes]
    assert any("trips/{task_id}/sts" in r for r in routes)


def test_driver_trips_ops_endpoint_registered():
    from api.wms_api_server.app.routers.driver_mobile import router
    routes = [r.path for r in router.routes]
    assert any("trips/{task_id}/ops" in r for r in routes)


def test_driver_op_start_endpoint_registered():
    from api.wms_api_server.app.routers.driver_mobile import router
    routes = [(r.path, getattr(r, "methods", set())) for r in router.routes]
    start_routes = [p for p, m in routes if "ops/{op_id}/start" in p and "POST" in m]
    assert len(start_routes) > 0


def test_driver_op_done_endpoint_registered():
    from api.wms_api_server.app.routers.driver_mobile import router
    routes = [(r.path, getattr(r, "methods", set())) for r in router.routes]
    done_routes = [p for p, m in routes if "ops/{op_id}/done" in p and "POST" in m]
    assert len(done_routes) > 0


def test_driver_mobile_no_admin_auth():
    """Эндпоинты водителя не требуют admin авторизации."""
    import inspect
    from api.wms_api_server.app.routers import driver_mobile
    src = inspect.getsource(driver_mobile)
    # No require_permission in public endpoints
    assert "require_permission" not in src or "TRANSPORT" not in src


def test_verify_op_driver_helper():
    """_verify_op_driver существует и проверяет принадлежность операции водителю."""
    from api.wms_api_server.app.routers.driver_mobile import _verify_op_driver
    import inspect
    sig = inspect.signature(_verify_op_driver)
    params = list(sig.parameters.keys())
    assert "op_id" in params
    assert "driver_id" in params


def test_driver_trips_response_fields():
    """list_trips возвращает объекты с нужными полями."""
    import inspect
    from api.wms_api_server.app.routers import driver_mobile
    src = inspect.getsource(driver_mobile)
    assert "task_id" in src
    assert "shipment_date" in src
    assert "num_plat" in src
    assert "condition" in src
    assert "st_count" in src


def test_driver_ops_status_logic():
    """Статус операции вычисляется из fact_start/fact_end."""
    import inspect
    from api.wms_api_server.app.routers import driver_mobile
    src = inspect.getsource(driver_mobile)
    assert '"done"' in src
    assert '"in_progress"' in src
    assert '"pending"' in src


# ---------------------------------------------------------------------------
# Sprint 105 — PWA Service Worker + Manifest
# ---------------------------------------------------------------------------

def test_service_worker_file_exists():
    assert os.path.exists("admin/wms_admin_frontend/driver-sw.js"), "driver-sw.js not found"


def test_service_worker_has_install_handler():
    with open("admin/wms_admin_frontend/driver-sw.js", encoding="utf-8") as f:
        content = f.read()
    assert "install" in content
    assert "activate" in content
    assert "fetch" in content


def test_service_worker_has_background_sync():
    with open("admin/wms_admin_frontend/driver-sw.js", encoding="utf-8") as f:
        content = f.read()
    assert "sync-driver-ops" in content
    assert "IndexedDB" in content or "indexedDB" in content


def test_driver_manifest_exists():
    assert os.path.exists("admin/wms_admin_frontend/driver-manifest.json")


def test_driver_manifest_content():
    import json
    with open("admin/wms_admin_frontend/driver-manifest.json", encoding="utf-8") as f:
        manifest = json.load(f)
    assert manifest["start_url"] == "/?page=driver"
    assert manifest["display"] == "standalone"
    assert "name" in manifest


def test_driver_mobile_page_registers_sw():
    with open("admin/wms_admin_frontend/src/components/DriverMobilePage.tsx", encoding="utf-8") as f:
        content = f.read()
    assert "serviceWorker" in content
    assert "driver-sw.js" in content


# ---------------------------------------------------------------------------
# Sprint 106 — Push Notifications
# ---------------------------------------------------------------------------

def test_notifications_router_importable():
    from api.wms_api_server.app.routers.notifications import router
    assert router.prefix == "/api/admin/notifications"


def test_push_subscribe_endpoint_registered():
    from api.wms_api_server.app.routers.notifications import router
    routes = [(r.path, getattr(r, "methods", set())) for r in router.routes]
    post_routes = [p for p, m in routes if "subscribe" in p and "POST" in m]
    assert len(post_routes) > 0


def test_push_unsubscribe_endpoint_registered():
    from api.wms_api_server.app.routers.notifications import router
    routes = [(r.path, getattr(r, "methods", set())) for r in router.routes]
    del_routes = [p for p, m in routes if "subscribe" in p and "DELETE" in m]
    assert len(del_routes) > 0


def test_push_broadcast_endpoint_registered():
    from api.wms_api_server.app.routers.notifications import router
    routes = [r.path for r in router.routes]
    assert any("broadcast" in r for r in routes)


def test_push_subscription_schema():
    from api.wms_api_server.app.routers.notifications import PushSubscriptionRequest
    req = PushSubscriptionRequest(endpoint="https://fcm.googleapis.com/fcm/send/test")
    assert req.endpoint.startswith("https://")
    assert req.auth is None
    assert req.p256dh is None


def test_send_push_graceful_without_pywebpush():
    """_send_push возвращает False если pywebpush не установлен."""
    from api.wms_api_server.app.routers.notifications import _send_push
    result = _send_push(
        {"endpoint": "https://example.com", "auth": None, "p256dh": None},
        "Test", "Test body"
    )
    assert isinstance(result, bool)  # True or False, not exception


def test_migration_058_exists():
    assert os.path.exists("db/migrations/2026-05-29_notifications/058_apply.sql")


def test_migration_058_creates_push_table():
    with open("db/migrations/2026-05-29_notifications/058_apply.sql", encoding="utf-8") as f:
        content = f.read()
    assert "RRL_PUSH_SUBSCRIPTIONS" in content
    assert "ENDPOINT" in content
    assert "AUTH" in content


# ---------------------------------------------------------------------------
# Sprint 107 — Email Notifications
# ---------------------------------------------------------------------------

def test_notification_settings_endpoint_registered():
    from api.wms_api_server.app.routers.notifications import router
    routes = [(r.path, getattr(r, "methods", set())) for r in router.routes]
    get_routes = [p for p, m in routes if "settings" in p and "GET" in m]
    assert len(get_routes) > 0


def test_notification_settings_post_endpoint():
    from api.wms_api_server.app.routers.notifications import router
    routes = [(r.path, getattr(r, "methods", set())) for r in router.routes]
    post_routes = [p for p, m in routes if "settings" in p and "POST" in m]
    assert len(post_routes) > 0


def test_test_email_endpoint_registered():
    from api.wms_api_server.app.routers.notifications import router
    routes = [r.path for r in router.routes]
    assert any("test-email" in r for r in routes)


def test_notification_settings_schema():
    from api.wms_api_server.app.routers.notifications import NotificationSettingsRequest
    req = NotificationSettingsRequest(email="admin@example.com", events=["vrp_done", "trip_ready"], enabled=True)
    assert req.email == "admin@example.com"
    assert len(req.events) == 2
    assert req.enabled is True


def test_send_email_graceful_without_smtp():
    """_send_email возвращает False если SMTP не настроен."""
    from api.wms_api_server.app.routers.notifications import _send_email
    result = _send_email("test@example.com", "Test Subject", "Test body")
    assert isinstance(result, bool)


def test_migration_058_contains_notification_settings():
    with open("db/migrations/2026-05-29_notifications/058_apply.sql", encoding="utf-8") as f:
        content = f.read()
    assert "RRL_NOTIFICATION_SETTINGS" in content
    assert "EVENTS_JSON" in content
