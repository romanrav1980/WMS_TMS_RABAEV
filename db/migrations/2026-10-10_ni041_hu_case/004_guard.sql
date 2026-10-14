create or replace trigger RRL_HU_LINK_WRITE_GUARD before insert or update or delete on RRL_WMS_HU_LINK for each row
declare v_op varchar2(100);v_kind varchar2(80);
begin
 if deleting then raise_application_error(-20863,'HU_LINK_HISTORY_IMMUTABLE');end if;
 v_op:=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID');
 if v_op is null or sys_context('RRL_STOCK_WRITE_CTX','TX_ID') is null or
  sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false) then raise_application_error(-20863,'HU_LINK_ROOT_COMMAND_REQUIRED');end if;
 select COMMAND_TYPE into v_kind from RRL_STOCK_OPERATION where OPERATION_ID=v_op;
 if v_kind not in('HU_ATTACH','HU_DETACH','HU_REPACK') then raise_application_error(-20863,'HU_LINK_COMMAND_INVALID');end if;
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
