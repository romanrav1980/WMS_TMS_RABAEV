begin dbms_utility.compile_schema(schema=>user,compile_all=>false);end;
/
declare n number;begin
 select count(*)into n from USER_ERRORS where NAME in('RRL_CASE_TASK_ACCESS','RRL_CASE_RESOURCE_POLICY','RRL_STOCK_CASE_PICK_CMD');
 if n!=0 then raise_application_error(-20886,'CASE_SCOPED_COMPILE_ERRORS');end if;
 select count(*)into n from USER_OBJECTS where STATUS='INVALID';
 if n!=0 then raise_application_error(-20886,'CASE_SCOPED_GLOBAL_INVALID');end if;
end;
/
