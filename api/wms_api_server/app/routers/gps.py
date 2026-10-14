"""
gps.py — GPS роутер для приёма и выдачи позиций машин.

Sprint 110: POST /api/gps/track — приём координат от трекеров
           GET  /api/admin/transport/vehicles/positions — текущие позиции
           GET  /api/admin/transport/vehicles/{id}/track — трек за день

Sprint 111: интеграция с картой (TransportPlannerPage) через
           GET /vehicles/positions (уже в transport_kpi или здесь).
"""

from datetime import date, datetime

from fastapi import APIRouter, Depends, Query, HTTPException, Path
from pydantic import BaseModel, Field, field_validator

from ..auth import AdminUser, TRANSPORT_DISPATCH_VIEW_PERMISSION, require_permission
from ..oracle_gateway import OracleGateway

router = APIRouter(tags=["gps"])


class GpsTrackRequest(BaseModel):
    vehicle_id: int = Field(gt=0)
    lat: float = Field(ge=-90, le=90, allow_inf_nan=False)
    lon: float = Field(ge=-180, le=180, allow_inf_nan=False)
    speed_kmh: float = Field(default=0, ge=0, lt=99999.5, allow_inf_nan=False)
    ts: datetime | None = None  # Oracle DATE: database-local wall time, seconds, no offset.

    @field_validator("ts", mode="before")
    @classmethod
    def validate_timestamp(cls, value):
        if value is None:
            return None
        if not isinstance(value, str):
            raise ValueError("ts must be YYYY-MM-DDTHH:mm:ss in database-local time")
        import re
        if not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}", value):
            raise ValueError("ts requires whole seconds and no timezone offset; database-local time")
        return datetime.strptime(value, "%Y-%m-%dT%H:%M:%S")


def _gw() -> OracleGateway:
    return OracleGateway()


# ---------------------------------------------------------------------------
# Sprint 110 — GPS Track receive
# ---------------------------------------------------------------------------

@router.post("/api/gps/track", status_code=200)
def receive_gps_track(req: GpsTrackRequest) -> dict:
    """
    Принять координату от GPS-трекера (Sprint 110).
    Endpoint без admin-авторизации — защищён IP-whitelist через nginx на prod.
    """
    gw = _gw()
    from ..modules.transport.public import ingest_gps, GpsVehicleMissing
    try:
        result = ingest_gps(gw, req.vehicle_id, req.lat, req.lon, req.speed_kmh, req.ts)
    except GpsVehicleMissing as exc:
        raise HTTPException(404, str(exc)) from exc
    result["geo_events"] = []
    if result["current_position_updated"]:
        try:
            from ..services.geofencing import check_geofences
            result["geo_events"] = check_geofences(req.vehicle_id, req.lat, req.lon, gw)
        except Exception:
            result["geofence_status"] = "LOOKUP_UNAVAILABLE"
    else:
        result["geofence_status"] = "SKIPPED_STALE_OBSERVATION"
    return result


# ---------------------------------------------------------------------------
# Sprint 110-111 — Read endpoints for map
# ---------------------------------------------------------------------------

@router.get("/api/admin/transport/geofences")
def list_geofences(
    addr_mask: str | None = Query(default=None),
    _user: AdminUser = Depends(require_permission(TRANSPORT_DISPATCH_VIEW_PERMISSION)),
) -> list[dict]:
    """Sprint 118: список геозон адресов (радиус в метрах)."""
    from ..modules.transport.public import list_address_geofences
    return list_address_geofences(_gw(), addr_mask)



class GeofenceRadiusUpdate(BaseModel):
    radius_m: int = Field(strict=True, gt=0, le=2147483647)


@router.patch("/api/admin/transport/geofences/{addr_id:path}")
def update_geofence_radius(
    body: GeofenceRadiusUpdate,
    addr_id: str = Path(min_length=1, max_length=255),
    _user: AdminUser = Depends(require_permission("warehouse_settings_edit")),
) -> dict:
    """Update radius using the actual ADDR key, including embedded slashes."""
    from ..modules.transport.public import update_address_geofence
    result = update_address_geofence(_gw(), addr_id, body.radius_m, _user.username)
    if result is None:
        raise HTTPException(404, "Адрес геозоны не найден или удалён")
    return result


@router.get("/api/admin/transport/vehicles/positions")
def get_vehicle_positions(
    _user: AdminUser = Depends(require_permission(TRANSPORT_DISPATCH_VIEW_PERMISSION)),
) -> list[dict]:
    """Текущие позиции всех машин (Sprint 111 — live иконки на карте)."""
    rows = _gw().fetch_all(
        """
        SELECT GL.VEHICLE_ID,
               V.NUM        AS NUM_PLAT,
               V.TR_TYPE    AS TRANSPORT_TYPE,
               GL.LAT,
               GL.LON,
               GL.SPEED_KMH,
               GL.TS        AS LAST_SEEN,
               GL.UPDATED_AT
          FROM RABAEV.RRL_VEHICLE_GPS_LAST GL
          JOIN RABAEV.RRL_TR_VEHICLE V ON V.ID = GL.VEHICLE_ID
         WHERE NVL(V.DELETED,0)=0
         ORDER BY GL.VEHICLE_ID
        """
    )
    return [
        {
            "vehicle_id": int(r.get("vehicle_id") or 0),
            "num_plat": str(r.get("num_plat") or ""),
            "transport_type": str(r.get("transport_type") or ""),
            "lat": float(r.get("lat") or 0),
            "lon": float(r.get("lon") or 0),
            "speed_kmh": float(r.get("speed_kmh") or 0),
            "last_seen": str(r.get("last_seen") or ""),
        }
        for r in rows
    ]


@router.get("/api/admin/transport/vehicles/{vehicle_id}/track")
def get_vehicle_track(
    vehicle_id: int,
    track_date: date = Query(default=None),
    _user: AdminUser = Depends(require_permission(TRANSPORT_DISPATCH_VIEW_PERMISSION)),
) -> list[dict]:
    """Трек машины за день — список координат по времени (Sprint 110)."""
    from datetime import date, datetime as _date
    d = track_date or _date.today()
    rows = _gw().fetch_all(
        """
        SELECT LAT, LON, SPEED_KMH, TS
          FROM RABAEV.RRL_VEHICLE_GPS
         WHERE VEHICLE_ID = :vid
           AND TS >= :d AND TS < :d + 1
         ORDER BY TS
        """,
        {"vid": vehicle_id, "d": d},
    )
    return [
        {
            "lat": float(r.get("lat") or 0),
            "lon": float(r.get("lon") or 0),
            "speed_kmh": float(r.get("speed_kmh") or 0),
            "ts": str(r.get("ts") or ""),
        }
        for r in rows
    ]
