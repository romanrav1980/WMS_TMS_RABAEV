@@installed_guard.sql
-- Stop writers first. Any manual fact OR rejected receipt is retained history: forward recovery only.
declare n number;begin
 select(select count(*)from RRL_PICKER_TIME_STREAM)+(select count(*)from RRL_PICKER_TIME_EVENT)
  +(select count(*)from RRL_PICKER_TIME_SPAN)+(select count(*)from RRL_PICKER_TIME_COMMAND)into n from dual;
 if n!=0 then raise_application_error(-20886,'PICKER_TIME_HISTORY_FORWARD_REPAIR_REQUIRED');end if;
 -- Never drop an unproven context after a partial CREATE CONTEXT/name collision.
 RRL_PICKER_TIME_API.verify_binding;
end;
/
drop trigger RRL_PICKER_TIME_COMMAND_G;
drop trigger RRL_PICKER_TIME_SPAN_G;
drop trigger RRL_PICKER_TIME_EVENT_G;
drop trigger RRL_PICKER_TIME_STREAM_G;
drop context RRL_PICKER_TIME_CTX;
drop package RRL_PICKER_TIME_API;
drop package RRL_PICKER_TIME_WRITE;
drop package RRL_PICKER_TIME_READ;
drop package RRL_PICKER_TIME_AUTH;
drop table RRL_PICKER_TIME_SPAN;
drop table RRL_PICKER_TIME_EVENT;
drop table RRL_PICKER_TIME_COMMAND;
drop table RRL_PICKER_TIME_STREAM;
begin dbms_utility.compile_schema(schema=>user,compile_all=>false);end;
/
declare n number;begin
 select count(*)into n from USER_OBJECTS where STATUS='INVALID'and OBJECT_NAME not like 'BIN$%';
 if n!=0 then raise_application_error(-20886,'PICKER_TIME_ROLLBACK_GLOBAL_INVALID');end if;
 select count(*)into n from USER_OBJECTS where OBJECT_NAME like 'RRL_PICKER_TIME_%';
 if n!=0 then raise_application_error(-20886,'PICKER_TIME_ROLLBACK_OBJECTS_REMAIN');end if;
end;
/
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK'where MIGRATION_ID='2026-10-15-picker-actual-time-source';
commit;
