whenever sqlerror exit failure rollback
@@before_access.sql
@@before_bind.sql
@@verify.sql
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK'where MIGRATION_ID='2026-10-21-tradecase-full-pallet-scoped-bind';
commit;
