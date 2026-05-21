-- Migration 043 rollback — восстановить RRL_V_AVAILABLE_STS в состояние из 042
CREATE OR REPLACE VIEW RABAEV.RRL_V_AVAILABLE_STS AS
SELECT
  P.ST_NUMBER,
  P.ADDR,
  NVL(A.REGION, P.ADDR)                                      AS REGION,
  A.RAION,
  A.ORD,
  A.SHIROTA,
  A.DOLGOTA,
  NVL(A.TRANSPORT_TYPE, '0')                                  AS TRANSPORT_TYPE,
  NVL(A.STOL, 0)                                              AS NEEDS_HYDRO_BOARD,
  P.WARE_ID,
  COUNT(DISTINCT P.PALLET_UID)                                AS PALLETS_COUNT,
  ROUND(SUM(NVL(R.ORDER_WEIGHT, 0)), 0)                       AS WEIGHT_KG,
  ROUND(SUM(NVL(R.TARESIZE, 0) * NVL(R.PACK_COUNT, 0))
        / 1000000, 2)                                         AS VOLUME_M3,
  MIN(P.STDATE)                                               AS STDATE,
  MAX(P.TRANSTASK_ID)                                         AS TRANSTASK_ID
FROM RABAEV.RRL_SBORKA_PALLETS P
JOIN RABAEV.RRL_SBORKA_PALLET_ROWS R ON R.PALLET_UID = P.PALLET_UID
LEFT JOIN RABAEV.RRL_ADDR A ON A.ADDR = P.ADDR
WHERE (P.DELETED IS NULL OR P.DELETED <> 1)
GROUP BY
  P.ST_NUMBER, P.ADDR, A.REGION, A.RAION, A.ORD,
  A.SHIROTA, A.DOLGOTA, P.WARE_ID, A.TRANSPORT_TYPE, A.STOL;

COMMIT;