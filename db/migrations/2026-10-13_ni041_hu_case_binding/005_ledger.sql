merge into RRL_SCHEMA_MIGRATIONS t using(select '2026-10-13-008-ni041-hu-case-binding'MIGRATION_ID from dual)s on(t.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Existing HU tree operations declare and preserve active CASE fulfillment versions in the same stock transaction through reused binding core; closed shipment history unchanged',sysdate,user,'apply.sql','rollback.sql','APPLIED');
/
