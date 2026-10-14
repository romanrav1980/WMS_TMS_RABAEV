@@../2026-10-08_stock_posting_core/259_task_domain_facts_rollback.sql
@@../2026-10-08_stock_posting_core/260_pool_read_facts_rollback.sql
@@../2026-10-08_stock_posting_core/014b_recompile.sql
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK' where MIGRATION_ID='2026-10-09-022-secured-demand';
commit;
/
