create or replace trigger RRL_HU_TASK_PLAN_GUARD
 before insert or update on RRL_WAREHOUSE_TASK
 for each row
declare v_op varchar2(100);v_kind varchar2(80);
begin
 if :new.HU_CONTENT_VERSION is null and (inserting or :old.HU_CONTENT_VERSION is null) then return;end if;
 if inserting then
  v_op:=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID');
  if v_op is null or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false) then raise_application_error(-20863,'HU_TASK_PLAN_ROOT_REQUIRED');end if;
  select COMMAND_TYPE into v_kind from RRL_STOCK_OPERATION where OPERATION_ID=v_op;
  if v_kind not in('HU_PLAN_MOVE','HU_UNPACK') then raise_application_error(-20863,'HU_TASK_PLAN_COMMAND_REQUIRED');end if;
  RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_WAREHOUSE_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(:new.TASK_ID)));
 else
  if nvl(:new.TO_CELL_SLOT_ID,-1)!=nvl(:old.TO_CELL_SLOT_ID,-1)
   or(:new.HU_MEASUREMENTS_JSON is null and :old.HU_MEASUREMENTS_JSON is not null)
   or(:new.HU_MEASUREMENTS_JSON is not null and :old.HU_MEASUREMENTS_JSON is null)
   or(:new.HU_MEASUREMENTS_JSON is not null and :old.HU_MEASUREMENTS_JSON is not null and dbms_lob.compare(:new.HU_MEASUREMENTS_JSON,:old.HU_MEASUREMENTS_JSON)!=0)
   or nvl(:new.HU_CONTENT_VERSION,-1)!=nvl(:old.HU_CONTENT_VERSION,-1)
   or nvl(:new.UID_PALLET,chr(0))!=nvl(:old.UID_PALLET,chr(0))
   or nvl(:new.FROM_CELL,chr(0))!=nvl(:old.FROM_CELL,chr(0)) or nvl(:new.TO_CELL,chr(0))!=nvl(:old.TO_CELL,chr(0))
   or nvl(:new.FROM_WARE_ID,-1)!=nvl(:old.FROM_WARE_ID,-1) or nvl(:new.TO_WARE_ID,-1)!=nvl(:old.TO_WARE_ID,-1)
   or nvl(:new.QTY,-1)!=nvl(:old.QTY,-1) or nvl(:new.UNIT_CODE,chr(0))!=nvl(:old.UNIT_CODE,chr(0))
   or nvl(:new.QTY_MODE,chr(0))!=nvl(:old.QTY_MODE,chr(0)) or nvl(:new.TASK_TYPE,chr(0))!=nvl(:old.TASK_TYPE,chr(0))
   or nvl(:new.TASK_SOURCE,chr(0))!=nvl(:old.TASK_SOURCE,chr(0)) or nvl(:new.SOURCE_DOC_TYPE,chr(0))!=nvl(:old.SOURCE_DOC_TYPE,chr(0))
   then raise_application_error(-20863,'HU_TASK_SOURCE_PLAN_IMMUTABLE_CANCEL_AND_REPLAN');end if;
 end if;
end;
/

create or replace trigger RRL_HU_CLAIM_MEASURE_GUARD before insert or update of HU_GROSS_WEIGHT_KG,HU_BOUNDING_VOLUME_M3,HU_COMPOSITION_VERSION on RRL_RECEIPT_SLOT_CLAIM for each row
declare op varchar2(100):=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID');kind varchar2(80);version_no number;begin
 if inserting and :new.HU_GROSS_WEIGHT_KG is null and :new.HU_BOUNDING_VOLUME_M3 is null and :new.HU_COMPOSITION_VERSION is null then return;end if;
 if updating then raise_application_error(-20863,'HU_CLAIM_MEASURE_IMMUTABLE');end if;
 if op is null or sys_context('RRL_STOCK_WRITE_CTX','TX_ID') is null or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false)
  or :new.HU_GROSS_WEIGHT_KG is null or :new.HU_BOUNDING_VOLUME_M3 is null or least(:new.HU_GROSS_WEIGHT_KG,:new.HU_BOUNDING_VOLUME_M3)<=0 then raise_application_error(-20863,'HU_CLAIM_MEASURE_ROOT_REQUIRED');end if;
 select COMMAND_TYPE into kind from RRL_STOCK_OPERATION where OPERATION_ID=op;
 if kind not in('HU_TASK_COMPLETE','HU_UNPACK') then raise_application_error(-20863,'HU_CLAIM_MEASURE_TASK_REQUIRED');end if;
 select HU_CONTENT_VERSION into version_no from RRL_PALLETS where UID_PALLET=:new.UID_PALLET and HU_KIND='CONTAINER';
 if :new.HU_COMPOSITION_VERSION is null or :new.HU_COMPOSITION_VERSION!=version_no then raise_application_error(-20863,'HU_CLAIM_MEASURE_VERSION_REQUIRED');end if;
 RRL_STOCK_LOCK_API.assert_held(30,RRL_STOCK_LOCK_API.resource_key('HU',:new.UID_PALLET));
