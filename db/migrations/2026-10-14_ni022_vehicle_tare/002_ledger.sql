merge into RRL_SCHEMA_MIGRATIONS t using(select '2026-10-14-1179-vehicle-tare-variants' MIGRATION_ID from dual)s on(t.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Explicit floor loading variants by existing active tare types through versioned vehicle profile; no derived area capacity',sysdate,user,'apply.sql','rollback.sql','APPLIED');
/
