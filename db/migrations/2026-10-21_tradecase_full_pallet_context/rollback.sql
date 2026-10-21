whenever sqlerror exit failure rollback
@@before_body.sql
@@before_context_spec.sql
@@before_context_body.sql
@@verify.sql
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK'where MIGRATION_ID='2026-10-21-tradecase-full-pallet-context';
commit;
