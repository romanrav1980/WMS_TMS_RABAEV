@@after_source_guard.sql
declare n number;begin
 select count(*)into n from USER_ERRORS where NAME not like 'BIN$%';if n!=0 then raise_application_error(-20886,'WTASK_COMPILE_ERRORS');end if;
 select count(*)into n from USER_OBJECTS where STATUS='INVALID';if n!=0 then raise_application_error(-20886,'WTASK_GLOBAL_INVALID');end if;
 select count(*)into n from USER_TAB_COLUMNS where TABLE_NAME='RRL_WTASK_ASSIGN_VERSION';if n!=3 then raise_application_error(-20886,'WTASK_CLOCK_COLUMNS');end if;
 select count(*)into n from USER_TAB_COLUMNS where TABLE_NAME='RRL_WTASK_RESOURCE_COMMAND';if n!=13 then raise_application_error(-20886,'WTASK_RECEIPT_COLUMNS');end if;
 select count(*)into n from USER_TAB_COLUMNS where TABLE_NAME='RRL_WAREHOUSE_TASK'and COLUMN_NAME='ASSIGNMENT_VERSION';if n!=0 then raise_application_error(-20886,'WTASK_NO_TABLE_ALTER');end if;
 select count(*)into n from USER_CONSTRAINTS where TABLE_NAME in('RRL_WTASK_ASSIGN_VERSION','RRL_WTASK_RESOURCE_COMMAND')and(STATUS!='ENABLED'or VALIDATED!='VALIDATED');if n!=0 then raise_application_error(-20886,'WTASK_CONSTRAINT_DISABLED');end if;
 select count(*)into n from USER_CONSTRAINTS where TABLE_NAME in('RRL_WTASK_ASSIGN_VERSION','RRL_WTASK_RESOURCE_COMMAND')and CONSTRAINT_TYPE='P';if n!=2 then raise_application_error(-20886,'WTASK_PRIMARY_KEYS');end if;
 select count(*)into n from USER_CONSTRAINTS where TABLE_NAME in('RRL_WTASK_ASSIGN_VERSION','RRL_WTASK_RESOURCE_COMMAND')and CONSTRAINT_TYPE='R'and DELETE_RULE='NO ACTION';if n!=2 then raise_application_error(-20886,'WTASK_RETAIN_HISTORY_FK');end if;
 select count(*)into n from USER_INDEXES where TABLE_NAME in('RRL_WTASK_ASSIGN_VERSION','RRL_WTASK_RESOURCE_COMMAND')and STATUS='VALID';if n!=3 then raise_application_error(-20886,'WTASK_INDEXES');end if;
 RRL_WTASK_ASSIGN_API.verify_binding;
end;
/
