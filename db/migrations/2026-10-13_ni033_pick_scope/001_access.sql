create or replace package body RRL_WAVE_EXEC_ACCESS as

 procedure assert_scope(p_wave number,p_actor varchar2,p_permission varchar2)is

  ware number;actor_ware number;grp varchar2(100);

 begin

  if p_permission not in('pick_wave_view','pick_wave_launch','pick_wave_cancel') or p_permission is null then

   raise_application_error(-20882,'WAVE_CURRENT_PERMISSION_REQUIRED');end if;

  begin select WARE_ID into ware from RRL_PICK_WAVE where PICK_WAVE_ID=p_wave;

  exception when no_data_found then raise_application_error(-20886,'WAVE_IDENTITY_MISSING');end;

  begin select WARE_ID,USER_GROUP into actor_ware,grp from RUSERS where ID=p_actor and nvl(DELETED,0)=0;

  exception when no_data_found then raise_application_error(-20882,'WAVE_ACTIVE_ACTOR_REQUIRED');end;

  if nvl(upper(trim(grp)),'-')!='GLOBAL_ADMIN' and (ware is null or actor_ware is null or actor_ware!=ware)then

   raise_application_error(-20882,'WAVE_CURRENT_WARE_FORBIDDEN');end if;

  if RRL_HAS_WRIGHT(p_actor,p_permission)!=1 then raise_application_error(-20882,'WAVE_CURRENT_ACTION_FORBIDDEN');end if;

 end;

 procedure assert_command(p_request clob,p_actor varchar2)is

  d json_object_t:=json_object_t.parse(p_request);wave number;v_disposition varchar2(100);

 begin

  if d.get_string('command_type')not in('WAVE_EXECUTION_FINISH','WAVE_PICK_RELEASE')then return;end if;

  wave:=d.get_object('source').get_number('wave_id');

  assert_scope(wave,p_actor,'pick_wave_launch');
  if d.get_string('command_type')='WAVE_PICK_RELEASE'then return;end if;

  v_disposition:=d.get_object('metadata').get_string('disposition');

  if v_disposition is not null then

   if v_disposition not in('RETURNED_TO_PLANNING','PARTIAL_SHIPPED_RETURNED')then raise_application_error(-20881,'WAVE_DISPOSITION_UNSUPPORTED');end if;

   assert_scope(wave,p_actor,'pick_wave_cancel');

   if trim(d.get_object('metadata').get_string('reason')) is null then

    raise_application_error(-20881,'WAVE_DEFER_REASON_REQUIRED');end if;

  end if;

 end;

 function decision_snapshot(p_wave number,p_allow_done number)return clob is

  j json_object_t:=json_object_t();demands json_array_t:=json_array_t();x json_object_t;

  n number;v_count number:=0;ware number;st varchar2(40);reason varchar2(100);blocked number:=0;

  procedure deny(p_reason varchar2)is begin if reason is null then reason:=p_reason;end if;blocked:=blocked+1;end;

 begin

  select WARE_ID,STATUS into ware,st from RRL_PICK_WAVE where PICK_WAVE_ID=p_wave;

  if st!='LAUNCHED'then deny('WAVE_DEFER_REQUIRES_LAUNCHED');end if;

  select count(*)into n from RRL_PICK_WAVE_TASK wt join RRL_PICK_TASK pt on pt.PICK_TASK_ID=wt.PICK_TASK_ID

   where wt.PICK_WAVE_ID=p_wave;

  if n=0 or n>200 then deny('WAVE_DEFER_TASK_BOUND_1_200');end if;

  select count(*)into n from RRL_PICK_WAVE_TASK wt join RRL_PICK_TASK pt on pt.PICK_TASK_ID=wt.PICK_TASK_ID

   where wt.PICK_WAVE_ID=p_wave and (pt.STATUS is null or pt.STATUS not in('CANCELLED','DONE')or(p_allow_done=0 and pt.STATUS='DONE'));

  if n>0 then deny('WAVE_DEFER_PICKING_NOT_CANCELLED');end if;

  select count(*)into n from RRL_PICK_WAVE_TASK wt join RRL_PICK_TASK pt on pt.PICK_TASK_ID=wt.PICK_TASK_ID

   where wt.PICK_WAVE_ID=p_wave and pt.STATUS='CANCELLED';

  if n=0 then deny('WAVE_DEFER_CANCELLED_DEMAND_REQUIRED');end if;

  if p_allow_done=1 then

   select count(*)into n from RRL_PICK_WAVE_TASK wt join RRL_PICK_TASK pt on pt.PICK_TASK_ID=wt.PICK_TASK_ID

    where wt.PICK_WAVE_ID=p_wave and pt.STATUS='DONE';

   if n=0 then deny('WAVE_MIXED_COMPLETED_TASK_REQUIRED');end if;

  end if;

  select count(*)into n from RRL_CASE_PICK_TASK ct where ct.PICK_WAVE_ID=p_wave

   and (ct.STATUS is null or ct.STATUS not in('CANCELLED','SHIPPED')or(p_allow_done=0 and ct.STATUS='SHIPPED')

    or(ct.STATUS='CANCELLED'and(ct.SHIPPED_OPERATION is not null

     or exists(select 1 from RRL_CASE_CARRIER_LOT h where h.CASE_PICK_TASK_ID=ct.CASE_PICK_TASK_ID))));

  if n>0 then deny('WAVE_DEFER_CASE_NOT_RETURNED');end if;

  select count(*)into n from RRL_TARE_BOOK b where b.STATUS='HELD'and b.PLACE_KIND='CASE'

   and exists(select 1 from RRL_CASE_PICK_TASK ct where ct.PICK_WAVE_ID=p_wave and to_char(ct.CASE_PICK_TASK_ID,'TM9')=b.PLACE_ID);

  if n>0 then deny('WAVE_DEFER_TARE_BOOK_REMAINS');end if;

  select count(*)into n from RRL_WAREHOUSE_TASK where TASK_SOURCE='WAVE'and SOURCE_DOC_ID=p_wave

   and (STATUS is null or STATUS not in('DONE','CANCELLED') or (STATUS='DONE'and nvl(TASK_TYPE,'-')!='REPLENISHMENT'

    and not(p_allow_done=1 and TASK_TYPE='PICKING_MOVE'and exists(select 1 from RRL_PICK_WAVE_TASK wt join RRL_PICK_TASK pt

     on pt.PICK_TASK_ID=wt.PICK_TASK_ID where wt.PICK_WAVE_ID=p_wave and wt.PICK_WAVE_TASK_ID=RRL_WAREHOUSE_TASK.SOURCE_TASK_ID and pt.STATUS='DONE'))));

  if n>0 then deny('WAVE_DEFER_PHYSICAL_TASK_PENDING');end if;

  select count(*)into n from RRL_PICK_WAVE_REPLENISH_TASK where PICK_WAVE_ID=p_wave

   and (STATUS is null or STATUS not in('DONE','CANCELLED'));

  if n>0 then deny('WAVE_DEFER_REPLENISHMENT_PENDING');end if;

  select count(*)into n from RRL_STOCK_RESERVATION where SOURCE_DOC_TYPE='PICK_WAVE'and SOURCE_DOC_ID=p_wave

   and STATUS in('ACTIVE','ALLOCATED','PICKING')and RESERVATION_KIND='HARD'and BASE_QTY>0;

  if n>0 then deny('WAVE_DEFER_ACTIVE_HARD_REMAINS');end if;

  for r in(select pl.PICK_PLAN_LINE_ID,pl.PICK_PLAN_ID,pl.REQUESTED_QTY,cr.CUSTOMER_ORDER_ROW_ID,

    cr.CUSTOMER_ORDER_ID,cr.ARTICUL,cr.ORDER_QTY,cr.UNIT_CODE,cr.STATUS ROW_STATUS,co.STATUS ORDER_STATUS,

    nvl(cr.WARE_ID,co.WARE_ID)ROW_WARE

    from RRL_PICK_WAVE_ORDER wo join RRL_PICK_PLAN_LINE pl on pl.PICK_PLAN_ID=wo.PICK_PLAN_ID

    join RRL_CUSTOMER_ORDER_ROW cr on cr.CUSTOMER_ORDER_ROW_ID=pl.CUSTOMER_ORDER_ROW_ID

    join RRL_CUSTOMER_ORDER co on co.CUSTOMER_ORDER_ID=cr.CUSTOMER_ORDER_ID

    where wo.PICK_WAVE_ID=p_wave and exists(select 1 from RRL_PICK_TASK pt where pt.PICK_PLAN_LINE_ID=pl.PICK_PLAN_LINE_ID and pt.STATUS='CANCELLED')

    order by pl.PICK_PLAN_LINE_ID fetch first 201 rows only)loop

   v_count:=v_count+1;if v_count>200 then raise_application_error(-20881,'WAVE_DEFER_DEMAND_BOUND_200');end if;

   if r.ROW_WARE!=ware or r.ROW_WARE is null or r.ORDER_QTY<=0 or r.ORDER_QTY is null

    or r.ROW_STATUS not in('OPEN','PLANNED_FULL','PLANNED_PARTIAL','NO_STOCK') or r.ROW_STATUS is null

    or r.ORDER_STATUS not in('IMPORTED','OPEN','PLANNED_FULL','PLANNED_PARTIAL','NO_STOCK')or r.ORDER_STATUS is null

    then deny('WAVE_DEFER_ORIGINAL_DEMAND_NOT_OPEN');end if;

   x:=json_object_t();x.put('pick_plan_id',r.PICK_PLAN_ID);x.put('pick_plan_line_id',r.PICK_PLAN_LINE_ID);

   x.put('order_id',r.CUSTOMER_ORDER_ID);x.put('order_line_id',r.CUSTOMER_ORDER_ROW_ID);

   x.put('article',r.ARTICUL);x.put('order_quantity',RRL_STOCK_PLAN_HELPER.decimal_text(r.ORDER_QTY));x.put('unit',r.UNIT_CODE);

   x.put('current_planning',json_object_t.parse(RRL_STOCK_POOL_READ.line_snapshot_json(r.CUSTOMER_ORDER_ROW_ID)));x.put('row_status',r.ROW_STATUS);x.put('order_status',r.ORDER_STATUS);x.put('warehouse',r.ROW_WARE);demands.append(x);

  end loop;

  select count(*)into n from RRL_PICK_WAVE_ORDER wo join RRL_PICK_PLAN_LINE pl on pl.PICK_PLAN_ID=wo.PICK_PLAN_ID where wo.PICK_WAVE_ID=p_wave

   and exists(select 1 from RRL_PICK_TASK pt where pt.PICK_PLAN_LINE_ID=pl.PICK_PLAN_LINE_ID and pt.STATUS='CANCELLED');

  if v_count=0 or v_count!=n then deny('WAVE_DEFER_ORIGINAL_DEMAND_MISSING');end if;

  select count(*)into n from RRL_CUSTOMER_ORDER_FULFILLMENT ff where exists(

   select 1 from RRL_PICK_WAVE_ORDER wo where wo.PICK_WAVE_ID=p_wave and wo.CUSTOMER_ORDER_ID=ff.CUSTOMER_ORDER_ID)

   and (ff.SHIPPED_OPERATION_ID is not null or ff.PICKED_CASE_TASK_ID is not null or ff.PICKED_WAREHOUSE_TASK_ID is not null or nvl(ff.FACT_QTY,0)>0)

   and (p_allow_done=0 or exists(select 1 from RRL_CASE_PICK_TASK ct where ct.PICK_WAVE_ID=p_wave

     and ct.STATUS='CANCELLED'and ct.CASE_PICK_TASK_ID=ff.PICKED_CASE_TASK_ID));

  if n>0 then deny('WAVE_DEFER_CURRENT_FULFILLMENT_REQUIRES_RECONCILIATION');end if;

  j.put('wave_id',p_wave);j.put('eligible',blocked=0);j.put('blocking_count',blocked);j.put('reason',reason);

  j.put('demands',demands);j.put('quantity_semantics','ORIGINAL_ORDER_DEMAND_NOT_DELIVERED');

  return j.to_clob;

 end;

 function deferred_snapshot_json(p_wave number)return clob is begin return decision_snapshot(p_wave,0);end;

 function mixed_snapshot_json(p_wave number)return clob is begin return decision_snapshot(p_wave,1);end;



end;


/
