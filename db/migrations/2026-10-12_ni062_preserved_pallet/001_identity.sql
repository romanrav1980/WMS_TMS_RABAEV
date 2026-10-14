create or replace package RRL_RETURN_PALLET_IDENTITY authid definer
 accessible by(package RRL_STORE_RETURN_UNIT_CORE,package RRL_STOCK_STORE_RETURN_REC_CMD)as
 procedure assert_preserved(p_approval varchar2,p_uid varchar2);
end;
/
create or replace package body RRL_RETURN_PALLET_IDENTITY as
 procedure assert_preserved(p_approval varchar2,p_uid varchar2)is
 a RRL_STORE_RETURN_APPROVAL%rowtype;p RRL_PALLETS%rowtype;n number;qty number;
 begin
  select *into a from RRL_STORE_RETURN_APPROVAL where OPERATION_ID=p_approval;
  if p_uid is null or p_uid!=a.LOT_UID then raise_application_error(-20886,'RETURN_PALLET_ORIGINAL_IDENTITY_REQUIRED');end if;
  select *into p from RRL_PALLETS where UID_PALLET=p_uid;
  if p.ARTICUL is null or p.ARTICUL!=a.ARTICLE or p.UNIT_COUNT is null or p.UNIT_COUNT!=a.BASE_QTY then
   raise_application_error(-20886,'RETURN_PALLET_FULL_ORIGINAL_QUANTITY_REQUIRED');
  end if;
  select count(*)into n from RRL_REMAINS where UID_POLETA=p_uid and(REMAIN!=0 or HARD_RESERVED_BASE!=0);
  if n!=0 then raise_application_error(-20890,'CLOSURE_CHANGED: preserved pallet still has warehouse stock');end if;
  select count(*)into n from RRL_WMS_HU_LINK where ACTIVE_FLAG=1 and(PARENT_UID=p_uid or CHILD_PALLET_UID=p_uid);
  if n!=0 then raise_application_error(-20886,'RETURN_PALLET_EXPLICIT_HU_UNPACK_REQUIRED');end if;
  select count(*)into n from RRL_CASE_CARRIER_LOT where LOT_UID=p_uid;
  if n!=0 then raise_application_error(-20886,'RETURN_PALLET_ORIGINAL_CASE_REPACKING_UNSUPPORTED');end if;
  select count(*)into n from RRL_WAREHOUSE_TASK where UID_PALLET=p_uid and STATUS not in('DONE','CANCELLED');
  if n!=0 then raise_application_error(-20890,'CLOSURE_CHANGED: preserved pallet physical task issued');end if;
  select count(*),sum(BASE_QTY)into n,qty from RRL_WMS_RECEIPT_UNIT
   where UID_PALLET=p_uid and CURRENT_UID=p_uid and STOCK_STATUS='ISSUED'and HARD_RESERVATION_ID is null;
  if n<1 or qty!=a.BASE_QTY then raise_application_error(-20886,'RETURN_PALLET_UNCHANGED_ORIGINAL_UNITS_REQUIRED');end if;
  select count(*)into n from RRL_WMS_RECEIPT_UNIT u where u.UID_PALLET=p_uid
   and not exists(select 1 from RRL_STORE_RETURN_UNIT b where b.APPROVAL_OPERATION_ID=p_approval and b.PHYSICAL_UNIT_KEY=u.PHYSICAL_UNIT_KEY);
  if n!=0 then raise_application_error(-20886,'RETURN_PALLET_FULL_APPROVED_COMPOSITION_REQUIRED');end if;
 end;
end;
/
