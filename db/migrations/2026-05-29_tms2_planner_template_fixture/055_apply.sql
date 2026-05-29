-- TMS-2 Sprint 9 deterministic historical template fixture.
-- Creates historical RRL_PLANNER_PLANS rows before accepted seed dates.
-- The 2026-05-23 row supports the current release seed 2026-05-24; the
-- 2026-05-24 row preserves compatibility with the earlier 2026-05-25 gate.
-- planner/templates acceptance gate without mutating transport tasks.

DECLARE
  PROCEDURE ensure_fixture(p_fixture_date DATE, p_source_date DATE) IS
    v_count  NUMBER := 0;
    v_stops  CLOB := EMPTY_CLOB();
    v_payload CLOB;
  BEGIN
    DELETE FROM RABAEV.RRL_PLANNER_PLANS
     WHERE SOLVER = 's9-template-fixture'
       AND PLAN_DATE = p_fixture_date;

    FOR rec IN (
      SELECT DISTINCT P.ST_NUMBER
        FROM RABAEV.RRL_SBORKA_PALLETS P
        JOIN RABAEV.RRL_SBORKA_PALLET_ROWS R ON R.PALLET_UID = P.PALLET_UID
       WHERE P.TRANSTASK_ID IS NULL
         AND NVL(P.CONDITION, 0) <> 2
         AND P.STDATE >= p_source_date
         AND P.STDATE <  p_source_date + 1
       ORDER BY P.ST_NUMBER
    ) LOOP
      IF v_count > 0 THEN
        v_stops := v_stops || ',';
      END IF;
      v_stops := v_stops || '"' || REPLACE(rec.ST_NUMBER, '"', '\"') || '"';
      v_count := v_count + 1;
    END LOOP;

    IF v_count = 0 THEN
      IF p_fixture_date = DATE '2026-05-24' THEN
        RETURN;
      END IF;
      RAISE_APPLICATION_ERROR(
        -20055,
        'No free ST rows for Sprint 9 template fixture source date ' || TO_CHAR(p_source_date, 'YYYY-MM-DD')
      );
    END IF;

    v_payload := '{"solver":"s9-template-fixture","routes":[{"vehicle_id":0,"vehicle_num":"FIXTURE","stops":[' ||
                 v_stops ||
                 '],"total_km":0,"total_pallets":0}],"unassigned":[],"total_km":0,"fleet_utilization_pct":0,"tw_violations":0,"score":1}';

    INSERT INTO RABAEV.RRL_PLANNER_PLANS
           (ID, PLAN_DATE, CREATED_AT, SOLVER, SCORE, PAYLOAD)
    VALUES (RABAEV.SEQ_PLANNER_PLANS.NEXTVAL, p_fixture_date, SYSDATE,
            's9-template-fixture', 1, v_payload);
  END ensure_fixture;
BEGIN
  ensure_fixture(DATE '2026-05-23', DATE '2026-05-24');
  ensure_fixture(DATE '2026-05-24', DATE '2026-05-25');
END;
/
