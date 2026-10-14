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
  if v_kind not in('HU_PLAN_MOVE','HU_UNPACK','HU_RELOCATE_SLOT','HU_REPACK_SLOT') then raise_application_error(-20863,'HU_TASK_PLAN_COMMAND_REQUIRED');end if;
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
