-- =============================================================================
-- Migration 055 — Fleet CRUD: Транспортные средства
-- Sprint 97 | 2026-05-29
-- =============================================================================

-- Последовательность для новых ID ТС (начинаем с 10000, чтобы не конфликтовать с legacy)
BEGIN
  EXECUTE IMMEDIATE 'CREATE SEQUENCE RABAEV.SEQ_TR_VEHICLE START WITH 10000 INCREMENT BY 1 NOCACHE';
EXCEPTION WHEN OTHERS THEN NULL; END;
/

-- Функция добавления нового ТС
CREATE OR REPLACE FUNCTION RABAEV.RRL_TR_VEHICLE_ADD(
    p_num_plat       VARCHAR2,
    p_transtype_id   NUMBER   DEFAULT NULL,
    p_max_weight_kg  NUMBER   DEFAULT 10000,
    p_max_pallets    NUMBER   DEFAULT 20,
    p_sobstvennyy    NUMBER   DEFAULT 1,
    p_doverennost_ot VARCHAR2 DEFAULT NULL
) RETURN NUMBER AS
    v_id NUMBER;
BEGIN
    v_id := RABAEV.SEQ_TR_VEHICLE.NEXTVAL;
    INSERT INTO RABAEV.RRL_TR_VEHICLE (
        ID, NUM_PLAT, TRANSTYPE, MAX_WEIGHT_KG, PALLETS,
        SOBSTVENNYY, DOVERENNOST_OT, DELETED
    ) VALUES (
        v_id, p_num_plat, p_transtype_id, p_max_weight_kg, p_max_pallets,
        p_sobstvennyy, p_doverennost_ot, 0
    );
    RETURN v_id;
EXCEPTION WHEN OTHERS THEN
    RAISE_APPLICATION_ERROR(-20097, 'RRL_TR_VEHICLE_ADD error: ' || SQLERRM);
END;
/

-- Процедура обновления ТС
CREATE OR REPLACE PROCEDURE RABAEV.RRL_TR_VEHICLE_UPDATE(
    p_id             NUMBER,
    p_num_plat       VARCHAR2,
    p_transtype_id   NUMBER,
    p_max_weight_kg  NUMBER,
    p_max_pallets    NUMBER,
    p_sobstvennyy    NUMBER,
    p_doverennost_ot VARCHAR2
) AS
    v_rows NUMBER;
BEGIN
    UPDATE RABAEV.RRL_TR_VEHICLE
       SET NUM_PLAT        = p_num_plat,
           TRANSTYPE       = p_transtype_id,
           MAX_WEIGHT_KG   = p_max_weight_kg,
           PALLETS         = p_max_pallets,
           SOBSTVENNYY     = p_sobstvennyy,
           DOVERENNOST_OT  = p_doverennost_ot
     WHERE ID = p_id AND NVL(DELETED, 0) = 0;
    v_rows := SQL%ROWCOUNT;
    IF v_rows = 0 THEN
        RAISE_APPLICATION_ERROR(-20098, 'Vehicle not found: ' || p_id);
    END IF;
END;
/

-- Мягкое удаление ТС
CREATE OR REPLACE PROCEDURE RABAEV.RRL_TR_VEHICLE_DEL(p_id NUMBER) AS
BEGIN
    UPDATE RABAEV.RRL_TR_VEHICLE SET DELETED = 1 WHERE ID = p_id;
    IF SQL%ROWCOUNT = 0 THEN
        RAISE_APPLICATION_ERROR(-20099, 'Vehicle not found: ' || p_id);
    END IF;
END;
/
