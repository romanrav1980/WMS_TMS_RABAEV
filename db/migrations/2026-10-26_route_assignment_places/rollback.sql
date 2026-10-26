whenever sqlerror exit failure rollback
@@verify.sql
@@before_001.sql
@@before_002.sql
@@rollback_verify.sql
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK'where MIGRATION_ID='2026-10-26-route-assignment-places';
commit;
