declare n number;begin
 select count(*)into n from USER_ERRORS where NAME in('RRL_WAVE_CONTINUE_API','RRL_WAVE_EXEC_ACCESS','RRL_STOCK_WAVE_CMD','RRL_STOCK_POSTING_API','RRL_WAVE_CONTINUE_GUARD','RRL_WAVE_CONTINUE_STEP_GUARD','RRL_WAVE_CONTINUE_SOURCE_GUARD');
 if n!=0 then raise_application_error(-20886,'WAVE_CONTINUATION_COMPILE_ERRORS');end if;
 select count(*)into n from USER_OBJECTS where STATUS='INVALID';
 if n!=0 then raise_application_error(-20886,'WAVE_CONTINUATION_GLOBAL_INVALID');end if;
end;
/
select MIGRATION_ID,STATUS from RRL_SCHEMA_MIGRATIONS where MIGRATION_ID='2026-10-15-wave-launch-continuation';
select STATE,count(*)from RRL_WAVE_CONTINUE group by STATE;
