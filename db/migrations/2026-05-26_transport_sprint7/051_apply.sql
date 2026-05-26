-- =============================================================================
-- Migration 051 — Transport Sprint 7: карта заказов и схема планировщика
-- =============================================================================
-- 1. Новые поля в RRL_ADDR: MAX_VEHICLE_TONS, UNLOAD_NORM_MIN, TW_STRICT
--    (SHIROTA, DOLGOTA уже существуют с момента создания таблицы)
-- 2. Таблица RRL_ADDR_DISTANCE_MATRIX — кэш матрицы расстояний
-- 3. Таблица RRL_PLANNER_PLANS + последовательность SEQ_PLANNER_PLANS
-- 4. Обновление RRL_V_AVAILABLE_STS: добавляет MAX_VEHICLE_TONS, TW_STRICT,
--    UNLOAD_NORM_MIN в SELECT и GROUP BY
-- 5. Заполнение тестовых координат (Московский регион) для seed-адресов
-- =============================================================================

prompt [051] Добавление полей планировщика в RRL_ADDR

-- ---------------------------------------------------------------------------
-- 1. Новые колонки в RRL_ADDR (идемпотентно)
-- ---------------------------------------------------------------------------
DECLARE
  PROCEDURE ensure_col(p_tbl VARCHAR2, p_col VARCHAR2, p_ddl VARCHAR2) IS
    v INTEGER;
  BEGIN
    SELECT COUNT(*) INTO v FROM user_tab_columns
     WHERE table_name = p_tbl AND column_name = p_col;
    IF v = 0 THEN
      EXECUTE IMMEDIATE 'ALTER TABLE RABAEV.' || p_tbl
                     || ' ADD (' || p_col || ' ' || p_ddl || ')';
      DBMS_OUTPUT.PUT_LINE('Added column ' || p_col || ' to ' || p_tbl);
    ELSE
      DBMS_OUTPUT.PUT_LINE('Column ' || p_col || ' already exists — skip');
    END IF;
  END;
BEGIN
  ensure_col('RRL_ADDR', 'MAX_VEHICLE_TONS', 'NUMBER(4) DEFAULT 20');
  ensure_col('RRL_ADDR', 'UNLOAD_NORM_MIN',  'NUMBER(5) DEFAULT 30');
  ensure_col('RRL_ADDR', 'TW_STRICT',        'NUMBER(1) DEFAULT 0');
END;
/

-- ---------------------------------------------------------------------------
-- 2. Таблица матрицы расстояний (идемпотентно)
-- ---------------------------------------------------------------------------
DECLARE
  v INTEGER;
BEGIN
  SELECT COUNT(*) INTO v FROM user_tables WHERE table_name = 'RRL_ADDR_DISTANCE_MATRIX';
  IF v = 0 THEN
    EXECUTE IMMEDIATE
      'CREATE TABLE RABAEV.RRL_ADDR_DISTANCE_MATRIX (
         FROM_ADDR    VARCHAR2(200) NOT NULL,
         TO_ADDR      VARCHAR2(200) NOT NULL,
         DISTANCE_KM  NUMBER(8,2),
         DURATION_MIN NUMBER(8,2),
         SOURCE       VARCHAR2(10) DEFAULT ''HAVERSINE'',
         UPDATED_AT   DATE DEFAULT SYSDATE,
         CONSTRAINT PK_DIST_MATRIX PRIMARY KEY (FROM_ADDR, TO_ADDR)
       )';
    DBMS_OUTPUT.PUT_LINE('Created table RRL_ADDR_DISTANCE_MATRIX');
  ELSE
    DBMS_OUTPUT.PUT_LINE('Table RRL_ADDR_DISTANCE_MATRIX already exists — skip');
  END IF;
END;
/

-- ---------------------------------------------------------------------------
-- 3. Таблица планов + последовательность (идемпотентно)
-- ---------------------------------------------------------------------------
DECLARE
  v_tbl INTEGER;
  v_seq INTEGER;
BEGIN
  SELECT COUNT(*) INTO v_tbl FROM user_tables WHERE table_name = 'RRL_PLANNER_PLANS';
  IF v_tbl = 0 THEN
    EXECUTE IMMEDIATE
      'CREATE TABLE RABAEV.RRL_PLANNER_PLANS (
         ID         NUMBER(10),
         PLAN_DATE  DATE         NOT NULL,
         SOLVER     VARCHAR2(20),
         SCORE      NUMBER(5,2),
         STATUS     VARCHAR2(20) DEFAULT ''DRAFT'',
         PAYLOAD    CLOB,
         CREATED_AT DATE         DEFAULT SYSDATE,
         CREATED_BY VARCHAR2(50),
         CONSTRAINT PK_PLANNER_PLANS PRIMARY KEY (ID)
       )';
    DBMS_OUTPUT.PUT_LINE('Created table RRL_PLANNER_PLANS');
  END IF;

  SELECT COUNT(*) INTO v_seq FROM user_sequences WHERE sequence_name = 'SEQ_PLANNER_PLANS';
  IF v_seq = 0 THEN
    EXECUTE IMMEDIATE 'CREATE SEQUENCE RABAEV.SEQ_PLANNER_PLANS START WITH 1 INCREMENT BY 1 NOCACHE';
    DBMS_OUTPUT.PUT_LINE('Created sequence SEQ_PLANNER_PLANS');
  END IF;
END;
/

-- ---------------------------------------------------------------------------
-- 4. Обновление вьюхи RRL_V_AVAILABLE_STS — добавляем поля планировщика
-- ---------------------------------------------------------------------------
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
  NVL(MAX(RABAEV.RRL_SUGAR_HAS(R.ARTICUL)), 0)                  AS SUGAR,
  NVL(A.MAX_VEHICLE_TONS, 20)                                   AS MAX_VEHICLE_TONS,
  NVL(A.TW_STRICT, 0)                                          AS TW_STRICT,
  NVL(A.UNLOAD_NORM_MIN, 30)                                    AS UNLOAD_NORM_MIN
FROM RABAEV.RRL_SBORKA_PALLETS P
JOIN RABAEV.RRL_SBORKA_PALLET_ROWS R ON R.PALLET_UID = P.PALLET_UID
LEFT JOIN RABAEV.RRL_ADDR A ON A.ADDR = P.ADDR
WHERE P.CONDITION <> 2
GROUP BY
  P.ST_NUMBER, P.ADDR, A.REGION, A.RAION, A.ORD,
  A.SHIROTA, A.DOLGOTA, P.WARE_ID,
  A.TRANSPORT_TYPE, A.STOL, A.PRIM1,
  A.MAX_VEHICLE_TONS, A.TW_STRICT, A.UNLOAD_NORM_MIN;

-- ---------------------------------------------------------------------------
-- 5. Тестовые координаты для seed-адресов «Добра Цен» (Московский регион)
--    ORA_HASH гарантирует детерминированное распределение без дублей
-- ---------------------------------------------------------------------------
UPDATE RABAEV.RRL_ADDR
   SET SHIROTA = 55.55 + MOD(ORA_HASH(ADDR),     300) / 1000.0,
       DOLGOTA = 37.10 + MOD(ORA_HASH(ADDR, 17), 500) / 1000.0
 WHERE (SHIROTA IS NULL OR SHIROTA = 0)
   AND ADDR LIKE 'ДЦ%';

COMMIT;
