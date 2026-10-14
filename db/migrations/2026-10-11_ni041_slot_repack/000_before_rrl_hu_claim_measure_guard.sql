create or replace trigger RRL_HU_CLAIM_MEASURE_GUARD before insert or update of HU_GROSS_WEIGHT_KG,HU_BOUNDING_VOLUME_M3,HU_COMPOSITION_VERSION,HU_STOCK_COMPOSITION_VERSION,HU_PHYSICAL_VERSION,HU_UNIT_SIGNATURE,HU_CASE_TASK_ID on RRL_RECEIPT_SLOT_CLAIM for each row
declare op varchar2(100):=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID');kind varchar2(80);version_no number;owner_kind varchar2(20);stock_epoch number;physical_epoch number;unit_sig varchar2(64);unit_count number;actual_cell varchar2(60);begin
 if inserting and :new.HU_GROSS_WEIGHT_KG is null and :new.HU_BOUNDING_VOLUME_M3 is null and :new.HU_COMPOSITION_VERSION is null
  and :new.HU_STOCK_COMPOSITION_VERSION is null and :new.HU_PHYSICAL_VERSION is null and :new.HU_UNIT_SIGNATURE is null and :new.HU_CASE_TASK_ID is null then return;end if;
 if updating then raise_application_error(-20863,'HU_CLAIM_MEASURE_IMMUTABLE');end if;
 if op is null or sys_context('RRL_STOCK_WRITE_CTX','TX_ID') is null or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false)
  or :new.HU_GROSS_WEIGHT_KG is null or :new.HU_BOUNDING_VOLUME_M3 is null or least(:new.HU_GROSS_WEIGHT_KG,:new.HU_BOUNDING_VOLUME_M3)<=0 then raise_application_error(-20863,'HU_CLAIM_MEASURE_ROOT_REQUIRED');end if;
 select COMMAND_TYPE into kind from RRL_STOCK_OPERATION where OPERATION_ID=op;
 if kind not in('HU_TASK_COMPLETE','HU_UNPACK','HU_RELOCATE_SLOT') then raise_application_error(-20863,'HU_CLAIM_MEASURE_TASK_REQUIRED');end if;
 if :new.HU_CASE_TASK_ID is not null then
  select CONTENT_VERSION,CURRENT_CELL into version_no,actual_cell from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:new.HU_CASE_TASK_ID and STATUS in('WAIT_CONTROL','CONTROL_IN_PROGRESS','CONTROLLED','READY_TO_SHIP');
  if :new.UID_PALLET!='CASE:'||RRL_STOCK_PLAN_HELPER.decimal_text(:new.HU_CASE_TASK_ID) or actual_cell is null or actual_cell!=:new.CELL
   or :new.HU_STOCK_COMPOSITION_VERSION is not null or :new.HU_PHYSICAL_VERSION is not null or :new.HU_UNIT_SIGNATURE is not null then raise_application_error(-20863,'CASE_CLAIM_IDENTITY_OR_CELL_INVALID');end if;
  owner_kind:='CASE';
  RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_CASE_PICK_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(:new.HU_CASE_TASK_ID)));
 else
 select HU_CONTENT_VERSION,HU_KIND,STOCK_COMPOSITION_VERSION into version_no,owner_kind,stock_epoch from RRL_PALLETS where UID_PALLET=:new.UID_PALLET;
 end if;
 if :new.HU_COMPOSITION_VERSION is null or :new.HU_COMPOSITION_VERSION!=version_no then raise_application_error(-20863,'HU_CLAIM_MEASURE_VERSION_REQUIRED');end if;
 RRL_STOCK_LOCK_API.assert_held(30,RRL_STOCK_LOCK_API.resource_key('HU',:new.UID_PALLET));
 if owner_kind='STOCK' then
  RRL_STOCK_LOCK_API.assert_held(50,RRL_STOCK_LOCK_API.resource_key('STOCK',:new.UID_PALLET));
  select PHYSICAL_VERSION into physical_epoch from RRL_REMAINS where UID_POLETA=:new.UID_PALLET and CELL=:new.CELL and REMAIN>0;
  RRL_STOCK_HU_UNIT_SIGNATURE.describe_units(:new.UID_PALLET,null,unit_sig,unit_count);
  if :new.HU_STOCK_COMPOSITION_VERSION is null or :new.HU_STOCK_COMPOSITION_VERSION!=stock_epoch
   or :new.HU_PHYSICAL_VERSION is null or :new.HU_PHYSICAL_VERSION!=physical_epoch or :new.HU_UNIT_SIGNATURE is null or :new.HU_UNIT_SIGNATURE!=unit_sig
   then raise_application_error(-20863,'STOCK_CLAIM_COMPOSITION_REQUIRED');end if;
 elsif owner_kind not in('CONTAINER','CASE') or :new.HU_STOCK_COMPOSITION_VERSION is not null or :new.HU_PHYSICAL_VERSION is not null or :new.HU_UNIT_SIGNATURE is not null then raise_application_error(-20863,'HU_CLAIM_OWNER_INVALID');end if;
end;
/
