-- Dormant in PREPARED. Enforcement begins with the one global release switch.
create or replace package RRL_STOCK_WRITE_GUARD authid definer as
 function enforcement_required return boolean;
 procedure require_effect(p_kind varchar2,p_uid varchar2 default null,p_cell varchar2 default null,p_row_id number default null);
 procedure require_unit(p_key varchar2,p_uid varchar2);
end;
/
create or replace package body RRL_STOCK_WRITE_GUARD as
 function enforcement_required return boolean is v_state varchar2(20);
 begin
  if sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID') is not null then return true;end if;
  select STATE into v_state from RRL_STOCK_RELEASE where RELEASE_ID=1;
  return v_state!='PREPARED';
 end;
 procedure require_effect(p_kind varchar2,p_uid varchar2 default null,p_cell varchar2 default null,p_row_id number default null) is v_tx varchar2(100);
 begin
  v_tx:=dbms_transaction.local_transaction_id(false);
  if v_tx is null or sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID') is null or
   sys_context('RRL_STOCK_WRITE_CTX','TX_ID') is null or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=v_tx or
   sys_context('RRL_STOCK_WRITE_CTX','EFFECT') is null or sys_context('RRL_STOCK_WRITE_CTX','EFFECT')!=p_kind then
   raise_application_error(-20863,'DIRECT_STOCK_WRITE_FORBIDDEN');end if;
  RRL_STOCK_LOCK_API.assert_policy(RRL_STOCK_LOCK_API.resource_key('RELEASE','STOCK'),4);
  if p_uid is not null then RRL_STOCK_LOCK_API.assert_held(50,RRL_STOCK_LOCK_API.resource_key('STOCK',p_uid));end if;
  if p_kind in('STOCK','JOURNAL') and
   (p_uid is null or p_cell is null or sys_context('RRL_STOCK_WRITE_CTX','EFFECT_UID') is null or sys_context('RRL_STOCK_WRITE_CTX','EFFECT_CELL') is null or sys_context('RRL_STOCK_WRITE_CTX','EFFECT_UID')!=p_uid or
    sys_context('RRL_STOCK_WRITE_CTX','EFFECT_CELL')!=p_cell) then raise_application_error(-20863,'STOCK_EFFECT_KEY_CONFLICT');end if;
  if p_kind='RESERVATION' then
   if p_row_id is null or sys_context('RRL_STOCK_WRITE_CTX','EFFECT_ROW_ID') is null or
    sys_context('RRL_STOCK_WRITE_CTX','EFFECT_ROW_ID')!=RRL_STOCK_PLAN_HELPER.decimal_text(p_row_id) then
    raise_application_error(-20863,'RESERVATION_EFFECT_KEY_CONFLICT');end if;
   RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_STOCK_RESERVATION',RRL_STOCK_PLAN_HELPER.decimal_text(p_row_id)));
  end if;
 end;
 procedure require_unit(p_key varchar2,p_uid varchar2) is
 begin
  if p_key is null or p_uid is null then raise_application_error(-20884,'UNIT_BINDING_REQUIRED');end if;
  RRL_STOCK_LOCK_API.assert_held(60,RRL_STOCK_LOCK_API.resource_key('UNIT',p_key));
  RRL_STOCK_LOCK_API.assert_held(50,RRL_STOCK_LOCK_API.resource_key('STOCK',p_uid));
 end;
end;
/
create or replace trigger RRL_STOCK_REMAINS_GUARD
 before insert or update or delete on RRL_REMAINS for each row
