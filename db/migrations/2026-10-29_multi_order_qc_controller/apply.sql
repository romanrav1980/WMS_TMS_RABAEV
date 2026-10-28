whenever sqlerror exit failure rollback
@@000_preflight.sql
@@001_qc_policy_multi_order_controller.sql
@@verify.sql
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-29-multi-order-qc-controller' MIGRATION_ID from dual)x on(d.MIGRATION_ID=x.MIGRATION_ID)when matched then update set STATUS='APPLIED',APPLIED_AT=sysdate,APPLIED_BY=user when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)values(x.MIGRATION_ID,'Evaluate independent QC controller against CASE facts for a multi-order root HU',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
