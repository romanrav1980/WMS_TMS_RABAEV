create or replace trigger RRL_STORE_RECEIPT_UNIT_GUARD before insert or update or delete on RRL_STORE_RECEIPT_UNIT for each row
declare op varchar2(100):=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID');n number;
begin
 if not inserting then raise_application_error(-20863,'STORE_UNIT_DISPOSITION_APPEND_ONLY');end if;
 if op is null or op!=:new.OPERATION_ID or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')is null or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false)or:new.RECORDED_BY!=sys_context('RRL_STOCK_WRITE_CTX','ACTOR')then raise_application_error(-20863,'STORE_UNIT_DISPOSITION_ROOT_REQUIRED');end if;
 RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_STORE_RECEIPT_UNIT',op||':'||:new.PHYSICAL_UNIT_KEY));
 select count(*)into n from RRL_STOCK_OPERATION o join json_table(o.RESOLVED_PLAN_JSON,'$.domain.marked_unit_dispositions[*]'columns(K varchar2(64)path '$.key',D varchar2(20)path '$.disposition',Q varchar2(60)path '$.quantity',B varchar2(20)path '$.base_uom',V number path '$.version'))u
  on u.K=:new.PHYSICAL_UNIT_KEY and u.D=:new.UNIT_DISPOSITION and RRL_STOCK_MATH.quantity(u.Q)=:new.BASE_QTY and u.B=:new.BASE_UOM and u.V=:new.SOURCE_UNIT_VERSION
  where o.OPERATION_ID=op and o.COMMAND_TYPE='STORE_RECEIPT'and o.STATE='IN_FLIGHT'and json_value(o.RESOLVED_PLAN_JSON,'$.domain.load_operation_id')=:new.LOAD_OPERATION_ID;
 if n!=1 then raise_application_error(-20863,'STORE_UNIT_DISPOSITION_FROZEN_PLAN_REQUIRED');end if;
end;
/