end;
/

create or replace trigger RRL_HU_LINK_WRITE_GUARD before insert or update or delete on RRL_WMS_HU_LINK for each row
declare v_op varchar2(100);v_kind varchar2(80);
begin
 if deleting then raise_application_error(-20863,'HU_LINK_HISTORY_IMMUTABLE');end if;
 v_op:=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID');
 if v_op is null or sys_context('RRL_STOCK_WRITE_CTX','TX_ID') is null or
  sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false) then raise_application_error(-20863,'HU_LINK_ROOT_COMMAND_REQUIRED');end if;
 select COMMAND_TYPE into v_kind from RRL_STOCK_OPERATION where OPERATION_ID=v_op;
 if v_kind not in('HU_ATTACH','HU_DETACH','HU_REPACK','HU_SHIP','HU_UNPACK') then raise_application_error(-20863,'HU_LINK_COMMAND_INVALID');end if;
 RRL_STOCK_LOCK_API.assert_held(30,RRL_STOCK_LOCK_API.resource_key('HU',:new.PARENT_UID));
 RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_WMS_HU_LINK',RRL_STOCK_PLAN_HELPER.decimal_text(:new.HU_LINK_ID)));
 if :new.CHILD_PALLET_UID is not null then RRL_STOCK_LOCK_API.assert_held(30,RRL_STOCK_LOCK_API.resource_key('HU',:new.CHILD_PALLET_UID));end if;
 if :new.CHILD_CASE_TASK_ID is not null then
  RRL_STOCK_LOCK_API.assert_held(30,RRL_STOCK_LOCK_API.resource_key('HU','CASE:'||RRL_STOCK_PLAN_HELPER.decimal_text(:new.CHILD_CASE_TASK_ID)));
  RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_CASE_PICK_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(:new.CHILD_CASE_TASK_ID)));
 end if;
 if inserting and (:new.ACTIVE_FLAG!=1 or :new.LINK_VERSION!=0 or :new.LINKED_OPERATION_ID!=v_op) then raise_application_error(-20863,'HU_LINK_INITIAL_VERSION_INVALID');end if;
 if updating and (:new.HU_LINK_ID!=:old.HU_LINK_ID or :new.PARENT_UID!=:old.PARENT_UID
  or nvl(:new.CHILD_PALLET_UID,chr(0))!=nvl(:old.CHILD_PALLET_UID,chr(0))
  or nvl(:new.CHILD_CASE_TASK_ID,-1)!=nvl(:old.CHILD_CASE_TASK_ID,-1)
  or :old.ACTIVE_FLAG!=1 or :new.ACTIVE_FLAG!=0 or :new.LINK_VERSION!=:old.LINK_VERSION+1
  or :new.UNLINKED_OPERATION_ID!=v_op or :new.LINKED_OPERATION_ID!=:old.LINKED_OPERATION_ID) then
  raise_application_error(-20863,'HU_LINK_HISTORY_OR_VERSION_INVALID');end if;
end;
/

create or replace trigger RRL_HU_CONTAINER_GUARD before insert or update of HU_KIND,HU_TYPE,HU_CONTENT_VERSION,HU_CURRENT_CELL,HU_TARE_WEIGHT_KG on RRL_PALLETS for each row
declare v_op varchar2(100);v_kind varchar2(80);
begin
 if inserting and :new.HU_KIND='STOCK' then return;end if;
 v_op:=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID');
 if v_op is null or sys_context('RRL_STOCK_WRITE_CTX','TX_ID') is null or
  sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false) then raise_application_error(-20863,'HU_METADATA_ROOT_COMMAND_REQUIRED');end if;
 select COMMAND_TYPE into v_kind from RRL_STOCK_OPERATION where OPERATION_ID=v_op;
 if v_kind not in('HU_CREATE','HU_ATTACH','HU_DETACH','HU_REPACK','HU_MOVE','HU_TASK_COMPLETE','HU_SHIP','HU_UNPACK') then raise_application_error(-20863,'HU_METADATA_COMMAND_INVALID');end if;
 RRL_STOCK_LOCK_API.assert_held(30,RRL_STOCK_LOCK_API.resource_key('HU',:new.UID_PALLET));
 if updating and (:new.HU_KIND!=:old.HU_KIND or :new.HU_CONTENT_VERSION!=:old.HU_CONTENT_VERSION+1) then raise_application_error(-20863,'HU_IDENTITY_OR_VERSION_INVALID');end if;
end;
/

