merge into RRL_SCHEMA_MIGRATIONS t using(select '2026-10-13-834-ni032-sequential-sources' MIGRATION_ID from dual)s on(t.MIGRATION_ID=s.MIGRATION_ID)
when matched then update set STATUS='APPLIED',APPLIED_AT=sysdate,APPLIED_BY=user
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Partial target rebind retains multiple distinct own sources and reuses original sequential replenishment continuation',sysdate,user,'apply.sql','rollback.sql','APPLIED');
/
