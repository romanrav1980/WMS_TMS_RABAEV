prompt [migration 2026-05-17-027] rollback is non-destructive

delete from RRL_SCHEMA_MIGRATIONS
 where MIGRATION_ID = '2026-05-17-027-warehouse-task-qty-mode';

commit;

prompt RRL_WAREHOUSE_TASK quantity-mode columns and task history are intentionally preserved.
prompt [migration 2026-05-17-027] rollback done
