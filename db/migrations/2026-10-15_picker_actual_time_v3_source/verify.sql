@@installed_guard.sql
declare n number;begin
 select count(*)into n from USER_OBJECTS where STATUS='INVALID'and OBJECT_NAME not like 'BIN$%';
 if n!=0 then raise_application_error(-20886,'PICKER_TIME_GLOBAL_INVALID_AFTER');end if;
 select count(*)into n from USER_ERRORS where NAME in('RRL_PICKER_TIME_API','RRL_PICKER_TIME_AUTH','RRL_PICKER_TIME_READ','RRL_PICKER_TIME_WRITE',
  'RRL_PICKER_TIME_STREAM_G','RRL_PICKER_TIME_EVENT_G','RRL_PICKER_TIME_SPAN_G','RRL_PICKER_TIME_COMMAND_G');
 if n!=0 then raise_application_error(-20886,'PICKER_TIME_COMPILE_ERRORS');end if;
 select count(*)into n from USER_TABLES where TABLE_NAME in('RRL_PICKER_TIME_STREAM','RRL_PICKER_TIME_EVENT','RRL_PICKER_TIME_SPAN','RRL_PICKER_TIME_COMMAND');
 if n!=4 then raise_application_error(-20886,'PICKER_TIME_FOUR_TABLES_REQUIRED');end if;
 select count(*)into n from USER_CONSTRAINTS where TABLE_NAME in('RRL_PICKER_TIME_STREAM','RRL_PICKER_TIME_EVENT','RRL_PICKER_TIME_SPAN','RRL_PICKER_TIME_COMMAND')and(STATUS!='ENABLED'or VALIDATED!='VALIDATED');
 if n!=0 then raise_application_error(-20886,'PICKER_TIME_CONSTRAINT_DISABLED');end if;
 select count(*)into n from USER_INDEXES where TABLE_NAME in('RRL_PICKER_TIME_STREAM','RRL_PICKER_TIME_EVENT','RRL_PICKER_TIME_SPAN','RRL_PICKER_TIME_COMMAND')and INDEX_TYPE!='LOB'and STATUS!='VALID';
 if n!=0 then raise_application_error(-20886,'PICKER_TIME_INDEX_INVALID');end if;
 RRL_PICKER_TIME_API.verify_binding;
end;
/
