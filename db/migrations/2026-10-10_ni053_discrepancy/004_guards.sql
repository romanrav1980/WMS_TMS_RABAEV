create or replace trigger RRL_STORE_CASE_APPEND_GUARD before insert or update or delete on RRL_STORE_DISCREPANCY_CASE for each row
declare op varchar2(100):=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID');kind_text varchar2(80);state_text varchar2(20);
begin
 if not inserting then raise_application_error(-20863,'STORE_CASE_EXPLICIT_DECISION_REQUIRED');end if;
 if op is null or op!=:new.CASE_ID or sys_context('RRL_STOCK_WRITE_CTX','TX_ID') is null or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false) then raise_application_error(-20863,'STORE_CASE_ROOT_REQUIRED');end if;
 select COMMAND_TYPE,STATE into kind_text,state_text from RRL_STOCK_OPERATION where OPERATION_ID=op;
 if kind_text!='STORE_RECEIPT' or state_text!='IN_FLIGHT' or :new.STATUS!='OPEN' then raise_application_error(-20863,'STORE_CASE_ROOT_REQUIRED');end if;
 RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_STORE_DISCREPANCY_CASE',op));
end;
/
create or replace trigger RRL_STORE_OBLIGATION_GUARD before insert or update or delete on RRL_STORE_DELIVERY_OBLIGATION for each row
declare op varchar2(100):=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID');kind_text varchar2(80);state_text varchar2(20);
begin
 if not inserting then raise_application_error(-20863,'STORE_OBLIGATION_EXPLICIT_DECISION_REQUIRED');end if;
 if op is null or op!=:new.CASE_ID or sys_context('RRL_STOCK_WRITE_CTX','TX_ID') is null or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false) then raise_application_error(-20863,'STORE_OBLIGATION_ROOT_REQUIRED');end if;
 select COMMAND_TYPE,STATE into kind_text,state_text from RRL_STOCK_OPERATION where OPERATION_ID=op;
 if kind_text!='STORE_RECEIPT' or state_text!='IN_FLIGHT' or :new.STATUS!='OPEN' then raise_application_error(-20863,'STORE_OBLIGATION_ROOT_REQUIRED');end if;
 RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_STORE_DELIVERY_OBLIGATION',op||':'||RRL_STOCK_PLAN_HELPER.decimal_text(:new.LINE_NO)||':'||:new.KIND));
end;
/
