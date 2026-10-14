create or replace package RRL_WEIGHT_BOX_CAPACITY authid definer as
 function enabled(p_article varchar2)return number;
 function kg_volume_upper_bound(p_cell varchar2,p_article varchar2)return number;
 function physical_volume(p_uid varchar2,p_cell varchar2,p_quantity number,p_exact number default 1)return number;
 function reservation_volume(p_reservation number,p_quantity number)return number;
end;
/
create or replace package body RRL_WEIGHT_BOX_CAPACITY as
 function enabled(p_article varchar2)return number is n number;begin
  select nvl(max(SERIALIZED_WEIGHT_BOXES),0)into n from RRL_SKU_RECEIPT_POLICY where ARTICUL=p_article;return n;
 end;
 function kg_volume_upper_bound(p_cell varchar2,p_article varchar2)return number is n number;bad number;ratio number;lot_count number;
 begin
  select count(*)into lot_count from(select r.UID_POLETA from RRL_REMAINS r join RRL_PALLETS p on p.UID_PALLET=r.UID_POLETA
   join RRL_CELLS c on c.CELL=r.CELL where p.ARTICUL=p_article and r.REMAIN>0
    and c.WARE_ID=(select WARE_ID from RRL_CELLS where CELL=p_cell)and rownum<=201);
  if lot_count>200 then raise_application_error(-20881,'WEIGHT_BOX_CAPACITY_LOT_BOUND_200');end if;
  select count(*),nvl(sum(case when BOX_VOLUME_M3 is null or BOX_VOLUME_M3<=0 or BASE_QTY is null or BASE_QTY<=0 or BASE_UOM is null or BASE_UOM!='KG'then 1 else 0 end),0),max(BOX_VOLUME_M3/nullif(BASE_QTY,0))
   into n,bad,ratio from(select u.BOX_VOLUME_M3,u.BASE_QTY,u.BASE_UOM
    from RRL_REMAINS r join RRL_PALLETS p on p.UID_PALLET=r.UID_POLETA join RRL_CELLS c on c.CELL=r.CELL
    join RRL_WMS_RECEIPT_UNIT u on u.CURRENT_UID=r.UID_POLETA and u.CURRENT_CELL=r.CELL and u.STOCK_STATUS!='ISSUED'
    where p.ARTICUL=p_article and r.REMAIN>0 and c.WARE_ID=(select WARE_ID from RRL_CELLS where CELL=p_cell)and rownum<=10001);
  if n>10000 then raise_application_error(-20881,'WEIGHT_BOX_CAPACITY_UNIT_BOUND_10000');end if;
  if n=0 or bad>0 or ratio is null or ratio<=0 then raise_application_error(-20887,'WEIGHT_BOX_ACTUAL_VOLUME_EVIDENCE_REQUIRED');end if;
  return ratio;
 end;
 function physical_volume(p_uid varchar2,p_cell varchar2,p_quantity number,p_exact number default 1)return number is
  n number;bad number;qty number;volume number;
 begin
  if p_quantity=0 then return 0;end if;
  select count(*),nvl(sum(BASE_QTY),0),nvl(sum(BOX_VOLUME_M3),0),
    nvl(sum(case when BOX_VOLUME_M3 is null or BOX_VOLUME_M3<=0 or BASE_QTY is null or BASE_UOM is null or BASE_UOM!='KG'then 1 else 0 end),0)
   into n,qty,volume,bad from(select BASE_QTY,BASE_UOM,BOX_VOLUME_M3 from RRL_WMS_RECEIPT_UNIT
    where CURRENT_UID=p_uid and CURRENT_CELL=p_cell and STOCK_STATUS!='ISSUED'and rownum<=10001);
  if n>10000 then raise_application_error(-20881,'WEIGHT_BOX_CAPACITY_UNIT_BOUND_10000');end if;
  if n=0 or bad>0 or (p_exact=1 and qty!=p_quantity)or qty<p_quantity then raise_application_error(-20887,'WEIGHT_BOX_VOLUME_COMPOSITION_MUST_COVER_KG');end if;
  -- A partial arrival charges the full source-box volume conservatively; never split a box volume by average mass.
  return volume;
 end;
 function reservation_volume(p_reservation number,p_quantity number)return number is n number;bad number;qty number;volume number;
 begin
  if p_quantity=0 then return 0;end if;
  select count(*),nvl(sum(u.BASE_QTY),0),nvl(sum(u.BOX_VOLUME_M3),0),
   nvl(sum(case when u.BOX_VOLUME_M3 is null or u.BOX_VOLUME_M3<=0 or u.BASE_QTY is null or u.BASE_UOM is null or u.BASE_UOM!='KG'then 1 else 0 end),0)
   into n,qty,volume,bad from(select BASE_QTY,BASE_UOM,BOX_VOLUME_M3 from RRL_WMS_RECEIPT_UNIT u
    where u.HARD_RESERVATION_ID=p_reservation and u.STOCK_STATUS!='ISSUED'and rownum<=10001)u;
  if n>10000 then raise_application_error(-20881,'WEIGHT_BOX_CAPACITY_UNIT_BOUND_10000');end if;
  if n=0 or bad>0 or qty<p_quantity then raise_application_error(-20887,'WEIGHT_BOX_RESERVED_VOLUME_MUST_COVER_ARRIVAL_KG');end if;
  return volume;
 end;
end;
/
