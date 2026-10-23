whenever sqlerror exit failure rollback
@@000_preflight.sql
@@001_ctx_spec.sql
@@002_ctx_body.sql
@@003_pool_read.sql
@@004_pool_cmd.sql
@@recompile.sql
@@verify.sql
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-23-trade-pool-eligibility' MIGRATION_ID from dual)x on(d.MIGRATION_ID=x.MIGRATION_ID)
when matched then update set STATUS='APPLIED',APPLIED_AT=sysdate,APPLIED_BY=user
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(x.MIGRATION_ID,'Trade rows get common-pool shares only from compatible physical classes',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
