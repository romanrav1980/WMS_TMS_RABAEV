merge into RRL_SCHEMA_MIGRATIONS t using(select '2026-10-13-009-ni041-case-slot-binding'MIGRATION_ID from dual)s on(t.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Existing direct CASE physical slot relocation preserves active fulfillment version through the shared binding core, current ST/CASE actual-row order and original placement/reservation transaction',sysdate,user,'apply.sql','rollback.sql','APPLIED');
/
