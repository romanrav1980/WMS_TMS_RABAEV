merge into RRL_SCHEMA_MIGRATIONS t using(select '2026-10-13-772-st-defer-wait-task'MIGRATION_ID from dual)s on(t.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Typed ST deferral waiting tasks reuse TASK_COMPLETE/TRANSFER_CORE and preserve hard reservations and original picking history',sysdate,user,'apply.sql','rollback.sql','APPLIED');
/
