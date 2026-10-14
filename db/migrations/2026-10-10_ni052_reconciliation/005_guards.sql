create or replace trigger RRL_TT_HU_LOAD_FACT_GUARD before insert or update or delete on RRL_TT_HU_LOAD_FACT for each row
declare op varchar2(100):=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID');kind_name varchar2(80);state_name varchar2(20);key_name varchar2(100);physical_key varchar2(200);
begin
 if deleting then raise_application_error(-20863,'PHYSICAL_LOAD_HISTORY_IMMUTABLE');end if;
 if op is null or sys_context('RRL_STOCK_WRITE_CTX','TX_ID') is null or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false) then raise_application_error(-20863,'PHYSICAL_LOAD_ROOT_REQUIRED');end if;
 select COMMAND_TYPE,STATE into kind_name,state_name from RRL_STOCK_OPERATION where OPERATION_ID=op;
 if state_name!='IN_FLIGHT' then raise_application_error(-20863,'PHYSICAL_LOAD_ROOT_IN_FLIGHT_REQUIRED');end if;
 key_name:=case when inserting then :new.LOAD_OPERATION_ID else :old.LOAD_OPERATION_ID end;
 RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_TT_HU_LOAD_FACT',key_name));
 if inserting then
  if kind_name not in('HU_SHIP','LOAD_SHIPMENT','RECONCILE_HU_LOAD') or :new.LOAD_OPERATION_ID!=op or :new.STATUS!='LOADED' or :new.DEPARTURE_OPERATION_ID is not null then raise_application_error(-20863,'PHYSICAL_LOAD_SHIPMENT_REQUIRED');end if;
  physical_key:=case when :new.ROOT_CASE_TASK_ID is null then :new.ROOT_UID else 'CASE:'||RRL_STOCK_PLAN_HELPER.decimal_text(:new.ROOT_CASE_TASK_ID) end;
  RRL_STOCK_LOCK_API.assert_held(30,RRL_STOCK_LOCK_API.resource_key('HU',physical_key));
 elsif kind_name!='TRIP_DEPART' or :old.STATUS!='LOADED' or :new.STATUS!='DEPARTED' or :new.DEPARTURE_OPERATION_ID is null or :new.DEPARTURE_OPERATION_ID!=op
  or :new.LOAD_OPERATION_ID!=:old.LOAD_OPERATION_ID or :new.TT_ID!=:old.TT_ID or nvl(:new.ROOT_UID,chr(0))!=nvl(:old.ROOT_UID,chr(0)) or nvl(:new.ROOT_CASE_TASK_ID,-1)!=nvl(:old.ROOT_CASE_TASK_ID,-1) or :new.VEHICLE_ID!=:old.VEHICLE_ID
  or :new.VEHICLE_NUMBER!=:old.VEHICLE_NUMBER or :new.DOCK!=:old.DOCK or :new.WARE_ID!=:old.WARE_ID
  or :new.GROSS_WEIGHT_KG!=:old.GROSS_WEIGHT_KG or :new.BOUNDING_VOLUME_M3!=:old.BOUNDING_VOLUME_M3 or :new.CONTENT_VERSION!=:old.CONTENT_VERSION
  or :new.LOADED_BY!=:old.LOADED_BY or :new.LOADED_AT!=:old.LOADED_AT or dbms_lob.compare(:new.COMPOSITION_JSON,:old.COMPOSITION_JSON)!=0 then raise_application_error(-20863,'PHYSICAL_LOAD_DEPARTURE_ONLY');end if;
end;
/
create or replace trigger RRL_TT_HU_LOAD_ST_GUARD before insert or update or delete on RRL_TT_HU_LOAD_ST for each row
declare op varchar2(100):=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID');kind_name varchar2(80);state_name varchar2(20);
begin
 if not inserting then raise_application_error(-20863,'PHYSICAL_LOAD_MEMBERS_IMMUTABLE');end if;
 if op is null or sys_context('RRL_STOCK_WRITE_CTX','TX_ID') is null or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false) then raise_application_error(-20863,'PHYSICAL_LOAD_ROOT_REQUIRED');end if;
 select COMMAND_TYPE,STATE into kind_name,state_name from RRL_STOCK_OPERATION where OPERATION_ID=op;
 if kind_name not in('HU_SHIP','LOAD_SHIPMENT','RECONCILE_HU_LOAD') or state_name!='IN_FLIGHT' or :new.LOAD_OPERATION_ID!=op then raise_application_error(-20863,'PHYSICAL_LOAD_MEMBER_SHIPMENT_REQUIRED');end if;
 RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_TT_HU_LOAD_ST',op||':'||RRL_STOCK_PLAN_HELPER.decimal_text(:new.SBORKA_PALLET_ID)));
end;
/
create or replace trigger RRL_TT_PHYSICAL_DEPART_GUARD before update or delete on RRL_TRANSPORT_TASK for each row
declare op varchar2(100):=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID');kind_name varchar2(80);state_name varchar2(20);n number;
begin
 if deleting then
  select count(*) into n from RRL_TT_HU_LOAD_FACT where TT_ID=:old.ID;
  if n>0 then raise_application_error(-20863,'TRIP_PHYSICAL_HISTORY_DELETE_FORBIDDEN');end if;return;
 end if;
 if nvl(:new.TRANSPORT,chr(0))!=nvl(:old.TRANSPORT,chr(0)) or nvl(:new.DOCK,chr(0))!=nvl(:old.DOCK,chr(0))
  or nvl(:new.VODITEL_ID,-1)!=nvl(:old.VODITEL_ID,-1) or nvl(:new.DELETED,0)!=nvl(:old.DELETED,0) then
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
create or replace trigger RRL_TT_LOADED_ST_ASSIGN_GUARD before update of TRANSTASK_ID or delete on RRL_SBORKA_PALLETS for each row
declare n number;
begin
 if updating and nvl(:new.TRANSTASK_ID,0)=nvl(:old.TRANSTASK_ID,0) then return;end if;
 select count(*) into n from RRL_TT_HU_LOAD_ST ls join RRL_TT_HU_LOAD_FACT lf on lf.LOAD_OPERATION_ID=ls.LOAD_OPERATION_ID
  where ls.SBORKA_PALLET_ID=:old.ID and ls.ACTIVE_FLAG=1 and lf.STATUS in('LOADED','DEPARTED');
 if n>0 then raise_application_error(-20886,'LOADED_ST_CONFIRMED_UNLOADING_REQUIRED');end if;
end;
/

create or replace trigger RRL_TT_RECONCILE_GUARD before insert or update or delete on RRL_TT_LOAD_RECONCILE for each row
declare op varchar2(100):=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID');kind_text varchar2(80);state_text varchar2(20);
begin
 if not inserting then raise_application_error(-20863,'RECONCILIATION_HISTORY_IMMUTABLE');end if;
 if op is null or op!=:new.LOAD_OPERATION_ID or sys_context('RRL_STOCK_WRITE_CTX','TX_ID') is null
  or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false) then raise_application_error(-20863,'RECONCILIATION_ROOT_REQUIRED');end if;
 select COMMAND_TYPE,STATE into kind_text,state_text from RRL_STOCK_OPERATION where OPERATION_ID=op;
 if kind_text!='RECONCILE_HU_LOAD' or state_text!='IN_FLIGHT' then raise_application_error(-20863,'RECONCILIATION_ROOT_REQUIRED');end if;
 RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_TT_LOAD_RECONCILE',op));
end;
/
