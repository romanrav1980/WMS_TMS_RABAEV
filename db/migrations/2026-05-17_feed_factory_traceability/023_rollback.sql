prompt [migration 2026-05-17-023] Common stock reservation model - rollback

prompt Safe rollback: keep RRL_STOCK_RESERVATION data and structure.
prompt To drop reservation data/table, create a separate explicitly approved destructive script.

delete from RIGHTS
 where USER_GROUP = 'GLOBAL_ADMIN'
   and upper(RIGHT1) in ('STOCK_RESERVATION_VIEW', 'STOCK_RESERVATION_EDIT');

delete from RRL_SCHEMA_MIGRATIONS
 where MIGRATION_ID = '2026-05-17-023-common-stock-reservation';

commit;

prompt [migration 2026-05-17-023] rollback done
