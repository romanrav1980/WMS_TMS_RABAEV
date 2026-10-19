whenever sqlerror exit failure rollback
@@before_package.sql
@@before_package_body.sql
alter package RRL_CASE_TASK_ACCESS compile body;
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK'where MIGRATION_ID='2026-10-19-tradecase-case-read';
commit;
