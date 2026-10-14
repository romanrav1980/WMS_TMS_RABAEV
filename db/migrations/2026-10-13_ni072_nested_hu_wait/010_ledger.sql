merge into RRL_SCHEMA_MIGRATIONS t using(select '2026-10-13-010-ni072-nested-hu-wait' MIGRATION_ID from dual)s on(t.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Prepared all-CASE nested HU waiting uses existing root HU_PLAN_MOVE/HU_TASK_COMPLETE, immutable whole-source plan and current ST/decision/trip guards',sysdate,user,'apply.sql','rollback.sql','APPLIED');
/
