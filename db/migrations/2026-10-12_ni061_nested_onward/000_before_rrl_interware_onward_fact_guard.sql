create or replace trigger RRL_INTERWARE_ONWARD_FACT_GUARD before insert or update or delete on RRL_INTERWARE_ONWARD_DISPATCH for each row 
declare op varchar2(100):=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID');n number; 
begin 
 if not inserting then raise_application_error(-20863,'INTERWARE_ONWARD_FACT_IMMUTABLE');end if; 
 if op is null or op!=:new.OPERATION_ID or sys_context('RRL_STOCK_WRITE_CTX','TX_ID') is null or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false)then raise_application_error(-20863,'INTERWARE_ONWARD_ROOT_REQUIRED');end if; 
 select count(*)into n from RRL_STOCK_OPERATION where OPERATION_ID=op and COMMAND_TYPE='LOAD_SHIPMENT'and STATE='IN_FLIGHT'and ACTOR=:new.ACTOR and json_value(RESOLVED_PLAN_JSON,'$.domain.shipment.domain.interwarehouse_onward_source.binding_operation_id')=:new.BIND_OPERATION_ID; 
 if n!=1 then raise_application_error(-20863,'INTERWARE_ONWARD_ORIGINAL_LOADING_REQUIRED');end if; 
 RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_INTERWARE_ONWARD_DISPATCH',op)); 
end;
/
