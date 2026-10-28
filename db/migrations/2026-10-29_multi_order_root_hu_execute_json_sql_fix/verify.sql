whenever sqlerror exit failure rollback
declare n number;begin select count(*) into n from user_objects where object_name='RRL_STOCK_SHIPPING_CORE' and object_type in('PACKAGE','PACKAGE BODY') and status!='VALID';if n<>0 then raise_application_error(-20999,'SHIPPING_CORE_EXECUTE_JSON_FIX_INVALID_OBJECT');end if;select count(*) into n from user_errors where name='RRL_STOCK_SHIPPING_CORE' and attribute='ERROR';if n<>0 then raise_application_error(-20999,'SHIPPING_CORE_EXECUTE_JSON_FIX_COMPILE_ERROR');end if;end;
/
