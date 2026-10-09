"""
distance_matrix_service.py — Пересчёт и сохранение матрицы расстояний.

Матрица хранится в RRL_ADDR_DISTANCE_MATRIX (FROM_ADDR VARCHAR2, TO_ADDR VARCHAR2,
DISTANCE_KM NUMBER, DURATION_MIN NUMBER, SOURCE VARCHAR2, UPDATED_AT DATE).
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


def _upper_keys(row: dict[str, Any]) -> dict[str, Any]:
    return {str(key).upper(): value for key, value in row.items()}


class DistanceMatrixService:
    def __init__(self, gateway: OracleGateway | None = None) -> None:
        self.gateway = gateway or OracleGateway()

    def _fetch_all(self, sql: str, params: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        return [_upper_keys(row) for row in self.gateway.fetch_all(sql, params)]

    def get_geocoded_addresses(self) -> list[dict[str, Any]]:
        return self._fetch_all(
            """
            SELECT ADDR, SHIROTA AS LAT, DOLGOTA AS LON
              FROM RABAEV.RRL_ADDR
             WHERE SHIROTA IS NOT NULL AND SHIROTA <> 0
               AND DOLGOTA IS NOT NULL AND DOLGOTA <> 0
             ORDER BY ADDR
            """
        )

    def _count_fresh_pairs(self, source: str, max_age_hours: int | None) -> int:
        freshness_clause = ""
        params: dict[str, Any] = {"source": source}
        if max_age_hours is not None and max_age_hours > 0:
            freshness_clause = "AND M.UPDATED_AT >= SYSDATE - (:max_age_hours / 24)"
            params["max_age_hours"] = max_age_hours
        rows = self._fetch_all(
            f"""
            WITH A AS (
                SELECT ADDR
                  FROM RABAEV.RRL_ADDR
                 WHERE SHIROTA IS NOT NULL AND SHIROTA <> 0
                   AND DOLGOTA IS NOT NULL AND DOLGOTA <> 0
            )
            SELECT COUNT(*) AS CNT
              FROM RABAEV.RRL_ADDR_DISTANCE_MATRIX M
              JOIN A F ON F.ADDR = M.FROM_ADDR
              JOIN A T ON T.ADDR = M.TO_ADDR
             WHERE M.FROM_ADDR <> M.TO_ADDR
               AND M.SOURCE = :source
               {freshness_clause}
            """,
            params,
        )
        return int(rows[0]["CNT"]) if rows else 0

    def _fetch_fresh_pair_keys(self, source: str, max_age_hours: int | None) -> set[tuple[str, str]]:
        freshness_clause = ""
        params: dict[str, Any] = {"source": source}
        if max_age_hours is not None and max_age_hours > 0:
            freshness_clause = "AND M.UPDATED_AT >= SYSDATE - (:max_age_hours / 24)"
            params["max_age_hours"] = max_age_hours
        rows = self._fetch_all(
            f"""
            WITH A AS (
                SELECT ADDR
                  FROM RABAEV.RRL_ADDR
                 WHERE SHIROTA IS NOT NULL AND SHIROTA <> 0
                   AND DOLGOTA IS NOT NULL AND DOLGOTA <> 0
            )
            SELECT M.FROM_ADDR, M.TO_ADDR
              FROM RABAEV.RRL_ADDR_DISTANCE_MATRIX M
              JOIN A F ON F.ADDR = M.FROM_ADDR
              JOIN A T ON T.ADDR = M.TO_ADDR
             WHERE M.FROM_ADDR <> M.TO_ADDR
               AND M.SOURCE = :source
               {freshness_clause}
            """,
            params,
        )
        return {(str(r["FROM_ADDR"]), str(r["TO_ADDR"])) for r in rows}

    def rebuild(
        self,
        source: str = "auto",
        *,
        force: bool = False,
        max_age_hours: int | None = 24 * 30,
    ) -> dict[str, Any]:
        """Пересчитывает матрицу и сохраняет в Oracle.

        source: 'auto' | 'haversine' | 'osrm' | 'valhalla'
        Возвращает total pairs and how many pairs were actually recomputed.
        """
        is_auto = source == "auto"
        if is_auto:
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
            return {
                "pairs": 0,
                "computed_pairs": 0,
                "skipped_pairs": 0,
                "source": provider.name,
                "addresses": 0,
                "cached": True,
                "force": force,
            }

        n = len(addrs)
        expected_pairs = n * (n - 1) if n > 0 else 0
        if not force:
            fresh_pairs = self._count_fresh_pairs(provider.name, max_age_hours)
            if fresh_pairs >= expected_pairs:
                return {
                    "pairs": expected_pairs,
                    "computed_pairs": 0,
                    "skipped_pairs": expected_pairs,
                    "source": provider.name,
                    "addresses": n,
                    "cached": True,
                    "force": False,
                }
            if is_auto:
                for cached_source in ("osrm", "valhalla", "haversine"):
                    if cached_source == provider.name:
                        continue
                    fresh_pairs = self._count_fresh_pairs(cached_source, max_age_hours)
                    if fresh_pairs >= expected_pairs:
                        return {
                            "pairs": expected_pairs,
                            "computed_pairs": 0,
                            "skipped_pairs": expected_pairs,
                            "source": cached_source,
                            "addresses": n,
                            "cached": True,
                            "force": False,
                        }

            fresh_pair_keys = self._fetch_fresh_pair_keys(provider.name, max_age_hours)
        else:
            fresh_pair_keys = set()

        points = [(float(a["LAT"]), float(a["LON"])) for a in addrs]
        try:
            matrix = provider.build_matrix(points)
        except Exception:
            if not is_auto:
                raise
            from .routing import HaversineProvider
            provider = HaversineProvider()
            if not force:
                fresh_pairs = self._count_fresh_pairs(provider.name, max_age_hours)
                if fresh_pairs >= expected_pairs:
                    return {
                        "pairs": expected_pairs,
                        "computed_pairs": 0,
                        "skipped_pairs": expected_pairs,
                        "source": provider.name,
                        "addresses": n,
                        "cached": True,
                        "force": False,
                    }
                fresh_pair_keys = self._fetch_fresh_pair_keys(provider.name, max_age_hours)
            matrix = provider.build_matrix(points)

        merge_sql = """
            MERGE INTO RABAEV.RRL_ADDR_DISTANCE_MATRIX T
            USING (SELECT :from_addr AS FROM_ADDR, :to_addr AS TO_ADDR FROM DUAL) S
            ON (T.FROM_ADDR = S.FROM_ADDR AND T.TO_ADDR = S.TO_ADDR)
            WHEN MATCHED THEN
                UPDATE SET DISTANCE_KM = :dist_km,
                           DURATION_MIN = :dur,
                           SOURCE = :source,
                           UPDATED_AT = SYSDATE
            WHEN NOT MATCHED THEN
                INSERT (FROM_ADDR, TO_ADDR, DISTANCE_KM, DURATION_MIN, SOURCE, UPDATED_AT)
                VALUES (:from_addr, :to_addr, :dist_km, :dur, :source, SYSDATE)
        """
        statements: list[tuple[str, dict[str, Any]]] = []
        computed_pairs = 0
        skipped_pairs = 0
        for i in range(n):
            for j in range(n):
                if i == j:
                    continue
                pair_key = (str(addrs[i]["ADDR"]), str(addrs[j]["ADDR"]))
                if pair_key in fresh_pair_keys:
                    skipped_pairs += 1
                    continue
                dist_km = matrix[i][j]
                # avg speed 50 km/h for duration estimate
                duration_min = round(dist_km / 50.0 * 60, 0)
                statements.append(
                    (
                        merge_sql,
                        {
                        "from_addr": addrs[i]["ADDR"],
                        "to_addr":   addrs[j]["ADDR"],
                        "dist_km":   dist_km,
                        "dur":       duration_min,
                        "source":    provider.name,
                        },
                    )
                )
                computed_pairs += 1

        if statements:
            self.gateway.execute_many(statements)

        return {
            "pairs": expected_pairs,
            "computed_pairs": computed_pairs,
            "skipped_pairs": skipped_pairs,
            "source": provider.name,
            "addresses": n,
            "cached": computed_pairs == 0,
            "force": force,
        }

    def get_matrix_as_dict(
        self,
        addr_list: list[str],
    ) -> dict[tuple[str, str], float]:
        """Загружает подматрицу из Oracle для заданных адресов."""
        if not addr_list:
            return {}
        placeholders = ",".join(f":a{i}" for i in range(len(addr_list)))
        params = {f"a{i}": a for i, a in enumerate(addr_list)}
        rows = self._fetch_all(
            f"""
            SELECT FROM_ADDR, TO_ADDR, DISTANCE_KM
              FROM RABAEV.RRL_ADDR_DISTANCE_MATRIX
             WHERE FROM_ADDR IN ({placeholders})
               AND TO_ADDR   IN ({placeholders})
            """,
            params,
        )
        return {(r["FROM_ADDR"], r["TO_ADDR"]): float(r["DISTANCE_KM"]) for r in rows}
