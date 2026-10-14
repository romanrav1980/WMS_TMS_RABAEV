declare n number;begin
 select count(*) into n from USER_OBJECTS where OBJECT_NAME in('RRL_STOCK_POOL_READ','RRL_STOCK_POOL_CMD','RRL_STOCK_POSTING_API') and STATUS!='VALID';
 if n>0 then raise_application_error(-20808,'SOFT_POOL_PACKAGES_INVALID');end if;
 select count(*) into n from USER_OBJECTS where OBJECT_NAME in('RRL_STOCK_POOL_READ','RRL_STOCK_POOL_CMD') and OBJECT_TYPE in('PACKAGE','PACKAGE BODY') and STATUS='VALID';
 if n!=4 then raise_application_error(-20808,'SOFT_POOL_PACKAGES_MISSING');end if;
end;
/
