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
  if :new.CUSTODY_RELEASED_AT is not null or :new.CUSTODY_RELEASE_OPERATION_ID is not null then raise_application_error(-20863,'NEW_LOAD_CANNOT_HAVE_RELEASED_CUSTODY');end if;
  if kind_name not in('HU_SHIP','LOAD_SHIPMENT','RECONCILE_HU_LOAD') or :new.LOAD_OPERATION_ID!=op or :new.STATUS!='LOADED' or :new.DEPARTURE_OPERATION_ID is not null then raise_application_error(-20863,'PHYSICAL_LOAD_SHIPMENT_REQUIRED');end if;
  physical_key:=case when :new.ROOT_CASE_TASK_ID is null then :new.ROOT_UID else 'CASE:'||RRL_STOCK_PLAN_HELPER.decimal_text(:new.ROOT_CASE_TASK_ID) end;
  RRL_STOCK_LOCK_API.assert_held(30,RRL_STOCK_LOCK_API.resource_key('HU',physical_key));
 elsif kind_name='INTERWARE_CUSTODY_RELEASE' then
  if :old.STATUS!='DEPARTED' or :new.STATUS!=:old.STATUS or :old.CUSTODY_RELEASED_AT is not null or :old.CUSTODY_RELEASE_OPERATION_ID is not null or :new.CUSTODY_RELEASED_AT is null or :new.CUSTODY_RELEASE_OPERATION_ID is null or :new.CUSTODY_RELEASE_OPERATION_ID!=op then raise_application_error(-20863,'INTERWARE_CUSTODY_RELEASE_REQUIRED');end if;
  if :new.LOAD_OPERATION_ID!=:old.LOAD_OPERATION_ID or :new.TT_ID!=:old.TT_ID or nvl(:new.ROOT_UID,chr(0))!=nvl(:old.ROOT_UID,chr(0))or nvl(:new.ROOT_CASE_TASK_ID,-1)!=nvl(:old.ROOT_CASE_TASK_ID,-1)or :new.VEHICLE_ID!=:old.VEHICLE_ID or :new.VEHICLE_NUMBER!=:old.VEHICLE_NUMBER or :new.DOCK!=:old.DOCK or :new.WARE_ID!=:old.WARE_ID or :new.GROSS_WEIGHT_KG!=:old.GROSS_WEIGHT_KG or :new.BOUNDING_VOLUME_M3!=:old.BOUNDING_VOLUME_M3 or :new.CONTENT_VERSION!=:old.CONTENT_VERSION or :new.LOADED_BY!=:old.LOADED_BY or :new.LOADED_AT!=:old.LOADED_AT or :new.DEPARTURE_OPERATION_ID!=:old.DEPARTURE_OPERATION_ID or :new.DEPARTED_AT!=:old.DEPARTED_AT or dbms_lob.compare(:new.COMPOSITION_JSON,:old.COMPOSITION_JSON)!=0 then raise_application_error(-20863,'INTERWARE_DEPARTURE_HISTORY_IMMUTABLE');end if;
  declare n number;begin
   select count(*)into n from RRL_INTERWARE_CUSTODY_PROOF f join RRL_INTERWARE_RECEIPT r on r.OPERATION_ID=f.RECEIPT_OPERATION_ID join RRL_INTERWARE_UNLOAD u on u.OPERATION_ID=r.UNLOAD_OPERATION_ID where f.OPERATION_ID=op and r.SOURCE_LOAD_OPERATION_ID=:old.LOAD_OPERATION_ID and r.ROOT_UID=:old.ROOT_UID and :new.CUSTODY_RELEASED_AT=u.CREATED_AT;
   if n!=1 then raise_application_error(-20863,'INTERWARE_ACTUAL_CUSTODY_PROOF_REQUIRED');end if;
  end;
 elsif :new.CUSTODY_RELEASED_AT is not null or :new.CUSTODY_RELEASE_OPERATION_ID is not null or kind_name!='TRIP_DEPART' or :old.STATUS!='LOADED' or :new.STATUS!='DEPARTED' or :new.DEPARTURE_OPERATION_ID is null or :new.DEPARTURE_OPERATION_ID!=op
  or :new.LOAD_OPERATION_ID!=:old.LOAD_OPERATION_ID or :new.TT_ID!=:old.TT_ID or nvl(:new.ROOT_UID,chr(0))!=nvl(:old.ROOT_UID,chr(0)) or nvl(:new.ROOT_CASE_TASK_ID,-1)!=nvl(:old.ROOT_CASE_TASK_ID,-1) or :new.VEHICLE_ID!=:old.VEHICLE_ID
  or :new.VEHICLE_NUMBER!=:old.VEHICLE_NUMBER or :new.DOCK!=:old.DOCK or :new.WARE_ID!=:old.WARE_ID
  or :new.GROSS_WEIGHT_KG!=:old.GROSS_WEIGHT_KG or :new.BOUNDING_VOLUME_M3!=:old.BOUNDING_VOLUME_M3 or :new.CONTENT_VERSION!=:old.CONTENT_VERSION
  or :new.LOADED_BY!=:old.LOADED_BY or :new.LOADED_AT!=:old.LOADED_AT or dbms_lob.compare(:new.COMPOSITION_JSON,:old.COMPOSITION_JSON)!=0 then raise_application_error(-20863,'PHYSICAL_LOAD_DEPARTURE_ONLY');end if;
end;
/
