declare n number;begin
 select count(*) into n from USER_OBJECTS where OBJECT_NAME in('RRL_STOCK_POOL_CMD','RRL_STOCK_WAVE_LAUNCH_CMD') and OBJECT_TYPE in('PACKAGE','PACKAGE BODY') and STATUS='VALID';
 if n!=4 then raise_application_error(-20808,'POOL_WAVE_PACKAGES_INVALID');end if;
end;
/
