create or replace trigger RRL_STORE_RETURN_TR_GUARD before insert or update or delete on RRL_STORE_RETURN_TRANSPORT for each row
declare op varchar2(100):=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID');v_kind varchar2(80);v_state varchar2(20);v_approval varchar2(100);v_trip number;
begin
 if not inserting then raise_application_error(-20863,'STORE_RETURN_TRANSPORT_HISTORY_IMMUTABLE');end if;
 if op is null or op!=:new.OPERATION_ID or sys_context('RRL_STOCK_WRITE_CTX','TX_ID') is null or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false) then raise_application_error(-20863,'STORE_RETURN_TRANSPORT_ROOT_REQUIRED');end if;
 select COMMAND_TYPE,STATE,json_value(RESOLVED_PLAN_JSON,'$.domain.approval_operation_id'),json_value(RESOLVED_PLAN_JSON,'$.domain.task_id' returning number) into v_kind,v_state,v_approval,v_trip from RRL_STOCK_OPERATION where OPERATION_ID=op;
 if v_kind!='STORE_RETURN_TRANSPORT_PLAN' or v_state!='IN_FLIGHT' or v_approval!=:new.APPROVAL_OPERATION_ID or v_trip!=:new.TT_ID then raise_application_error(-20863,'STORE_RETURN_TRANSPORT_ROOT_REQUIRED');end if;
 RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_STORE_RETURN_TRANSPORT',op));
 RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_TRANSPORT_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(v_trip)));
end;
/
