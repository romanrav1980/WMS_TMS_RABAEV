whenever sqlerror exit failure rollback
@@000_preflight.sql
@@001_pool_cmd_spec.sql
@@002_pool_cmd_body.sql
@@003_posting_api_body.sql
@@recompile.sql
@@verify.sql
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-23-trade-pool-access' MIGRATION_ID from dual)x on(d.MIGRATION_ID=x.MIGRATION_ID)
when matched then update set STATUS='APPLIED',APPLIED_AT=sysdate,APPLIED_BY=user
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(x.MIGRATION_ID,'Current warehouse/owner rights for the common pool, before committed replay too',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
