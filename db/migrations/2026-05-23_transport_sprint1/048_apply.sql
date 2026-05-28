-- =============================================================================
-- Migration 048 — Sprint 1: расширение RRL_V_AVAILABLE_STS
-- =============================================================================
-- Добавляет в вьюху колонки, необходимые для полной таблицы СТ (16 колонок §3.3):
--   STOL       — требование стол-лифта (RRL_ADDR.STOL)
--   PRIM1      — примечание к адресу (RRL_ADDR.PRIM1)
--   DATE_LOAD  — дата первой паллеты СТ (MIN STDATE; замена MIN(CREATE_DATE))
--   SUGAR      — признак наличия сахара (MAX(RRL_SUGAR_HAS(ARTICUL)))
--
-- NEEDS_HYDRO_BOARD сохранён для обратной совместимости (= A.STOL).
-- Требует: RABAEV.RRL_SUGAR_HAS(p_articul VARCHAR2) RETURN NUMBER — должна существовать.
-- Применяется поверх 043. Безопасно повторно: CREATE OR REPLACE VIEW.
-- =============================================================================

prompt [048] Sprint 1 — расширение RRL_V_AVAILABLE_STS

CREATE OR REPLACE VIEW RABAEV.RRL_V_AVAILABLE_STS AS
SELECT
  P.ST_NUMBER,
  P.ADDR,
  NVL(A.REGION, P.ADDR)                                        AS REGION,
  A.RAION,
  A.ORD,
  A.SHIROTA,
  A.DOLGOTA,
  NVL(A.TRANSPORT_TYPE, '0')                                    AS TRANSPORT_TYPE,
  -- NEEDS_HYDRO_BOARD сохранён для обратной совместимости (= STOL)
  NVL(A.STOL, 0)                                                AS NEEDS_HYDRO_BOARD,
  NVL(A.STOL, 0)                                                AS STOL,
  A.PRIM1,
  P.WARE_ID,
  MAX(P.NAPR)                                                   AS NAPR,
  COUNT(DISTINCT P.PALLET_UID)                                  AS PALLETS_COUNT,
  ROUND(SUM(NVL(R.ORDER_WEIGHT, 0)), 0)                         AS WEIGHT_KG,
  ROUND(SUM(NVL(R.TARESIZE, 0) * NVL(R.PACK_COUNT, 0))
        / 1000000, 2)                                           AS VOLUME_M3,
  MIN(P.STDATE)                                                 AS STDATE,
  MIN(P.STDATE)                                                 AS DATE_LOAD,
  MAX(P.TRANSTASK_ID)                                           AS TRANSTASK_ID,
  MAX(RABAEV.RRL_ST_VERYFY_PERC(P.ST_NUMBER))                  AS VERIFY_PERC,
  NVL(MAX(RABAEV.RRL_SUGAR_HAS(R.ARTICUL)), 0)                  AS SUGAR
FROM RABAEV.RRL_SBORKA_PALLETS P
JOIN RABAEV.RRL_SBORKA_PALLET_ROWS R ON R.PALLET_UID = P.PALLET_UID
LEFT JOIN RABAEV.RRL_ADDR A ON A.ADDR = P.ADDR
WHERE P.CONDITION <> 2
GROUP BY
  P.ST_NUMBER, P.ADDR, A.REGION, A.RAION, A.ORD,
  A.SHIROTA, A.DOLGOTA, P.WARE_ID,
  A.TRANSPORT_TYPE, A.STOL, A.PRIM1;

COMMIT;
