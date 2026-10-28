whenever sqlerror exit failure rollback
declare n number;begin
 select count(*) into n from user_objects where object_name='RRL_STOCK_TARE_BOOK_CMD' and object_type='PACKAGE BODY' and status<>'VALID';if n<>0 then raise_application_error(-20999,'ROOT_HU_TARE_ROLLBACK_INVALID');end if;
 select count(*) into n from user_errors where name='RRL_STOCK_TARE_BOOK_CMD' and attribute='ERROR';if n<>0 then raise_application_error(-20999,'ROOT_HU_TARE_ROLLBACK_COMPILE_ERROR');end if;
end;
/
