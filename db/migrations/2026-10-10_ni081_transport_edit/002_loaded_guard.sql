create or replace trigger RRL_TT_PHYSICAL_DEPART_GUARD before update or delete on RRL_TRANSPORT_TASK for each row
declare op varchar2(100):=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID');kind_name varchar2(80);state_name varchar2(20);n number;
begin
 if deleting then
  select count(*) into n from RRL_TT_HU_LOAD_FACT where TT_ID=:old.ID;
  if n>0 then raise_application_error(-20863,'TRIP_PHYSICAL_HISTORY_DELETE_FORBIDDEN');end if;return;
 end if;
 if nvl(:new.TRANSPORT,chr(0))!=nvl(:old.TRANSPORT,chr(0)) or nvl(:new.DOCK,chr(0))!=nvl(:old.DOCK,chr(0))
  or nvl(:new.VODITEL_ID,-1)!=nvl(:old.VODITEL_ID,-1) or nvl(:new.DELETED,0)!=nvl(:old.DELETED,0)
  or nvl(:new.SHIPMENT_DATE,date '1900-01-01')!=nvl(:old.SHIPMENT_DATE,date '1900-01-01')
  or nvl(:new.SHIPMENT_TIME,date '1900-01-01')!=nvl(:old.SHIPMENT_TIME,date '1900-01-01')
  or nvl(:new.TRANSTYPE,chr(0))!=nvl(:old.TRANSTYPE,chr(0)) then
  select count(*) into n from RRL_TT_HU_LOAD_FACT where TT_ID=:old.ID and STATUS in('LOADED','DEPARTED');
  if n>0 then raise_application_error(-20886,'TRIP_CONFIRMED_UNLOADING_REQUIRED_BEFORE_REASSIGNMENT');end if;
 end if;
 if :new.CONDITION=unistr('\041E\0442\0433\0440\0443\0436\0435\043D') and nvl(:old.CONDITION,chr(0))!=:new.CONDITION then
  if op is null or sys_context('RRL_STOCK_WRITE_CTX','TX_ID') is null or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false) then raise_application_error(-20863,'TRIP_PHYSICAL_DEPARTURE_COMMAND_REQUIRED');end if;
  select COMMAND_TYPE,STATE into kind_name,state_name from RRL_STOCK_OPERATION where OPERATION_ID=op;
  if kind_name!='TRIP_DEPART' or state_name!='IN_FLIGHT' then raise_application_error(-20863,'TRIP_PHYSICAL_DEPARTURE_COMMAND_REQUIRED');end if;
  RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_TRANSPORT_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(:old.ID)));
 end if;
end;
/
