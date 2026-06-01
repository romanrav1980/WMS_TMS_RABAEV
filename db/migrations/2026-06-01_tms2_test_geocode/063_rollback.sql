-- Rollback 063 — restore RRL_ADDR coordinates saved before test geocode.

prompt [063 rollback] TMS-2 test geocode restore - start

MERGE INTO RABAEV.RRL_ADDR A
USING (
  SELECT ADDR, OLD_SHIROTA, OLD_DOLGOTA
    FROM RABAEV.RRL_ADDR_TEST_GEOCODE_BAK
   WHERE MIGRATION_TAG = '063_tms2_test_geocode'
) B
ON (A.ADDR = B.ADDR)
WHEN MATCHED THEN UPDATE
   SET A.SHIROTA = B.OLD_SHIROTA,
       A.DOLGOTA = B.OLD_DOLGOTA;

DELETE FROM RABAEV.RRL_ADDR_TEST_GEOCODE_BAK
 WHERE MIGRATION_TAG = '063_tms2_test_geocode';

COMMIT;

prompt [063 rollback] TMS-2 test geocode restore - done
