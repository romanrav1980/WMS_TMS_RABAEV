-- =============================================================================
-- Migration 056 — Fleet CRUD: Водители
-- Sprint 98 | 2026-05-29
-- =============================================================================

BEGIN
  EXECUTE IMMEDIATE 'CREATE SEQUENCE RABAEV.SEQ_TR_VODITEL START WITH 10000 INCREMENT BY 1 NOCACHE';
EXCEPTION WHEN OTHERS THEN NULL; END;
/

-- Добавить столбцы если их нет (идемпотентно)
BEGIN
  EXECUTE IMMEDIATE 'ALTER TABLE RABAEV.RRL_TR_VODITEL ADD LICENSE_NUMBER VARCHAR2(30)';
EXCEPTION WHEN OTHERS THEN NULL; END;
/
BEGIN
  EXECUTE IMMEDIATE 'ALTER TABLE RABAEV.RRL_TR_VODITEL ADD COMPANY VARCHAR2(100)';
EXCEPTION WHEN OTHERS THEN NULL; END;
/

CREATE OR REPLACE FUNCTION RABAEV.RRL_TR_VODITEL_ADD(
    p_name           VARCHAR2,
    p_phone          VARCHAR2 DEFAULT NULL,
    p_license_number VARCHAR2 DEFAULT NULL,
    p_company        VARCHAR2 DEFAULT NULL
) RETURN NUMBER AS
    v_id NUMBER;
BEGIN
    v_id := RABAEV.SEQ_TR_VODITEL.NEXTVAL;
    INSERT INTO RABAEV.RRL_TR_VODITEL (ID, F, TEL, LICENSE_NUMBER, COMPANY, DELETED)
    VALUES (v_id, p_name, p_phone, p_license_number, p_company, 0);
    RETURN v_id;
EXCEPTION WHEN OTHERS THEN
    RAISE_APPLICATION_ERROR(-20094, 'RRL_TR_VODITEL_ADD error: ' || SQLERRM);
END;
/

CREATE OR REPLACE PROCEDURE RABAEV.RRL_TR_VODITEL_UPDATE(
    p_id             NUMBER,
    p_name           VARCHAR2,
    p_phone          VARCHAR2,
    p_license_number VARCHAR2,
    p_company        VARCHAR2
) AS
BEGIN
    UPDATE RABAEV.RRL_TR_VODITEL
       SET F              = p_name,
           TEL            = p_phone,
           LICENSE_NUMBER = p_license_number,
           COMPANY        = p_company
     WHERE ID = p_id AND NVL(DELETED, 0) = 0;
    IF SQL%ROWCOUNT = 0 THEN
        RAISE_APPLICATION_ERROR(-20095, 'Driver not found: ' || p_id);
    END IF;
END;
/

CREATE OR REPLACE PROCEDURE RABAEV.RRL_TR_VODITEL_DEL(p_id NUMBER) AS
BEGIN
    UPDATE RABAEV.RRL_TR_VODITEL SET DELETED = 1 WHERE ID = p_id;
    IF SQL%ROWCOUNT = 0 THEN
        RAISE_APPLICATION_ERROR(-20096, 'Driver not found: ' || p_id);
    END IF;
END;
/
