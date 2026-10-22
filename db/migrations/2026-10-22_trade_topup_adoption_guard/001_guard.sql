create or replace trigger RRL_STOCK_RESERVATION_GUARD
 before insert or update or delete on RRL_STOCK_RESERVATION for each row
declare adoption_count number:=0;
begin
 if not RRL_STOCK_WRITE_GUARD.enforcement_required then return;end if;
 if deleting then raise_application_error(-20863,'RESERVATION_DELETE_FORBIDDEN');end if;
 RRL_STOCK_WRITE_GUARD.require_effect('RESERVATION',:new.UID_PALLET,:new.CELL,:new.RESERVATION_ID);
 if updating then
  if :old.UID_PALLET is not null then RRL_STOCK_LOCK_API.assert_held(50,RRL_STOCK_LOCK_API.resource_key('STOCK',:old.UID_PALLET));end if;
  -- The only permitted document change is an owned top-up hold in the current frozen wave launch.
  -- Quantity, physical source, unit, status and reservation identity stay unchanged.
  if :old.SOURCE_DOC_TYPE='TRADE_TOPUP' and :new.SOURCE_DOC_TYPE='PICK_WAVE'
   and :old.RESERVATION_KIND='HARD' and :new.RESERVATION_KIND=:old.RESERVATION_KIND
   and :new.UID_PALLET=:old.UID_PALLET and :new.CELL=:old.CELL and :new.BASE_UOM=:old.BASE_UOM
   and :new.BASE_QTY=:old.BASE_QTY and :new.BASE_QTY>0 and :new.QTY=:old.QTY
   and :new.STATUS=:old.STATUS and :new.STATUS in('ACTIVE','ALLOCATED') and :new.RESERVATION_DOMAIN='PICKING'
   and :new.PICK_WAVE_ID=:new.SOURCE_DOC_ID
   and sys_context('RRL_STOCK_WRITE_CTX','TX_ID')=dbms_transaction.local_transaction_id(false) then
   select count(*) into adoption_count from RRL_STOCK_OPERATION op
    join json_table(op.RESOLVED_PLAN_JSON,'$.domain.reservations[*]' columns(PROJECTION_ID number path '$.projection_id',NEW_RESERVATION_ID number path '$.reservation_id')) frozen on 1=1
    join RRL_PICK_RESERVATION pr on pr.PICK_RESERVATION_ID=frozen.PROJECTION_ID
    join RRL_PICK_PLAN_LINE pl on pl.PICK_PLAN_LINE_ID=pr.PICK_PLAN_LINE_ID
    join RRL_TRADE_TOPUP_HOLD h on h.PROPOSAL_ID=:old.SOURCE_DOC_ID and h.UID_PALLET=:old.UID_PALLET and h.CELL=:old.CELL
    join RRL_TRADE_TOPUP_PROPOSAL p on p.PROPOSAL_ID=h.PROPOSAL_ID
    where op.OPERATION_ID=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID') and op.COMMAND_TYPE='WAVE_LAUNCH' and op.STATE='IN_FLIGHT'
     and json_value(op.RESOLVED_PLAN_JSON,'$.domain.wave' returning number)=:new.SOURCE_DOC_ID
     and pr.PICK_TASK_ID=:new.SOURCE_LINE_ID and pr.PICK_PLAN_ID=:new.PICK_PLAN_ID and pr.PICK_PLAN_LINE_ID=:new.PICK_PLAN_LINE_ID
     and pr.CUSTOMER_ORDER_ID=:new.CUSTOMER_ORDER_ID and pr.CUSTOMER_ID=:new.CUSTOMER_ID
     and pr.PALLET_UID=:old.UID_PALLET and pr.SOURCE_CELL_CODE=:old.CELL and pr.RESERVED_QTY=:new.BASE_QTY
     and pr.RESERVATION_STATUS='ACTIVE' and pr.RESERVATION_LEVEL='SOFT' and h.STATUS='ACTIVE' and h.BASE_QTY>=:new.BASE_QTY
     and (h.RESERVATION_ID=:old.RESERVATION_ID or frozen.NEW_RESERVATION_ID=:old.RESERVATION_ID)
     and p.STATUS='SAP_ACCEPTED' and RRL_TRADE_TOPUP_ADOPT.line_proposal(pl.CUSTOMER_ORDER_ROW_ID)=p.PROPOSAL_ID;
  end if;
  if :new.RESERVATION_ID!=:old.RESERVATION_ID or :new.RESERVATION_VERSION!=:old.RESERVATION_VERSION+1
   or (adoption_count<>1 and ((:new.SOURCE_DOC_TYPE!=:old.SOURCE_DOC_TYPE or (:new.SOURCE_DOC_TYPE is null and :old.SOURCE_DOC_TYPE is not null) or (:new.SOURCE_DOC_TYPE is not null and :old.SOURCE_DOC_TYPE is null))
    or (:new.SOURCE_DOC_ID!=:old.SOURCE_DOC_ID or (:new.SOURCE_DOC_ID is null and :old.SOURCE_DOC_ID is not null) or (:new.SOURCE_DOC_ID is not null and :old.SOURCE_DOC_ID is null)))) then
   raise_application_error(-20869,'RESERVATION_IDENTITY_OR_VERSION_CONFLICT');end if;
 end if;
end;
/
