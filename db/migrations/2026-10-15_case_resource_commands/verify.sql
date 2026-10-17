begin dbms_utility.compile_schema(schema=>user,compile_all=>false);end;
/
declare n number;begin
 select count(*)into n from USER_ERRORS where NAME in('RRL_CASE_ASSIGNMENT_API','RRL_CASE_ASSIGN_VERSION_GUARD','RRL_CASE_RESOURCE_CMD_GUARD','RRL_CASE_START_TIME_GUARD','RRL_CASE_TASK_ACCESS','RRL_CASE_RESOURCE_POLICY');
 if n!=0 then raise_application_error(-20886,'CASE_RESOURCE_COMPILE_ERRORS');end if;
 select count(*)into n from USER_OBJECTS where STATUS='INVALID';if n!=0 then raise_application_error(-20886,'CASE_RESOURCE_GLOBAL_INVALID');end if;
 select count(*)into n from USER_CONSTRAINTS where TABLE_NAME in('RRL_CASE_RESOURCE_COMMAND')and STATUS!='ENABLED';if n!=0 then raise_application_error(-20886,'CASE_RESOURCE_CONSTRAINT_DISABLED');end if;
end;
/
