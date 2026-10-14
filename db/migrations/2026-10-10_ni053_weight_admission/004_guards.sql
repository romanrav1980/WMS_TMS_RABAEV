create or replace trigger RRL_STORE_RECEIPT_WEIGHT_GUARD before insert or update or delete on RRL_STORE_RECEIPT_WEIGHT for each row
declare op varchar2(100):=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID');v_kind varchar2(80);v_state varchar2(20);
begin
 if not inserting then raise_application_error(-20863,'STORE_WEIGHT_EVIDENCE_IMMUTABLE');end if;
 if op is null or op!=:new.OPERATION_ID or sys_context('RRL_STOCK_WRITE_CTX','TX_ID') is null or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false) then raise_application_error(-20863,'STORE_WEIGHT_ROOT_REQUIRED');end if;
 select COMMAND_TYPE,STATE into v_kind,v_state from RRL_STOCK_OPERATION where OPERATION_ID=op;
 if v_kind!='STORE_RECEIPT' or v_state!='IN_FLIGHT' then raise_application_error(-20863,'STORE_WEIGHT_ROOT_REQUIRED');end if;
 RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_STORE_RECEIPT_WEIGHT',op));
end;
/
create or replace trigger RRL_STORE_WEIGHT_PHOTO_GUARD before insert or update or delete on RRL_STORE_RECEIPT_WEIGHT_PHOTO for each row
declare op varchar2(100):=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID');v_kind varchar2(80);v_state varchar2(20);
begin
 if not inserting then raise_application_error(-20863,'STORE_WEIGHT_PHOTO_IMMUTABLE');end if;
 if op is null or op!=:new.OPERATION_ID or sys_context('RRL_STOCK_WRITE_CTX','TX_ID') is null or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false) then raise_application_error(-20863,'STORE_WEIGHT_ROOT_REQUIRED');end if;
 select COMMAND_TYPE,STATE into v_kind,v_state from RRL_STOCK_OPERATION where OPERATION_ID=op;
 if v_kind!='STORE_RECEIPT' or v_state!='IN_FLIGHT' then raise_application_error(-20863,'STORE_WEIGHT_ROOT_REQUIRED');end if;
 RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_STORE_RECEIPT_WEIGHT_PHOTO',op||':'||:new.PHOTO_ID));
end;
/
