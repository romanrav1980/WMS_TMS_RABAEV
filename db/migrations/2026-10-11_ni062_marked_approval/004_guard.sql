create or replace trigger RRL_STORE_RETURN_UNIT_GUARD before insert or update or delete on RRL_STORE_RETURN_UNIT for each row
declare op varchar2(100):=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID');n number;
begin
 if not inserting then raise_application_error(-20863,'STORE_RETURN_UNIT_APPEND_ONLY');end if;
 if op is null or op!=:new.APPROVAL_OPERATION_ID or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')is null or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false)then raise_application_error(-20863,'STORE_RETURN_UNIT_ROOT_REQUIRED');end if;
 RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_STORE_RETURN_UNIT',op||':'||:new.PHYSICAL_UNIT_KEY));
 RRL_STOCK_LOCK_API.assert_held(60,RRL_STOCK_LOCK_API.resource_key('UNIT',:new.PHYSICAL_UNIT_KEY));
 select count(*)into n from RRL_STOCK_OPERATION o join json_table(o.RESOLVED_PLAN_JSON,'$.domain.return_units[*]'columns(K varchar2(64)path '$.key',Q varchar2(60)path '$.quantity',B varchar2(20)path '$.base_uom',V number path '$.version'))u
 on u.K=:new.PHYSICAL_UNIT_KEY and RRL_STOCK_MATH.quantity(u.Q)=:new.BASE_QTY and u.B=:new.BASE_UOM and u.V=:new.SOURCE_UNIT_VERSION
 where o.OPERATION_ID=op and o.COMMAND_TYPE='STORE_RETURN_APPROVE'and o.STATE='IN_FLIGHT'
 and json_value(o.RESOLVED_PLAN_JSON,'$.domain.receipt_operation_id')=:new.RECEIPT_OPERATION_ID and json_value(o.RESOLVED_PLAN_JSON,'$.domain.lot_uid')=:new.ORIGINAL_UID and json_value(o.RESOLVED_PLAN_JSON,'$.domain.source_cell')=:new.SOURCE_CELL;
 if n!=1 then raise_application_error(-20863,'STORE_RETURN_UNIT_FROZEN_SOURCE_REQUIRED');end if;
end;
/
