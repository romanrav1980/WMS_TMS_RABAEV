create or replace trigger RRL_SAP_STORE_ADM_GUARD before update of ADMISSION_STATUS or delete on RRL_SAP_STORE_ORDER for each row
begin
 if RRL_SAP_STORE_ADMISSION_API.write_allowed!=1 then raise_application_error(-20863,'STORE_ADMISSION_NATIVE_DECISION_REQUIRED');end if;
end;
/
create or replace trigger RRL_SAP_STORE_DEC_GUARD before insert or update or delete on RRL_SAP_STORE_DECISION for each row
begin
 if not inserting or RRL_SAP_STORE_ADMISSION_API.write_allowed!=1 then raise_application_error(-20863,'STORE_ADMISSION_DECISION_IMMUTABLE');end if;
end;
/
create or replace trigger RRL_SAP_STORE_PICK_GUARD before insert or update of CUSTOMER_ORDER_ID on RRL_PICK_PLAN for each row
declare n number;v_ware number;v_store number;v_day date;v_offset number;v_allowed number;v_rule clob;v_original_offset number;
begin
 select count(*)into n from RRL_SAP_STORE_ORDER where CUSTOMER_ORDER_ID=:new.CUSTOMER_ORDER_ID;
 if n>0 then
  select count(*)into n from RRL_SAP_STORE_ORDER where CUSTOMER_ORDER_ID=:new.CUSTOMER_ORDER_ID and ADMISSION_STATUS!='ACCEPTED';
  if n>0 then raise_application_error(-20863,'SAP_ORDER_ADMISSION_NOT_ACCEPTED');end if;
  select c.WARE_ID,c.CUSTOMER_STORE_MAP_ID,s.DELIVERY_DATE,s.UTC_OFFSET_MINUTES into v_ware,v_store,v_day,v_original_offset
   from RRL_CUSTOMER_ORDER c join RRL_SAP_STORE_ORDER s on s.CUSTOMER_ORDER_ID=c.CUSTOMER_ORDER_ID where c.CUSTOMER_ORDER_ID=:new.CUSTOMER_ORDER_ID;
  RRL_STORE_CALENDAR_API.delivery_rule(v_ware,v_store,v_day,v_offset,v_allowed,v_rule);
  if v_allowed!=1 or v_offset!=v_original_offset then raise_application_error(-20863,'SAP_ORDER_CURRENT_CALENDAR_NOT_ADMITTED');end if;
 end if;
end;
/
