-- 052_apply.sql — Sprint 8: матрица расстояний + VRP-планировщик
-- Добавляет APPLIED_AT в RRL_PLANNER_PLANS (если таблица создана в 051).
-- RRL_ADDR_DISTANCE_MATRIX — гарантирует индекс на FROM_ADDR.
-- Всё идемпотентно.

-- ---------------------------------------------------------------------------
-- 1. Добавить APPLIED_AT в RRL_PLANNER_PLANS (если ещё нет)
-- ---------------------------------------------------------------------------
DECLARE
  v_cnt NUMBER;
BEGIN
  SELECT COUNT(*) INTO v_cnt
    FROM user_tab_columns
   WHERE table_name = 'RRL_PLANNER_PLANS'
     AND column_name = 'APPLIED_AT';
  IF v_cnt = 0 THEN
    EXECUTE IMMEDIATE
      'ALTER TABLE RABAEV.RRL_PLANNER_PLANS ADD (APPLIED_AT DATE)';
  END IF;
END;
/

-- ---------------------------------------------------------------------------
-- 2. Индекс на RRL_ADDR_DISTANCE_MATRIX (FROM_ADDR) для быстрой подматрицы
-- ---------------------------------------------------------------------------
DECLARE
  v_cnt NUMBER;
BEGIN
  SELECT COUNT(*) INTO v_cnt
    FROM user_indexes
   WHERE index_name = 'IDX_RLADM_FROM';
  IF v_cnt = 0 THEN
    EXECUTE IMMEDIATE
      'CREATE INDEX RABAEV.IDX_RLADM_FROM ON RABAEV.RRL_ADDR_DISTANCE_MATRIX(FROM_ADDR)';
  END IF;
END;
/

-- ---------------------------------------------------------------------------
-- 3. Индекс на RRL_PLANNER_PLANS (PLAN_DATE) для быстрого поиска по дате
-- ---------------------------------------------------------------------------
DECLARE
  v_cnt NUMBER;
BEGIN
  SELECT COUNT(*) INTO v_cnt
    FROM user_indexes
   WHERE index_name = 'IDX_RLP_PLANDATE';
  IF v_cnt = 0 THEN
    EXECUTE IMMEDIATE
      'CREATE INDEX RABAEV.IDX_RLP_PLANDATE ON RABAEV.RRL_PLANNER_PLANS(PLAN_DATE)';
  END IF;
END;
/

COMMIT;
