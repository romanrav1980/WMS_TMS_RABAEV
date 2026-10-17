-- MIGRATION_ID: 2026-10-15-warehouse-task-scoped-assignment
@@before.sql
@@schema.sql
@@version_api.sql
@@spec.sql
@@access_spec.sql
@@access_body.sql
@@resource_policy.sql
@@body.sql
@@version_trigger.sql
@@receipt_guard.sql
@@identity_guard.sql
alter package RRL_STOCK_TASK_PLAN compile body;
alter package RRL_STOCK_TASK_CORE compile body;
alter package RRL_STOCK_POSTING_API compile body;
alter package RRL_STOCK_HU_TASK compile body;
alter package RRL_ST_DEFER_CASE_WAIT compile body;
@@verify.sql
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-15-warehouse-task-scoped-assignment'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when matched then update set d.STATUS='APPLIED',d.APPLIED_AT=sysdate,d.APPLIED_BY=user where d.STATUS='ROLLED_BACK'
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)values(s.MIGRATION_ID,'Scoped ordinary STOCK ASSIGN/START metadata; trigger-derived retained version sidecar; no stock writer',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
