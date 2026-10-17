create or replace trigger RRL_HU_CONTAINER_GUARD before insert or update of HU_KIND,HU_TYPE,HU_CONTENT_VERSION,HU_CURRENT_CELL,HU_TARE_WEIGHT_KG on RRL_PALLETS for each row
declare v_op varchar2(100);v_kind varchar2(80);
begin
 if inserting and :new.HU_KIND='STOCK' then return;end if;
 v_op:=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID');
 if v_op is null or sys_context('RRL_STOCK_WRITE_CTX','TX_ID') is null or
  sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false) then raise_application_error(-20863,'HU_METADATA_ROOT_COMMAND_REQUIRED');end if;
 select COMMAND_TYPE into v_kind from RRL_STOCK_OPERATION where OPERATION_ID=v_op;
 if v_kind not in('HU_CREATE','HU_ATTACH','HU_DETACH','HU_REPACK','HU_MOVE','HU_TASK_COMPLETE','HU_SHIP','HU_UNPACK','HU_RELOCATE_SLOT','HU_REPACK_SLOT','UNLOAD_SHIPMENT','INTERWARE_RECEIVE') then raise_application_error(-20863,'HU_METADATA_COMMAND_INVALID');end if;
 if v_kind='INTERWARE_RECEIVE'then
 if not updating then raise_application_error(-20863,'INTERWARE_EXISTING_CONTAINER_ONLY');end if;
 declare wire clob;n number;state_name varchar2(20);cell_text varchar2(60);load_id varchar2(100);begin
 select STATE,RESOLVED_PLAN_JSON into state_name,wire from RRL_STOCK_OPERATION where OPERATION_ID=v_op;
 cell_text:=json_object_t.parse(wire).get_object('domain').get_string('receive_cell');load_id:=json_object_t.parse(wire).get_object('domain').get_string('source_load_operation_id');
 select count(*)into n from json_table(wire,'$.domain.nested_source.containers[*]'columns(U varchar2(200)path '$.uid',V number path '$.version',T varchar2(20)path '$.type',W varchar2(60)path '$.tare'))frozen
 where frozen.U=:new.UID_PALLET and frozen.V=:old.HU_CONTENT_VERSION and frozen.T=:old.HU_TYPE and frozen.W=RRL_STOCK_PLAN_HELPER.decimal_text(:old.HU_TARE_WEIGHT_KG);
 if state_name!='IN_FLIGHT'or n!=1 or :old.HU_SHIPPED_OPERATION!=load_id or :old.HU_CURRENT_CELL is not null or :new.HU_SHIPPED_OPERATION is not null or :new.HU_CURRENT_CELL!=cell_text or nvl(:new.HU_TYPE,'~')!=nvl(:old.HU_TYPE,'~')or nvl(:new.HU_TARE_WEIGHT_KG,-1)!=nvl(:old.HU_TARE_WEIGHT_KG,-1)then raise_application_error(-20863,'INTERWARE_FROZEN_CONTAINER_RECEIPT_REQUIRED');end if;
 end;
 end if;
 if v_kind='UNLOAD_SHIPMENT'then
  if not updating then raise_application_error(-20863,'UNLOAD_ORIGINAL_CONTAINER_ONLY');end if;
  declare wire clob;load_id varchar2(100);n number;state_name varchar2(20);cell_text varchar2(60);begin
   select STATE,RESOLVED_PLAN_JSON into state_name,wire from RRL_STOCK_OPERATION where OPERATION_ID=v_op;
   load_id:=json_object_t.parse(wire).get_object('domain').get_string('load_id');cell_text:=json_object_t.parse(wire).get_object('domain').get_object('snapshot').get_string('cell');
   select count(*)into n from json_table(wire,'$.domain.snapshot.nodes[*]'columns(U varchar2(150)path '$.uid',K varchar2(20)path '$.kind',V number path '$.version'))j where j.U=:new.UID_PALLET and j.K='CONTAINER'and j.V+1=:old.HU_CONTENT_VERSION;
   if state_name!='IN_FLIGHT'or n!=1 or :old.HU_SHIPPED_OPERATION!=load_id or :old.HU_CURRENT_CELL is not null or :new.HU_SHIPPED_OPERATION is not null or :new.HU_CURRENT_CELL!=cell_text or nvl(:new.HU_TYPE,'~')!=nvl(:old.HU_TYPE,'~')or nvl(:new.HU_TARE_WEIGHT_KG,-1)!=nvl(:old.HU_TARE_WEIGHT_KG,-1)then raise_application_error(-20863,'UNLOAD_ORIGINAL_CONTAINER_PLAN_REQUIRED');end if;
  end;
 end if;
 RRL_STOCK_LOCK_API.assert_held(30,RRL_STOCK_LOCK_API.resource_key('HU',:new.UID_PALLET));
 if updating and (:new.HU_KIND!=:old.HU_KIND or :new.HU_CONTENT_VERSION!=:old.HU_CONTENT_VERSION+1) then raise_application_error(-20863,'HU_IDENTITY_OR_VERSION_INVALID');end if;
end;
/
