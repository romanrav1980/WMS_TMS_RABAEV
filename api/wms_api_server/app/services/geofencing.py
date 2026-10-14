"""
geofencing.py — Sprint 118-119: Geofencing logic.

Детекция входа/выхода машины в геозоны адресов активных рейсов.
Вызывается из /api/gps/track при каждом поступлении координаты.
"""

import logging
import math
from typing import Any

log = logging.getLogger(__name__)

_GEO_STATE: dict[str, set[tuple[int, str]]] = {}  # vehicle_id → {(trip_id, address)} inside


def haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Расстояние в метрах между двумя точками (WGS84)."""
    R = 6_371_000.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def check_geofences(
    vehicle_id: int,
    lat: float,
    lon: float,
    gateway: Any,
) -> list[dict]:
    """
    Sprint 118: проверить геозоны активных рейсов для машины.
    Возвращает список событий: {event: 'enter'|'exit', addr_id, task_id, addr}.
    GPS наблюдение не подтверждает выполнение UNLOAD без точной привязки к операции.
    """
    events: list[dict] = []
    if not math.isfinite(lat) or not math.isfinite(lon) or not -90 <= lat <= 90 or not -180 <= lon <= 180:
        return events

    # Получаем активные рейсы машины с адресами и их координатами
    rows = gateway.fetch_all(
        """
        SELECT TT.ID AS TASK_ID, A.ADDR AS ADDR_ID, A.ADDR,
               A.SHIROTA AS LATITUDE, A.DOLGOTA AS LONGITUDE,
               NVL(A.GEO_FENCE_RADIUS_M, 200) AS RADIUS_M
          FROM RABAEV.RRL_TRANSPORT_TASK TT
          JOIN RABAEV.RRL_SBORKA_PALLETS SP ON SP.TRANSTASK_ID = TT.ID AND SP.CONDITION<>2
          JOIN RABAEV.RRL_ADDR A ON A.ADDR = SP.ADDR
         WHERE TT.TRANSPORT IN (
           SELECT NUM FROM RABAEV.RRL_TR_VEHICLE WHERE ID=:vid AND NVL(DELETED,0)=0
         )
           AND TT.CONDITION NOT IN ('Отгружен','Отменён')
           AND NVL(TT.DELETED,0)=0
           AND NVL(A.DELETED3,0)=0
           AND A.SHIROTA BETWEEN -90 AND 90 AND A.DOLGOTA BETWEEN -180 AND 180
         GROUP BY TT.ID, A.ADDR, A.SHIROTA, A.DOLGOTA, A.GEO_FENCE_RADIUS_M
        """,
        {"vid": vehicle_id},
    )

    state_key = str(vehicle_id)
    current_inside = _GEO_STATE.get(state_key, set())
    new_inside: set[tuple[int, str]] = set()

    for r in rows:
        addr_id = str(r["addr_id"])
        addr_lat = float(r["latitude"])
        addr_lon = float(r["longitude"])
        radius = float(r.get("radius_m") or 200)
        task_id = int(r.get("task_id") or 0)

        identity = (task_id, addr_id)
        dist = haversine_m(lat, lon, addr_lat, addr_lon)
        inside = dist <= radius

        if inside:
            new_inside.add(identity)
            if identity not in current_inside:
                # Entered geofence
                events.append({"event": "enter", "addr_id": addr_id, "task_id": task_id, "addr": r.get("addr")})
                events[-1].update(operational_fact_applied=False, reason="unambiguous_binding_required")
        else:
            if identity in current_inside:
                # Exited geofence
                events.append({"event": "exit", "addr_id": addr_id, "task_id": task_id, "addr": r.get("addr")})
                events[-1].update(operational_fact_applied=False, reason="unambiguous_binding_required")

    _GEO_STATE[state_key] = new_inside
    return events



