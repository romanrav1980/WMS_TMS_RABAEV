create or replace trigger RRL_IW_REC_DISPATCH_GUARD before insert or update or delete on RRL_IW_RECOVERY_DISPATCH for each row
declare n number;kind varchar2(80);begin
 if updating or deleting then raise_application_error(-20878,'RECOVERY_DISPATCH_IMMUTABLE');end if;
 select COMMAND_TYPE into kind from RRL_STOCK_OPERATION where OPERATION_ID=:new.OPERATION_ID and STATE='IN_FLIGHT';
 if kind not in('LOAD_SHIPMENT','HU_SHIP')then raise_application_error(-20863,'RECOVERY_ACTUAL_LOADING_COMMAND_REQUIRED');end if;
 RRL_IW_SHORTAGE_GUARD.require_command(:new.OPERATION_ID,kind);
 if kind='HU_SHIP'then
  select count(*)into n from RRL_STOCK_OPERATION op,json_table(op.RESOLVED_PLAN_JSON,'$.domain.shipments[*]'columns(
   BIND_ID varchar2(100)path '$.domain.interwarehouse_onward_source.binding_operation_id',
   ST_NO number path '$.domain.interwarehouse_onward_source.st_id',
   REC_ID varchar2(100)path '$.domain.interwarehouse_onward_source.recovery_operation_id'))j
  where op.OPERATION_ID=:new.OPERATION_ID and j.BIND_ID=:new.BIND_OPERATION_ID and j.ST_NO=:new.ST_ID and j.REC_ID=:new.RECOVERY_OPERATION_ID;
  if n!=1 then raise_application_error(-20886,'RECOVERY_CONSOLIDATED_CAPTURED_LINEAGE_REQUIRED');end if;
 end if;
 RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_IW_RECOVERY_DISPATCH',:new.OPERATION_ID));
 select count(*)into n from RRL_IW_RECOVERY_ST_BIND b join RRL_INTERWARE_RECOVERY_RECEIPT r on r.OPERATION_ID=b.RECOVERY_OPERATION_ID
 join RRL_IW_RECOVERY_PLACEMENT p on p.RECOVERY_OPERATION_ID=r.OPERATION_ID
 where b.OPERATION_ID=:new.BIND_OPERATION_ID and b.ST_ID=:new.ST_ID and b.ROOT_UID=:new.ROOT_UID
 and b.RECOVERY_OPERATION_ID=:new.RECOVERY_OPERATION_ID and b.RECEIPT_OPERATION_ID=:new.RECEIPT_OPERATION_ID
 and b.SOURCE_LOAD_OPERATION_ID=:new.SOURCE_LOAD_OPERATION_ID and r.ROOT_UID=:new.ROOT_UID
 and r.BASE_QTY=:new.BASE_QTY and r.BASE_UOM=:new.BASE_UOM and p.TARGET_CELL=b.SOURCE_CELL;
 if n!=1 then raise_application_error(-20886,'RECOVERY_DISPATCH_EXACT_LINEAGE_REQUIRED');end if;
end;
/
