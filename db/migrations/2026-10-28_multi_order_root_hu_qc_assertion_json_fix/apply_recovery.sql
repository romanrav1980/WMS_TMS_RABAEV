whenever sqlerror exit failure rollback
@@001_qc_gate_assertion_json_fix.sql
@@verify.sql
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-28-multi-order-root-hu-qc-assertion-json-fix' MIGRATION_ID from dual)x on(d.MIGRATION_ID=x.MIGRATION_ID)when matched then update set STATUS='APPLIED',APPLIED_AT=sysdate,APPLIED_BY=user when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)values(x.MIGRATION_ID,'Materialize the multi-order QC exemption JSON before approval evaluation',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
