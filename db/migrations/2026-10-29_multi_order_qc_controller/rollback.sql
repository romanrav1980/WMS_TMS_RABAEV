whenever sqlerror exit failure rollback
@@900_before_qc_policy_multi_order_controller.sql
@@verify.sql
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK',APPLIED_AT=sysdate,APPLIED_BY=user where MIGRATION_ID='2026-10-29-multi-order-qc-controller';
commit;
