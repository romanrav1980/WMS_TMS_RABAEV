whenever sqlerror exit failure rollback
@@900_before_qc_gate_json_value_fix.sql
@@verify.sql
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK',APPLIED_AT=sysdate,APPLIED_BY=user where MIGRATION_ID='2026-10-28-multi-order-root-hu-qc-json-value-fix';
commit;
