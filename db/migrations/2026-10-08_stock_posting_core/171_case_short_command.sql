-- Approval of measured shortage; physical quantity remains unchanged.
create or replace package RRL_STOCK_CASE_SHORT_CMD authid definer
 accessible by(package RRL_STOCK_POSTING_API) as
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
end;
/
create or replace package body RRL_STOCK_CASE_SHORT_CMD as
 function unused_reservations(p_wave number,p_task number) return json_array_t is
  a json_array_t:=json_array_t();x json_object_t;
 begin
  for z in(select RESERVATION_ID,RESERVATION_VERSION,UID_PALLET,CELL,ARTICUL,BASE_QTY,BASE_UOM from RRL_STOCK_RESERVATION sr
   where sr.SOURCE_DOC_TYPE='PICK_WAVE' and sr.SOURCE_DOC_ID=p_wave and sr.SOURCE_LINE_ID=p_task
    and sr.RESERVATION_KIND='HARD' and sr.STATUS in('ACTIVE','ALLOCATED','PICKING')
    and not exists(select 1 from RRL_CASE_CARRIER_LOT c where c.LOT_UID=sr.UID_PALLET)
   order by RESERVATION_ID) loop
   if a.get_size>=200 then raise_application_error(-20881,'CASE_SHORT_RESERVATION_BOUND');end if;
   x:=json_object_t();x.put('id',z.RESERVATION_ID);x.put('version',z.RESERVATION_VERSION);x.put('uid',z.UID_PALLET);
   x.put('cell',z.CELL);x.put('article',z.ARTICUL);x.put('qty',RRL_STOCK_PLAN_HELPER.decimal_text(z.BASE_QTY));x.put('base',z.BASE_UOM);a.append(x);
  end loop;
  return a;
 end;
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob) is
  d json_object_t:=json_object_t.parse(p_request);v json_object_t:=json_object_t();x json_object_t;
  f json_array_t:=json_array_t();r json_array_t:=json_array_t();a json_array_t;carrier json_array_t;
  sh RRL_CASE_PICK_SHORT%rowtype;l RRL_CASE_PICK_LINE%rowtype;ct RRL_CASE_PICK_TASK%rowtype;inventory_id number;
 begin
  declare
 v_json_sql_1_1 number:=d.get_object('source').get_number('short_id');
