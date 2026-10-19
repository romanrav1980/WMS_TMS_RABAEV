create or replace package body RRL_STOCK_WAVE_PICK_CMD as
 function signature(p_json clob) return varchar2 is
 begin return rawtohex(sys.dbms_crypto.hash(p_json,sys.dbms_crypto.hash_sh256));end;
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob) is
  d json_object_t:=json_object_t.parse(p_request);snapshot clob;j json_object_t;v json_object_t:=json_object_t();
  tasks json_array_t;repl json_array_t;owned json_array_t;t json_object_t;sr json_object_t;
  f json_array_t:=json_array_t();r json_array_t:=json_array_t();wave number;
 begin
  wave:=d.get_object('source').get_number('wave_id');snapshot:=RRL_STOCK_WAVE_READY.snapshot_json(wave);j:=json_object_t.parse(snapshot);
  RRL_STOCK_PLAN_HELPER.fence(f,'RELEASE','STOCK');RRL_STOCK_PLAN_HELPER.fence(f,'CONFIG','WAREHOUSE');
  RRL_STOCK_PLAN_HELPER.anchor(r,10,'OP',p_operation);RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_PICK_WAVE',RRL_STOCK_PLAN_HELPER.decimal_text(wave));
  RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','STOCK.OUTBOX:'||rawtohex(sys.dbms_crypto.hash(utl_i18n.string_to_raw(p_operation,'AL32UTF8'),sys.dbms_crypto.hash_sh256)));
  tasks:=j.get_array('tasks');
  for i in 0..tasks.get_size-1 loop
   t:=treat(tasks.get(i) as json_object_t);
   RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_PICK_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(t.get_number('pick_task_id')));
   RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_PICK_WAVE_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(t.get_number('wave_task_id')));
   RRL_STOCK_PLAN_HELPER.fence(f,'SKU',t.get_string('article'));
   if t.get_string('cell') is not null then RRL_STOCK_PLAN_HELPER.fence(f,'CELL',t.get_string('cell'));end if;
   owned:=t.get_array('reservations');
   for k in 0..owned.get_size-1 loop
    sr:=treat(owned.get(k) as json_object_t);
    RRL_STOCK_PLAN_HELPER.stock_closure(f,r,sr.get_string('uid'),sr.get_string('article'),sr.get_string('cell'),null);
   end loop;
  end loop;
  repl:=j.get_array('open_replenishments');
  for i in 0..repl.get_size-1 loop
   t:=treat(repl.get(i) as json_object_t);
   RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_PICK_WAVE_REPLENISH_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(t.get_number('replenishment_id')));
   if t.get_number('warehouse_task_id') is not null then RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_WAREHOUSE_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(t.get_number('warehouse_task_id')));end if;
  end loop;
  v.put('wave_id',wave);v.put('signature',signature(snapshot));p_domain:=v.to_clob;p_policies:=f.to_clob;p_resources:=r.to_clob;
 end;
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob) is
  d json_object_t:=json_object_t.parse(p_request);plan clob;v json_object_t;snapshot clob;j json_object_t;
  wave number;op varchar2(100);w RRL_PICK_WAVE%rowtype;rows json_array_t;rowdata json_object_t;row_id number;
 begin
  if RRL_HAS_WRIGHT(p_actor,'pick_wave_launch')!=1 then raise_application_error(-20882,'WAVE_PICK_RELEASE_FORBIDDEN');end if;
  op:=d.get_string('operation_id');select RESOLVED_PLAN_JSON into plan from RRL_STOCK_OPERATION where OPERATION_ID=op;
  v:=json_object_t.parse(plan).get_object('domain');wave:=v.get_number('wave_id');
  select * into w from RRL_PICK_WAVE where PICK_WAVE_ID=wave for update;
  if w.STATUS!='LAUNCHED' or w.STATUS is null then raise_application_error(-20886,'WAVE_NOT_LAUNCHED');end if;
  if w.PICK_RELEASED_AT is null then
   snapshot:=RRL_STOCK_WAVE_READY.snapshot_json(wave);
   if signature(snapshot)!=v.get_string('signature') then raise_application_error(-20890,'CLOSURE_CHANGED: wave picking coverage');end if;
   j:=json_object_t.parse(snapshot);
   if not j.get_boolean('ready') then raise_application_error(-20886,'WAVE_PICK_COVERAGE_OR_REPLENISHMENT_PENDING');end if;
   rows:=j.get_array('open_replenishments');
   for i in 0..rows.get_size-1 loop
    rowdata:=treat(rows.get(i) as json_object_t);
    if rowdata.get_boolean('can_cancel_before_release') then
     row_id:=rowdata.get_number('replenishment_id');
     RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_PICK_WAVE_REPLENISH_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(row_id)));
     update RRL_PICK_WAVE_REPLENISH_TASK set STATUS='CANCELLED',
      WAIT_REASON='Actual eligible owned stock covers selected demand; no physical source was allocated',
      UPDATED_AT=sysdate,UPDATED_BY=p_actor where PICK_WAVE_REPLENISH_TASK_ID=row_id and SOURCE_RESERVATION_ID is null;
     if sql%rowcount!=1 then raise_application_error(-20890,'CLOSURE_CHANGED: covered replenishment');end if;
    end if;
   end loop;
   update RRL_PICK_WAVE set PICK_RELEASED_AT=systimestamp,PICK_RELEASED_BY=p_actor,PICK_RELEASE_OPERATION_ID=op where PICK_WAVE_ID=wave;
  end if;
  p_result:=RRL_STOCK_WAVE_READY.snapshot_json(wave);
 end;
end;

/
