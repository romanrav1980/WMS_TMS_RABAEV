create or replace trigger RRL_STORE_RECEIPT_POLICY_GUARD before insert or update or delete on RRL_STORE_RECEIPT_POLICY for each row
begin
 if sys_context('RRL_STOCK_WRITE_CTX','MODE') is null or sys_context('RRL_STOCK_WRITE_CTX','MODE')!='CONFIG'
  or sys_context('RRL_STOCK_WRITE_CTX','TX_ID') is null or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false) then raise_application_error(-20863,'STORE_RECEIPT_CONFIGURATION_REQUIRED');end if;
 RRL_STOCK_LOCK_API.assert_policy(RRL_STOCK_LOCK_API.resource_key('CONFIG','WAREHOUSE'),6);
end;
/
create or replace trigger RRL_STORE_RECEIPT_USER_GUARD before insert or update or delete on RRL_STORE_RECEIPT_USER for each row
begin
 if sys_context('RRL_STOCK_WRITE_CTX','MODE') is null or sys_context('RRL_STOCK_WRITE_CTX','MODE')!='CONFIG'
  or sys_context('RRL_STOCK_WRITE_CTX','TX_ID') is null or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false) then raise_application_error(-20863,'STORE_RECEIPT_CONFIGURATION_REQUIRED');end if;
 RRL_STOCK_LOCK_API.assert_policy(RRL_STOCK_LOCK_API.resource_key('CONFIG','WAREHOUSE'),6);
end;
/
create or replace trigger RRL_STORE_RECEIPT_FACT_GUARD before insert or update or delete on RRL_STORE_RECEIPT_FACT for each row
declare op varchar2(100):=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID');kind_text varchar2(80);state_text varchar2(20);
begin
 if not inserting then raise_application_error(-20863,'STORE_RECEIPT_HISTORY_IMMUTABLE');end if;
 if op is null or op!=:new.OPERATION_ID or sys_context('RRL_STOCK_WRITE_CTX','TX_ID') is null or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false) then raise_application_error(-20863,'STORE_RECEIPT_ROOT_REQUIRED');end if;
 select COMMAND_TYPE,STATE into kind_text,state_text from RRL_STOCK_OPERATION where OPERATION_ID=op;
 if kind_text!='STORE_RECEIPT' or state_text!='IN_FLIGHT' then raise_application_error(-20863,'STORE_RECEIPT_ROOT_REQUIRED');end if;
 RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_STORE_RECEIPT_FACT',op));
end;
/
create or replace trigger RRL_STORE_RECEIPT_LINE_GUARD before insert or update or delete on RRL_STORE_RECEIPT_LINE for each row
declare op varchar2(100):=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID');kind_text varchar2(80);state_text varchar2(20);
begin
 if not inserting then raise_application_error(-20863,'STORE_RECEIPT_HISTORY_IMMUTABLE');end if;
 if op is null or op!=:new.OPERATION_ID or sys_context('RRL_STOCK_WRITE_CTX','TX_ID') is null or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false) then raise_application_error(-20863,'STORE_RECEIPT_ROOT_REQUIRED');end if;
 select COMMAND_TYPE,STATE into kind_text,state_text from RRL_STOCK_OPERATION where OPERATION_ID=op;
 if kind_text!='STORE_RECEIPT' or state_text!='IN_FLIGHT' then raise_application_error(-20863,'STORE_RECEIPT_ROOT_REQUIRED');end if;
 RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_STORE_RECEIPT_LINE',op||':'||RRL_STOCK_PLAN_HELPER.decimal_text(:new.LINE_NO)));
end;
/
