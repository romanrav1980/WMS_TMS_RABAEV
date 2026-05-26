-- Sprint 11: Модель операций и нормативы (база ARM)
-- Создаёт RRL_TRANSPORT_NORMS и RRL_TT_OPERATIONS
-- Идемпотентно: таблицы и последовательности создаются только если отсутствуют.

-- Последовательность для RRL_TRANSPORT_NORMS
DECLARE
  v_cnt NUMBER;
BEGIN
  SELECT COUNT(*) INTO v_cnt FROM user_sequences WHERE sequence_name = 'SEQ_TRANSPORT_NORMS';
  IF v_cnt = 0 THEN
    EXECUTE IMMEDIATE 'CREATE SEQUENCE RABAEV.SEQ_TRANSPORT_NORMS START WITH 1 INCREMENT BY 1 NOCACHE NOCYCLE';
  END IF;
END;
/

-- Таблица нормативов операций
DECLARE
  v_cnt NUMBER;
BEGIN
  SELECT COUNT(*) INTO v_cnt FROM user_tables WHERE table_name = 'RRL_TRANSPORT_NORMS';
  IF v_cnt = 0 THEN
    EXECUTE IMMEDIATE '
      CREATE TABLE RABAEV.RRL_TRANSPORT_NORMS (
        ID              NUMBER(10)    NOT NULL,
        OPERATION_CODE  VARCHAR2(30)  NOT NULL,
        DURATION_MIN    NUMBER(6,2)   NOT NULL,
        PER_UNIT        NUMBER(1)     DEFAULT 0 NOT NULL,
        COMMENT_TXT     VARCHAR2(200),
        CONSTRAINT PK_RRL_TRANSPORT_NORMS PRIMARY KEY (ID),
        CONSTRAINT UQ_RRL_TN_CODE UNIQUE (OPERATION_CODE)
      )
    ';
  END IF;
END;
/

-- Последовательность для RRL_TT_OPERATIONS
DECLARE
  v_cnt NUMBER;
BEGIN
  SELECT COUNT(*) INTO v_cnt FROM user_sequences WHERE sequence_name = 'SEQ_TT_OPERATIONS';
  IF v_cnt = 0 THEN
    EXECUTE IMMEDIATE 'CREATE SEQUENCE RABAEV.SEQ_TT_OPERATIONS START WITH 1 INCREMENT BY 1 NOCACHE NOCYCLE';
  END IF;
END;
/

-- Таблица план/факт операций рейса
DECLARE
  v_cnt NUMBER;
BEGIN
  SELECT COUNT(*) INTO v_cnt FROM user_tables WHERE table_name = 'RRL_TT_OPERATIONS';
  IF v_cnt = 0 THEN
    EXECUTE IMMEDIATE '
      CREATE TABLE RABAEV.RRL_TT_OPERATIONS (
        ID              NUMBER(10)    NOT NULL,
        TT_ID           NUMBER(10)    NOT NULL,
        OPERATION_CODE  VARCHAR2(30)  NOT NULL,
        ORD             NUMBER(3)     NOT NULL,
        DURATION_MIN    NUMBER(6,2),
        PLAN_START      DATE,
        PLAN_END        DATE,
        FACT_START      DATE,
        FACT_END        DATE,
        NOTE            VARCHAR2(200),
        CONSTRAINT PK_RRL_TT_OPERATIONS PRIMARY KEY (ID),
        CONSTRAINT FK_TTOPS_TASK FOREIGN KEY (TT_ID)
          REFERENCES RABAEV.RRL_TRANSPORT_TASK(ID)
      )
    ';
    EXECUTE IMMEDIATE '
      CREATE INDEX IDX_TTOPS_TT_ID ON RABAEV.RRL_TT_OPERATIONS(TT_ID)
    ';
  END IF;
END;
/

-- Seed начальных нормативов (MERGE — идемпотентно)
MERGE INTO RABAEV.RRL_TRANSPORT_NORMS tgt
USING (
  SELECT 'DOCK_ASSIGN'    AS code,  15 AS dur, 0 AS pu, 'Постановка на ворота'        AS cmt FROM DUAL UNION ALL
  SELECT 'WAIT_LOAD',                10,        0,       'Ожидание начала погрузки'    FROM DUAL UNION ALL
  SELECT 'LOADING',                   3,        1,       'Погрузка (мин/палл)'         FROM DUAL UNION ALL
  SELECT 'CLOSE_GATE',               10,        0,       'Закрытие ворот'              FROM DUAL UNION ALL
  SELECT 'DOCUMENTS',                10,        0,       'Оформление документов'       FROM DUAL UNION ALL
  SELECT 'DEPART',                    0,        0,       'Выезд'                       FROM DUAL UNION ALL
  SELECT 'DRIVE',                     0,        0,       'Движение к клиенту'          FROM DUAL UNION ALL
  SELECT 'UNLOAD',                    3,        1,       'Разгрузка у клиента (мин/палл)' FROM DUAL UNION ALL
  SELECT 'LOAD_RETURNS',             15,        0,       'Погрузка возвратов'          FROM DUAL UNION ALL
  SELECT 'DRIVE_BACK',                0,        0,       'Обратный путь'               FROM DUAL UNION ALL
  SELECT 'RETURN_HANDOVER',          20,        0,       'Сдача возвратов'             FROM DUAL UNION ALL
  SELECT 'CLEAN_RETURNS',            20,        0,       'Очистка и подготовка ТС'     FROM DUAL
) src ON (tgt.OPERATION_CODE = src.code)
WHEN NOT MATCHED THEN
  INSERT (ID, OPERATION_CODE, DURATION_MIN, PER_UNIT, COMMENT_TXT)
  VALUES (RABAEV.SEQ_TRANSPORT_NORMS.NEXTVAL, src.code, src.dur, src.pu, src.cmt)
WHEN MATCHED THEN
  UPDATE SET tgt.DURATION_MIN = src.dur, tgt.PER_UNIT = src.pu;

COMMIT;
