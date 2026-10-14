prompt Common SOFT pool to existing wave HARD, one root transaction
@@003_snapshot.sql
@@001_pool_command.sql
@@002_wave_launch.sql
@@../2026-10-08_stock_posting_core/014b_recompile.sql
@@verify.sql
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-09-020-pool-wave-bridge' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Common SOFT consumed atomically by existing wave HARD launch',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
/
