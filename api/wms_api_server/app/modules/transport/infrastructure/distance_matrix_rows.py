"""Bounded rows for the existing distance-matrix MERGE; no execution or provider calls."""
from typing import Any

def matrix_merge_statements(addrs: list[dict],matrix: list[list[float]],durations: list[list[float]] | None,fresh_pair_keys: set,source: str) -> tuple[list,int,int]:
    n=len(addrs)
    merge_sql = """
        MERGE INTO RABAEV.RRL_ADDR_DISTANCE_MATRIX T
        USING (SELECT :from_addr AS FROM_ADDR, :to_addr AS TO_ADDR FROM DUAL) S
        ON (T.FROM_ADDR = S.FROM_ADDR AND T.TO_ADDR = S.TO_ADDR)
        WHEN MATCHED THEN
            UPDATE SET DISTANCE_KM = :dist_km,
                       DURATION_MIN = :dur,
                       DURATION_BASIS = :duration_basis,
                       SOURCE = :source,
                       UPDATED_AT = SYSDATE
        WHEN NOT MATCHED THEN
            INSERT (FROM_ADDR, TO_ADDR, DISTANCE_KM, DURATION_MIN, DURATION_BASIS, SOURCE, UPDATED_AT)
            VALUES (:from_addr, :to_addr, :dist_km, :dur, :duration_basis, :source, SYSDATE)
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
            duration_min = durations[i][j]if durations is not None else round(dist_km / 50.0 * 60, 0)
            statements.append(
                (
                    merge_sql,
                    {
                    "from_addr": addrs[i]["ADDR"],
                    "to_addr":   addrs[j]["ADDR"],
                    "dist_km":   dist_km,
                    "dur":       duration_min,
                    "duration_basis":"ROAD_PROFILE_ESTIMATE"if durations is not None else "SPEED_50_ESTIMATE",
                    "source":    source,
                    },
                )
            )
            computed_pairs += 1

    return statements,computed_pairs,skipped_pairs
