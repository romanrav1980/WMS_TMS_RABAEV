prompt [migration 2026-05-23-044] ban zero warehouse id - smoke cleanup

delete from RRL_WAREHOUSE_MAP_CANVAS
 where CANVAS_CODE = 'SMOKE-ZERO-CANVAS';

delete from RRL_WARES
 where ID = 0
   and NAME = 'ZERO SHOULD FAIL';

commit;

prompt [migration 2026-05-23-044] smoke cleanup done
