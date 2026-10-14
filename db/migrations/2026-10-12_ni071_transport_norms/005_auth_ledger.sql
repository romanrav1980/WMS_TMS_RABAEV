merge into RRL_SCHEMA_MIGRATIONS t using(select '2026-10-12-534-transport-norm-current-auth-locks' MIGRATION_ID from dual)s on(t.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Norm publication locks actor/grant then exact source/head; saved replay cannot outlive current rights',sysdate,user,'004_auth_locks.sql','rollback.sql','APPLIED');
/
