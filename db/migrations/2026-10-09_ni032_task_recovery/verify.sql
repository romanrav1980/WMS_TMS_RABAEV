declare n number;begin
 select count(*) into n from USER_OBJECTS where OBJECT_NAME='RRL_STOCK_TASK_CORE' and STATUS!='VALID';
 if n>0 then raise_application_error(-20808,'TASK_CORE_INVALID');end if;
 select count(*) into n from USER_ERRORS where NAME='RRL_STOCK_TASK_CORE';
 if n>0 then raise_application_error(-20808,'TASK_CORE_ERRORS');end if;
end;
/
