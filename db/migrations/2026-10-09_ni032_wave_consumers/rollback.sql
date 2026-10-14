@@../2026-10-08_stock_posting_core/255_task_plan_bind_rollback.sql
@@../2026-10-08_stock_posting_core/256_task_core_bind_rollback.sql
@@../2026-10-08_stock_posting_core/257_reserve_bind_acl_rollback.sql
@@../2026-10-08_stock_posting_core/258_unit_bind_acl_rollback.sql
drop package RRL_STOCK_REPL_BIND;
@@../2026-10-08_stock_posting_core/014b_recompile.sql
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK' where MIGRATION_ID='2026-10-09-021-wave-consumer-binding';
commit;
/
