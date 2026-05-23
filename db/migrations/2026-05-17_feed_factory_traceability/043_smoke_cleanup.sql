prompt [migration 2026-05-23-043] warehouse map operation idempotency keys - smoke cleanup

delete from RRL_PICK_ROUTE where CREATED_BY = 'SMOKE_043';
delete from RRL_WAREHOUSE_MAP_CANVAS where CREATED_BY = 'SMOKE_043';
delete from RRL_WAREHOUSE_TOPOLOGY where CREATED_BY = 'SMOKE_043';
commit;

select (
  (select count(*) from RRL_PICK_ROUTE where CREATED_BY = 'SMOKE_043') +
  (select count(*) from RRL_WAREHOUSE_MAP_CANVAS where CREATED_BY = 'SMOKE_043') +
  (select count(*) from RRL_WAREHOUSE_TOPOLOGY where CREATED_BY = 'SMOKE_043')
) SMOKE_043_REMAINING_ROWS
from dual;

prompt [migration 2026-05-23-043] smoke cleanup done
