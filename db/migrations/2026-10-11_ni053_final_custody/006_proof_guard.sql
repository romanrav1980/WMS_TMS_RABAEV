create or replace trigger RRL_STORE_LOAD_CUSTODY_GUARD before insert or update or delete on RRL_STORE_LOAD_CUSTODY for each row
declare op varchar2(100):=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID');kind varchar2(80);state_value varchar2(30);n number;
begin
 if not inserting then raise_application_error(-20863,'STORE_CUSTODY_APPEND_ONLY');end if;
 if op is null or op!=:new.OPERATION_ID or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')is null or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false)or:new.RELEASED_BY!=sys_context('RRL_STOCK_WRITE_CTX','ACTOR')then raise_application_error(-20863,'STORE_CUSTODY_ROOT_REQUIRED');end if;
 select COMMAND_TYPE,STATE into kind,state_value from RRL_STOCK_OPERATION where OPERATION_ID=op;
 if kind not in('STORE_RECEIPT','STORE_CUSTODY_RELEASE')or state_value!='IN_FLIGHT'then raise_application_error(-20863,'STORE_CUSTODY_COMMAND_REQUIRED');end if;
 if kind='STORE_RECEIPT'and:new.RECEIPT_OPERATION_ID!=op then raise_application_error(-20863,'STORE_CUSTODY_RECEIPT_SOURCE_REQUIRED');end if;
 RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_STORE_LOAD_CUSTODY',:new.OPERATION_ID));
 select count(*)into n from RRL_STORE_RECEIPT_FACT where OPERATION_ID=:new.RECEIPT_OPERATION_ID and LOAD_OPERATION_ID=:new.LOAD_OPERATION_ID and RECEIPT_STATE='ACCEPTED'and RECEIVED_AT=:new.RELEASED_AT;
 if n!=1 then raise_application_error(-20863,'STORE_CUSTODY_FULL_PHYSICAL_RECEIPT_REQUIRED');end if;
end;
/
