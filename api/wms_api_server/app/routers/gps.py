"""
gps.py — GPS роутер для приёма и выдачи позиций машин.

Sprint 110: POST /api/gps/track — приём координат от трекеров
           GET  /api/admin/transport/vehicles/positions — текущие позиции
           GET  /api/admin/transport/vehicles/{id}/track — трек за день

Sprint 111: интеграция с картой (TransportPlannerPage) через
           GET /vehicles/positions (уже в transport_kpi или здесь).
"""

from datetime import date

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel

from ..auth import AdminUser, TRANSPORT_DISPATCH_VIEW_PERMISSION, require_permission
from ..oracle_gateway import OracleGateway

router = APIRouter(tags=["gps"])


class GpsTrackRequest(BaseModel):
    vehicle_id: int
    lat: float
    lon: float
    speed_kmh: float = 0
    ts: str | None = None  # ISO datetime; defaults to SYSDATE


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
    # Insert history
    gw.execute(
        """
        INSERT INTO RABAEV.RRL_VEHICLE_GPS (ID, VEHICLE_ID, LAT, LON, SPEED_KMH, TS)
        VALUES (RABAEV.SEQ_VEHICLE_GPS.NEXTVAL, :vid, :lat, :lon, :speed,
                NVL(TO_DATE(:ts, 'YYYY-MM-DD"T"HH24:MI:SS'), SYSDATE))
        """,
        {
            "vid": req.vehicle_id,
            "lat": req.lat,
            "lon": req.lon,
            "speed": req.speed_kmh,
            "ts": req.ts,
        },
    )
    # Upsert last position
    existing = gw.fetch_all(
        "SELECT VEHICLE_ID FROM RABAEV.RRL_VEHICLE_GPS_LAST WHERE VEHICLE_ID=:vid",
        {"vid": req.vehicle_id},
    )
    if existing:
        gw.execute(
            """
            UPDATE RABAEV.RRL_VEHICLE_GPS_LAST
               SET LAT=:lat, LON=:lon, SPEED_KMH=:speed, TS=SYSDATE, UPDATED_AT=SYSDATE
             WHERE VEHICLE_ID=:vid
            """,
            {"lat": req.lat, "lon": req.lon, "speed": req.speed_kmh, "vid": req.vehicle_id},
        )
    else:
        gw.execute(
            """
            INSERT INTO RABAEV.RRL_VEHICLE_GPS_LAST (VEHICLE_ID, LAT, LON, SPEED_KMH, TS)
            VALUES (:vid, :lat, :lon, :speed, SYSDATE)
            """,
            {"vid": req.vehicle_id, "lat": req.lat, "lon": req.lon, "speed": req.speed_kmh},
        )
    # Sprint 118-119 — check geofences and auto-mark operations
    try:
        from ..services.geofencing import check_geofences
        geo_events = check_geofences(req.vehicle_id, req.lat, req.lon, gw)
    except Exception:
        geo_events = []

    return {"ok": True, "vehicle_id": req.vehicle_id, "geo_events": geo_events}


# ---------------------------------------------------------------------------
# Sprint 110-111 — Read endpoints for map
# ---------------------------------------------------------------------------

@router.get("/api/admin/transport/geofences")
def list_geofences(
    addr_mask: str | None = Query(default=None),
    _user: AdminUser = Depends(require_permission(TRANSPORT_DISPATCH_VIEW_PERMISSION)),
) -> list[dict]:
    """Sprint 118: список геозон адресов (радиус в метрах)."""
    gw = _gw()
    where = "WHERE LATITUDE IS NOT NULL"
    params: dict = {}
    if addr_mask:
        where += " AND UPPER(ADDR) LIKE UPPER(:mask)"
        params["mask"] = f"%{addr_mask}%"
    rows = gw.fetch_all(
        f"""
        SELECT ID, ADDR, LATITUDE, LONGITUDE,
               NVL(GEO_FENCE_RADIUS_M, 200) AS RADIUS_M
          FROM RABAEV.RRL_ADDR
          {where}
         ORDER BY ADDR
         FETCH FIRST 200 ROWS ONLY
        """,
        params,
    )
    return [
        {
            "addr_id": int(r.get("id") or 0),
            "addr": str(r.get("addr") or ""),
            "lat": float(r.get("latitude") or 0),
            "lon": float(r.get("longitude") or 0),
            "radius_m": int(r.get("radius_m") or 200),
        }
        for r in rows
    ]


@router.patch("/api/admin/transport/geofences/{addr_id}")
def update_geofence_radius(
    addr_id: int,
    body: dict,
    _user: AdminUser = Depends(require_permission(TRANSPORT_DISPATCH_VIEW_PERMISSION)),
) -> dict:
    """Sprint 118: обновить радиус геозоны адреса."""
    radius = int(body.get("radius_m") or 200)
    _gw().execute(
        "UPDATE RABAEV.RRL_ADDR SET GEO_FENCE_RADIUS_M = :r WHERE ID = :aid",
        {"r": radius, "aid": addr_id},
    )
    return {"addr_id": addr_id, "radius_m": radius}


@router.get("/api/admin/transport/vehicles/positions")
def get_vehicle_positions(
    _user: AdminUser = Depends(require_permission(TRANSPORT_DISPATCH_VIEW_PERMISSION)),
) -> list[dict]:
    """Текущие позиции всех машин (Sprint 111 — live иконки на карте)."""
    rows = _gw().fetch_all(
        """
        SELECT GL.VEHICLE_ID,
               V.NUM_PLAT,
               V.TRANSTYPE  AS TRANSPORT_TYPE,
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
    from datetime import date as _date
    d = track_date or _date.today()
    rows = _gw().fetch_all(
        """
        SELECT LAT, LON, SPEED_KMH, TS
          FROM RABAEV.RRL_VEHICLE_GPS
         WHERE VEHICLE_ID = :vid
           AND TRUNC(TS) = TRUNC(:d)
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
