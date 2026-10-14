declare n number;begin
 select count(*) into n from USER_OBJECTS where OBJECT_NAME in('RRL_STOCK_TASK_DOMAIN','RRL_STOCK_POOL_READ') and OBJECT_TYPE in('PACKAGE','PACKAGE BODY') and STATUS='VALID';
 if n!=4 then raise_application_error(-20808,'SECURED_DEMAND_PACKAGES_INVALID');end if;
end;
/
