prompt [migration 2026-05-17-028] rollback is non-destructive

delete from RRL_SCHEMA_MIGRATIONS
 where MIGRATION_ID = '2026-05-17-028-warehouse-task-domain-sync';

commit;

prompt RRL_WAREHOUSE_TASK_SYNC data is intentionally preserved.
prompt [migration 2026-05-17-028] rollback done
