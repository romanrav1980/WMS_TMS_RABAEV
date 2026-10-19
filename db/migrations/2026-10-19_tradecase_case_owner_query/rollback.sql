whenever sqlerror exit failure rollback
@@before.sql
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK'where MIGRATION_ID='2026-10-19-tradecase-case-owner-query';
commit;
