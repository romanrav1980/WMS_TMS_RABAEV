declare n number;begin
 select count(*) into n from USER_OBJECTS where OBJECT_NAME in('RRL_STOCK_REPL_BIND','RRL_STOCK_RESERVE_CORE','RRL_STOCK_UNIT_CORE','RRL_STOCK_TASK_PLAN','RRL_STOCK_TASK_CORE') and OBJECT_TYPE in('PACKAGE','PACKAGE BODY') and STATUS='VALID';
 if n!=10 then raise_application_error(-20808,'WAVE_CONSUMER_BINDING_INVALID');end if;
end;
/
