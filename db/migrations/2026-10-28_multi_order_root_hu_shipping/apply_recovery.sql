whenever sqlerror exit failure rollback
@@003_qc_case.sql
@@004_qc_scope.sql
@@005_qc_policy.sql
@@006_qc_gate.sql
@@007_final_scale_admission.sql
@@002_shipping_core.sql
@@verify.sql
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-28-multi-order-root-hu-shipping' MIGRATION_ID from dual)x on(d.MIGRATION_ID=x.MIGRATION_ID)when matched then update set STATUS='APPLIED',APPLIED_AT=sysdate,APPLIED_BY=user when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)values(x.MIGRATION_ID,'Atomic root-HU shipment with several CASE orders of one recipient',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;

