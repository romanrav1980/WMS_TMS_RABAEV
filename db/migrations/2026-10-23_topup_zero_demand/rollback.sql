whenever sqlerror exit failure rollback
@@before_read.sql
@@rollback_verify.sql
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK' where MIGRATION_ID='2026-10-23-topup-zero-demand';
commit;
