merge into RRL_SCHEMA_MIGRATIONS t using(select '2026-10-13-004-ni072-case-waiting'MIGRATION_ID from dual)s on(t.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Standalone prepared CASE waiting task through existing CASE_CARRIER_MOVE root with exact owned lots/reservations and same-transaction completion',sysdate,user,'apply.sql','rollback.sql','APPLIED');
/
