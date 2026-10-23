whenever sqlerror exit failure rollback
@@verify.sql
@@before_access_body.sql
@@rollback_verify.sql
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK'where MIGRATION_ID='2026-10-23-inventory-current-owner';
commit;
