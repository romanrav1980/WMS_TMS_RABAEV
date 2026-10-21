whenever sqlerror exit failure rollback
@@before.sql
@@verify.sql
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-22-tradecase-pallet-floor' MIGRATION_ID from dual)x on(d.MIGRATION_ID=x.MIGRATION_ID)
when matched then update set STATUS='ROLLED_BACK',APPLIED_AT=sysdate,APPLIED_BY=user
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(x.MIGRATION_ID,'Allow existing zero quantity floor type confirmation with current trade owner check',sysdate,user,'apply.sql','rollback.sql','ROLLED_BACK');
commit;
