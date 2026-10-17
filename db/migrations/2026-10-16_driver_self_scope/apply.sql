@@before.sql
@@rrl_driver_scope_package.sql
@@rrl_driver_scope_package_body.sql
@@rrl_tt_operation_plan_api_package_body.sql
@@rrl_transport_driver_user_guard_trigger.sql
@@rrl_stock_store_return_cust_cmd_package_body.sql
@@rrl_stock_posting_api_package_body.sql
@@compile_dependents.sql
@@verify.sql
insert into RRL_SCHEMA_MIGRATIONS(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)values('2026-10-16-driver-self-scope','Guarded package-only increment; see frozen manifest and wiki',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
