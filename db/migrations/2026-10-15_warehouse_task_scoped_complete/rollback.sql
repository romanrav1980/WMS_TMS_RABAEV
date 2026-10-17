-- MIGRATION_ID: 2026-10-15-warehouse-task-scoped-complete
@@before_posting.sql
@@before_task_plan.sql
@@before_task_core.sql
@@before_resource_policy.sql
@@before_task_plan_spec.sql
@@before_access_spec.sql
@@before_access_body.sql
alter package RRL_STOCK_TASK_PLAN compile body;
alter package RRL_WAREHOUSE_TASK_ACCESS compile body;
alter package RRL_TASK_RESOURCE_POLICY compile body;
alter package RRL_STOCK_TASK_CORE compile body;
alter package RRL_STOCK_POSTING_API compile body;
alter package RRL_STOCK_HU_TASK compile body;
alter package RRL_ST_DEFER_CASE_WAIT compile body;
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK'where MIGRATION_ID='2026-10-15-warehouse-task-scoped-complete';
commit;
