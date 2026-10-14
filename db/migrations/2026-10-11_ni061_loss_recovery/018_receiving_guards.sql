create or replace trigger RRL_IW_RECOVERY_RECEIPT_G before insert or update or delete on RRL_INTERWARE_RECOVERY_RECEIPT for each row
begin
 if updating or deleting then raise_application_error(-20863,'INTERWARE_RECOVERY_HISTORY_IMMUTABLE');end if;
 RRL_IW_SHORTAGE_GUARD.require_command(:new.OPERATION_ID,'INTERWARE_SHORTAGE_RECOVER');
end;
/
create or replace trigger RRL_IW_RECOVERY_UNIT_G before insert or update or delete on RRL_INTERWARE_RECOVERY_UNIT for each row
declare n number;op varchar2(100):=:new.RECOVERY_OPERATION_ID;
begin
 if updating or deleting then raise_application_error(-20863,'INTERWARE_RECOVERY_HISTORY_IMMUTABLE');end if;
 RRL_IW_SHORTAGE_GUARD.require_command(op,'INTERWARE_SHORTAGE_RECOVER');
 RRL_STOCK_LOCK_API.assert_held(60,RRL_STOCK_LOCK_API.resource_key('UNIT',:new.PHYSICAL_UNIT_KEY));
 select count(*)into n from RRL_STOCK_OPERATION o,json_table(o.RESOLVED_PLAN_JSON,'$.domain.source_units[*]'columns(K varchar2(64)path '$.key',Q varchar2(60)path '$.quantity',B varchar2(20)path '$.base_uom',V number path '$.version'))j
 where o.OPERATION_ID=op and j.K=:new.PHYSICAL_UNIT_KEY and RRL_STOCK_MATH.quantity(j.Q)=:new.BASE_QTY and j.B=:new.BASE_UOM and j.V=:new.PREVIOUS_UNIT_VERSION
 and json_value(o.RESOLVED_PLAN_JSON,'$.domain.loss_operation_id')=:new.LOSS_OPERATION_ID;
 if n!=1 then raise_application_error(-20863,'INTERWARE_RECOVERY_CAPTURED_UNIT_PROOF_REQUIRED');end if;
end;
/
