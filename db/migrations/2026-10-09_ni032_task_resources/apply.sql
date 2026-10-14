prompt NI03.2 authoritative task assignment/session policy; checkpoints 223/224
@@001_policy.sql
@@002_task_plan.sql
@@003_task_core.sql
@@../2026-10-08_stock_posting_core/014b_recompile.sql
@@verify.sql
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-09-009-task-resource-policy' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'NI03.2 shared assignment/session ownership, dispatch rights and physical step protection',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
/
