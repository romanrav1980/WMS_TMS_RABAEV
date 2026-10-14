create or replace trigger RRL_STORE_RETURN_TASK_ID_GUARD before insert or update of TASK_TYPE,TASK_SOURCE,SOURCE_DOC_TYPE,SOURCE_DOC_ID,UID_PALLET,FROM_CELL,TO_CELL,QTY,UNIT_CODE,QTY_MODE on RRL_WAREHOUSE_TASK for each row
declare op varchar2(100):=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID');v_kind varchar2(80);v_state varchar2(20);
begin
 if inserting and(:new.SOURCE_DOC_TYPE is null or :new.SOURCE_DOC_TYPE!='STORE_RETURN')then return;end if;
 if updating and(:old.SOURCE_DOC_TYPE is null or :old.SOURCE_DOC_TYPE!='STORE_RETURN')and(:new.SOURCE_DOC_TYPE is null or :new.SOURCE_DOC_TYPE!='STORE_RETURN')then return;end if;
 if updating then
  if :new.TASK_TYPE=:old.TASK_TYPE and :new.TASK_SOURCE=:old.TASK_SOURCE and :new.SOURCE_DOC_TYPE=:old.SOURCE_DOC_TYPE and :new.SOURCE_DOC_ID=:old.SOURCE_DOC_ID and :new.UID_PALLET=:old.UID_PALLET and :new.FROM_CELL=:old.FROM_CELL and :new.TO_CELL=:old.TO_CELL and :new.QTY=:old.QTY and :new.UNIT_CODE=:old.UNIT_CODE and :new.QTY_MODE=:old.QTY_MODE then return;end if;
  raise_application_error(-20863,'STORE_RETURN_TASK_IDENTITY_IMMUTABLE');
 end if;
 if op is null or sys_context('RRL_STOCK_WRITE_CTX','TX_ID') is null or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false)then raise_application_error(-20863,'STORE_RETURN_TASK_PLAN_ROOT_REQUIRED');end if;
 select COMMAND_TYPE,STATE into v_kind,v_state from RRL_STOCK_OPERATION where OPERATION_ID=op;
 if v_kind!='STORE_RETURN_PUTAWAY_PLAN' or v_state!='IN_FLIGHT' then raise_application_error(-20863,'STORE_RETURN_TASK_PLAN_ROOT_REQUIRED');end if;
 RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_WAREHOUSE_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(:new.TASK_ID)));
end;
/
