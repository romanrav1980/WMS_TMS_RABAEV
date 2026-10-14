merge into RRL_SCHEMA_MIGRATIONS t using(select '2026-10-12-309-flexible-unit-mode' MIGRATION_ID from dual)s on(t.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)values(s.MIGRATION_ID,'Existing interwarehouse unique-unit capture accepts UNIT_OR_AGGREGATION; BOX and PALLET still require composition evidence',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
