whenever sqlerror exit failure rollback
@@000_preflight.sql
@@001_qc_gate_json_value_fix.sql
@@verify.sql
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-28-multi-order-root-hu-qc-json-value-fix' MIGRATION_ID from dual)x on(d.MIGRATION_ID=x.MIGRATION_ID)when matched then update set STATUS='APPLIED',APPLIED_AT=sysdate,APPLIED_BY=user when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)values(x.MIGRATION_ID,'Materialize JSON values before adding them to the multi-order QC status response',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
