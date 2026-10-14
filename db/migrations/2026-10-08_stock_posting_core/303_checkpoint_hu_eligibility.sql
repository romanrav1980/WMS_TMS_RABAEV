create or replace package RRL_STOCK_ELIGIBILITY authid definer as
 function reason(p_uid varchar2,p_cell varchar2,p_warehouse number,p_quantity number default 0,
  p_min_days number default null,p_min_percent number default null,p_purpose varchar2 default 'ALLOCATE',
  p_owner_reservation number default null,p_article varchar2 default null) return varchar2;
 procedure assert_source(p_uid varchar2,p_cell varchar2,p_warehouse number,p_quantity number,
  p_min_days number default null,p_min_percent number default null,p_purpose varchar2 default 'ALLOCATE',
  p_owner_reservation number default null,p_article varchar2 default null);
end;
/

create or replace package body RRL_STOCK_ELIGIBILITY as
 function reason(p_uid varchar2,p_cell varchar2,p_warehouse number,p_quantity number default 0,
  p_min_days number default null,p_min_percent number default null,p_purpose varchar2 default 'ALLOCATE',
  p_owner_reservation number default null,p_article varchar2 default null) return varchar2 is
  v_ware number;v_p number;v_h number;v_owned number:=0;v_article varchar2(160);v_expiry date;v_produced date;
  v_block number;v_system number;v_uom varchar2(20);v_mode varchar2(20);v_ready number;v_pending number;v_count number;v_days number;
 begin
  if p_warehouse is null or p_warehouse<1 or p_quantity is null or p_quantity<0
   or p_min_days<0 or p_min_percent<0 or p_min_percent>100
   or p_purpose is null or p_purpose not in('ALLOCATE','PICK','REPLENISH') then return 'SOURCE_ARGUMENT_INVALID';end if;
  begin
   select c.WARE_ID,s.REMAIN,s.HARD_RESERVED_BASE,s.BASE_UOM,p.ARTICUL,p.EXPIRY_DATE,p.PRODUCED_DATE,
    greatest(nvl(c.BLOCKED_FOR_REMAINS,0),nvl(c.BLOCKED_FOR_POPOLNENIE,0)),nvl(c.IS_SYSTEM,0),
    nvl(rule.SOURCE_PICK_MODE,'AFTER_PUTAWAY'),nvl(rule.MIN_SHELF_DAYS,0),nvl(br.IS_SHIPMENT_ALLOWED,1)
   into v_ware,v_p,v_h,v_uom,v_article,v_expiry,v_produced,v_block,v_system,v_mode,v_days,v_ready
   from RRL_REMAINS s join RRL_PALLETS p on p.UID_PALLET=s.UID_POLETA join RRL_CELLS c on c.CELL=s.CELL
    left join RRL_RECEIPT_SKU_RULE rule on rule.WARE_ID=c.WARE_ID and rule.ARTICUL=p.ARTICUL
    left join RRL_PROD_BATCH_READY_V br on br.PROD_BATCH_ID=p.PROD_BATCH_ID
   where s.UID_POLETA=p_uid and s.CELL=p_cell;
  exception when no_data_found then return 'SOURCE_STOCK_NOT_FOUND';end;
  if v_ware is null or v_ware!=p_warehouse then return 'WAREHOUSE_LOCATION_CONFLICT';end if;
  if p_article is not null and p_article!=v_article then return 'SOURCE_ARTICLE_CONFLICT';end if;
  if v_block!=0 then return 'LOCATION_BLOCKED';end if;
  select count(*) into v_count from RRL_CASE_PICK_SHORT sh
   where sh.CELL_CODE=p_cell and sh.ARTICUL=v_article and
    (sh.STATUS in('CREATED','PENDING_APPROVAL') or sh.RECOVERY_STATE='WAIT_INVENTORY'
     or exists(select 1 from RRL_INVENTORY_TASK it where it.INVENTORY_TASK_ID=sh.INVENTORY_TASK_ID
       and it.STATUS not in('DONE','CANCELLED')));
  if v_count>0 then return 'SOURCE_INVENTORY_PENDING';end if;
  if v_p is null or v_h is null or v_p<0 or v_h<0 or v_h>v_p or v_uom is null then return 'SOURCE_BALANCE_INVALID';end if;
  select count(*) into v_count from RRL_CASE_CARRIER_LOT where LOT_UID=p_uid;
  if v_count>0 then return 'CASE_CARRIER_NOT_ALLOCATABLE';end if;
  if v_ready!=1 then return 'SOURCE_REGULATORY_NOT_READY';end if;
  if v_expiry is not null and trunc(v_expiry)<trunc(sysdate) then return 'SOURCE_EXPIRED';end if;
  v_days:=greatest(v_days,nvl(p_min_days,0));
  if v_days>0 and (v_expiry is null or trunc(v_expiry)-trunc(sysdate)<v_days) then return 'SOURCE_SHELF_DAYS';end if;
  if p_min_percent is not null and (v_expiry is null or v_produced is null
   or trunc(v_expiry)<=trunc(v_produced) or
   (trunc(v_expiry)-trunc(sysdate))*100<p_min_percent*(trunc(v_expiry)-trunc(v_produced))) then return 'SOURCE_SHELF_PERCENT';end if;
  select count(*) into v_pending from dual where exists(
   select 1 from RRL_WAREHOUSE_TASK t where t.UID_PALLET=p_uid and t.TASK_TYPE='PUTAWAY' and t.FROM_CELL=p_cell and t.STATUS not in('DONE','CANCELLED'))
   or exists(select 1 from RRL_SAP_PALLET_RECEIPT rec join RRL_SAP_SUPPLY_ORDER so on so.ORDER_ID=rec.ORDER_ID
    where rec.UID_PALLET=p_uid and so.RECEIVE_CELL=p_cell);
  if v_pending>0 and not(v_mode='DIRECT' and p_purpose in('PICK','ALLOCATE')) then return 'SOURCE_PUTAWAY_REQUIRED';end if;
  if v_system!=0 and not(v_pending>0 and v_mode='DIRECT' and p_purpose in('PICK','ALLOCATE')) then return 'SOURCE_SYSTEM_LOCATION';end if;
  if p_purpose='PICK' and v_pending=0 then
   select count(*) into v_count from RRL_PICK_FACE pf join RRL_PICK_FACE_ARTICUL a on a.PICK_FACE_ID=pf.PICK_FACE_ID
    where pf.WARE_ID=p_warehouse and pf.CELL_CODE=p_cell and pf.ACTIVE=1 and a.ARTICUL=v_article and a.ACTIVE=1
     and a.CASE_PICK_ENABLED=1 and (a.VALID_FROM is null or a.VALID_FROM<=sysdate) and (a.VALID_TO is null or a.VALID_TO>=sysdate);
   if v_count=0 and p_owner_reservation is not null then
    select count(*) into v_count from RRL_PICK_FACE_ASSIGNMENT a
     join RRL_PICK_FACE pf on pf.PICK_FACE_ID=a.PICK_FACE_ID
     join RRL_PICK_WAVE w on w.PICK_WAVE_ID=a.PICK_WAVE_ID
     join RRL_STOCK_RESERVATION sr on sr.RESERVATION_ID=p_owner_reservation
     where a.CELL_CODE=p_cell and a.ARTICUL=v_article and a.STATUS='ACTIVE'
      and a.BASE_UOM=v_uom and pf.ACTIVE=1 and pf.WARE_ID=p_warehouse
      and w.STATUS='LAUNCHED' and sr.SOURCE_DOC_TYPE='PICK_WAVE' and sr.SOURCE_DOC_ID=a.PICK_WAVE_ID;
   end if;
   if v_count=0 then return 'SOURCE_PICK_FACE_UNPUBLISHED';end if;
  end if;
  if p_owner_reservation is not null then
   begin select BASE_QTY into v_owned from RRL_STOCK_RESERVATION where RESERVATION_ID=p_owner_reservation
    and UID_PALLET=p_uid and CELL=p_cell and ARTICUL=v_article and BASE_UOM=v_uom
    and RESERVATION_KIND='HARD' and STATUS in('ACTIVE','ALLOCATED','PICKING');
   exception when no_data_found then return 'SOURCE_RESERVATION_CONFLICT';end;
   if v_owned is null or v_owned<=0 or v_owned>v_h then return 'SOURCE_RESERVATION_CONFLICT';end if;
  end if;
  begin RRL_STOCK_UNIT_CORE.assert_composition(p_uid,p_cell);
  exception when others then
   if sqlcode in(-20884,-20868) then return 'SOURCE_COMPOSITION_CONFLICT';else raise;end if;
  end;
  if v_p<=0 or v_p-v_h+v_owned<p_quantity or (p_quantity=0 and v_p-v_h+v_owned<=0) then return 'SOURCE_FREE_INSUFFICIENT';end if;
  return null;
 end;
 procedure assert_source(p_uid varchar2,p_cell varchar2,p_warehouse number,p_quantity number,
  p_min_days number default null,p_min_percent number default null,p_purpose varchar2 default 'ALLOCATE',
  p_owner_reservation number default null,p_article varchar2 default null) is v_reason varchar2(100);
 begin
  RRL_STOCK_LOCK_API.assert_policy(RRL_STOCK_LOCK_API.resource_key('CONFIG','WAREHOUSE'),4);
  RRL_STOCK_LOCK_API.assert_policy(RRL_STOCK_LOCK_API.resource_key('CELL',p_cell),4);
  RRL_STOCK_LOCK_API.assert_held(30,RRL_STOCK_LOCK_API.resource_key('HU',p_uid));
  RRL_STOCK_LOCK_API.assert_held(50,RRL_STOCK_LOCK_API.resource_key('STOCK',p_uid));
  v_reason:=reason(p_uid,p_cell,p_warehouse,p_quantity,p_min_days,p_min_percent,p_purpose,p_owner_reservation,p_article);
  if v_reason is not null then raise_application_error(-20886,'SOURCE_INELIGIBLE: '||v_reason);end if;
 end;
end;
/
