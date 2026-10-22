whenever sqlerror exit failure rollback
@@preflight.sql
@@001_cmd.sql
@@verify.sql
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-22-trade-topup-cancelled-wave-reconcile' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID) when matched then update set STATUS='APPLIED',APPLIED_AT=sysdate,APPLIED_BY=user when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)values(s.MIGRATION_ID,'Reconcile adopted topup only after native unpicked wave cancellation',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
