-- Verify 063 — TMS-2 test geocode coverage.

SELECT COUNT(*) AS total_addrs,
       SUM(CASE WHEN SHIROTA IS NOT NULL AND SHIROTA <> 0
                 AND DOLGOTA IS NOT NULL AND DOLGOTA <> 0
                THEN 1 ELSE 0 END) AS geocoded,
       SUM(CASE WHEN SHIROTA IS NULL OR SHIROTA = 0
                 OR DOLGOTA IS NULL OR DOLGOTA = 0
                THEN 1 ELSE 0 END) AS missing_coords
  FROM RABAEV.RRL_ADDR;

SELECT COUNT(*) AS backup_rows
  FROM RABAEV.RRL_ADDR_TEST_GEOCODE_BAK
 WHERE MIGRATION_TAG = '063_tms2_test_geocode';

SELECT MIN(SHIROTA) AS min_lat,
       MAX(SHIROTA) AS max_lat,
       MIN(DOLGOTA) AS min_lon,
       MAX(DOLGOTA) AS max_lon
  FROM RABAEV.RRL_ADDR
 WHERE SHIROTA IS NOT NULL
   AND DOLGOTA IS NOT NULL;
