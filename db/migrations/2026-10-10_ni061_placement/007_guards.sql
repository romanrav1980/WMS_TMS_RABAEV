create or replace trigger RRL_INTERWARE_PUT_GUARD before insert or update or delete on RRL_INTERWARE_PUT_PLAN for each row
declare op varchar2(100):=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID');n number;
begin
 if not inserting then raise_application_error(-20863,'INTERWARE_PUT_PLAN_IMMUTABLE');end if;
 if op is null or op!=:new.OPERATION_ID or sys_context('RRL_STOCK_WRITE_CTX','TX_ID') is null or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false)then raise_application_error(-20863,'INTERWARE_PUT_PLAN_ROOT_REQUIRED');end if;
 select count(*)into n from RRL_STOCK_OPERATION where OPERATION_ID=op and COMMAND_TYPE='INTERWARE_PUTAWAY_PLAN'and STATE='IN_FLIGHT'and json_value(RESOLVED_PLAN_JSON,'$.domain.receipt_operation_id')=:new.RECEIPT_OPERATION_ID and json_value(RESOLVED_PLAN_JSON,'$.domain.task_id' returning number)=:new.TASK_ID and json_value(RESOLVED_PLAN_JSON,'$.domain.target_cell')=:new.TARGET_CELL and ACTOR=:new.ACTOR;
 if n!=1 then raise_application_error(-20863,'INTERWARE_PUT_PLAN_RESOLVED_SOURCE_REQUIRED');end if;
 RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_INTERWARE_RECEIPT',:new.RECEIPT_OPERATION_ID));
 RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_INTERWARE_PUT_PLAN',op));
end;
/
create or replace trigger RRL_INTERWARE_PLACEMENT_GUARD before insert or update or delete on RRL_INTERWARE_PLACEMENT for each row
declare op varchar2(100):=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID');n number;
begin
 if not inserting then raise_application_error(-20863,'INTERWARE_PLACEMENT_IMMUTABLE');end if;
 if op is null or op!=:new.OPERATION_ID or sys_context('RRL_STOCK_WRITE_CTX','TX_ID') is null or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false)then raise_application_error(-20863,'INTERWARE_PLACEMENT_ROOT_REQUIRED');end if;
 select count(*)into n from RRL_STOCK_OPERATION where OPERATION_ID=op and COMMAND_TYPE='TASK_COMPLETE'and STATE='IN_FLIGHT'and json_value(CANONICAL_REQUEST,'$.source.task_id' returning number)=:new.TASK_ID and ACTOR=:new.ACTOR;
 if n!=1 then raise_application_error(-20863,'INTERWARE_PLACEMENT_TASK_ROOT_REQUIRED');end if;
 select count(*)into n from RRL_INTERWARE_PUT_PLAN p join RRL_INTERWARE_RECEIPT r on r.OPERATION_ID=p.RECEIPT_OPERATION_ID where p.TASK_ID=:new.TASK_ID and r.OPERATION_ID=:new.RECEIPT_OPERATION_ID and p.TARGET_CELL=:new.TARGET_CELL and r.ROOT_UID=:new.ROOT_UID and r.WARE_ID=:new.WARE_ID and r.BASE_QTY=:new.BASE_QTY and r.BASE_UOM=:new.BASE_UOM;
 if n!=1 then raise_application_error(-20863,'INTERWARE_PLACEMENT_ORIGINAL_RECEIPT_REQUIRED');end if;
 RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_INTERWARE_PLACEMENT',to_char(:new.TASK_ID,'TM9')));
end;
/
create or replace trigger RRL_INTERWARE_TASK_ID_GUARD before insert or update of TASK_TYPE,TASK_SOURCE,SOURCE_DOC_TYPE,SOURCE_DOC_ID,UID_PALLET,FROM_CELL,TO_CELL,QTY,UNIT_CODE,QTY_MODE on RRL_WAREHOUSE_TASK for each row
declare op varchar2(100):=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID');v_kind varchar2(80);v_state varchar2(20);
begin
 if inserting and(:new.SOURCE_DOC_TYPE is null or :new.SOURCE_DOC_TYPE!='INTERWARE')then return;end if;
 if updating and(:old.SOURCE_DOC_TYPE is null or :old.SOURCE_DOC_TYPE!='INTERWARE')and(:new.SOURCE_DOC_TYPE is null or :new.SOURCE_DOC_TYPE!='INTERWARE')then return;end if;
 if updating then
  if :new.TASK_TYPE=:old.TASK_TYPE and :new.TASK_SOURCE=:old.TASK_SOURCE and :new.SOURCE_DOC_TYPE=:old.SOURCE_DOC_TYPE and :new.SOURCE_DOC_ID=:old.SOURCE_DOC_ID and :new.UID_PALLET=:old.UID_PALLET and :new.FROM_CELL=:old.FROM_CELL and :new.TO_CELL=:old.TO_CELL and :new.QTY=:old.QTY and :new.UNIT_CODE=:old.UNIT_CODE and :new.QTY_MODE=:old.QTY_MODE then return;end if;
  raise_application_error(-20863,'INTERWARE_TASK_IDENTITY_IMMUTABLE');
 end if;
 if op is null or sys_context('RRL_STOCK_WRITE_CTX','TX_ID') is null or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false)then raise_application_error(-20863,'INTERWARE_TASK_PLAN_ROOT_REQUIRED');end if;
 select COMMAND_TYPE,STATE into v_kind,v_state from RRL_STOCK_OPERATION where OPERATION_ID=op;
 if v_kind!='INTERWARE_PUTAWAY_PLAN' or v_state!='IN_FLIGHT' then raise_application_error(-20863,'INTERWARE_TASK_PLAN_ROOT_REQUIRED');end if;
 RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_WAREHOUSE_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(:new.TASK_ID)));
end;
/
