whenever sqlerror exit failure rollback
@@before.sql
@@rollback_verify.sql
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-22-trade-topup-adoption-guard' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID) when matched then update set STATUS='ROLLED_BACK',APPLIED_AT=sysdate,APPLIED_BY=user when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)values(s.MIGRATION_ID,'Allow only frozen same-stock topup-to-wave reservation adoption',sysdate,user,'apply.sql','rollback.sql','ROLLED_BACK');
commit;
