-- Migration 054: Sprint 15 — Биллинг, создание счёта
-- Создаёт SEQ_BILL_ORDERS (если отсутствует) и таблицу RRL_BILL_ORDERS (если отсутствует).
-- В production Oracle с C# WinForms таблица уже существует; миграция идемпотентна.

-- SEQ_BILL_ORDERS
DECLARE
  v_cnt NUMBER;
BEGIN
  SELECT COUNT(*) INTO v_cnt FROM USER_SEQUENCES WHERE SEQUENCE_NAME = 'SEQ_BILL_ORDERS';
  IF v_cnt = 0 THEN
    EXECUTE IMMEDIATE '
      CREATE SEQUENCE RABAEV.SEQ_BILL_ORDERS
        START WITH 1 INCREMENT BY 1 NOCACHE NOCYCLE';
  END IF;
END;
/

-- RRL_BILL_ORDERS (создаётся только если не существует)
DECLARE
  v_cnt NUMBER;
BEGIN
  SELECT COUNT(*) INTO v_cnt FROM USER_TABLES WHERE TABLE_NAME = 'RRL_BILL_ORDERS';
  IF v_cnt = 0 THEN
    EXECUTE IMMEDIATE '
      CREATE TABLE RABAEV.RRL_BILL_ORDERS (
        ID          NUMBER(10)    NOT NULL,
        NUM         VARCHAR2(30),
        COMPANY     VARCHAR2(200),
        DATEOFORDER DATE,
        DATEFROM    DATE,
        DATETO      DATE,
        CLOSED      NUMBER(1)     DEFAULT 0,
        PAYED       NUMBER(1)     DEFAULT 0,
        CONSTRAINT PK_BILL_ORDERS PRIMARY KEY (ID)
      )';
  END IF;
END;
/

-- Расширение COMPANY для существующих legacy-таблиц.
DECLARE
  v_cnt NUMBER;
BEGIN
  SELECT COUNT(*) INTO v_cnt FROM USER_TABLES WHERE TABLE_NAME = 'RRL_BILL_ORDERS';
  IF v_cnt > 0 THEN
    EXECUTE IMMEDIATE 'ALTER TABLE RABAEV.RRL_BILL_ORDERS MODIFY (COMPANY VARCHAR2(200))';
  END IF;
END;
/

COMMIT;
