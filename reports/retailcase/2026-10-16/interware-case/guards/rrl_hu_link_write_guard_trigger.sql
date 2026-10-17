create or replace trigger RRL_HU_LINK_WRITE_GUARD before insert or update or delete on RRL_WMS_HU_LINK for each row
declare v_op varchar2(100);v_kind varchar2(80);
begin
 if deleting then raise_application_error(-20863,'HU_LINK_HISTORY_IMMUTABLE');end if;
 v_op:=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID');
 if v_op is null or sys_context('RRL_STOCK_WRITE_CTX','TX_ID') is null or
  sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false) then raise_application_error(-20863,'HU_LINK_ROOT_COMMAND_REQUIRED');end if;
 select COMMAND_TYPE into v_kind from RRL_STOCK_OPERATION where OPERATION_ID=v_op;
 if v_kind not in('HU_ATTACH','HU_DETACH','HU_REPACK','HU_SHIP','HU_UNPACK','HU_REPACK_SLOT','UNLOAD_SHIPMENT','INTERWARE_RECEIVE') then raise_application_error(-20863,'HU_LINK_COMMAND_INVALID');end if;
 if v_kind='INTERWARE_RECEIVE'then
 if not inserting or :new.CHILD_CASE_TASK_ID is not null then raise_application_error(-20863,'INTERWARE_APPEND_SOURCE_LINK_ONLY');end if;
 declare wire clob;state_name varchar2(20);n number;begin
 select RESOLVED_PLAN_JSON,STATE into wire,state_name from RRL_STOCK_OPERATION where OPERATION_ID=v_op;
 select count(*)into n from json_table(wire,'$.domain.nested_source.links[*]'columns(
 N number path '$.new_id',P varchar2(200)path '$.parent',C varchar2(200)path '$.child'))frozen
 where frozen.N=:new.HU_LINK_ID and frozen.P=:new.PARENT_UID and frozen.C=:new.CHILD_PALLET_UID;
 if state_name!='IN_FLIGHT'or n!=1 then raise_application_error(-20863,'INTERWARE_FROZEN_LINK_RECEIPT_REQUIRED');end if;
 end;
 end if;
 if v_kind='UNLOAD_SHIPMENT'then
  if not inserting then raise_application_error(-20863,'UNLOAD_APPEND_NEW_LINK_ONLY');end if;
  declare wire clob;load_id varchar2(100);n number;state_name varchar2(20);child_key varchar2(200):=nvl(:new.CHILD_PALLET_UID,'CASE:'||RRL_STOCK_PLAN_HELPER.decimal_text(:new.CHILD_CASE_TASK_ID));begin
   select RESOLVED_PLAN_JSON,STATE into wire,state_name from RRL_STOCK_OPERATION where OPERATION_ID=v_op;
   load_id:=json_object_t.parse(wire).get_object('domain').get_string('load_id');
   select count(*)into n from json_table(wire,'$.domain.recover_links[*]'columns(NEW_ID number path '$.new_id',OLD_ID number path '$.id',P varchar2(150)path '$.parent',C varchar2(200)path '$.child',V number path '$.version'))j join RRL_WMS_HU_LINK old_link on old_link.HU_LINK_ID=j.OLD_ID and old_link.PARENT_UID=j.P and old_link.ACTIVE_FLAG=0 and old_link.UNLINKED_OPERATION_ID=load_id and old_link.LINK_VERSION=j.V+1
    where j.NEW_ID=:new.HU_LINK_ID and j.P=:new.PARENT_UID and j.C=child_key;
   if state_name!='IN_FLIGHT'or n!=1 then raise_application_error(-20863,'UNLOAD_ORIGINAL_LINK_PLAN_REQUIRED');end if;
  end;
 end if;
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
