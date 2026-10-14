create or replace trigger RRL_STOCK_UNIT_GUARD
 before insert or update or delete on RRL_WMS_RECEIPT_UNIT for each row
begin
 if not RRL_STOCK_WRITE_GUARD.enforcement_required then return;end if;
 if deleting then raise_application_error(-20863,'UNIT_HISTORY_DELETE_FORBIDDEN');end if;
 if inserting then
  RRL_STOCK_WRITE_GUARD.require_effect('RECEIPT_CAPTURE',:new.CURRENT_UID,:new.CURRENT_CELL);
  if :new.CURRENT_UID!=sys_context('RRL_STOCK_WRITE_CTX','EFFECT_UID') or
   :new.CURRENT_CELL!=sys_context('RRL_STOCK_WRITE_CTX','EFFECT_CELL') or :new.STOCK_STATUS!='CAPTURED'
   or :new.STOCK_STATUS is null or :new.UNIT_VERSION!=0 or :new.HARD_RESERVATION_ID is not null then
   raise_application_error(-20884,'UNIT_CAPTURE_CONFLICT');end if;
 else
  RRL_STOCK_WRITE_GUARD.require_effect('UNIT',:old.CURRENT_UID,:old.CURRENT_CELL);
  RRL_STOCK_WRITE_GUARD.require_unit(:old.PHYSICAL_UNIT_KEY,:old.CURRENT_UID);
  if :new.UID_PALLET!=:old.UID_PALLET or :new.UNIT_ID!=:old.UNIT_ID or :new.PHYSICAL_UNIT_KEY!=:old.PHYSICAL_UNIT_KEY
   or :new.BASE_QTY!=:old.BASE_QTY or :new.BASE_UOM!=:old.BASE_UOM or :new.UNIT_VERSION!=:old.UNIT_VERSION+1 then
   raise_application_error(-20884,'UNIT_PROVENANCE_OR_VERSION_CONFLICT');end if;
 end if;
 RRL_STOCK_WRITE_GUARD.require_unit(:new.PHYSICAL_UNIT_KEY,:new.CURRENT_UID);
 if :new.CURRENT_CELL is null or :new.BASE_UOM is null or :new.BASE_QTY is null or :new.BASE_QTY<=0 or
  :new.STOCK_STATUS is null or :new.STOCK_STATUS not in('CAPTURED','AVAILABLE','BLOCKED','ISSUED') then
  raise_application_error(-20884,'UNIT_BINDING_CONFLICT');end if;
 RRL_STOCK_MATH.assert_base(:new.BASE_QTY,9);
end;
/
