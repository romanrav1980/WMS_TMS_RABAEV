-- Rollback for TMS-2 Sprint 9 deterministic historical template fixture.

DELETE FROM RABAEV.RRL_PLANNER_PLANS
 WHERE SOLVER = 's9-template-fixture'
   AND PLAN_DATE IN (DATE '2026-05-23', DATE '2026-05-24');

COMMIT;
