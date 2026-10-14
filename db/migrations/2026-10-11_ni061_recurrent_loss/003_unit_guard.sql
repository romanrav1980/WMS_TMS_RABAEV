create or replace trigger RRL_IW_SHORT_UNIT_G before insert or update or delete on RRL_INTERWARE_SHORTAGE_UNIT for each row
declare n number;begin
 if updating or deleting then raise_application_error(-20863,'INTERWARE_SHORTAGE_HISTORY_IMMUTABLE');end if;
 RRL_IW_SHORTAGE_GUARD.require_command(:new.FACT_OPERATION_ID,'INTERWARE_SHORTAGE_CONFIRM');
 RRL_STOCK_LOCK_API.assert_held(60,RRL_STOCK_LOCK_API.resource_key('UNIT',:new.PHYSICAL_UNIT_KEY));
 select count(*)into n from RRL_STOCK_OPERATION operation,
 json_table(operation.RESOLVED_PLAN_JSON,'$.domain.missing_units[*]'columns(K varchar2(64)path '$.key',Q varchar2(60)path '$.quantity',B varchar2(20)path '$.base_uom',V number path '$.version'))frozen,
 RRL_WMS_RECEIPT_UNIT unit_row
 where operation.OPERATION_ID=:new.FACT_OPERATION_ID and operation.STATE='IN_FLIGHT'and operation.COMMAND_TYPE='INTERWARE_SHORTAGE_CONFIRM'
 and frozen.K=:new.PHYSICAL_UNIT_KEY and RRL_STOCK_MATH.quantity(frozen.Q)=:new.BASE_QTY and frozen.B=:new.BASE_UOM and frozen.V=:new.UNIT_VERSION
 and unit_row.PHYSICAL_UNIT_KEY=frozen.K and unit_row.CURRENT_UID=:new.ORIGINAL_UID and unit_row.STOCK_STATUS='ISSUED'
 and unit_row.UNIT_VERSION=:new.UNIT_VERSION and unit_row.BASE_QTY=:new.BASE_QTY and unit_row.BASE_UOM=:new.BASE_UOM and unit_row.HARD_RESERVATION_ID is null;
 if n!=1 then raise_application_error(-20886,'INTERWARE_LOSS_EXACT_CAPTURED_CURRENT_UNIT_REQUIRED');end if;
end;
/
