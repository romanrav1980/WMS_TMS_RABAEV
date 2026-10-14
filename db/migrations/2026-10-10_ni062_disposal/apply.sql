@@001_schema.sql
@@002_command.sql
@@003_effect.sql
@@004_root.sql
@@005_guards.sql
@@../2026-10-08_stock_posting_core/014b_recompile.sql
@@verify.sql
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-10-110-return-disposal-original-loss-store' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Independent destruction decision consumes exact blocked DISPOSAL return through original effect core, loss attributed to original store, atomic SAP outbox',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
/
