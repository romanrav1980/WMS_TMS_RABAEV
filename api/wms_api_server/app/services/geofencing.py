"""
geofencing.py — Sprint 118-119: Geofencing logic.

Детекция входа/выхода машины в геозоны адресов активных рейсов.
Вызывается из /api/gps/track при каждом поступлении координаты.
"""

import logging
import math
from typing import Any

log = logging.getLogger(__name__)

_GEO_STATE: dict[str, set[int]] = {}  # vehicle_id → {addr_id} inside


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
    Sprint 119: при enter/exit — автоматически выставляет fact операций UNLOAD.
    """
    events: list[dict] = []
    if not lat or not lon:
        return events

    # Получаем активные рейсы машины с адресами и их координатами
    rows = gateway.fetch_all(
        """
        SELECT TT.ID AS TASK_ID, A.ID AS ADDR_ID, A.ADDR,
               A.LATITUDE, A.LONGITUDE,
               NVL(A.GEO_FENCE_RADIUS_M, 200) AS RADIUS_M
          FROM RABAEV.RRL_TRANSPORT_TASK TT
          JOIN RABAEV.RRL_SBORKA_PALLETS SP ON SP.TRANSTASK_ID = TT.ID AND NVL(SP.DELETED,0)=0
          JOIN RABAEV.RRL_ADDR A ON A.ADDR = SP.ADDR
         WHERE TT.TRANSPORT IN (
           SELECT NUM_PLAT FROM RABAEV.RRL_TR_VEHICLE WHERE ID=:vid AND NVL(DELETED,0)=0
         )
           AND TT.CONDITION NOT IN ('Отгружен','Отменён')
           AND NVL(TT.DELETED,0)=0
           AND A.LATITUDE IS NOT NULL AND A.LONGITUDE IS NOT NULL
         GROUP BY TT.ID, A.ID, A.ADDR, A.LATITUDE, A.LONGITUDE, A.GEO_FENCE_RADIUS_M
        """,
        {"vid": vehicle_id},
    )

    state_key = str(vehicle_id)
    current_inside = _GEO_STATE.get(state_key, set())
    new_inside: set[int] = set()

    for r in rows:
        addr_id = int(r.get("addr_id") or 0)
        addr_lat = float(r.get("latitude") or 0)
        addr_lon = float(r.get("longitude") or 0)
        radius = float(r.get("radius_m") or 200)
        task_id = int(r.get("task_id") or 0)

        dist = haversine_m(lat, lon, addr_lat, addr_lon)
        inside = dist <= radius

        if inside:
            new_inside.add(addr_id)
            if addr_id not in current_inside:
                # Entered geofence
                events.append({"event": "enter", "addr_id": addr_id, "task_id": task_id, "addr": r.get("addr")})
                _auto_mark_unload_start(gateway, task_id, addr_id)
        else:
            if addr_id in current_inside:
                # Exited geofence
                events.append({"event": "exit", "addr_id": addr_id, "task_id": task_id, "addr": r.get("addr")})
                _auto_mark_unload_done(gateway, task_id, addr_id)

    _GEO_STATE[state_key] = new_inside
    return events


def _auto_mark_unload_start(gateway: Any, task_id: int, addr_id: int) -> None:
    """Sprint 119: авто-отметка начала UNLOAD при входе в геозону."""
    try:
        gateway.execute(
            """
            UPDATE RABAEV.RRL_TT_OPERATIONS
               SET FACT_START = NVL(FACT_START, SYSDATE),
                   NOTE = NVL(NOTE, '') || ' [GPS-auto]'
             WHERE TT_ID = :tid
               AND OPERATION_CODE = 'UNLOAD'
               AND FACT_START IS NULL
               AND ROWNUM = 1
            """,
            {"tid": task_id},
        )
        log.debug("Auto-marked UNLOAD start for task %d addr_id %d", task_id, addr_id)
    except Exception as exc:
        log.warning("Auto mark UNLOAD start failed: %s", exc)


def _auto_mark_unload_done(gateway: Any, task_id: int, addr_id: int) -> None:
    """Sprint 119: авто-отметка завершения UNLOAD при выходе из геозоны."""
    try:
        gateway.execute(
            """
            UPDATE RABAEV.RRL_TT_OPERATIONS
               SET FACT_END = NVL(FACT_END, SYSDATE),
                   NOTE = NVL(NOTE, '') || ' [GPS-auto]'
             WHERE TT_ID = :tid
               AND OPERATION_CODE = 'UNLOAD'
               AND FACT_START IS NOT NULL
               AND FACT_END IS NULL
               AND ROWNUM = 1
            """,
            {"tid": task_id},
        )
        log.debug("Auto-marked UNLOAD done for task %d addr_id %d", task_id, addr_id)
    except Exception as exc:
        log.warning("Auto mark UNLOAD done failed: %s", exc)
