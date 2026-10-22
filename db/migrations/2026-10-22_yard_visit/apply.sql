whenever sqlerror exit failure rollback
@@000_preflight.sql
@@001_schema.sql
@@002_api.sql
@@verify.sql
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-22-yard-visit' MIGRATION_ID from dual)x on(d.MIGRATION_ID=x.MIGRATION_ID)
when matched then update set STATUS='APPLIED',APPLIED_AT=sysdate,APPLIED_BY=user
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(x.MIGRATION_ID,'TRADECASE yard visits: versioned dock/vehicle occupancy without stock effects',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
