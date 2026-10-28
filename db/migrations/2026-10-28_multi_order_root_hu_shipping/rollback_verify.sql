whenever sqlerror exit failure rollback
declare n number;begin
 select count(*) into n from user_objects where object_name in('RRL_STOCK_SHIPPING_CORE','RRL_STOCK_QC_CASE','RRL_QC_SCOPE_READ','RRL_STOCK_QC_POLICY','RRL_STOCK_QC_GATE','RRL_WH_FINAL_SCALE_ADMISSION') and object_type in('PACKAGE','PACKAGE BODY') and status!='VALID';
 if n<>0 then raise_application_error(-20999,'MULTI_ORDER_ROLLBACK_INVALID_OBJECT');end if;
end;
/

