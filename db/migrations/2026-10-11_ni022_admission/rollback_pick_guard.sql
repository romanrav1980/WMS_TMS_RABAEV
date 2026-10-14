create or replace trigger RRL_SAP_STORE_PICK_GUARD
before insert or update of CUSTOMER_ORDER_ID on RRL_PICK_PLAN for each row
declare n number;
begin
 select count(*) into n from RRL_SAP_STORE_ORDER where CUSTOMER_ORDER_ID=:new.CUSTOMER_ORDER_ID and ADMISSION_STATUS!='ACCEPTED';
 if n>0 then raise_application_error(-20863,'Late SAP order requires explicit logistics admission before planning'); end if;
end;
/
