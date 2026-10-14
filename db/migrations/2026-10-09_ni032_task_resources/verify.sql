declare n number;begin
 select count(*) into n from USER_OBJECTS where OBJECT_NAME in('RRL_TASK_RESOURCE_POLICY','RRL_STOCK_TASK_PLAN','RRL_STOCK_TASK_CORE','RRL_STOCK_POSTING_API') and STATUS!='VALID';
 if n>0 then raise_application_error(-20808,'TASK_RESOURCE_OBJECT_INVALID');end if;
 select count(*) into n from USER_ERRORS where NAME in('RRL_TASK_RESOURCE_POLICY','RRL_STOCK_TASK_PLAN','RRL_STOCK_TASK_CORE','RRL_STOCK_POSTING_API');
 if n>0 then raise_application_error(-20808,'TASK_RESOURCE_COMPILATION_ERRORS');end if;
end;
/
