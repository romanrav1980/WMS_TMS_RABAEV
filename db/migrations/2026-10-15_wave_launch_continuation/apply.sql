-- MIGRATION_ID: 2026-10-15-wave-launch-continuation
@@schema.sql
@@continuation_api.sql
@@guards.sql
@@wave_access.sql
@@wave_sources.sql
@@posting.sql
declare n number;begin
 select count(*)into n from USER_ERRORS where NAME in('RRL_WAVE_CONTINUE_API','RRL_WAVE_EXEC_ACCESS','RRL_STOCK_WAVE_CMD','RRL_STOCK_POSTING_API','RRL_WAVE_CONTINUE_GUARD','RRL_WAVE_CONTINUE_STEP_GUARD','RRL_WAVE_CONTINUE_SOURCE_GUARD');
 if n!=0 then raise_application_error(-20886,'WAVE_CONTINUATION_COMPILE_ERRORS');end if;
 select count(*)into n from USER_OBJECTS where STATUS='INVALID';
 if n!=0 then raise_application_error(-20886,'WAVE_CONTINUATION_GLOBAL_INVALID');end if;
end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-15-wave-launch-continuation' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Scoped original wave launch continuation with atomic metadata steps and frozen canonical source intents',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
