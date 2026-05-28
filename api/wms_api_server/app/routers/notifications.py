"""
notifications.py — FastAPI роутер уведомлений.

Sprint 106: Browser Push (Web Push API + VAPID)
Sprint 107: Email-уведомления (SMTP)
"""

import json
import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr, Field

from ..auth import AdminUser, TRANSPORT_DISPATCH_VIEW_PERMISSION, require_permission
from ..config import get_settings
from ..oracle_gateway import OracleGateway

log = logging.getLogger(__name__)
router = APIRouter(prefix="/api/admin/notifications", tags=["notifications"])


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class PushSubscriptionRequest(BaseModel):
    endpoint: str
    auth: str | None = None
    p256dh: str | None = None


class NotificationSettingsRequest(BaseModel):
    email: str | None = None
    events: list[str] = Field(default_factory=list)
    enabled: bool = True


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _gw() -> OracleGateway:
    return OracleGateway()


def _send_push(subscription: dict[str, Any], title: str, body: str) -> bool:
    """Отправить push через pywebpush или логировать если не установлен."""
    try:
        from pywebpush import webpush, WebPushException  # type: ignore[import]
        settings = get_settings()
        vapid_private = getattr(settings, "vapid_private_key", None)
        vapid_email = getattr(settings, "vapid_email", "mailto:admin@tms.local")
        if not vapid_private:
            log.warning("VAPID_PRIVATE_KEY not set; push skipped")
            return False
        webpush(
            subscription_info={
                "endpoint": subscription["endpoint"],
                "keys": {"auth": subscription.get("auth"), "p256dh": subscription.get("p256dh")},
            },
            data=json.dumps({"title": title, "body": body}),
            vapid_private_key=vapid_private,
            vapid_claims={"sub": vapid_email},
        )
        return True
    except ImportError:
        log.debug("pywebpush not installed; push notification logged only: %s — %s", title, body)
        return False
    except Exception as exc:
        log.warning("Push send failed: %s", exc)
        return False


def _send_email(to: str, subject: str, body: str) -> bool:
    """Отправить email через SMTP."""
    try:
        import smtplib
        from email.mime.text import MIMEText
        settings = get_settings()
        smtp_host = getattr(settings, "smtp_host", None)
        if not smtp_host:
            log.debug("SMTP not configured; email logged: %s → %s: %s", to, subject, body[:80])
            return False
        msg = MIMEText(body, "plain", "utf-8")
        msg["Subject"] = subject
        msg["From"] = getattr(settings, "smtp_from", "tms@localhost")
        msg["To"] = to
        with smtplib.SMTP(smtp_host, int(getattr(settings, "smtp_port", 25))) as s:
            user = getattr(settings, "smtp_user", None)
            password = getattr(settings, "smtp_pass", None)
            if user and password:
                s.login(user, password)
            s.send_message(msg)
        return True
    except Exception as exc:
        log.warning("Email send failed to %s: %s", to, exc)
        return False


# ---------------------------------------------------------------------------
# Sprint 106 — Push subscriptions
# ---------------------------------------------------------------------------

@router.post("/subscribe", status_code=201)
def subscribe_push(
    req: PushSubscriptionRequest,
    user: AdminUser = Depends(require_permission(TRANSPORT_DISPATCH_VIEW_PERMISSION)),
) -> dict:
    """Сохранить push-подписку (Sprint 106)."""
    gw = _gw()
    # Upsert: если endpoint уже есть — обновить, иначе вставить
    existing = gw.fetch_all(
        "SELECT ID FROM RABAEV.RRL_PUSH_SUBSCRIPTIONS WHERE ENDPOINT=:ep AND USER_ID=:uid",
        {"ep": req.endpoint, "uid": user.username},
    )
    if existing:
        gw.execute(
            """
            UPDATE RABAEV.RRL_PUSH_SUBSCRIPTIONS
               SET AUTH=:auth, P256DH=:p256dh, ACTIVE=1, CREATED_AT=SYSDATE
             WHERE ENDPOINT=:ep AND USER_ID=:uid
            """,
            {"auth": req.auth, "p256dh": req.p256dh, "ep": req.endpoint, "uid": user.username},
        )
    else:
        gw.execute(
            """
            INSERT INTO RABAEV.RRL_PUSH_SUBSCRIPTIONS (ID, USER_ID, ENDPOINT, AUTH, P256DH)
            VALUES (RABAEV.SEQ_PUSH_SUB.NEXTVAL, :uid, :ep, :auth, :p256dh)
            """,
            {"uid": user.username, "ep": req.endpoint, "auth": req.auth, "p256dh": req.p256dh},
        )
    return {"subscribed": True}


