@@before.sql
@@rrl_case_task_access_package.sql
@@rrl_case_task_access_package_body.sql
@@rrl_case_assignment_api_package_body.sql
@@rrl_case_lifecycle_api_package_body.sql
@@rrl_asm_meta_scope_package_body.sql
@@rrl_assembly_scale_api_package_body.sql
@@rrl_case_resource_policy_package_body.sql
@@rrl_wh_weigh_request_api_package_body.sql
@@rrl_stock_case_pick_cmd_package_body.sql
@@rrl_inventory_task_access_package_body.sql
@@rrl_stock_metadata_tx_package_body.sql
@@compile_dependents.sql
@@verify.sql
insert into RRL_SCHEMA_MIGRATIONS(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)values('2026-10-16-additive-legacy-task-scopes','Guarded package-only increment; see frozen manifest and wiki',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
