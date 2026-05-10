prompt Applying transport seed compatibility patch
set define off

DECLARE
  v_count NUMBER;
BEGIN
  SELECT COUNT(*) INTO v_count
  FROM user_tab_columns
  WHERE table_name = 'RRL_TT_DOCK'
    AND column_name = 'DOCK_IS_BLOCKED';

  IF v_count = 0 THEN
    EXECUTE IMMEDIATE 'ALTER TABLE RRL_TT_DOCK ADD (DOCK_IS_BLOCKED NUMBER DEFAULT 0)';
    EXECUTE IMMEDIATE 'UPDATE RRL_TT_DOCK SET DOCK_IS_BLOCKED = 0 WHERE DOCK_IS_BLOCKED IS NULL';
    COMMIT;
  END IF;
END;
/
