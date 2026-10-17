-- PREPARE only: no existing package, task, session, balance or legacy clock is changed.
declare n number;begin
 if user!='RABAEV'then raise_application_error(-20886,'PICKER_TIME_SCHEMA_MISMATCH');end if;
 select count(*)into n from USER_CONSTRAINTS c where c.TABLE_NAME='RRL_WARES'and c.CONSTRAINT_TYPE in('P','U')and c.STATUS='ENABLED'and c.VALIDATED='VALIDATED'
  and(select count(*)from USER_CONS_COLUMNS x where x.CONSTRAINT_NAME=c.CONSTRAINT_NAME)=1
  and exists(select 1 from USER_CONS_COLUMNS x where x.CONSTRAINT_NAME=c.CONSTRAINT_NAME and x.COLUMN_NAME='ID'and x.POSITION=1);
 if n<1 then raise_application_error(-20886,'PICKER_TIME_WARE_UNIQUE_TARGET_REQUIRED');end if;
 select count(*)into n from USER_OBJECTS where STATUS='INVALID'and OBJECT_NAME not like 'BIN$%';
 if n!=0 then raise_application_error(-20886,'PICKER_TIME_GLOBAL_INVALID_BEFORE');end if;
 select count(*)into n from USER_OBJECTS where OBJECT_NAME in('RRL_PICKER_TIME_STREAM','RRL_PICKER_TIME_EVENT','RRL_PICKER_TIME_SPAN','RRL_PICKER_TIME_COMMAND',
  'RRL_PICKER_TIME_API','RRL_PICKER_TIME_AUTH','RRL_PICKER_TIME_READ','RRL_PICKER_TIME_WRITE',
  'RRL_PICKER_TIME_STREAM_G','RRL_PICKER_TIME_EVENT_G','RRL_PICKER_TIME_SPAN_G','RRL_PICKER_TIME_COMMAND_G');
 if n!=0 then raise_application_error(-20886,'PICKER_TIME_NAMESPACE_ALREADY_PRESENT');end if;
 select count(*)into n from USER_CONSTRAINTS where regexp_like(CONSTRAINT_NAME,'^PT_(STR|EV|SP|CMD)_[0-9]+$');
 if n!=0 then raise_application_error(-20886,'PICKER_TIME_CONSTRAINT_NAMESPACE_ALREADY_PRESENT');end if;
 select count(*)into n from USER_INDEXES where regexp_like(INDEX_NAME,'^PT_(STR|EV|SP|CMD)_[0-9]+$')or INDEX_NAME in('RRL_PICKER_TIME_EVENT_OP_IX','RRL_PICKER_TIME_SPAN_OP_IX','RRL_PICKER_TIME_CMD_OP_IX');
 if n!=0 then raise_application_error(-20886,'PICKER_TIME_INDEX_NAMESPACE_ALREADY_PRESENT');end if;
 select count(*)into n from RRL_SCHEMA_MIGRATIONS where MIGRATION_ID='2026-10-15-picker-actual-time-source';
 if n!=0 then raise_application_error(-20886,'PICKER_TIME_LEDGER_ALREADY_PRESENT');end if;
 -- ALL_CONTEXT is session values, not a context namespace catalog. CREATE CONTEXT is stop-on-error.
end;
/
