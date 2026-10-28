whenever sqlerror exit failure rollback
@@900_before_shipping_core_execute_json_sql_fix.sql
@@verify.sql
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK',APPLIED_AT=sysdate,APPLIED_BY=user where MIGRATION_ID='2026-10-29-multi-order-root-hu-execute-json-sql-fix';
commit;
