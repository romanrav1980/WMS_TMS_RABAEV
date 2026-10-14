merge into RRL_SCHEMA_MIGRATIONS t using(select '2026-10-12-559-vehicle-source-at-departure' MIGRATION_ID from dual)s on(t.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Versioned cargo dimensions/class on existing vehicle; immutable actual carrier/type/region/profile at original departure, one timestamp for whole trip',sysdate,user,'apply.sql','rollback.sql','APPLIED');
/
