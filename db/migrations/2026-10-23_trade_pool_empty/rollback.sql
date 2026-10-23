whenever sqlerror exit failure rollback
@@before_cmd.sql
@@rollback_verify.sql
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK' where MIGRATION_ID='2026-10-23-trade-pool-empty';
commit;
