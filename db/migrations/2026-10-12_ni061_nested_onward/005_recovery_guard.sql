create or replace trigger RRL_IW_REC_DISPATCH_GUARD before insert or update or delete on RRL_IW_RECOVERY_DISPATCH for each row
declare v_kind varchar2(80);n number;
begin 
 if updating or deleting then raise_application_error(-20878,'RECOVERY_DISPATCH_IMMUTABLE');end if; 
 select COMMAND_TYPE into v_kind from RRL_STOCK_OPERATION where OPERATION_ID=:new.OPERATION_ID;
 if v_kind='HU_SHIP'then
 RRL_IW_SHORTAGE_GUARD.require_command(:new.OPERATION_ID,'HU_SHIP');
 select count(*)into n from RRL_STOCK_OPERATION root_op where root_op.OPERATION_ID=:new.OPERATION_ID and root_op.ACTOR=:new.ACTOR
 and json_value(root_op.RESOLVED_PLAN_JSON,'$.domain.loading.trip'returning number)=(select TARGET_TT_ID from RRL_IW_RECOVERY_ST_BIND where OPERATION_ID=:new.BIND_OPERATION_ID)
 and exists(select 1 from json_table(root_op.RESOLVED_PLAN_JSON,'$.domain.shipments[*]'columns(
  BINDING_ID varchar2(100)path '$.domain.interwarehouse_onward_source.binding_operation_id',
  ST_NO number path '$.domain.interwarehouse_onward_source.st_id'))resolved
  where resolved.BINDING_ID=:new.BIND_OPERATION_ID and resolved.ST_NO=:new.ST_ID);
 if n!=1 then raise_application_error(-20863,'RECOVERY_NESTED_ACTUAL_LOADING_REQUIRED');end if;
 else RRL_IW_SHORTAGE_GUARD.require_command(:new.OPERATION_ID,'LOAD_SHIPMENT');end if; 
 RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_IW_RECOVERY_DISPATCH',:new.OPERATION_ID)); 
end;
/
