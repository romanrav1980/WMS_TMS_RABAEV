"""
distance_matrix_service.py — Пересчёт и сохранение матрицы расстояний.

Матрица хранится в RRL_ADDR_DISTANCE_MATRIX (FROM_ADDR VARCHAR2, TO_ADDR VARCHAR2,
DIST_KM NUMBER, DURATION_MIN NUMBER, SOURCE VARCHAR2, CALC_AT DATE).
Первичный ключ — (FROM_ADDR, TO_ADDR).

Пересчёт делается за один проход:
  1. Загрузить все геокодированные адреса.
  2. Построить матрицу N×N через RoutingProvider.
  3. Сохранить в Oracle через MERGE (идемпотентно).
"""

from __future__ import annotations

from typing import Any

from ..oracle_gateway import OracleGateway
from .routing import RoutingProvider, get_active_provider


class DistanceMatrixService:
    def __init__(self, gateway: OracleGateway | None = None) -> None:
        self.gateway = gateway or OracleGateway()

    def get_geocoded_addresses(self) -> list[dict[str, Any]]:
        return self.gateway.fetch_all(
            """
            SELECT ADDR, SHIROTA AS LAT, DOLGOTA AS LON
              FROM RABAEV.RRL_ADDR
             WHERE SHIROTA IS NOT NULL AND SHIROTA <> 0
               AND DOLGOTA IS NOT NULL AND DOLGOTA <> 0
             ORDER BY ADDR
            """
        )

    def rebuild(self, source: str = "auto") -> dict[str, Any]:
        """Пересчитывает матрицу и сохраняет в Oracle.

        source: 'auto' | 'haversine' | 'osrm' | 'valhalla'
        Возвращает: {"pairs": int, "source": str, "addresses": int}
        """
        if source == "auto":
            provider: RoutingProvider = get_active_provider()
        elif source == "haversine":
            from .routing import HaversineProvider
            provider = HaversineProvider()
        elif source == "osrm":
            from .routing import OsrmProvider
            provider = OsrmProvider()
        elif source == "valhalla":
            from .routing import ValhallaProvider
            provider = ValhallaProvider()
        else:
            provider = get_active_provider()

        addrs = self.get_geocoded_addresses()
        if not addrs:
            return {"pairs": 0, "source": provider.name, "addresses": 0}

        n = len(addrs)
        points = [(float(a["LAT"]), float(a["LON"])) for a in addrs]
        matrix = provider.build_matrix(points)

        pairs = 0
        for i in range(n):
            for j in range(n):
                if i == j:
                    continue
                dist_km = matrix[i][j]
                # avg speed 50 km/h for duration estimate
                duration_min = round(dist_km / 50.0 * 60, 0)
                self.gateway.execute(
                    """
                    MERGE INTO RABAEV.RRL_ADDR_DISTANCE_MATRIX T
                    USING (SELECT :from_addr AS FROM_ADDR, :to_addr AS TO_ADDR FROM DUAL) S
                    ON (T.FROM_ADDR = S.FROM_ADDR AND T.TO_ADDR = S.TO_ADDR)
                    WHEN MATCHED THEN
                        UPDATE SET DIST_KM = :dist_km,
                                   DURATION_MIN = :dur,
                                   SOURCE = :source,
                                   CALC_AT = SYSDATE
                    WHEN NOT MATCHED THEN
                        INSERT (FROM_ADDR, TO_ADDR, DIST_KM, DURATION_MIN, SOURCE, CALC_AT)
                        VALUES (:from_addr, :to_addr, :dist_km, :dur, :source, SYSDATE)
                    """,
                    {
                        "from_addr": addrs[i]["ADDR"],
                        "to_addr":   addrs[j]["ADDR"],
                        "dist_km":   dist_km,
                        "dur":       duration_min,
                        "source":    provider.name,
                    },
                )
                pairs += 1

        return {"pairs": pairs, "source": provider.name, "addresses": n}

    def get_matrix_as_dict(
        self,
        addr_list: list[str],
    ) -> dict[tuple[str, str], float]:
        """Загружает подматрицу из Oracle для заданных адресов."""
        if not addr_list:
            return {}
        placeholders = ",".join(f":a{i}" for i in range(len(addr_list)))
        params = {f"a{i}": a for i, a in enumerate(addr_list)}
        rows = self.gateway.fetch_all(
            f"""
            SELECT FROM_ADDR, TO_ADDR, DIST_KM
              FROM RABAEV.RRL_ADDR_DISTANCE_MATRIX
             WHERE FROM_ADDR IN ({placeholders})
               AND TO_ADDR   IN ({placeholders})
            """,
            params,
        )
        return {(r["FROM_ADDR"], r["TO_ADDR"]): float(r["DIST_KM"]) for r in rows}
