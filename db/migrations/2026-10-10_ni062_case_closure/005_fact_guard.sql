create or replace trigger RRL_STORE_CASE_CLOSE_GUARD before insert or update or delete on RRL_STORE_CASE_CLOSURE for each row
declare op varchar2(100):=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID');n number;
begin
 if not inserting then raise_application_error(-20863,'STORE_CASE_CLOSURE_IMMUTABLE');end if;
 if op is null or :new.OPERATION_ID!=op or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')is null or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false)or :new.ACTOR!=sys_context('RRL_STOCK_WRITE_CTX','ACTOR')then raise_application_error(-20863,'STORE_CASE_CLOSURE_ROOT_REQUIRED');end if;
 select count(*)into n from RRL_STOCK_OPERATION where OPERATION_ID=op and COMMAND_TYPE='STORE_CASE_WORK' and STATE='IN_FLIGHT'and json_value(RESOLVED_PLAN_JSON,'$.domain.action')='CLOSE';
 if n!=1 then raise_application_error(-20863,'STORE_CASE_EXPLICIT_CLOSURE_REQUIRED');end if;
 RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_STORE_CASE_CLOSURE',op));
end;
/
