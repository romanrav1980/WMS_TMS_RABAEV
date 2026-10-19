whenever sqlerror exit failure rollback
@@before_context.sql
@@before_binding.sql
@@before_documents.sql
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK'where MIGRATION_ID='2026-10-19-tradecase-box-boundaries';
commit;
