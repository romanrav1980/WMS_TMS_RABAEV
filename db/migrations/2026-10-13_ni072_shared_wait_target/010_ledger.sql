merge into RRL_SCHEMA_MIGRATIONS t using(select '2026-10-13-013-ni072-shared-wait-target'MIGRATION_ID from dual)s on(t.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Allow shared waiting-zone admission only for trusted current defer planning and registered physical WAIT tasks; preserve generic exclusive targets',sysdate,user,'apply.sql','rollback.sql','APPLIED');
/
