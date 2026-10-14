                SELECT P.ST_NUMBER,
                       P.ADDR,
                       NVL(A.REGION, P.ADDR) AS REGION,
                       A.RAION,
                       A.ORD,
                       NVL(A.TRANSPORT_TYPE, '0') AS TRANSPORT_TYPE,
                       NVL(A.STOL, 0) AS NEEDS_HYDRO_BOARD,
                       NVL(A.STOL, 0) AS STOL,
                       A.PRIM1,
                       P.WARE_ID,
                       MAX(P.NAPR) AS NAPR,
                       COUNT(DISTINCT P.PALLET_UID) AS PALLETS_COUNT,
                       {weight_expr} AS WEIGHT_KG,
                       {volume_expr} AS VOLUME_M3,
                       MIN(P.STDATE) AS STDATE,
                       MIN(P.STDATE) AS DATE_LOAD,
                       MAX(P.TRANSTASK_ID) AS TRANSTASK_ID,
                       MAX(P.ZONE) AS ZONE,
                       MIN(P.ZONE_TIME_PLAN_IN) AS TIME_FROM,
                       MAX(P.ZONE_TIME_PLAN_OUT) AS TIME_TO,
                       NVL({verify_expr}, 0) AS VERIFY_PERC,
                       MAX(CASE WHEN R.ARTICUL IN ('Т0000008795', 'Т0000127793', 'Т0000127794') THEN 1 ELSE 0 END) AS SUGAR
                  FROM RABAEV.RRL_SBORKA_PALLETS P
                  JOIN RABAEV.RRL_SBORKA_PALLET_ROWS R ON R.PALLET_UID = P.PALLET_UID
                  LEFT JOIN RABAEV.RRL_ADDR A ON A.ADDR = P.ADDR
                  {where_sql}
                 GROUP BY P.ST_NUMBER, P.ADDR, A.REGION, A.RAION, A.ORD,
                          A.TRANSPORT_TYPE, A.STOL, A.PRIM1, P.WARE_ID
                  {having_sql}
                 ORDER BY A.ORD NULLS LAST, NVL(A.REGION, P.ADDR), P.ST_NUMBER, P.WARE_ID, P.ADDR
