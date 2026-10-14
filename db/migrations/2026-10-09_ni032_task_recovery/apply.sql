@@001_residual_identity.sql
prompt NI03.2 task remainder and recovery; source checkpoint 221
@@002_task_plan.sql
@@003_task_core.sql
@@verify.sql
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-09-008-task-recovery' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'NI03.2 residual tasks reset execution resources and return exact remaining quantity',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
/
