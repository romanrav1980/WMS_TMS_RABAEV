-- MIGRATION_ID: 2026-10-15-store-app-final-leg
@@body.sql
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-15-store-app-final-leg' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)values(s.MIGRATION_ID,'Store preview must be final destination, same as existing receipt trigger',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
