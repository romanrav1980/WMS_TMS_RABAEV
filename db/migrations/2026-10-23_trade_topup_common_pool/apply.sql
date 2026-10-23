whenever sqlerror exit failure rollback
@@000_preflight.sql
@@001_pool_read.sql
@@002_pool_cmd.sql
@@003_topup_adopt.sql
@@verify.sql
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-23-trade-topup-common-pool' MIGRATION_ID from dual)x on(d.MIGRATION_ID=x.MIGRATION_ID)
when matched then update set STATUS='APPLIED',APPLIED_AT=sysdate,APPLIED_BY=user
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(x.MIGRATION_ID,'Held SAP top-up of a common-pool article served by its own hold, not by the pool',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
