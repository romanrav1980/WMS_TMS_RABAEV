declare n number;
begin
 select count(*) into n from USER_OBJECTS where OBJECT_NAME in('RRL_STOCK_TASK_SCAN','RRL_STOCK_TASK_PLAN','RRL_STOCK_TASK_CORE','RRL_TASK_SCAN_IMMUTABLE') and STATUS!='VALID';
 if n>0 then raise_application_error(-20808,'TASK_SCAN_OBJECTS_INVALID');end if;
end;
/
