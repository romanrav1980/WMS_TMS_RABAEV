@@before.sql
@@rrl_inventory_task_access_package.sql
@@rrl_inventory_task_access_package_body.sql
@@rrl_stock_inventory_cmd_package_body.sql
@@rrl_stock_short_recovery_package_body.sql
@@rrl_stock_posting_api_package_body.sql
@@verify.sql
insert into RRL_SCHEMA_MIGRATIONS(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)values('2026-10-16-inventory-task-scope','Assigned inventory task claim/count/current read scope; unchanged quantity owner',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
