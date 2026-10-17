-- Refuse destructive rollback once any durable workflow receipt exists. Export/recovery decision required.
declare n number;begin select count(*)into n from RRL_WAVE_CONTINUE;
 if n!=0 then raise_application_error(-20886,'WAVE_CONTINUATION_RECEIPTS_MUST_BE_PRESERVED');end if;end;
/
@@before_posting.sql
@@before_wave_sources.sql
@@before_wave_access.sql
drop table RRL_WAVE_CONTINUE_SOURCE;
drop table RRL_WAVE_CONTINUE_STEP;
drop table RRL_WAVE_CONTINUE;
drop package RRL_WAVE_CONTINUE_API;
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK' where MIGRATION_ID='2026-10-15-wave-launch-continuation';
commit;
declare n number;begin
 select count(*)into n from USER_ERRORS where NAME in('RRL_WAVE_CONTINUE_API','RRL_WAVE_EXEC_ACCESS','RRL_STOCK_WAVE_CMD','RRL_STOCK_POSTING_API','RRL_WAVE_CONTINUE_GUARD','RRL_WAVE_CONTINUE_STEP_GUARD','RRL_WAVE_CONTINUE_SOURCE_GUARD');
 if n!=0 then raise_application_error(-20886,'WAVE_CONTINUATION_COMPILE_ERRORS');end if;
 select count(*)into n from USER_OBJECTS where STATUS='INVALID';
 if n!=0 then raise_application_error(-20886,'WAVE_CONTINUATION_GLOBAL_INVALID');end if;
end;
/
