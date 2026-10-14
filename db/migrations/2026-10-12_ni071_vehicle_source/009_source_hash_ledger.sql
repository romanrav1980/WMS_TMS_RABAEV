merge into RRL_SCHEMA_MIGRATIONS t using(select '2026-10-12-561-vehicle-profile-base-hash' MIGRATION_ID from dual)s on(t.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Expected base hash prevents stale dimensions attaching to changed existing vehicle record; cached operation remains historical result',sysdate,user,'apply_source_hash.sql','rollback_source_hash.sql','APPLIED');
/
