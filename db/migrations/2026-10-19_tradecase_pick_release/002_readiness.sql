create or replace package RRL_STOCK_WAVE_READY authid definer as
 function snapshot_json(p_wave number,p_actor varchar2 default null,p_write number default 1) return clob;
 procedure assert_released(p_wave number);
end;
/
create or replace package body RRL_STOCK_WAVE_READY as
 procedure assert_released(p_wave number) is n number;
 begin
  select count(*) into n from RRL_PICK_WAVE where PICK_WAVE_ID=p_wave and STATUS='LAUNCHED' and PICK_RELEASED_AT is not null;
  if n!=1 then raise_application_error(-20886,'WAVE_PICK_RELEASE_REQUIRED');end if;
 end;
 function snapshot_json(p_wave number,p_actor varchar2 default null,p_write number default 1) return clob is
  w RRL_PICK_WAVE%rowtype;j json_object_t:=json_object_t();tasks json_array_t:=json_array_t();
  repl json_array_t:=json_array_t();owned json_array_t;entry json_object_t;x json_object_t;
  missing number;covered number;needed number;v_cell varchar2(60);v_reason varchar2(100);v_base varchar2(20);
  v_ready boolean:=true;v_total number:=0;v_hard_count number:=0;
 begin
  select * into w from RRL_PICK_WAVE where PICK_WAVE_ID=p_wave;
  if w.STATUS!='LAUNCHED' or w.STATUS is null then v_ready:=false;end if;
  for rt in(select rt.*,wh.TASK_ID WH_TASK_ID,wh.STATUS WH_STATUS,wh.ASSIGNED_TO,wh.RESOURCE_ID
   from RRL_PICK_WAVE_REPLENISH_TASK rt left join RRL_WAREHOUSE_TASK wh
    on wh.TASK_SOURCE='WAVE' and wh.TASK_TYPE='REPLENISHMENT' and wh.SOURCE_DOC_ID=rt.PICK_WAVE_ID
    and wh.SOURCE_TASK_ID=rt.PICK_WAVE_REPLENISH_TASK_ID and wh.PARENT_TASK_ID is null
   where rt.PICK_WAVE_ID=p_wave and (rt.STATUS is null or rt.STATUS not in('DONE','CANCELLED'))
   order by rt.PICK_WAVE_REPLENISH_TASK_ID,wh.TASK_ID fetch first 201 rows only) loop
   if repl.get_size>=200 then raise_application_error(-20881,'WAVE_READY_REPL_BOUND');end if;
   x:=json_object_t();x.put('replenishment_id',rt.PICK_WAVE_REPLENISH_TASK_ID);x.put('status',rt.STATUS);
   x.put('article',rt.ARTICUL);x.put('quantity',RRL_STOCK_PLAN_HELPER.decimal_text(rt.QTY));
   x.put('demand_base',RRL_STOCK_PLAN_HELPER.decimal_text(rt.DEMAND_BASE_QTY));x.put('target',rt.TARGET_CELL_CODE);
   x.put('warehouse_task_id',rt.WH_TASK_ID);x.put('warehouse_task_status',rt.WH_STATUS);
   x.put('assigned_to',rt.ASSIGNED_TO);x.put('resource_id',rt.RESOURCE_ID);x.put('reason',rt.WAIT_REASON);
   x.put('source_reservation_id',rt.SOURCE_RESERVATION_ID);repl.append(x);
  end loop;
  for t in(select pt.*,wt.PICK_WAVE_TASK_ID from RRL_PICK_WAVE_TASK wt join RRL_PICK_TASK pt on pt.PICK_TASK_ID=wt.PICK_TASK_ID
   where wt.PICK_WAVE_ID=p_wave and wt.TASK_TYPE in('CASE_PICK','FULL_PALLET')
    and nvl(wt.STATUS,'?')!='CANCELLED' and nvl(pt.STATUS,'?')!='CANCELLED'
   order by wt.PICK_WAVE_TASK_ID fetch first 201 rows only) loop
   RRL_TRADE_PICK_CONTEXT.enter_pick_task(t.PICK_TASK_ID,p_actor,p_write);
   if tasks.get_size>=200 then raise_application_error(-20881,'WAVE_READY_TASK_BOUND');end if;
   v_total:=v_total+1;needed:=greatest(nvl(t.QTY,0)-nvl(t.FACT_QTY,0),0);
   v_cell:=t.SOURCE_CELL_CODE;covered:=0;v_base:=null;owned:=json_array_t();
   if t.TASK_TYPE='CASE_PICK' then
    select nvl(max(CELL_CODE),v_cell) into v_cell from RRL_CASE_PICK_LINE
     where PICK_TASK_ID=t.PICK_TASK_ID and PICK_WAVE_ID=p_wave and STATUS!='CANCELLED';
   end if;
   for sr in(select sr.*,s.REMAIN,s.STOCK_VERSION,s.HARD_RESERVED_BASE
    from RRL_STOCK_RESERVATION sr left join RRL_REMAINS s on s.UID_POLETA=sr.UID_PALLET and s.CELL=sr.CELL
    where sr.SOURCE_DOC_TYPE='PICK_WAVE' and sr.SOURCE_DOC_ID=p_wave and sr.SOURCE_LINE_ID=t.PICK_TASK_ID
     and sr.ARTICUL=t.ARTICUL and sr.RESERVATION_KIND='HARD' and sr.STATUS in('ACTIVE','ALLOCATED','PICKING')
     and not exists(select 1 from RRL_CASE_CARRIER_LOT h where h.LOT_UID=sr.UID_PALLET)
    order by sr.RESERVATION_ID fetch first 501 rows only) loop
    v_hard_count:=v_hard_count+1;if v_hard_count>500 then raise_application_error(-20881,'WAVE_READY_HARD_BOUND');end if;
    v_reason:=RRL_STOCK_ELIGIBILITY.reason(sr.UID_PALLET,sr.CELL,w.WARE_ID,sr.BASE_QTY,null,null,
      case when t.TASK_TYPE='CASE_PICK' then 'PICK' else 'ALLOCATE' end,sr.RESERVATION_ID,t.ARTICUL);
    if sr.CELL!=v_cell or v_cell is null then v_reason:='PICK_TARGET_RESERVATION_REQUIRED';end if;
    if v_base is not null and v_base!=sr.BASE_UOM then v_reason:='PICK_BASE_UOM_CONFLICT';end if;
    if v_reason is null then covered:=covered+sr.BASE_QTY;v_base:=sr.BASE_UOM;end if;
    x:=json_object_t();x.put('reservation_id',sr.RESERVATION_ID);x.put('uid',sr.UID_PALLET);
    x.put('cell',sr.CELL);x.put('article',sr.ARTICUL);x.put('quantity',RRL_STOCK_PLAN_HELPER.decimal_text(sr.BASE_QTY));
    x.put('base_uom',sr.BASE_UOM);x.put('stock_version',sr.STOCK_VERSION);x.put('physical',RRL_STOCK_PLAN_HELPER.decimal_text(sr.REMAIN));
    x.put('hard',RRL_STOCK_PLAN_HELPER.decimal_text(sr.HARD_RESERVED_BASE));x.put('reason',v_reason);owned.append(x);
   end loop;
   missing:=greatest(needed-covered,0);if missing>0 or t.QTY is null or t.QTY<=0 then v_ready:=false;end if;
   entry:=json_object_t();entry.put('pick_task_id',t.PICK_TASK_ID);entry.put('wave_task_id',t.PICK_WAVE_TASK_ID);
   entry.put('article',t.ARTICUL);entry.put('task_type',t.TASK_TYPE);entry.put('status',t.STATUS);entry.put('cell',v_cell);
   entry.put('required_base',RRL_STOCK_PLAN_HELPER.decimal_text(needed));entry.put('covered_base',RRL_STOCK_PLAN_HELPER.decimal_text(covered));
   entry.put('missing_base',RRL_STOCK_PLAN_HELPER.decimal_text(missing));entry.put('base_uom',v_base);entry.put('reservations',owned);tasks.append(entry);
  end loop;
  if v_total=0 then v_ready:=false;end if;
  for i in 0..repl.get_size-1 loop
   x:=treat(repl.get(i) as json_object_t);
   declare v_covered boolean:=false;v_cancel boolean:=false;t json_object_t;begin
    if x.get_number('source_reservation_id') is null and
      (x.get_number('warehouse_task_id') is null or x.get_string('warehouse_task_status') in('DONE','CANCELLED')) then
     for k in 0..tasks.get_size-1 loop
      t:=treat(tasks.get(k) as json_object_t);
      if t.get_string('article')=x.get_string('article') and t.get_string('cell')=x.get_string('target')
       and t.get_string('missing_base')='0' then v_covered:=true;end if;
     end loop;
     v_cancel:=v_covered;
    end if;
    x.put('can_cancel_before_release',v_cancel);repl.put(i,x,true);
    if not v_cancel then v_ready:=false;end if;
   end;
  end loop;
  j.put('wave_id',p_wave);j.put('warehouse',w.WARE_ID);j.put('status',w.STATUS);
  j.put('released_at',to_char(w.PICK_RELEASED_AT,'YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM'));
  j.put('released_by',w.PICK_RELEASED_BY);j.put('release_operation_id',w.PICK_RELEASE_OPERATION_ID);
  j.put('ready',v_ready);j.put('tasks',tasks);j.put('open_replenishments',repl);RRL_TRADE_PICK_CONTEXT.clear_line;return j.to_clob;
 exception when others then RRL_TRADE_PICK_CONTEXT.clear_line;raise;
 end;
end;
/