begin
select * into sh from RRL_CASE_PICK_SHORT where CASE_PICK_SHORT_ID=v_json_sql_1_1;
end;
  select * into l from RRL_CASE_PICK_LINE where CASE_PICK_LINE_ID=sh.CASE_PICK_LINE_ID;
  select * into ct from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=l.CASE_PICK_TASK_ID;
  RRL_STOCK_PLAN_HELPER.fence(f,'RELEASE','STOCK');RRL_STOCK_PLAN_HELPER.fence(f,'CONFIG','WAREHOUSE');
  RRL_STOCK_PLAN_HELPER.anchor(r,10,'OP',p_operation);
  RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','STOCK.OUTBOX:'||rawtohex(sys.dbms_crypto.hash(utl_i18n.string_to_raw(p_operation,'AL32UTF8'),sys.dbms_crypto.hash_sh256)));
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_PICK_WAVE',RRL_STOCK_PLAN_HELPER.decimal_text(l.PICK_WAVE_ID));
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_CASE_PICK_SHORT',RRL_STOCK_PLAN_HELPER.decimal_text(sh.CASE_PICK_SHORT_ID));
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_CASE_PICK_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(ct.CASE_PICK_TASK_ID));
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_CASE_PICK_LINE',RRL_STOCK_PLAN_HELPER.decimal_text(l.CASE_PICK_LINE_ID));
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_PICK_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(l.PICK_TASK_ID));
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_PICK_WAVE_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(l.PICK_WAVE_TASK_ID));
  RRL_STOCK_PLAN_HELPER.anchor(r,30,'HU','CASE:'||ct.CASE_PICK_TASK_ID);
  a:=unused_reservations(l.PICK_WAVE_ID,l.PICK_TASK_ID);
  for i in 0..a.get_size-1 loop
   x:=treat(a.get(i) as json_object_t);
   RRL_STOCK_PLAN_HELPER.stock_closure(f,r,x.get_string('uid'),x.get_string('article'),x.get_string('cell'),null);
  end loop;
  carrier:=json_array_t.parse(RRL_STOCK_CASE_PICK_CMD.carrier_rows(ct.CASE_PICK_TASK_ID));
  for i in 0..carrier.get_size-1 loop
   x:=treat(carrier.get(i) as json_object_t);
   RRL_STOCK_PLAN_HELPER.stock_closure(f,r,x.get_string('uid'),x.get_string('article'),x.get_string('cell'),null);
  end loop;
  select RRL_INVENTORY_TASK_SQ.nextval into inventory_id from dual;
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_INVENTORY_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(inventory_id));
  v.put('short_id',sh.CASE_PICK_SHORT_ID);v.put('line_id',l.CASE_PICK_LINE_ID);v.put('task_id',ct.CASE_PICK_TASK_ID);
  v.put('pick_task',l.PICK_TASK_ID);v.put('wave_task',l.PICK_WAVE_TASK_ID);v.put('wave',l.PICK_WAVE_ID);
  v.put('warehouse',ct.WARE_ID);v.put('article',l.ARTICUL);v.put('cell',l.CELL_CODE);v.put('version',ct.CONTENT_VERSION);
  v.put('planned',RRL_STOCK_PLAN_HELPER.decimal_text(l.PLANNED_QTY));v.put('picked',RRL_STOCK_PLAN_HELPER.decimal_text(l.PICKED_QTY));
  v.put('short',RRL_STOCK_PLAN_HELPER.decimal_text(sh.SHORT_QTY));v.put('inventory_id',inventory_id);
  v.put('reservations',a);v.put('carrier',carrier);
  p_policies:=f.to_clob;p_resources:=r.to_clob;p_domain:=v.to_clob;
 end;
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob) is
  d json_object_t:=json_object_t.parse(p_request);v json_object_t;x json_object_t;j json_object_t:=json_object_t();
  a json_array_t;carrier json_array_t;sh RRL_CASE_PICK_SHORT%rowtype;l RRL_CASE_PICK_LINE%rowtype;ct RRL_CASE_PICK_TASK%rowtype;
  sr RRL_STOCK_RESERVATION%rowtype;plan clob;op varchar2(100);short_id number;line_id number;task_id number;wave_id number;
  inv_id number;pt_id number;wt_id number;ware number;ver number;sid number;auto_inv number:=1;resource_type varchar2(100):='INVENTORY';
  wave_status varchar2(40);pt_status varchar2(40);wt_status varchar2(40);total number:=0;held number:=0;qty number;article varchar2(160);v_cell varchar2(60);reason varchar2(1000);
 begin
  if RRL_HAS_WRIGHT(p_actor,'case_pick_short_approve')!=1 then raise_application_error(-20882,'CASE_SHORT_APPROVE_FORBIDDEN');end if;
  op:=d.get_string('operation_id');select RESOLVED_PLAN_JSON into plan from RRL_STOCK_OPERATION where OPERATION_ID=op;v:=json_object_t.parse(plan).get_object('domain');
  short_id:=v.get_number('short_id');line_id:=v.get_number('line_id');task_id:=v.get_number('task_id');wave_id:=v.get_number('wave');
  pt_id:=v.get_number('pick_task');wt_id:=v.get_number('wave_task');ware:=v.get_number('warehouse');article:=v.get_string('article');v_cell:=v.get_string('cell');
  select STATUS into wave_status from RRL_PICK_WAVE where PICK_WAVE_ID=wave_id for update;
  select * into ct from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=task_id for update;
  select * into l from RRL_CASE_PICK_LINE where CASE_PICK_LINE_ID=line_id for update;
  select * into sh from RRL_CASE_PICK_SHORT where CASE_PICK_SHORT_ID=short_id for update;
  select STATUS into pt_status from RRL_PICK_TASK where PICK_TASK_ID=pt_id for update;
  select STATUS into wt_status from RRL_PICK_WAVE_TASK where PICK_WAVE_TASK_ID=wt_id and PICK_TASK_ID=pt_id and PICK_WAVE_ID=wave_id for update;
  if ct.CONTENT_VERSION!=v.get_number('version') or ct.WARE_ID!=ware or l.CASE_PICK_TASK_ID!=task_id
   or l.PICK_TASK_ID!=pt_id or l.PICK_WAVE_ID!=wave_id or l.PICK_WAVE_TASK_ID!=wt_id or l.ARTICUL!=article or l.CELL_CODE!=v_cell
   or RRL_STOCK_PLAN_HELPER.decimal_text(l.PLANNED_QTY)!=v.get_string('planned')
   or RRL_STOCK_PLAN_HELPER.decimal_text(l.PICKED_QTY)!=v.get_string('picked')
   or RRL_STOCK_PLAN_HELPER.decimal_text(sh.SHORT_QTY)!=v.get_string('short') then raise_application_error(-20890,'CLOSURE_CHANGED: case shortage');end if;
  if wave_status is null or wave_status in('CANCELLED','CLOSED','COMPLETED','SHIPPED','DRAFT','PREVIEW')
   or ct.STATUS is null or ct.STATUS not in('IN_PROGRESS','PARTIAL','WAIT_REPLENISHMENT')
   or sh.STATUS is null or sh.STATUS not in('CREATED','PENDING_APPROVAL')
   or l.STATUS is null or l.STATUS!='PARTIAL' or pt_status in('DONE','CANCELLED','FAILED') or wt_status in('DONE','CANCELLED','FAILED')
   or sh.CASE_PICK_TASK_ID!=task_id or sh.CASE_PICK_LINE_ID!=line_id or sh.PICK_WAVE_ID!=wave_id
   or sh.PICKED_QTY!=l.PICKED_QTY or sh.PLANNED_QTY!=l.PLANNED_QTY or sh.SHORT_QTY<=0
   or sh.PICKED_QTY+sh.SHORT_QTY!=sh.PLANNED_QTY then raise_application_error(-20886,'CASE_SHORT_APPROVAL_STATE_CONFLICT');end if;
  a:=v.get_array('reservations');carrier:=v.get_array('carrier');
  if dbms_lob.compare(unused_reservations(wave_id,pt_id).to_clob,a.to_clob)!=0
   or dbms_lob.compare(RRL_STOCK_CASE_PICK_CMD.carrier_rows(task_id),carrier.to_clob)!=0 then raise_application_error(-20890,'CLOSURE_CHANGED: case shortage composition');end if;
  for i in 0..carrier.get_size-1 loop
   x:=treat(carrier.get(i) as json_object_t);
   if x.get_number('case_line')=line_id then total:=total+RRL_STOCK_MATH.quantity(x.get_string('quantity'));end if;
  end loop;
  if total!=l.PICKED_QTY then raise_application_error(-20887,'CASE_SHORT_PHYSICAL_FACT_CONFLICT');end if;
  for i in 0..a.get_size-1 loop
   x:=treat(a.get(i) as json_object_t);held:=held+RRL_STOCK_MATH.quantity(x.get_string('qty'));
  end loop;
  if held>sh.SHORT_QTY then raise_application_error(-20869,'CASE_SHORT_UNUSED_RESERVE_EXCEEDS_REMAINDER');end if;
  for i in 0..a.get_size-1 loop
   x:=treat(a.get(i) as json_object_t);sid:=x.get_number('id');
   select * into sr from RRL_STOCK_RESERVATION where RESERVATION_ID=sid for update;
   if sr.RESERVATION_VERSION!=x.get_number('version') or sr.ARTICUL!=article then raise_application_error(-20890,'CLOSURE_CHANGED: case shortage reservation');end if;
   select max(POLICY_VERSION) into ver from RRL_STOCK_UOM_CONVERSION where ARTICUL=sr.ARTICUL and INPUT_UOM=sr.BASE_UOM and BASE_UOM=sr.BASE_UOM and NUMERATOR=1 and DENOMINATOR=1;
   if ver is null then raise_application_error(-20868,'CASE_SHORT_BASE_POLICY_REQUIRED');end if;
   RRL_STOCK_UNIT_CORE.release_units(sid,sr.BASE_QTY,null,0);
   RRL_STOCK_RESERVE_CORE.release_hard(sid,sr.BASE_QTY,ver,'PICK_WAVE',wave_id,p_actor);
  end loop;
  begin
   select AUTO_INVENTORY_ON_SHORT,INVENTORY_RESOURCE_TYPE into auto_inv,resource_type from RRL_CASE_PICK_SETTING where WARE_ID=ware and ACTIVE=1;
  exception when no_data_found then null;end;
  if nvl(auto_inv,1)!=0 then
   inv_id:=v.get_number('inventory_id');
   insert into RRL_INVENTORY_TASK(INVENTORY_TASK_ID,TASK_TYPE,TASK_SOURCE,SOURCE_DOC_TYPE,SOURCE_DOC_ID,STATUS,WARE_ID,CELL_CODE,ARTICUL,PLANNED_QTY,ASSIGNED_RESOURCE_TYPE,CREATED_AT,CREATED_BY)
    values(inv_id,'INVENTORY_CHECK','CASE_PICK_SHORT','CASE_PICK_SHORT',short_id,'NEW',ware,v_cell,article,l.PLANNED_QTY,nvl(resource_type,'INVENTORY'),systimestamp,p_actor);
  end if;
  reason:=d.get_object('metadata').get_string('reason');
  update RRL_CASE_PICK_SHORT set STATUS='ACCEPTED',INVENTORY_TASK_ID=inv_id,APPROVED_AT=systimestamp,APPROVED_BY=p_actor,
   REASON_TEXT=substr(nvl(reason,REASON_TEXT),1,1000) where CASE_PICK_SHORT_ID=short_id;
  update RRL_CASE_PICK_LINE set STATUS='SHORT_PICKED',DONE_AT=systimestamp,UPDATED_AT=systimestamp,UPDATED_BY=p_actor where CASE_PICK_LINE_ID=line_id;
  update RRL_PICK_TASK set FACT_QTY=l.PICKED_QTY,STATUS='DONE',DONE_AT=sysdate,DONE_BY=p_actor,UPDATED_AT=sysdate,UPDATED_BY=p_actor where PICK_TASK_ID=pt_id;
  update RRL_PICK_WAVE_TASK set FACT_QTY=l.PICKED_QTY,STATUS='DONE',DONE_AT=sysdate,DONE_BY=p_actor,UPDATED_AT=sysdate,UPDATED_BY=p_actor where PICK_WAVE_TASK_ID=wt_id;
  update RRL_CASE_PICK_TASK set CONTENT_VERSION=CONTENT_VERSION+1,
   PICKED_LINES=(select count(*) from RRL_CASE_PICK_LINE where CASE_PICK_TASK_ID=task_id and STATUS in('PICKED','SHORT_PICKED','CANCELLED')),
   UPDATED_AT=systimestamp,UPDATED_BY=p_actor where CASE_PICK_TASK_ID=task_id;
  insert into RRL_CASE_PICK_EVENT(CASE_PICK_EVENT_ID,CASE_PICK_TASK_ID,CASE_PICK_LINE_ID,EVENT_TYPE,PAYLOAD_JSON,CREATED_BY)
   values(RRL_CASE_PICK_EVENT_SQ.nextval,task_id,line_id,'SHORT_ACCEPTED',p_request,p_actor);
  j.put('status','ACCEPTED');j.put('inventory_task_id',inv_id);j.put('released_reservations',a.get_size);j.put('operation_id',op);p_result:=j.to_clob;
 end;
end;
/
