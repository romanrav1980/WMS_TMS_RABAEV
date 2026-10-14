prompt NS21 stock-backed SOFT demand pool, existing root transaction
@@001_schema.sql
@@002_snapshot.sql
@@004_context.sql
@@003_command.sql
@@005_posting.sql
@@../2026-10-08_stock_posting_core/014b_recompile.sql
@@verify.sql
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-09-019-soft-demand-pool' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Stock-backed SOFT demand allocation across open orders, whole pick quantum and locked snapshot; no physical binding',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
/
