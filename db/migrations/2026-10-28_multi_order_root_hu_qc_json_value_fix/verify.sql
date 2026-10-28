whenever sqlerror exit failure rollback
declare n number;begin select count(*) into n from user_objects where object_name='RRL_STOCK_QC_GATE' and object_type in('PACKAGE','PACKAGE BODY') and status!='VALID';if n<>0 then raise_application_error(-20999,'QC_GATE_JSON_VALUE_FIX_INVALID_OBJECT');end if;select count(*) into n from user_errors where name='RRL_STOCK_QC_GATE' and attribute='ERROR';if n<>0 then raise_application_error(-20999,'QC_GATE_JSON_VALUE_FIX_COMPILE_ERROR');end if;end;
/
