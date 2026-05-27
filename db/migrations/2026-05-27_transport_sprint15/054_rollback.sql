-- Rollback 054: Sprint 15 — Биллинг
-- Внимание: не удаляем RRL_BILL_ORDERS, если она существовала до миграции (C# WinForms).
-- Удаляем только SEQ_BILL_ORDERS если она была создана этой миграцией.

DECLARE
  v_cnt NUMBER;
BEGIN
  SELECT COUNT(*) INTO v_cnt FROM USER_SEQUENCES WHERE SEQUENCE_NAME = 'SEQ_BILL_ORDERS';
  IF v_cnt > 0 THEN
    EXECUTE IMMEDIATE 'DROP SEQUENCE RABAEV.SEQ_BILL_ORDERS';
  END IF;
END;
/

COMMIT;
