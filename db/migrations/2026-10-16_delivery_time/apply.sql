@@before.sql
@@rrl_delivery_time_api_package.sql
@@context.sql
@@schema.sql
@@rrl_delivery_time_api_package_body.sql
@@rrl_deliv_window_guard.sql
@@rrl_deliv_arrival_guard.sql
@@compile_dependents.sql
@@verify.sql
insert into RRL_SCHEMA_MIGRATIONS(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)values('2026-10-16-delivery-time','Guarded package-only increment; see frozen manifest and wiki',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