@router.delete("/subscribe", status_code=204)
def unsubscribe_push(
    req: PushSubscriptionRequest,
    user: AdminUser = Depends(require_permission(TRANSPORT_DISPATCH_VIEW_PERMISSION)),
) -> None:
    """Удалить push-подписку (Sprint 106)."""
    _gw().execute(
        "UPDATE RABAEV.RRL_PUSH_SUBSCRIPTIONS SET ACTIVE=0 WHERE ENDPOINT=:ep AND USER_ID=:uid",
        {"ep": req.endpoint, "uid": user.username},
    )


@router.post("/broadcast")
def broadcast_push(
    body: dict,
    user: AdminUser = Depends(require_permission(TRANSPORT_DISPATCH_VIEW_PERMISSION)),
) -> dict:
    """Отправить push всем активным подписчикам (Sprint 106). Internal use."""
    title = str(body.get("title", "ТМС"))
    message = str(body.get("body", ""))
    gw = _gw()
    subs = gw.fetch_all(
        "SELECT ENDPOINT, AUTH, P256DH FROM RABAEV.RRL_PUSH_SUBSCRIPTIONS WHERE ACTIVE=1",
    )
    sent = 0
    for s in subs:
        if _send_push({"endpoint": s["endpoint"], "auth": s["auth"], "p256dh": s["p256dh"]}, title, message):
            sent += 1
    return {"sent": sent, "total": len(subs)}


# ---------------------------------------------------------------------------
# Sprint 107 — Email notification settings
# ---------------------------------------------------------------------------

@router.get("/settings")
def get_notification_settings(
    user: AdminUser = Depends(require_permission(TRANSPORT_DISPATCH_VIEW_PERMISSION)),
) -> dict:
    """Настройки уведомлений пользователя (Sprint 107)."""
    rows = _gw().fetch_all(
        "SELECT EMAIL, EVENTS_JSON, ENABLED FROM RABAEV.RRL_NOTIFICATION_SETTINGS WHERE USER_ID=:uid",
        {"uid": user.username},
    )
    if not rows:
        return {"email": None, "events": [], "enabled": False}
    r = rows[0]
    events: list[str] = []
    try:
        events = json.loads(r.get("events_json") or "[]")
    except Exception:
        pass
    return {
        "email": r.get("email"),
        "events": events,
        "enabled": bool(r.get("enabled")),
    }


@router.post("/settings")
def save_notification_settings(
    req: NotificationSettingsRequest,
    user: AdminUser = Depends(require_permission(TRANSPORT_DISPATCH_VIEW_PERMISSION)),
) -> dict:
    """Сохранить настройки уведомлений (Sprint 107)."""
    gw = _gw()
    events_json = json.dumps(req.events, ensure_ascii=False)
    existing = gw.fetch_all(
        "SELECT ID FROM RABAEV.RRL_NOTIFICATION_SETTINGS WHERE USER_ID=:uid",
        {"uid": user.username},
    )
    if existing:
        gw.execute(
            """
            UPDATE RABAEV.RRL_NOTIFICATION_SETTINGS
               SET EMAIL=:email, EVENTS_JSON=:events, ENABLED=:enabled, UPDATED_AT=SYSDATE
             WHERE USER_ID=:uid
            """,
            {"email": req.email, "events": events_json, "enabled": 1 if req.enabled else 0, "uid": user.username},
        )
    else:
        gw.execute(
            """
            INSERT INTO RABAEV.RRL_NOTIFICATION_SETTINGS (ID, USER_ID, EMAIL, EVENTS_JSON, ENABLED)
            VALUES (RABAEV.SEQ_NOTIF_SETTINGS.NEXTVAL, :uid, :email, :events, :enabled)
            """,
            {"uid": user.username, "email": req.email, "events": events_json, "enabled": 1 if req.enabled else 0},
        )
    return {"saved": True}


@router.post("/test-email")
def send_test_email(
    user: AdminUser = Depends(require_permission(TRANSPORT_DISPATCH_VIEW_PERMISSION)),
) -> dict:
    """Отправить тестовое письмо (Sprint 107)."""
    rows = _gw().fetch_all(
        "SELECT EMAIL FROM RABAEV.RRL_NOTIFICATION_SETTINGS WHERE USER_ID=:uid",
        {"uid": user.username},
    )
    email = (rows[0].get("email") if rows else None) if rows else None
    if not email:
        raise HTTPException(status_code=422, detail="Email not configured")
    ok = _send_email(email, "ТМС: тестовое письмо", f"Уведомления настроены для {user.display_name}.")
    return {"sent": ok, "to": email}
