-- TMS-2 Sprint 9 deterministic historical template fixture.
-- Creates one historical RRL_PLANNER_PLANS row for plan_date 2026-05-24
-- using current free ST numbers from 2026-05-25. This closes the
-- planner/templates acceptance gate without mutating transport tasks.

DECLARE
  v_exists NUMBER := 0;
  v_stops  VARCHAR2(3900);
  v_payload CLOB;
BEGIN
  SELECT COUNT(*)
    INTO v_exists
    FROM RABAEV.RRL_PLANNER_PLANS
   WHERE SOLVER = 's9-template-fixture'
     AND PLAN_DATE = DATE '2026-05-24';

  IF v_exists = 0 THEN
    SELECT LISTAGG('"' || REPLACE(ST_NUMBER, '"', '\"') || '"', ',')
             WITHIN GROUP (ORDER BY ST_NUMBER)
      INTO v_stops
      FROM (
        SELECT ST_NUMBER
          FROM (
            SELECT DISTINCT P.ST_NUMBER
              FROM RABAEV.RRL_SBORKA_PALLETS P
              JOIN RABAEV.RRL_SBORKA_PALLET_ROWS R ON R.PALLET_UID = P.PALLET_UID
             WHERE P.TRANSTASK_ID IS NULL
               AND NVL(P.CONDITION, 0) <> 2
               AND P.STDATE >= DATE '2026-05-25'
               AND P.STDATE <  DATE '2026-05-26'
             ORDER BY P.ST_NUMBER
          )
         WHERE ROWNUM <= 100
      );

    IF v_stops IS NULL THEN
      RAISE_APPLICATION_ERROR(-20055, 'No free ST rows for Sprint 9 template fixture date 2026-05-25');
    END IF;

    v_payload := '{"solver":"s9-template-fixture","routes":[{"vehicle_id":0,"vehicle_num":"FIXTURE","stops":[' ||
                 v_stops ||
                 '],"total_km":0,"total_pallets":0}],"unassigned":[],"total_km":0,"fleet_utilization_pct":0,"tw_violations":0,"score":1}';

    INSERT INTO RABAEV.RRL_PLANNER_PLANS
           (ID, PLAN_DATE, CREATED_AT, SOLVER, SCORE, PAYLOAD)
    VALUES (RABAEV.SEQ_PLANNER_PLANS.NEXTVAL, DATE '2026-05-24', SYSDATE,
            's9-template-fixture', 1, v_payload);
  END IF;
END;
/
