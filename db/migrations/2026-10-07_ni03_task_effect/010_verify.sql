select column_name,data_type from user_tab_columns where table_name='RRL_WAREHOUSE_TASK' and column_name in('COMPLETION_HASH','COMPLETION_JSON');
select constraint_name,status from user_constraints where constraint_name='RRL_WH_TASK_COMPLETION_JSON';
select status from RRL_SCHEMA_MIGRATIONS where MIGRATION_ID='2026-10-07-010-ni03-task-effect';