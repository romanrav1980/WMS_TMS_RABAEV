-- MIGRATION_ID: 2026-10-15-wave-scoped-views
@@rrl_wave_exec_access.sql
@@rrl_wave_time_api.sql
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-15-wave-scoped-views' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Native scoped wave/time view; legacy write gates retained',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
