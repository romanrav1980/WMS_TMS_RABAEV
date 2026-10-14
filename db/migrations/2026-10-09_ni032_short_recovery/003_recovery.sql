create or replace package body RRL_STOCK_SHORT_RECOVERY as
 procedure add_case_rows(s RRL_CASE_PICK_SHORT%rowtype,p_resources in out nocopy json_array_t) is l RRL_CASE_PICK_LINE%rowtype;
 begin
  select * into l from RRL_CASE_PICK_LINE where CASE_PICK_LINE_ID=s.CASE_PICK_LINE_ID;
  RRL_STOCK_PLAN_HELPER.row_key(p_resources,'RRL_CASE_PICK_SHORT',RRL_STOCK_PLAN_HELPER.decimal_text(s.CASE_PICK_SHORT_ID));
  RRL_STOCK_PLAN_HELPER.row_key(p_resources,'RRL_PICK_WAVE',RRL_STOCK_PLAN_HELPER.decimal_text(s.PICK_WAVE_ID));
  RRL_STOCK_PLAN_HELPER.row_key(p_resources,'RRL_CASE_PICK_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(s.CASE_PICK_TASK_ID));
  RRL_STOCK_PLAN_HELPER.row_key(p_resources,'RRL_CASE_PICK_LINE',RRL_STOCK_PLAN_HELPER.decimal_text(s.CASE_PICK_LINE_ID));
  RRL_STOCK_PLAN_HELPER.row_key(p_resources,'RRL_PICK_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(l.PICK_TASK_ID));
  RRL_STOCK_PLAN_HELPER.row_key(p_resources,'RRL_PICK_WAVE_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(l.PICK_WAVE_TASK_ID));
 end;
 procedure plan_inventory(p_request clob,p_resources in out nocopy json_array_t,p_policies in out nocopy json_array_t,p_domain in out nocopy json_object_t) is
  d json_object_t:=json_object_t.parse(p_request);m json_object_t;counts json_array_t;x json_object_t;
  it RRL_INVENTORY_TASK%rowtype;s RRL_CASE_PICK_SHORT%rowtype;doc number;ware number;new_repl number;n number;id number;found boolean;
 begin
  m:=d.get_object('metadata');m.on_error(0);
  if not m.has('inventory_task_id') or m.get('inventory_task_id').is_null then return;end if;
  id:=m.get_number('inventory_task_id');doc:=d.get_object('source').get_number('revision_id');
  if id is null or id<=0 or id!=trunc(id) then raise_application_error(-20881,'INVENTORY_TASK_ID_REQUIRED');end if;
  select * into it from RRL_INVENTORY_TASK where INVENTORY_TASK_ID=id;
  select * into s from RRL_CASE_PICK_SHORT where CASE_PICK_SHORT_ID=it.SOURCE_DOC_ID;
  select WARE_ID into ware from RRL_REVIZION where ID=doc;
  if it.SOURCE_DOC_TYPE!='CASE_PICK_SHORT' or it.TASK_SOURCE!='CASE_PICK_SHORT'
    or it.INVENTORY_TASK_ID!=s.INVENTORY_TASK_ID or it.STATUS not in('NEW','ASSIGNED','IN_PROGRESS')
    or s.STATUS!='ACCEPTED' or s.RECOVERY_STATE is null or s.RECOVERY_STATE!='WAIT_INVENTORY'
    or it.WARE_ID!=ware or it.CELL_CODE!=s.CELL_CODE or it.ARTICUL!=s.ARTICUL then
   raise_application_error(-20886,'SHORT_INVENTORY_TASK_STATE_CONFLICT');end if;
  counts:=m.get_array('counts');
  for i in 0..counts.get_size-1 loop
   x:=treat(counts.get(i) as json_object_t);
   if x.get_string('cell')!=it.CELL_CODE or x.get_string('article')!=it.ARTICUL then
    raise_application_error(-20887,'SHORT_INVENTORY_SCOPE_CONFLICT');end if;
  end loop;
  for lot in(select r.UID_POLETA from RRL_REMAINS r join RRL_PALLETS p on p.UID_PALLET=r.UID_POLETA
   where r.CELL=it.CELL_CODE and p.ARTICUL=it.ARTICUL and r.REMAIN>0 fetch first 201 rows only) loop
   found:=false;
   for i in 0..counts.get_size-1 loop
    x:=treat(counts.get(i) as json_object_t);
    if x.get_string('uid')=lot.UID_POLETA then found:=true;exit;end if;
   end loop;
   if not found then raise_application_error(-20887,'SHORT_INVENTORY_SCOPE_INCOMPLETE: refresh all lots');end if;
  end loop;
  RRL_STOCK_PLAN_HELPER.fence(p_policies,'CELL',it.CELL_CODE,6);
  RRL_STOCK_PLAN_HELPER.row_key(p_resources,'RRL_INVENTORY_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(id));
  add_case_rows(s,p_resources);
  select RRL_PICK_WAVE_REPL_SQ.nextval into new_repl from dual;
  RRL_STOCK_PLAN_HELPER.row_key(p_resources,'RRL_PICK_WAVE_REPLENISH_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(new_repl));
  p_domain.put('inventory_task_id',id);p_domain.put('short_id',s.CASE_PICK_SHORT_ID);p_domain.put('new_repl_id',new_repl);
 end;
 procedure finish_inventory(p_request clob,p_actor varchar2,p_domain json_object_t,p_facts json_array_t,p_result in out nocopy json_object_t) is
  d json_object_t:=json_object_t.parse(p_request);id number;it RRL_INVENTORY_TASK%rowtype;s RRL_CASE_PICK_SHORT%rowtype;l RRL_CASE_PICK_LINE%rowtype;
  qty number:=0;need number;new_repl number;op varchar2(100);x json_object_t;found boolean;min_days number;min_percent number;
 begin
  if not p_domain.has('inventory_task_id') then return;end if;
  if RRL_HAS_WRIGHT(p_actor,'inventory_task_execute')!=1 then raise_application_error(-20882,'SHORT_INVENTORY_EXECUTE_FORBIDDEN');end if;
  id:=p_domain.get_number('inventory_task_id');new_repl:=p_domain.get_number('new_repl_id');op:=d.get_string('operation_id');
  RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_INVENTORY_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(id)));
  select * into it from RRL_INVENTORY_TASK where INVENTORY_TASK_ID=id for update;
  select * into s from RRL_CASE_PICK_SHORT where CASE_PICK_SHORT_ID=it.SOURCE_DOC_ID for update;
  select * into l from RRL_CASE_PICK_LINE where CASE_PICK_LINE_ID=s.CASE_PICK_LINE_ID for update;
  if s.CASE_PICK_SHORT_ID!=p_domain.get_number('short_id') or s.RECOVERY_STATE!='WAIT_INVENTORY'
    or it.STATUS not in('NEW','ASSIGNED','IN_PROGRESS') or (it.ASSIGNED_TO is not null and it.ASSIGNED_TO!=p_actor) then
   raise_application_error(-20886,'SHORT_INVENTORY_EXECUTOR_OR_STATE_CONFLICT');end if;
  for i in 0..p_facts.get_size-1 loop x:=treat(p_facts.get(i) as json_object_t);if not regexp_like(x.get_string('after'),'^0([.]0{1,9})?$') then qty:=qty+RRL_STOCK_MATH.quantity(x.get_string('after'));end if;end loop;
  -- CELL X prevents an unobserved concurrent arrival. A new unlisted lot requires refresh.
  for lot in(select r.UID_POLETA from RRL_REMAINS r join RRL_PALLETS p on p.UID_PALLET=r.UID_POLETA
    where r.CELL=it.CELL_CODE and p.ARTICUL=it.ARTICUL and r.REMAIN>0) loop
   found:=false;
   for i in 0..p_facts.get_size-1 loop x:=treat(p_facts.get(i) as json_object_t);if x.get_string('uid')=lot.UID_POLETA then found:=true;exit;end if;end loop;
   if not found then raise_application_error(-20890,'CLOSURE_CHANGED: short inventory lot set');end if;
  end loop;
  need:=l.PLANNED_QTY-l.PICKED_QTY;
  if need<=0 or need!=s.SHORT_QTY or l.STATUS!='WAIT_REPLENISHMENT' then raise_application_error(-20886,'SHORT_RECOVERY_REMAINDER_CHANGED');end if;
  select max(MIN_SHELF_LIFE_DAYS),max(MIN_SHELF_LIFE_PERCENT) into min_days,min_percent from RRL_PICK_WAVE_REPLENISH_TASK where PICK_TASK_ID=l.PICK_TASK_ID;
  insert into RRL_PICK_WAVE_REPLENISH_TASK(PICK_WAVE_REPLENISH_TASK_ID,PICK_WAVE_ID,PICK_TASK_ID,STATUS,ARTICUL,
   TARGET_CELL_CODE,QTY,PICK_SEQUENCE,CREATED_BY,REPLENISHMENT_METHOD,REPLENISHMENT_QTY_MODE,RELEASED_AT,RELEASED_BY,MIN_SHELF_LIFE_DAYS,MIN_SHELF_LIFE_PERCENT)
   values(new_repl,l.PICK_WAVE_ID,l.PICK_TASK_ID,'RELEASED',l.ARTICUL,l.CELL_CODE,need,l.PICK_SEQUENCE,p_actor,'IMMEDIATE','FILL_TO_VOLUME',sysdate,p_actor,min_days,min_percent);
  declare
 v_json_sql_1_1 number:=p_domain.get_number('document');
begin
update RRL_INVENTORY_TASK set STATUS='DONE',FACT_QTY=qty,DONE_AT=systimestamp,UPDATED_AT=systimestamp,UPDATED_BY=p_actor,
   ASSIGNED_TO=nvl(ASSIGNED_TO,p_actor),REVISION_ID=v_json_sql_1_1,COUNT_OPERATION_ID=op where INVENTORY_TASK_ID=id;
end;
  update RRL_CASE_PICK_SHORT set RECOVERY_STATE='WAIT_REPLENISHMENT',REPLENISH_TASK_ID=new_repl,RECOVERY_LAST_ERROR=null,RECOVERY_WORKER=null,RECOVERY_LEASE_UNTIL=null where CASE_PICK_SHORT_ID=s.CASE_PICK_SHORT_ID;
  p_result.put('inventory_task_id',id);p_result.put('short_id',s.CASE_PICK_SHORT_ID);p_result.put('replenish_task_id',new_repl);
  p_result.put('observed_quantity',RRL_STOCK_PLAN_HELPER.decimal_text(qty));p_result.put('recovery_state','WAIT_REPLENISHMENT');
 end;

 procedure set_ready(s RRL_CASE_PICK_SHORT%rowtype,p_actor varchar2) is
 begin
  update RRL_CASE_PICK_SHORT set RECOVERY_STATE='READY',RECOVERY_LAST_ERROR=null,RECOVERY_WORKER=null,RECOVERY_LEASE_UNTIL=null
   where CASE_PICK_SHORT_ID=s.CASE_PICK_SHORT_ID;
  update RRL_CASE_PICK_LINE set STATUS='ACTIVE',UPDATED_AT=systimestamp,UPDATED_BY=p_actor where CASE_PICK_LINE_ID=s.CASE_PICK_LINE_ID;
  update RRL_CASE_PICK_TASK set STATUS=case when exists(select 1 from RRL_CASE_PICK_LINE l
    where l.CASE_PICK_TASK_ID=s.CASE_PICK_TASK_ID and l.STATUS='WAIT_REPLENISHMENT') then 'WAIT_REPLENISHMENT' else 'IN_PROGRESS' end,
   CONTENT_VERSION=CONTENT_VERSION+1,UPDATED_AT=systimestamp,UPDATED_BY=p_actor where CASE_PICK_TASK_ID=s.CASE_PICK_TASK_ID;
 end;
 procedure plan_replenishment(p_repl number,p_resources in out nocopy json_array_t) is
 begin
  for s in(select * from RRL_CASE_PICK_SHORT where REPLENISH_TASK_ID=p_repl and RECOVERY_STATE='WAIT_REPLENISHMENT') loop add_case_rows(s,p_resources);end loop;
 end;
 procedure finish_replenishment(p_task RRL_WAREHOUSE_TASK%rowtype,p_actor varchar2) is
  qty number;need number;status varchar2(30);
 begin
  for s in(select * from RRL_CASE_PICK_SHORT where REPLENISH_TASK_ID=p_task.SOURCE_TASK_ID and RECOVERY_STATE='WAIT_REPLENISHMENT') loop
   RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_CASE_PICK_SHORT',RRL_STOCK_PLAN_HELPER.decimal_text(s.CASE_PICK_SHORT_ID)));
   select STATUS into status from RRL_PICK_WAVE_REPLENISH_TASK where PICK_WAVE_REPLENISH_TASK_ID=s.REPLENISH_TASK_ID;
   select PLANNED_QTY-PICKED_QTY into need from RRL_CASE_PICK_LINE where CASE_PICK_LINE_ID=s.CASE_PICK_LINE_ID;
   select nvl(sum(sr.BASE_QTY),0) into qty from RRL_STOCK_RESERVATION sr join RRL_CASE_PICK_LINE l on l.CASE_PICK_LINE_ID=s.CASE_PICK_LINE_ID
    where sr.SOURCE_DOC_TYPE='PICK_WAVE' and sr.SOURCE_DOC_ID=s.PICK_WAVE_ID and sr.SOURCE_LINE_ID=l.PICK_TASK_ID
     and sr.CELL=s.CELL_CODE and sr.RESERVATION_KIND='HARD' and sr.STATUS in('ACTIVE','ALLOCATED','PICKING')
     and not exists(select 1 from RRL_CASE_CARRIER_LOT h where h.LOT_UID=sr.UID_PALLET);
   if status='DONE' and need>0 and qty>=need then set_ready(s,p_actor);end if;
  end loop;
 end;
 procedure plan_pick(p_line number,p_resources in out nocopy json_array_t) is
 begin
  for s in(select * from RRL_CASE_PICK_SHORT where CASE_PICK_LINE_ID=p_line and RECOVERY_STATE in('WAIT_INVENTORY','WAIT_REPLENISHMENT','READY')) loop
   if s.RECOVERY_STATE!='READY' then raise_application_error(-20886,'SHORT_RECOVERY_NOT_READY');end if;
   RRL_STOCK_PLAN_HELPER.row_key(p_resources,'RRL_CASE_PICK_SHORT',RRL_STOCK_PLAN_HELPER.decimal_text(s.CASE_PICK_SHORT_ID));
  end loop;
 end;
 procedure finish_pick(p_line number,p_actor varchar2) is
 begin
  for s in(select * from RRL_CASE_PICK_SHORT where CASE_PICK_LINE_ID=p_line and RECOVERY_STATE in('WAIT_INVENTORY','WAIT_REPLENISHMENT','READY')) loop
   RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_CASE_PICK_SHORT',RRL_STOCK_PLAN_HELPER.decimal_text(s.CASE_PICK_SHORT_ID)));
   if s.RECOVERY_STATE!='READY' then raise_application_error(-20886,'SHORT_RECOVERY_NOT_READY');end if;
   update RRL_CASE_PICK_SHORT set RECOVERY_STATE='RESUMED',RESTORED_AT=systimestamp,RECOVERY_WORKER=null,RECOVERY_LEASE_UNTIL=null
    where CASE_PICK_SHORT_ID=s.CASE_PICK_SHORT_ID;
  end loop;
 end;

 procedure plan_ready(p_request clob,p_policies in out nocopy json_array_t,p_resources in out nocopy json_array_t,p_domain in out nocopy json_object_t) is
  d json_object_t:=json_object_t.parse(p_request);s RRL_CASE_PICK_SHORT%rowtype;l RRL_CASE_PICK_LINE%rowtype;rt RRL_PICK_WAVE_REPLENISH_TASK%rowtype;
  chunks json_array_t:=json_array_t();x json_object_t;id number;ware number;need number;covered number;take_qty number;rid number;ver number;
 begin
  id:=d.get_object('source').get_number('short_id');select * into s from RRL_CASE_PICK_SHORT where CASE_PICK_SHORT_ID=id;
  select * into l from RRL_CASE_PICK_LINE where CASE_PICK_LINE_ID=s.CASE_PICK_LINE_ID;
  select WARE_ID into ware from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=s.CASE_PICK_TASK_ID;
  if s.STATUS!='ACCEPTED' or s.RECOVERY_STATE is null or s.RECOVERY_STATE not in('WAIT_REPLENISHMENT','READY') then
   raise_application_error(-20886,'SHORT_READY_STATE_CONFLICT');end if;
  RRL_STOCK_PLAN_HELPER.fence(p_policies,'RELEASE','STOCK');RRL_STOCK_PLAN_HELPER.fence(p_policies,'CONFIG','WAREHOUSE');
  RRL_STOCK_PLAN_HELPER.anchor(p_resources,10,'OP',d.get_string('operation_id'));
  RRL_STOCK_PLAN_HELPER.anchor(p_resources,70,'UNIQUE','STOCK.OUTBOX:'||rawtohex(sys.dbms_crypto.hash(utl_i18n.string_to_raw(d.get_string('operation_id'),'AL32UTF8'),sys.dbms_crypto.hash_sh256)));
  add_case_rows(s,p_resources);
  select * into rt from RRL_PICK_WAVE_REPLENISH_TASK where PICK_WAVE_REPLENISH_TASK_ID=s.REPLENISH_TASK_ID;
  RRL_STOCK_PLAN_HELPER.row_key(p_resources,'RRL_PICK_WAVE_REPLENISH_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(s.REPLENISH_TASK_ID));
  need:=l.PLANNED_QTY-l.PICKED_QTY;
  if need<=0 or need!=s.SHORT_QTY or rt.PICK_TASK_ID!=l.PICK_TASK_ID or rt.PICK_WAVE_ID!=l.PICK_WAVE_ID or rt.ARTICUL!=l.ARTICUL or rt.TARGET_CELL_CODE!=l.CELL_CODE then
   raise_application_error(-20886,'SHORT_READY_IDENTITY_CONFLICT');end if;
  select nvl(sum(sr.BASE_QTY),0) into covered from RRL_STOCK_RESERVATION sr
   where sr.SOURCE_DOC_TYPE='PICK_WAVE' and sr.SOURCE_DOC_ID=l.PICK_WAVE_ID and sr.SOURCE_LINE_ID=l.PICK_TASK_ID
    and sr.RESERVATION_KIND='HARD' and sr.STATUS in('ACTIVE','ALLOCATED','PICKING') and sr.CELL=l.CELL_CODE
    and not exists(select 1 from RRL_CASE_CARRIER_LOT h where h.LOT_UID=sr.UID_PALLET);
  if rt.SOURCE_RESERVATION_ID is not null and (rt.STATUS!='DONE' or covered<need) then
   raise_application_error(-20886,'SHORT_EXISTING_REPLENISHMENT_MUST_FINISH');end if;
  p_domain.put('short_id',id);p_domain.put('repl_id',s.REPLENISH_TASK_ID);p_domain.put('repl_status',rt.STATUS);
  p_domain.put('source_reservation',rt.SOURCE_RESERVATION_ID);p_domain.put('line_id',s.CASE_PICK_LINE_ID);
  p_domain.put('remaining',RRL_STOCK_PLAN_HELPER.decimal_text(need));p_domain.put('warehouse',ware);
  p_domain.put('covered',RRL_STOCK_PLAN_HELPER.decimal_text(covered));p_domain.put('decision','READY');
  need:=greatest(need-covered,0);
  for c in(select rr.UID_POLETA,rr.REMAIN,rr.HARD_RESERVED_BASE,rr.STOCK_VERSION,rr.BASE_UOM,p.EXPIRY_DATE
    from RRL_REMAINS rr join RRL_PALLETS p on p.UID_PALLET=rr.UID_POLETA
    where rr.CELL=l.CELL_CODE and p.ARTICUL=l.ARTICUL and rr.REMAIN>rr.HARD_RESERVED_BASE
    order by p.EXPIRY_DATE nulls last,rr.UID_POLETA fetch first 201 rows only) loop
   exit when need=0;
   if RRL_STOCK_ELIGIBILITY.reason(c.UID_POLETA,l.CELL_CODE,ware,0,rt.MIN_SHELF_LIFE_DAYS,rt.MIN_SHELF_LIFE_PERCENT,'PICK',null,l.ARTICUL) is not null then continue;end if;
   if chunks.get_size>=200 then raise_application_error(-20881,'SHORT_READY_SOURCE_BOUND');end if;
   take_qty:=least(need,c.REMAIN-c.HARD_RESERVED_BASE);need:=need-take_qty;
   select RRL_STOCK_RESERVATION_SQ.nextval into rid from dual;
   select max(POLICY_VERSION) into ver from RRL_STOCK_UOM_CONVERSION where ARTICUL=l.ARTICUL and INPUT_UOM=c.BASE_UOM and BASE_UOM=c.BASE_UOM and NUMERATOR=1 and DENOMINATOR=1;
   if ver is null then raise_application_error(-20868,'SHORT_READY_BASE_POLICY_REQUIRED');end if;
   RRL_STOCK_PLAN_HELPER.stock_closure(p_policies,p_resources,c.UID_POLETA,l.ARTICUL,l.CELL_CODE,null);
   RRL_STOCK_PLAN_HELPER.row_key(p_resources,'RRL_STOCK_RESERVATION',RRL_STOCK_PLAN_HELPER.decimal_text(rid));
   x:=json_object_t();x.put('uid',c.UID_POLETA);x.put('quantity',RRL_STOCK_PLAN_HELPER.decimal_text(take_qty));x.put('base',c.BASE_UOM);
   x.put('version',c.STOCK_VERSION);x.put('reservation',rid);x.put('policy',ver);chunks.append(x);
  end loop;
  if need>0 then raise_application_error(-20886,'SHORT_NO_ELIGIBLE_TARGET_STOCK');end if;
  p_domain.put('chunks',chunks);
 end;
 procedure execute_ready(p_request clob,p_actor varchar2,p_result out clob) is
  d json_object_t:=json_object_t.parse(p_request);v json_object_t;chunks json_array_t;x json_object_t;detail json_object_t:=json_object_t();j json_object_t:=json_object_t();
  plan clob;op varchar2(100);s RRL_CASE_PICK_SHORT%rowtype;l RRL_CASE_PICK_LINE%rowtype;rt RRL_PICK_WAVE_REPLENISH_TASK%rowtype;
  qty number;covered number;ver number;uid varchar2(200);rid number;base varchar2(20);policy number;stockver number;units clob;wave_status varchar2(40);
 begin
  if RRL_HAS_WRIGHT(p_actor,'case_pick_short_approve')!=1 then raise_application_error(-20882,'SHORT_READY_FORBIDDEN');end if;
  op:=d.get_string('operation_id');select RESOLVED_PLAN_JSON into plan from RRL_STOCK_OPERATION where OPERATION_ID=op;
  v:=json_object_t.parse(plan).get_object('domain');
  declare
 v_json_sql_2_1 number:=v.get_number('short_id');
begin
select * into s from RRL_CASE_PICK_SHORT where CASE_PICK_SHORT_ID=v_json_sql_2_1 for update;
end;
  select STATUS into wave_status from RRL_PICK_WAVE where PICK_WAVE_ID=s.PICK_WAVE_ID for update;
  select * into l from RRL_CASE_PICK_LINE where CASE_PICK_LINE_ID=s.CASE_PICK_LINE_ID for update;
  select * into rt from RRL_PICK_WAVE_REPLENISH_TASK where PICK_WAVE_REPLENISH_TASK_ID=s.REPLENISH_TASK_ID for update;
  if wave_status is null or wave_status in('CANCELLED','CLOSED','COMPLETED','SHIPPED','DRAFT','PREVIEW') or
   s.STATUS!='ACCEPTED' or s.RECOVERY_STATE not in('WAIT_REPLENISHMENT','READY') or s.REPLENISH_TASK_ID!=v.get_number('repl_id')
   or rt.STATUS!=v.get_string('repl_status') or nvl(rt.SOURCE_RESERVATION_ID,-1)!=nvl(v.get_number('source_reservation'),-1)
   or RRL_STOCK_PLAN_HELPER.decimal_text(l.PLANNED_QTY-l.PICKED_QTY)!=v.get_string('remaining') then
   raise_application_error(-20890,'CLOSURE_CHANGED: short target stock');end if;
  select nvl(sum(sr.BASE_QTY),0) into covered from RRL_STOCK_RESERVATION sr
   where sr.SOURCE_DOC_TYPE='PICK_WAVE' and sr.SOURCE_DOC_ID=l.PICK_WAVE_ID and sr.SOURCE_LINE_ID=l.PICK_TASK_ID
    and sr.RESERVATION_KIND='HARD' and sr.STATUS in('ACTIVE','ALLOCATED','PICKING') and sr.CELL=l.CELL_CODE
    and not exists(select 1 from RRL_CASE_CARRIER_LOT h where h.LOT_UID=sr.UID_PALLET);
  if RRL_STOCK_PLAN_HELPER.decimal_text(covered)!=v.get_string('covered') then raise_application_error(-20890,'CLOSURE_CHANGED: short target coverage');end if;
  chunks:=v.get_array('chunks');
  for i in 0..chunks.get_size-1 loop
   x:=treat(chunks.get(i) as json_object_t);uid:=x.get_string('uid');rid:=x.get_number('reservation');base:=x.get_string('base');policy:=x.get_number('policy');
   qty:=RRL_STOCK_MATH.quantity(x.get_string('quantity'));
   select STOCK_VERSION into stockver from RRL_REMAINS where UID_POLETA=uid and CELL=l.CELL_CODE;
   if stockver!=x.get_number('version') then raise_application_error(-20890,'CLOSURE_CHANGED: short target stock version');end if;
   RRL_STOCK_ELIGIBILITY.assert_source(uid,l.CELL_CODE,v.get_number('warehouse'),qty,rt.MIN_SHELF_LIFE_DAYS,rt.MIN_SHELF_LIFE_PERCENT,'PICK',null,l.ARTICUL);
   units:=RRL_STOCK_UNIT_CORE.automatic_units(uid,l.CELL_CODE,qty);detail.put('pick_wave_id',l.PICK_WAVE_ID);detail.put('reservation_scope','QTY');
   RRL_STOCK_RESERVE_CORE.create_hard(rid,uid,l.CELL_CODE,qty,base,policy,'PICK_WAVE',l.PICK_WAVE_ID,l.PICK_TASK_ID,'PICKING',p_actor,detail.to_clob);
   RRL_STOCK_UNIT_CORE.reserve_units(uid,l.CELL_CODE,rid,qty,units);
  end loop;
  if rt.SOURCE_RESERVATION_ID is null then update RRL_PICK_WAVE_REPLENISH_TASK set STATUS='CANCELLED',WAIT_REASON='Confirmed stock available at original pick cell',UPDATED_AT=sysdate,UPDATED_BY=p_actor where PICK_WAVE_REPLENISH_TASK_ID=s.REPLENISH_TASK_ID;end if;
  set_ready(s,p_actor);j.put('operation_id',op);j.put('short_id',s.CASE_PICK_SHORT_ID);j.put('recovery_state','READY');j.put('new_reservations',chunks.get_size);
  p_result:=j.to_clob;
 end;
end;
/
