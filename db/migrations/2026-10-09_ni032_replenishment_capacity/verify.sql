declare n number;begin
 select count(*) into n from USER_OBJECTS where OBJECT_NAME in('RRL_STOCK_REPL_CAPACITY','RRL_STOCK_WAVE_CMD','RRL_STOCK_TASK_PLAN','RRL_STOCK_TASK_CORE') and STATUS!='VALID';
 if n>0 then raise_application_error(-20808,'REPLENISHMENT_CAPACITY_PACKAGES_INVALID');end if;
end;
/
