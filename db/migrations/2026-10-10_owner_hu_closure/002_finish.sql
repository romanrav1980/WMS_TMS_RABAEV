create or replace package RRL_STOCK_WAVE_FINISH_CMD authid definer as
 function snapshot_json(p_wave number) return clob;
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
end;
/
create or replace package body RRL_STOCK_WAVE_FINISH_CMD as
 function snapshot_json(p_wave number) return clob is
  j json_object_t:=json_object_t();a json_array_t:=json_array_t();x json_object_t;
  v_status varchar2(40);v_kind varchar2(40);v_count number:=0;v_block number:=0;v_ship number;v_short number;v_pt number:=0;
  procedure item(p_kind varchar2,p_id varchar2,p_status varchar2,p_actor varchar2,p_reason varchar2,p_qty number default null) is
  begin
   v_count:=v_count+1;if v_count>1200 then raise_application_error(-20881,'WAVE_EXECUTION_SNAPSHOT_BOUND_1200');end if;
   x:=json_object_t();x.put('kind',p_kind);x.put('id',p_id);x.put('status',p_status);x.put('actor',p_actor);
   x.put('reason',p_reason);x.put('quantity',RRL_STOCK_PLAN_HELPER.decimal_text(p_qty));a.append(x);
   if p_reason is not null then v_block:=v_block+1;end if;
  end;
 begin
  select STATUS,WAVE_KIND into v_status,v_kind from RRL_PICK_WAVE where PICK_WAVE_ID=p_wave;
  for pt in(select pt.* from RRL_PICK_WAVE_TASK wt join RRL_PICK_TASK pt on pt.PICK_TASK_ID=wt.PICK_TASK_ID
   where wt.PICK_WAVE_ID=p_wave order by pt.PICK_TASK_ID) loop
   v_pt:=v_pt+1;if v_pt>200 then raise_application_error(-20881,'WAVE_EXECUTION_TASK_BOUND_200');end if;
   v_ship:=0;
   if nvl(pt.FACT_QTY,0)>0 then
    select count(*) into v_ship from RRL_CUSTOMER_ORDER_FULFILLMENT ff
     where ff.CUSTOMER_ORDER_ID=pt.CUSTOMER_ORDER_ID and ff.STATUS='SHIPPED' and ff.SHIPPED_OPERATION_ID is not null
      and (exists(select 1 from RRL_WAREHOUSE_TASK wh join RRL_PICK_WAVE_TASK wt on wt.PICK_WAVE_TASK_ID=wh.SOURCE_TASK_ID
        where wh.TASK_ID=ff.PICKED_WAREHOUSE_TASK_ID and wh.TASK_SOURCE='WAVE' and wh.SOURCE_DOC_ID=p_wave
         and wt.PICK_TASK_ID=pt.PICK_TASK_ID and wh.STATUS='DONE')
       or exists(select 1 from RRL_CASE_PICK_LINE cl join RRL_CASE_PICK_TASK ct on ct.CASE_PICK_TASK_ID=cl.CASE_PICK_TASK_ID
        where cl.PICK_TASK_ID=pt.PICK_TASK_ID and ct.PICK_WAVE_ID=p_wave and ff.PICKED_CASE_TASK_ID=ct.CASE_PICK_TASK_ID
         and ct.STATUS='SHIPPED' and cl.PICKED_QTY>0));
   end if;
   select nvl(sum(greatest(l.PLANNED_QTY-l.PICKED_QTY,0)),0) into v_short from RRL_CASE_PICK_LINE l
    where l.PICK_WAVE_ID=p_wave and l.PICK_TASK_ID=pt.PICK_TASK_ID and l.STATUS='SHORT_PICKED'
     and exists(select 1 from RRL_CASE_PICK_SHORT sh where sh.CASE_PICK_LINE_ID=l.CASE_PICK_LINE_ID
      and sh.STATUS='ACCEPTED' and sh.SHORT_QTY=l.PLANNED_QTY-l.PICKED_QTY and sh.APPROVED_BY is not null);
   item('PICK_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(pt.PICK_TASK_ID),pt.STATUS,pt.ASSIGNED_TO,
    case when pt.STATUS not in('DONE','CANCELLED') then 'PICKING_PENDING'
     when pt.STATUS='CANCELLED' then 'CANCELLED_DEMAND_REQUIRES_RECONCILIATION'
     when nvl(pt.FACT_QTY,0)+v_short!=pt.QTY then 'FACT_OR_APPROVED_SHORT_INCOMPLETE'
     when nvl(pt.FACT_QTY,0)>0 and v_ship=0 then 'PHYSICAL_FULFILLMENT_OR_SHIPPING_PENDING' end,pt.FACT_QTY);
  end loop;
  for rt in(select * from RRL_PICK_WAVE_REPLENISH_TASK where PICK_WAVE_ID=p_wave order by PICK_WAVE_REPLENISH_TASK_ID) loop
   item('REPLENISHMENT',RRL_STOCK_PLAN_HELPER.decimal_text(rt.PICK_WAVE_REPLENISH_TASK_ID),rt.STATUS,null,
    case when rt.STATUS not in('DONE','CANCELLED') then 'REPLENISHMENT_PENDING' end,case when rt.STATUS='DONE' then rt.QTY end);
  end loop;
  for wh in(select * from RRL_WAREHOUSE_TASK where TASK_SOURCE='WAVE' and SOURCE_DOC_ID=p_wave order by TASK_ID) loop
   item('WAREHOUSE_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(wh.TASK_ID),wh.STATUS,wh.ASSIGNED_TO,
    case when wh.STATUS not in('DONE','CANCELLED') then 'PHYSICAL_TASK_PENDING' end,wh.FACT_QTY);
  end loop;
  for ct in(select * from RRL_CASE_PICK_TASK where PICK_WAVE_ID=p_wave order by CASE_PICK_TASK_ID) loop
   item('CASE',RRL_STOCK_PLAN_HELPER.decimal_text(ct.CASE_PICK_TASK_ID),ct.STATUS,ct.ASSIGNED_TO,
    case when nvl(ct.PICKED_QTY,0)>0 and ct.STATUS!='SHIPPED' then 'CASE_CONTROL_OR_SHIPPING_PENDING'
     when nvl(ct.PICKED_QTY,0)=0 and ct.STATUS not in('CONTROLLED','READY_TO_SHIP','SHIPPED','CANCELLED') then 'EMPTY_CASE_DECISION_PENDING' end,ct.PICKED_QTY);
  end loop;
  for sr in(select * from RRL_STOCK_RESERVATION where SOURCE_DOC_TYPE='PICK_WAVE' and SOURCE_DOC_ID=p_wave
   and RESERVATION_KIND='HARD' and STATUS in('ACTIVE','ALLOCATED','PICKING') and BASE_QTY>0 order by RESERVATION_ID) loop
   item('HARD',RRL_STOCK_PLAN_HELPER.decimal_text(sr.RESERVATION_ID),sr.STATUS,null,'ACTIVE_WAVE_HARD_REMAINS',sr.BASE_QTY);
  end loop;
  j.put('wave_id',p_wave);j.put('status',v_status);j.put('kind',v_kind);j.put('items',a);j.put('blocking_count',v_block);
  j.put('ready',v_count>0 and v_block=0 and (v_pt>0 or v_kind='REPLENISHMENT') and v_status='LAUNCHED');
  j.put('completed',v_status='DONE');return j.to_clob;
 end;
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob) is
  d json_object_t:=json_object_t.parse(p_request);v_wave number:=d.get_object('source').get_number('wave_id');
  f json_array_t:=json_array_t();r json_array_t:=json_array_t();v json_object_t:=json_object_t();a json_array_t;x json_object_t;
  s clob;v_kind varchar2(40);v_id varchar2(200);v_ff number:=0;
 begin
  s:=snapshot_json(v_wave);a:=json_object_t.parse(s).get_array('items');
  RRL_STOCK_PLAN_HELPER.fence(f,'RELEASE','STOCK');RRL_STOCK_PLAN_HELPER.fence(f,'CONFIG','WAREHOUSE');
  RRL_STOCK_PLAN_HELPER.anchor(r,10,'OP',p_operation);
  RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','STOCK.OUTBOX:'||rawtohex(sys.dbms_crypto.hash(utl_i18n.string_to_raw(p_operation,'AL32UTF8'),sys.dbms_crypto.hash_sh256)));
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_PICK_WAVE',RRL_STOCK_PLAN_HELPER.decimal_text(v_wave));
  for i in 0..a.get_size-1 loop
   x:=treat(a.get(i) as json_object_t);v_kind:=x.get_string('kind');v_id:=x.get_string('id');
   RRL_STOCK_PLAN_HELPER.row_key(r,case v_kind when 'PICK_TASK' then 'RRL_PICK_TASK' when 'REPLENISHMENT' then 'RRL_PICK_WAVE_REPLENISH_TASK'
    when 'WAREHOUSE_TASK' then 'RRL_WAREHOUSE_TASK' when 'CASE' then 'RRL_CASE_PICK_TASK' when 'HARD' then 'RRL_STOCK_RESERVATION' end,v_id);
  end loop;
  for ff in(select ff.FULFILLMENT_ID from RRL_CUSTOMER_ORDER_FULFILLMENT ff where
   exists(select 1 from RRL_CASE_PICK_TASK ct where ct.CASE_PICK_TASK_ID=ff.PICKED_CASE_TASK_ID and ct.PICK_WAVE_ID=v_wave)
   or exists(select 1 from RRL_WAREHOUSE_TASK wh where wh.TASK_ID=ff.PICKED_WAREHOUSE_TASK_ID and wh.TASK_SOURCE='WAVE' and wh.SOURCE_DOC_ID=v_wave)
   order by ff.FULFILLMENT_ID fetch first 201 rows only) loop
   v_ff:=v_ff+1;if v_ff>200 then raise_application_error(-20881,'WAVE_FULFILLMENT_CLOSURE_BOUND_200');end if;
   RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_CUSTOMER_ORDER_FULFILLMENT',RRL_STOCK_PLAN_HELPER.decimal_text(ff.FULFILLMENT_ID));
  end loop;
  v.put('wave_id',v_wave);v.put('signature',rawtohex(sys.dbms_crypto.hash(s,sys.dbms_crypto.hash_sh256)));
  p_domain:=v.to_clob;p_policies:=f.to_clob;p_resources:=r.to_clob;
 end;
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob) is
  d json_object_t:=json_object_t.parse(p_request);v json_object_t;j json_object_t;v_plan clob;s clob;
  v_op varchar2(100):=d.get_string('operation_id');v_wave number;
 begin
  if RRL_HAS_WRIGHT(p_actor,'pick_wave_launch')!=1 then raise_application_error(-20882,'WAVE_FINISH_FORBIDDEN');end if;
  select RESOLVED_PLAN_JSON into v_plan from RRL_STOCK_OPERATION where OPERATION_ID=v_op;
  v:=json_object_t.parse(v_plan).get_object('domain');v_wave:=v.get_number('wave_id');s:=snapshot_json(v_wave);
  if rawtohex(sys.dbms_crypto.hash(s,sys.dbms_crypto.hash_sh256))!=v.get_string('signature') then
   raise_application_error(-20890,'CLOSURE_CHANGED: wave execution');end if;
  j:=json_object_t.parse(s);
  if not j.get_boolean('ready') then raise_application_error(-20886,'WAVE_EXECUTION_OR_SHIPPING_PENDING');end if;
  update RRL_PICK_WAVE set STATUS='DONE',UPDATED_AT=sysdate,UPDATED_BY=p_actor where PICK_WAVE_ID=v_wave and STATUS='LAUNCHED';
  if sql%rowcount!=1 then raise_application_error(-20890,'CLOSURE_CHANGED: wave finish');end if;
  j.put('operation_id',v_op);j.put('status','DONE');j.put('completed',true);j.put('ready',false);p_result:=j.to_clob;
 end;
end;
/
