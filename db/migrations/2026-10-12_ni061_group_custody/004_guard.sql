create or replace trigger RRL_IW_GROUP_CUSTODY_GUARD before insert or update or delete on RRL_IW_GROUP_CUSTODY for each row
declare op varchar2(100):=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID');n number;
begin
 if not inserting or op is null or op!=:new.OPERATION_ID or :new.ACTOR!=sys_context('RRL_STOCK_WRITE_CTX','ACTOR')or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')is null or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false)then raise_application_error(-20863,'INTERWARE_GROUP_CUSTODY_ROOT_REQUIRED');end if;
 select count(*)into n from RRL_STOCK_OPERATION where OPERATION_ID=op and COMMAND_TYPE='INTERWARE_CUSTODY_RELEASE'and STATE='IN_FLIGHT'and json_value(RESOLVED_PLAN_JSON,'$.domain.group_custody')='true'and json_value(RESOLVED_PLAN_JSON,'$.domain.receipt_operation_id')=:new.RECEIPT_OPERATION_ID and json_value(RESOLVED_PLAN_JSON,'$.domain.source_load_operation_id')=:new.SOURCE_LOAD_OPERATION_ID;
 if n!=1 then raise_application_error(-20863,'INTERWARE_GROUP_CUSTODY_EXACT_SOURCE_REQUIRED');end if;
 RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_IW_GROUP_CUSTODY',op));
end;
/
