create or replace trigger RRL_STORE_RETURN_SAP_GUARD before insert or update or delete on RRL_STORE_RETURN_SAP for each row
declare op varchar2(100):=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID');v_kind varchar2(80);v_state varchar2(20);v_approval varchar2(100);
begin
 if not inserting then raise_application_error(-20863,'SAP_RETURN_BINDING_IMMUTABLE');end if;
 if op is null or op!=:new.OPERATION_ID or sys_context('RRL_STOCK_WRITE_CTX','TX_ID') is null or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false) then raise_application_error(-20863,'SAP_RETURN_BINDING_ROOT_REQUIRED');end if;
 select COMMAND_TYPE,STATE,json_value(RESOLVED_PLAN_JSON,'$.domain.approval_operation_id') into v_kind,v_state,v_approval from RRL_STOCK_OPERATION where OPERATION_ID=op;
 if v_kind!='STORE_RETURN_SAP_BIND' or v_state!='IN_FLIGHT' or v_approval!=:new.APPROVAL_OPERATION_ID then raise_application_error(-20863,'SAP_RETURN_BINDING_ROOT_REQUIRED');end if;
 RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_STORE_RETURN_SAP',op));
end;
/
