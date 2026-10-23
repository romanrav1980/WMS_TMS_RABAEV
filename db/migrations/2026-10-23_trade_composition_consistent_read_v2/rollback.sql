whenever sqlerror exit failure rollback
@@verify.sql
@@before_body.sql
@@rollback_verify.sql
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK'where MIGRATION_ID='2026-10-23-trade-composition-consistent-read-v2';
commit;
