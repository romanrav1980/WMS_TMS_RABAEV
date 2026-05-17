prompt [migration 2026-05-17-026] warehouse reachtruck tasks - rollback

delete from RIGHTS
 where upper(RIGHT1) in ('WAREHOUSE_TASK_VIEW', 'WAREHOUSE_TASK_EXECUTE');

delete from RRL_SCHEMA_MIGRATIONS
 where MIGRATION_ID = '2026-05-17-026-warehouse-tasks';

commit;

prompt RRL_WAREHOUSE_TASK data is intentionally preserved.
prompt [migration 2026-05-17-026] rollback done
