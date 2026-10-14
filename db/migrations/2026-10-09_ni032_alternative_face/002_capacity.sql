-- One canonical pick-face volume budget shared by planner, reserve and locked execution.
create or replace package RRL_STOCK_REPL_CAPACITY authid definer as
 function unit_volume(p_cell varchar2,p_article varchar2) return number;
 function remaining_base_quantity(p_cell varchar2,p_article varchar2,p_exclude_repl number default null) return number;
 procedure assert_arrival(p_repl number,p_base_quantity number);
end;
/
create or replace package body RRL_STOCK_REPL_CAPACITY as
 function unit_volume(p_cell varchar2,p_article varchar2) return number is
  v_box number;v_num number;v_den number;n number;
 begin
  select count(*),max(coalesce(case when a.USE_ARTICUL_REPLENISH_RULE=1 then ar.BOX_VOLUME_M3 end,a.BOX_VOLUME_M3))
   into n,v_box from RRL_PICK_FACE pf join RRL_PICK_FACE_ARTICUL a on a.PICK_FACE_ID=pf.PICK_FACE_ID
   left join RRL_ARTICUL_REPLENISH_RULE ar on ar.ARTICUL=a.ARTICUL
   where pf.CELL_CODE=p_cell and pf.ACTIVE=1 and a.ARTICUL=p_article and a.ACTIVE=1;
  if n=0 then
   select count(*),max(UNIT_VOLUME_M3) into n,v_box from RRL_PICK_FACE_ASSIGNMENT
    where CELL_CODE=p_cell and ARTICUL=p_article and STATUS='ACTIVE'
     and BASE_UOM=(select max(BASE_UOM) from RRL_STOCK_UOM_CONVERSION where ARTICUL=p_article
      and INPUT_UOM=BASE_UOM and NUMERATOR=1 and DENOMINATOR=1);
   if n=1 and v_box>0 then return v_box;end if;
   raise_application_error(-20887,'PICK_CAPACITY_DYNAMIC_VOLUME_REQUIRED:'||p_article);
  end if;
  if n!=1 or v_box is null or v_box<=0 then raise_application_error(-20887,'PICK_CAPACITY_BOX_VOLUME_REQUIRED:'||p_article);end if;
  begin
   select NUMERATOR,DENOMINATOR into v_num,v_den from RRL_STOCK_UOM_CONVERSION
    where ARTICUL=p_article and INPUT_UOM='BOX' and POLICY_VERSION=(select max(POLICY_VERSION) from RRL_STOCK_UOM_CONVERSION where ARTICUL=p_article and INPUT_UOM='BOX');
  exception when no_data_found then raise_application_error(-20887,'PICK_CAPACITY_BOX_BASE_CONVERSION_REQUIRED:'||p_article);end;
  if v_num<=0 or v_den<=0 then raise_application_error(-20887,'PICK_CAPACITY_CONVERSION_INVALID');end if;
  return v_box*v_den/v_num;
 end;
 function remaining_base_quantity(p_cell varchar2,p_article varchar2,p_exclude_repl number default null) return number is
  v_max number;n number;v_occupied number:=0;v_arriving number:=0;v_unit number;v_scale number;v_base varchar2(20);v_remaining number;
  type volume_map is table of number index by varchar2(160);volumes volume_map;
  function volume_for(p_art varchar2) return number is
  begin
   if not volumes.exists(p_art) then volumes(p_art):=unit_volume(p_cell,p_art);end if;
   return volumes(p_art);
  end;
 begin
  select count(*),max(MAX_VOLUME) into n,v_max from RRL_PICK_FACE where CELL_CODE=p_cell and ACTIVE=1;
  if n=0 or v_max is null then return null;end if;
  if n!=1 or v_max<=0 then raise_application_error(-20887,'PICK_CAPACITY_VOLUME_AMBIGUOUS_OR_INVALID');end if;
  n:=0;
  for r in(select p.ARTICUL,s.REMAIN from RRL_REMAINS s join RRL_PALLETS p on p.UID_PALLET=s.UID_POLETA
   where s.CELL=p_cell and s.REMAIN>0 order by s.UID_POLETA fetch first 201 rows only) loop
   n:=n+1;if n>200 then raise_application_error(-20881,'PICK_CAPACITY_STOCK_BOUND');end if;
   v_occupied:=v_occupied+r.REMAIN*volume_for(r.ARTICUL);
  end loop;
  n:=0;
  for r in(select rt.ARTICUL,rt.QTY,
    nvl((select sum(m.BASE_QTY) from RRL_WAREHOUSE_TASK t join RRL_WAREHOUSE_TASK_STOCK_MOVE m on m.TASK_ID=t.TASK_ID
      where t.TASK_SOURCE='WAVE' and t.TASK_TYPE='REPLENISHMENT' and t.SOURCE_TASK_ID=rt.PICK_WAVE_REPLENISH_TASK_ID),0) ARRIVED
    from RRL_PICK_WAVE_REPLENISH_TASK rt where rt.TARGET_CELL_CODE=p_cell
     and rt.SOURCE_RESERVATION_ID is not null and rt.STATUS not in('DONE','CANCELLED','FAILED')
     and (p_exclude_repl is null or rt.PICK_WAVE_REPLENISH_TASK_ID!=p_exclude_repl)
    order by rt.PICK_WAVE_REPLENISH_TASK_ID fetch first 201 rows only) loop
   n:=n+1;if n>200 then raise_application_error(-20881,'PICK_CAPACITY_OPEN_ARRIVAL_BOUND');end if;
   v_arriving:=v_arriving+greatest(0,r.QTY-r.ARRIVED)*volume_for(r.ARTICUL);
  end loop;
  n:=0;
  for r in(select p.ARTICUL,
    case when t.QTY_MODE='PALLET' then ss.REMAIN else t.QTY*
     case when nvl(t.UNIT_CODE,ss.BASE_UOM)=ss.BASE_UOM then 1 else cv.NUMERATOR/cv.DENOMINATOR end end BASE_QTY
    from RRL_WAREHOUSE_TASK t join RRL_PALLETS p on p.UID_PALLET=nvl(t.UID_PALLET,t.SSCC)
    join RRL_REMAINS ss on ss.UID_POLETA=p.UID_PALLET and ss.CELL=t.FROM_CELL
    left join RRL_STOCK_UOM_CONVERSION cv on cv.ARTICUL=p.ARTICUL and cv.INPUT_UOM=t.UNIT_CODE
     and cv.POLICY_VERSION=(select max(POLICY_VERSION) from RRL_STOCK_UOM_CONVERSION where ARTICUL=p.ARTICUL and INPUT_UOM=t.UNIT_CODE)
    where t.TO_CELL=p_cell and t.FROM_CELL!=p_cell and t.STATUS in('PLANNED','ASSIGNED','IN_PROGRESS')
     and not(t.TASK_SOURCE='WAVE' and t.TASK_TYPE='REPLENISHMENT')
    order by t.TASK_ID fetch first 201 rows only) loop
   n:=n+1;if n>200 then raise_application_error(-20881,'PICK_CAPACITY_OTHER_ARRIVAL_BOUND');end if;
   if r.BASE_QTY is null or r.BASE_QTY<0 then raise_application_error(-20887,'PICK_CAPACITY_ARRIVAL_UOM_REQUIRED');end if;
   v_arriving:=v_arriving+r.BASE_QTY*volume_for(r.ARTICUL);
  end loop;
  v_unit:=volume_for(p_article);
  begin
   select BASE_UOM,BASE_SCALE into v_base,v_scale from RRL_STOCK_UOM_CONVERSION
    where ARTICUL=p_article and INPUT_UOM=BASE_UOM and NUMERATOR=1 and DENOMINATOR=1
     and POLICY_VERSION=(select max(POLICY_VERSION) from RRL_STOCK_UOM_CONVERSION where ARTICUL=p_article and INPUT_UOM=BASE_UOM and NUMERATOR=1 and DENOMINATOR=1);
  exception when no_data_found or too_many_rows then raise_application_error(-20887,'PICK_CAPACITY_BASE_POLICY_REQUIRED');end;
  if v_base in('PCE','PCS','PC','EA','ST','STK','ШТ','ШТУКА') then v_scale:=0;end if;
  v_remaining:=greatest(0,v_max-v_occupied-v_arriving)/v_unit;
  return floor(v_remaining*power(10,v_scale))/power(10,v_scale);
 end;
 procedure assert_arrival(p_repl number,p_base_quantity number) is rt RRL_PICK_WAVE_REPLENISH_TASK%rowtype;q number;
 begin
  select * into rt from RRL_PICK_WAVE_REPLENISH_TASK where PICK_WAVE_REPLENISH_TASK_ID=p_repl;
  RRL_STOCK_LOCK_API.assert_policy(RRL_STOCK_LOCK_API.resource_key('CONFIG','WAREHOUSE'),4);
  RRL_STOCK_LOCK_API.assert_policy(RRL_STOCK_LOCK_API.resource_key('CELL',rt.TARGET_CELL_CODE),6);
  q:=remaining_base_quantity(rt.TARGET_CELL_CODE,rt.ARTICUL,p_repl);
  if q is not null and p_base_quantity>q then raise_application_error(-20886,'PICK_CAPACITY_INSUFFICIENT: wait for free capacity');end if;
 end;
end;
/
