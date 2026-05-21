-- =============================================================================
-- Migration 041 — Topology Grid Editor: aisle distances + pick-face slots
-- =============================================================================
-- Добавляет три столбца к RRL_TOPOLOGY_AISLE для хранения расстояний аллей,
-- рассчитываемых редактором сетки.
-- Создаёт таблицу RRL_TOPOLOGY_PICK_FACE_SLOT для мелкоштучного деления ячеек.
--
-- Безопасно применять повторно (идемпотентные проверки через user_tab_columns).
-- =============================================================================

-- ---------------------------------------------------------------------------
-- 1. RRL_TOPOLOGY_AISLE — добавить столбцы для редактора сетки
-- ---------------------------------------------------------------------------
DECLARE
  PROCEDURE ensure_col(p_table VARCHAR2, p_col VARCHAR2, p_ddl VARCHAR2) IS
    v INTEGER;
  BEGIN
    SELECT COUNT(*) INTO v
      FROM user_tab_columns
     WHERE table_name = p_table
       AND column_name = p_col;
    IF v = 0 THEN
      EXECUTE IMMEDIATE p_ddl;
      DBMS_OUTPUT.PUT_LINE('Added column ' || p_table || '.' || p_col);
    ELSE
      DBMS_OUTPUT.PUT_LINE('Column ' || p_table || '.' || p_col || ' already exists — skip');
    END IF;
  END;
BEGIN
  -- Отображаемое имя аллеи (пользователь задаёт в редакторе)
  ensure_col(
    'RRL_TOPOLOGY_AISLE',
    'AISLE_LABEL',
    'ALTER TABLE RABAEV.RRL_TOPOLOGY_AISLE ADD (AISLE_LABEL VARCHAR2(100))'
  );

  -- Расстояние аллеи от начала склада в метрах (для расчёта длины маршрута)
  -- По умолчанию NULL — значит «не задано редактором», сервис подставит формулу
  ensure_col(
    'RRL_TOPOLOGY_AISLE',
    'DISTANCE_FROM_START_M',
    'ALTER TABLE RABAEV.RRL_TOPOLOGY_AISLE ADD (DISTANCE_FROM_START_M NUMBER(8,2) DEFAULT NULL)'
  );

  -- Ширина прохода аллеи (используется при расчёте расстояний по умолчанию)
  ensure_col(
    'RRL_TOPOLOGY_AISLE',
    'AISLE_WIDTH_M',
    'ALTER TABLE RABAEV.RRL_TOPOLOGY_AISLE ADD (AISLE_WIDTH_M NUMBER(5,2) DEFAULT 3.5)'
  );
END;
/

-- ---------------------------------------------------------------------------
-- 2. RRL_TOPOLOGY_PICK_FACE_SLOT — мелкоштучные слоты внутри одного паллето-места
-- ---------------------------------------------------------------------------
-- Одна физическая ячейка (CELL_ID) может быть разделена на SLOT_COLS × SLOT_ROWS
-- внутренних слотов. Каждый слот адресуется при операциях отбора отдельно.
--
-- Пример: ячейка 800×1800 мм, деление 3×3 → 9 слотов А1, А2, А3, Б1, Б2, Б3, В1, В2, В3.
-- ---------------------------------------------------------------------------
DECLARE
  v INTEGER;
BEGIN
  SELECT COUNT(*) INTO v
    FROM user_tables
   WHERE table_name = 'RRL_TOPOLOGY_PICK_FACE_SLOT';

  IF v = 0 THEN
    EXECUTE IMMEDIATE '
      CREATE TABLE RABAEV.RRL_TOPOLOGY_PICK_FACE_SLOT (
        SLOT_ID       NUMBER(10)    NOT NULL,
        CELL_ID       NUMBER(10)    NOT NULL,
        SLOT_COL      NUMBER(2)     NOT NULL,   -- 1-based, позиция по ширине
        SLOT_ROW      NUMBER(2)     NOT NULL,   -- 1-based, позиция по высоте (1 = низ)
        SLOT_CODE     VARCHAR2(10),             -- авто-код: А1, А2, Б1...
        IS_ACTIVE     NUMBER(1)     DEFAULT 1  NOT NULL,
        CREATED_AT    DATE          DEFAULT SYSDATE,
        CONSTRAINT PK_TOPO_SLOT
          PRIMARY KEY (SLOT_ID),
        CONSTRAINT FK_TOPO_SLOT_CELL
          FOREIGN KEY (CELL_ID)
          REFERENCES RABAEV.RRL_TOPOLOGY_CELL (CELL_ID)
          ON DELETE CASCADE,
        CONSTRAINT UQ_TOPO_SLOT_POS
          UNIQUE (CELL_ID, SLOT_COL, SLOT_ROW),
        CONSTRAINT CK_SLOT_COL
          CHECK (SLOT_COL BETWEEN 1 AND 5),
        CONSTRAINT CK_SLOT_ROW
          CHECK (SLOT_ROW BETWEEN 1 AND 5)
      )';
    DBMS_OUTPUT.PUT_LINE('Table RRL_TOPOLOGY_PICK_FACE_SLOT created');

    EXECUTE IMMEDIATE '
      CREATE SEQUENCE RABAEV.RRL_TOPOLOGY_PICK_FACE_SLOT_SEQ
        START WITH 1
        INCREMENT BY 1
        NOCACHE';
    DBMS_OUTPUT.PUT_LINE('Sequence RRL_TOPOLOGY_PICK_FACE_SLOT_SEQ created');
  ELSE
    DBMS_OUTPUT.PUT_LINE('Table RRL_TOPOLOGY_PICK_FACE_SLOT already exists — skip');
  END IF;
END;
/

COMMIT;
