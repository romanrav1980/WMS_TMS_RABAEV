merge into RRL_SCHEMA_MIGRATIONS t using(select '2026-10-12-312-nested-onward-leaf' MIGRATION_ID from dual)s on(t.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)values(s.MIGRATION_ID,'Existing HU shipping includes one whole interwarehouse onward stock leaf; native target loading proof and frozen source bindings retained; no second fulfillment',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
