-- =============================================================================
-- Migration 042 — Transport Dispatch Phase 1
-- =============================================================================
-- Создаёт вспомогательные объекты для API диспетчера отгрузки.
-- Не изменяет существующие таблицы (RRL_TRANSPORT_TASK, RRL_SBORKA_PALLETS и др.).
-- Безопасно применять повторно: CREATE OR REPLACE VIEW + IF NOT EXISTS для индексов.
-- =============================================================================

-- ---------------------------------------------------------------------------
-- 1. Представление свободных СТ для диспетчера
-- ---------------------------------------------------------------------------
-- Группирует паллеты по СТ, присоединяет адрес.
-- TRANSTASK_ID IS NULL → не назначено; NOT NULL → уже в рейсе.
-- ---------------------------------------------------------------------------
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

-- ---------------------------------------------------------------------------
-- 2. Индексы производительности (idempotent)
-- ---------------------------------------------------------------------------
DECLARE
  PROCEDURE ensure_index(p_name VARCHAR2, p_ddl VARCHAR2) IS
    v INTEGER;
  BEGIN
    SELECT COUNT(*) INTO v FROM user_indexes WHERE index_name = p_name;
    IF v = 0 THEN
      EXECUTE IMMEDIATE p_ddl;
      DBMS_OUTPUT.PUT_LINE('Created index ' || p_name);
    ELSE
      DBMS_OUTPUT.PUT_LINE('Index ' || p_name || ' already exists — skip');
    END IF;
  END;
BEGIN
  -- Быстрый поиск паллет рейса
  ensure_index(
    'IDX_SP_TRANSTASK',
    'CREATE INDEX RABAEV.IDX_SP_TRANSTASK ON RABAEV.RRL_SBORKA_PALLETS (TRANSTASK_ID, DELETED)'
  );
  -- Быстрый поиск паллет по дате сборки
  ensure_index(
    'IDX_SP_STDATE',
    'CREATE INDEX RABAEV.IDX_SP_STDATE ON RABAEV.RRL_SBORKA_PALLETS (STDATE, DELETED)'
  );
  -- Быстрый поиск рейсов по дате отгрузки
  ensure_index(
    'IDX_TT_SHIPDATE',
    'CREATE INDEX RABAEV.IDX_TT_SHIPDATE ON RABAEV.RRL_TRANSPORT_TASK (SHIPMENT_DATE, DELETED)'
  );
END;
/

COMMIT;
