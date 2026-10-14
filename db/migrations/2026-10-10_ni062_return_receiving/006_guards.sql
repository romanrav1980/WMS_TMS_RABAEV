create or replace trigger RRL_STORE_RETURN_WARE_GUARD before insert or update or delete on RRL_STORE_RETURN_WARE_POLICY for each row
declare n number;
begin
 if deleting then raise_application_error(-20863,'STORE_RETURN_WARE_POLICY_PRESERVE_REQUIRED');end if;
 if sys_context('RRL_STOCK_WRITE_CTX','MODE') is null or sys_context('RRL_STOCK_WRITE_CTX','MODE')!='CONFIG' or sys_context('RRL_STOCK_WRITE_CTX','CONFIG_PERMISSION') is null or sys_context('RRL_STOCK_WRITE_CTX','CONFIG_PERMISSION')!='warehouse_settings_edit'
 or sys_context('RRL_STOCK_WRITE_CTX','TX_ID') is null or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false) then raise_application_error(-20863,'STORE_RETURN_WARE_EXPLICIT_CONFIG_REQUIRED');end if;
 RRL_STOCK_LOCK_API.assert_policy(RRL_STOCK_LOCK_API.resource_key('CONFIG','WAREHOUSE'),6);
 select count(*) into n from RRL_WARES where ID=:new.WARE_ID;
 if n!=1 then raise_application_error(-20886,'STORE_RETURN_SINGLE_WAREHOUSE_REQUIRED');end if;
 select count(*) into n from RRL_CELLS where WARE_ID=:new.WARE_ID and CELL=:new.SUPPLIER_RECEIVE_CELL and nvl(BLOCKED_FOR_ACCEPT,0)=0 and BLOCKED_FOR_REMAINS=1 and BLOCKED_FOR_POPOLNENIE=1;
 if n!=1 then raise_application_error(-20886,'STORE_RETURN_SUPPLIER_BLOCKED_RECEIVING_CELL_REQUIRED');end if;
 select count(*) into n from RRL_CELLS where WARE_ID=:new.WARE_ID and CELL=:new.DISPOSAL_RECEIVE_CELL and nvl(BLOCKED_FOR_ACCEPT,0)=0 and BLOCKED_FOR_REMAINS=1 and BLOCKED_FOR_POPOLNENIE=1;
 if n!=1 or :new.DISPOSAL_RECEIVE_CELL=:new.SUPPLIER_RECEIVE_CELL then raise_application_error(-20886,'STORE_RETURN_DISPOSAL_SEPARATE_BLOCKED_CELL_REQUIRED');end if;
 if inserting and :new.POLICY_VERSION!=1 then raise_application_error(-20863,'STORE_RETURN_INITIAL_POLICY_VERSION_REQUIRED');end if;
 if updating and(:new.WARE_ID!=:old.WARE_ID or :new.POLICY_VERSION!=:old.POLICY_VERSION+1)then raise_application_error(-20863,'STORE_RETURN_WARE_POLICY_VERSION_REQUIRED');end if;
 if :new.CHANGED_BY!=sys_context('RRL_STOCK_WRITE_CTX','ACTOR') then raise_application_error(-20863,'STORE_RETURN_CONFIG_ACTOR_REQUIRED');end if;
end;
/
create or replace trigger RRL_STORE_RETURN_RECEIPT_GUARD before insert or update or delete on RRL_STORE_RETURN_RECEIPT for each row
declare op varchar2(100):=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID');v_kind varchar2(80);v_state varchar2(20);v_pickup varchar2(100);v_uid varchar2(200);
begin
 if not inserting then raise_application_error(-20863,'STORE_RETURN_RECEIPT_HISTORY_IMMUTABLE');end if;
 if op is null or op!=:new.OPERATION_ID or sys_context('RRL_STOCK_WRITE_CTX','TX_ID') is null or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false) then raise_application_error(-20863,'STORE_RETURN_RECEIPT_ROOT_REQUIRED');end if;
 select COMMAND_TYPE,STATE,json_value(RESOLVED_PLAN_JSON,'$.domain.pickup_operation_id'),json_value(RESOLVED_PLAN_JSON,'$.domain.uid') into v_kind,v_state,v_pickup,v_uid from RRL_STOCK_OPERATION where OPERATION_ID=op;
 if v_kind!='STORE_RETURN_RECEIVE' or v_state!='IN_FLIGHT' or v_pickup!=:new.PICKUP_OPERATION_ID or v_uid!=:new.UID_PALLET then raise_application_error(-20863,'STORE_RETURN_RECEIPT_ROOT_REQUIRED');end if;
 RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_STORE_RETURN_RECEIPT',op));
 RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_STORE_RETURN_PICKUP',v_pickup));
end;
/