begin
 if not RRL_STOCK_WRITE_GUARD.enforcement_required then return;end if;
 if deleting then raise_application_error(-20863,'STOCK_ROW_DELETE_FORBIDDEN');end if;
 RRL_STOCK_WRITE_GUARD.require_effect('STOCK',:new.UID_POLETA,:new.CELL);
 if :new.BASE_UOM is null or :new.STOCK_VERSION is null then raise_application_error(-20868,'STOCK_BASE_BINDING_REQUIRED');end if;
 RRL_STOCK_MATH.assert_base(:new.REMAIN,9);RRL_STOCK_MATH.assert_base(:new.HARD_RESERVED_BASE,9);
 if updating and (:old.UID_POLETA!=:new.UID_POLETA or :old.CELL!=:new.CELL or :old.BASE_UOM!=:new.BASE_UOM
   or :new.STOCK_VERSION!=:old.STOCK_VERSION+1) then raise_application_error(-20867,'STOCK_KEY_OR_VERSION_CONFLICT');end if;
 if inserting and :new.STOCK_VERSION!=1 then raise_application_error(-20867,'STOCK_INITIAL_VERSION_CONFLICT');end if;
end;
/
create or replace trigger RRL_STOCK_JOURNAL_GUARD
 before insert or update or delete on RRL_EVENTS for each row
begin
 if not RRL_STOCK_WRITE_GUARD.enforcement_required then return;end if;
 if updating or deleting then raise_application_error(-20863,'POSTED_HISTORY_IMMUTABLE');end if;
 RRL_STOCK_WRITE_GUARD.require_effect('JOURNAL',:new.UID_POLETA,nvl(:new.CELL_FROM,:new.CELL_TO));
 if :new.OPERATION_ID is null or :new.OPERATION_ID!=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID')
  or :new.BASE_QTY is null or :new.BASE_QTY=0 or :new.BASE_UOM is null or :new.COUNT_EVENT!=abs(:new.BASE_QTY)
  or :new.LINE_NO is null or :new.LINE_NO<1 or :new.LEG_NO is null or :new.LEG_NO<1
  or (:new.CELL_FROM is null and :new.CELL_TO is null)
  or (:new.CELL_FROM is not null and :new.CELL_TO is not null and
      (:new.TYPE_EVENT!=2 or :new.TYPE_EVENT is null or :new.CELL_FROM=:new.CELL_TO or :new.BASE_QTY<=0))
  or (:new.CELL_TO is null and (:new.TYPE_EVENT not in(2,3) or :new.TYPE_EVENT is null or :new.BASE_QTY>=0))
  or (:new.CELL_FROM is null and (:new.TYPE_EVENT not in(1,2) or :new.TYPE_EVENT is null or :new.BASE_QTY<=0)) then
  raise_application_error(-20870,'JOURNAL_CONTRACT_REQUIRED');end if;
end;
/
create or replace trigger RRL_STOCK_RESERVATION_GUARD
 before insert or update or delete on RRL_STOCK_RESERVATION for each row
begin
 if not RRL_STOCK_WRITE_GUARD.enforcement_required then return;end if;
 if deleting then raise_application_error(-20863,'RESERVATION_DELETE_FORBIDDEN');end if;
 RRL_STOCK_WRITE_GUARD.require_effect('RESERVATION',:new.UID_PALLET,:new.CELL,:new.RESERVATION_ID);
 if updating then
  if :old.UID_PALLET is not null then RRL_STOCK_LOCK_API.assert_held(50,RRL_STOCK_LOCK_API.resource_key('STOCK',:old.UID_PALLET));end if;
  if :new.RESERVATION_ID!=:old.RESERVATION_ID or :new.RESERVATION_VERSION!=:old.RESERVATION_VERSION+1
   or (:new.SOURCE_DOC_TYPE!=:old.SOURCE_DOC_TYPE or (:new.SOURCE_DOC_TYPE is null and :old.SOURCE_DOC_TYPE is not null) or (:new.SOURCE_DOC_TYPE is not null and :old.SOURCE_DOC_TYPE is null)) or (:new.SOURCE_DOC_ID!=:old.SOURCE_DOC_ID or (:new.SOURCE_DOC_ID is null and :old.SOURCE_DOC_ID is not null) or (:new.SOURCE_DOC_ID is not null and :old.SOURCE_DOC_ID is null)) then
   raise_application_error(-20869,'RESERVATION_IDENTITY_OR_VERSION_CONFLICT');end if;
 end if;
end;
/
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
