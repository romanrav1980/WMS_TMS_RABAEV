create or replace package RRL_STOCK_DOC_RESERVE_CMD authid definer
 accessible by(package RRL_STOCK_POSTING_API) as
 procedure compile_release(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_release(p_request clob,p_actor varchar2,p_result out clob);
end;
/
create or replace package body RRL_STOCK_DOC_RESERVE_CMD as
 function document_table(p_type varchar2) return varchar2 is
 begin
  case p_type when 'PICK_WAVE' then return 'RRL_PICK_WAVE';when 'PICK_PLAN' then return 'RRL_PICK_PLAN';
   when 'PRODUCTION_ORDER' then return 'RRL_PRODUCTION_ORDER';else raise_application_error(-20869,'RESERVATION_DOCUMENT_TYPE_UNSUPPORTED');end case;
 end;
 procedure compile_release(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob) is
  d json_object_t:=json_object_t.parse(p_request);s json_object_t;v_type varchar2(40);v_doc number;v_only number;v_kind varchar2(10);
  f json_array_t:=json_array_t();r json_array_t:=json_array_t();a json_array_t:=json_array_t();v json_object_t:=json_object_t();x json_object_t;
 begin
  s:=d.get_object('source');v_type:=s.get_string('document_type');v_doc:=s.get_number('document_id');
  v_only:=nvl(d.get_object('metadata').get_number('only_cancelled_replenishment'),0);v_kind:=d.get_object('metadata').get_string('reservation_kind');
  if v_kind is not null and v_kind not in('SOFT','HARD') then raise_application_error(-20869,'RESERVATION_KIND_INVALID');end if;
  RRL_STOCK_PLAN_HELPER.fence(f,'RELEASE','STOCK');RRL_STOCK_PLAN_HELPER.fence(f,'CONFIG','WAREHOUSE');
  RRL_STOCK_PLAN_HELPER.anchor(r,10,'OP',p_operation);
  RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','STOCK.OUTBOX:'||rawtohex(sys.dbms_crypto.hash(utl_i18n.string_to_raw(p_operation,'AL32UTF8'),sys.dbms_crypto.hash_sh256)));
  RRL_STOCK_PLAN_HELPER.row_key(r,document_table(v_type),RRL_STOCK_PLAN_HELPER.decimal_text(v_doc));
  for sr in(select * from RRL_STOCK_RESERVATION where ((SOURCE_DOC_TYPE=v_type and SOURCE_DOC_ID=v_doc) or (v_type='PICK_PLAN' and (PICK_PLAN_ID=v_doc or (RESERVATION_DOMAIN='WAVE' and exists(select 1 from RRL_PICK_WAVE_REPLENISH_TASK rt join RRL_PICK_TASK pt on pt.PICK_TASK_ID=rt.PICK_TASK_ID where rt.PICK_WAVE_REPLENISH_TASK_ID=SOURCE_LINE_ID and pt.PICK_PLAN_ID=v_doc)))))
   and STATUS in('ACTIVE','ALLOCATED','PICKING') and (v_kind is null or RESERVATION_KIND=v_kind) and
    (v_only=0 or (v_type='PICK_WAVE' and RESERVATION_DOMAIN='WAVE' and exists(
     select 1 from RRL_PICK_WAVE_REPLENISH_TASK rt where rt.PICK_WAVE_ID=v_doc and rt.PICK_WAVE_REPLENISH_TASK_ID=SOURCE_LINE_ID and rt.STATUS in('CANCELLED','FAILED'))))
   order by RESERVATION_ID) loop
   if a.get_size>=10000 then raise_application_error(-20881,'DOCUMENT_RESERVATION_BOUND');end if;
   RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_STOCK_RESERVATION',RRL_STOCK_PLAN_HELPER.decimal_text(sr.RESERVATION_ID));
   if sr.UID_PALLET is not null then RRL_STOCK_PLAN_HELPER.stock_closure(f,r,sr.UID_PALLET,sr.ARTICUL,sr.CELL,null);
   else RRL_STOCK_PLAN_HELPER.fence(f,'SKU',sr.ARTICUL);end if;
   if v_only=1 then RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_PICK_WAVE_REPLENISH_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(sr.SOURCE_LINE_ID));end if;
   x:=json_object_t();x.put('id',sr.RESERVATION_ID);x.put('version',sr.RESERVATION_VERSION);x.put('uid',sr.UID_PALLET);x.put('cell',sr.CELL);x.put('owner_type',sr.SOURCE_DOC_TYPE);x.put('owner_id',sr.SOURCE_DOC_ID);a.append(x);
  end loop;
  if d.get_string('command_type') in('WAVE_CANCEL','WAVE_RELEASE') then
   for z in(select PICK_WAVE_TASK_ID,PICK_TASK_ID from RRL_PICK_WAVE_TASK where PICK_WAVE_ID=v_doc order by PICK_WAVE_TASK_ID) loop
    RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_PICK_WAVE_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(z.PICK_WAVE_TASK_ID));
    RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_PICK_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(z.PICK_TASK_ID));
   end loop;
   for z in(select PICK_RESERVATION_ID from RRL_PICK_RESERVATION where PICK_PLAN_ID in(select PICK_PLAN_ID from RRL_PICK_WAVE_ORDER where PICK_WAVE_ID=v_doc) order by PICK_RESERVATION_ID) loop
    RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_PICK_RESERVATION',RRL_STOCK_PLAN_HELPER.decimal_text(z.PICK_RESERVATION_ID));
   end loop;
   for z in(select PICK_WAVE_REPLENISH_TASK_ID from RRL_PICK_WAVE_REPLENISH_TASK where PICK_WAVE_ID=v_doc order by PICK_WAVE_REPLENISH_TASK_ID) loop
    RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_PICK_WAVE_REPLENISH_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(z.PICK_WAVE_REPLENISH_TASK_ID));
   end loop;
   for z in(select TASK_ID from RRL_WAREHOUSE_TASK where SOURCE_DOC_TYPE='PICK_WAVE' and SOURCE_DOC_ID=v_doc order by TASK_ID) loop
    RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_WAREHOUSE_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(z.TASK_ID));
   end loop;
  end if;
  if d.get_string('command_type')='PICK_PLAN_CANCEL' then
   for z in(select PICK_TASK_ID from RRL_PICK_TASK where PICK_PLAN_ID=v_doc order by PICK_TASK_ID) loop
    RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_PICK_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(z.PICK_TASK_ID));
    for wt in(select PICK_WAVE_TASK_ID,PICK_WAVE_ID from RRL_PICK_WAVE_TASK where PICK_TASK_ID=z.PICK_TASK_ID order by PICK_WAVE_TASK_ID) loop
     RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_PICK_WAVE',RRL_STOCK_PLAN_HELPER.decimal_text(wt.PICK_WAVE_ID));
     RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_PICK_WAVE_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(wt.PICK_WAVE_TASK_ID));
    end loop;
   end loop;
   for pr in(select PICK_RESERVATION_ID from RRL_PICK_RESERVATION where PICK_PLAN_ID=v_doc order by PICK_RESERVATION_ID) loop
    RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_PICK_RESERVATION',RRL_STOCK_PLAN_HELPER.decimal_text(pr.PICK_RESERVATION_ID));
   end loop;
   for task in(select w.TASK_ID from RRL_WAREHOUSE_TASK w where w.TASK_SOURCE='WAVE' and (
    (w.TASK_TYPE='PICKING_MOVE' and exists(select 1 from RRL_PICK_WAVE_TASK wt join RRL_PICK_TASK pt on pt.PICK_TASK_ID=wt.PICK_TASK_ID where wt.PICK_WAVE_TASK_ID=w.SOURCE_TASK_ID and pt.PICK_PLAN_ID=v_doc))
    or (w.TASK_TYPE='REPLENISHMENT' and exists(select 1 from RRL_PICK_WAVE_REPLENISH_TASK rt join RRL_PICK_TASK pt on pt.PICK_TASK_ID=rt.PICK_TASK_ID where rt.PICK_WAVE_REPLENISH_TASK_ID=w.SOURCE_TASK_ID and pt.PICK_PLAN_ID=v_doc))) order by w.TASK_ID) loop
    RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_WAREHOUSE_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(task.TASK_ID));
   end loop;
  end if;
  if d.get_string('command_type') in('WAVE_CANCEL','WAVE_RELEASE','PICK_PLAN_CANCEL') then
   for wr in(select PICK_WAVE_RESERVATION_ID from RRL_PICK_WAVE_RESERVATION where (v_type='PICK_WAVE' and PICK_WAVE_ID=v_doc) or (v_type='PICK_PLAN' and PICK_PLAN_ID=v_doc) order by PICK_WAVE_RESERVATION_ID) loop
    RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_PICK_WAVE_RESERVATION',RRL_STOCK_PLAN_HELPER.decimal_text(wr.PICK_WAVE_RESERVATION_ID));
   end loop;
  end if;
  if d.get_string('command_type')='PICK_PLAN_CANCEL' then
   for rt in(select r.PICK_WAVE_REPLENISH_TASK_ID from RRL_PICK_WAVE_REPLENISH_TASK r join RRL_PICK_TASK pt on pt.PICK_TASK_ID=r.PICK_TASK_ID where pt.PICK_PLAN_ID=v_doc order by r.PICK_WAVE_REPLENISH_TASK_ID) loop
    RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_PICK_WAVE_REPLENISH_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(rt.PICK_WAVE_REPLENISH_TASK_ID));
   end loop;
  end if;
  v.put('document_type',v_type);v.put('document_id',v_doc);v.put('only_cancelled',v_only);v.put('reservations',a);
  p_domain:=v.to_clob;p_policies:=f.to_clob;p_resources:=r.to_clob;
 end;
 procedure execute_release(p_request clob,p_actor varchar2,p_result out clob) is
  d json_object_t:=json_object_t.parse(p_request);v json_object_t;x json_object_t;j json_object_t:=json_object_t();
  a json_array_t;sr RRL_STOCK_RESERVATION%rowtype;v_plan clob;v_type varchar2(40);v_doc number;v_status varchar2(40);v_version number;
 begin
  declare
 v_json_sql_1_1 varchar2(32767):=d.get_string('operation_id');
begin
select RESOLVED_PLAN_JSON into v_plan from RRL_STOCK_OPERATION where OPERATION_ID=v_json_sql_1_1;
end;
  v:=json_object_t.parse(v_plan).get_object('domain');v_type:=v.get_string('document_type');v_doc:=v.get_number('document_id');a:=v.get_array('reservations');
  if RRL_HAS_WRIGHT(p_actor,'stock_reservation_edit')!=1
   and not(v_type='PICK_WAVE' and (RRL_HAS_WRIGHT(p_actor,'pick_wave_launch')=1 or RRL_HAS_WRIGHT(p_actor,'pick_wave_cancel')=1 or RRL_HAS_WRIGHT(p_actor,'pick_wave_release_reserves')=1))
   and not(v_type='PICK_PLAN' and RRL_HAS_WRIGHT(p_actor,'pick_plan_cancel')=1)
   and not(v_type='PRODUCTION_ORDER' and (RRL_HAS_WRIGHT(p_actor,'mes_raw_transfer_create')=1 or RRL_HAS_WRIGHT(p_actor,'mes_raw_transfer_cancel')=1 or RRL_HAS_WRIGHT(p_actor,'mes_raw_supply_calculate')=1))
   then raise_application_error(-20882,'DOCUMENT_RESERVATION_RELEASE_FORBIDDEN');end if;
  case v_type when 'PICK_WAVE' then select STATUS into v_status from RRL_PICK_WAVE where PICK_WAVE_ID=v_doc for update;
   when 'PICK_PLAN' then select STATUS into v_status from RRL_PICK_PLAN where PICK_PLAN_ID=v_doc for update;
   when 'PRODUCTION_ORDER' then select STATUS into v_status from RRL_PRODUCTION_ORDER where PRODUCTION_ORDER_ID=v_doc for update;
   else raise_application_error(-20869,'DOCUMENT_TYPE_INVALID');end case;
  for i in 0..a.get_size-1 loop
   x:=treat(a.get(i) as json_object_t);
   declare
 v_json_sql_2_1 number:=x.get_number('id');
begin
select * into sr from RRL_STOCK_RESERVATION where RESERVATION_ID=v_json_sql_2_1 for update;
end;
   if sr.RESERVATION_VERSION!=x.get_number('version') or sr.SOURCE_DOC_TYPE!=x.get_string('owner_type') or sr.SOURCE_DOC_ID!=x.get_number('owner_id') or sr.STATUS not in('ACTIVE','ALLOCATED','PICKING') then raise_application_error(-20890,'CLOSURE_CHANGED: document reservation');end if;
   if v.get_number('only_cancelled')=1 then
    select STATUS into v_status from RRL_PICK_WAVE_REPLENISH_TASK where PICK_WAVE_ID=v_doc and PICK_WAVE_REPLENISH_TASK_ID=sr.SOURCE_LINE_ID for update;
    if v_status not in('CANCELLED','FAILED') then raise_application_error(-20890,'CLOSURE_CHANGED: replenishment cancellation');end if;
   end if;
   if sr.RESERVATION_KIND='HARD' then
    select max(POLICY_VERSION) into v_version from RRL_STOCK_UOM_CONVERSION where ARTICUL=sr.ARTICUL and INPUT_UOM=sr.BASE_UOM and BASE_UOM=sr.BASE_UOM and NUMERATOR=1 and DENOMINATOR=1;
    if v_version is null then raise_application_error(-20868,'RESERVATION_RELEASE_BASE_POLICY_REQUIRED');end if;
    RRL_STOCK_UNIT_CORE.release_units(sr.RESERVATION_ID,sr.BASE_QTY,null,0);
    RRL_STOCK_RESERVE_CORE.release_hard(sr.RESERVATION_ID,sr.BASE_QTY,v_version,sr.SOURCE_DOC_TYPE,sr.SOURCE_DOC_ID,p_actor);
   elsif sr.RESERVATION_KIND='SOFT' then
    RRL_STOCK_CTX_API.begin_effect('RESERVATION',sr.UID_PALLET,sr.CELL,sr.RESERVATION_ID);
    declare
 v_json_sql_3_1 varchar2(32767):=d.get_object('metadata').get_string('reason');
begin
update RRL_STOCK_RESERVATION set STATUS='RELEASED',RELEASED_AT=systimestamp,RELEASED_BY=p_actor,
     RELEASE_REASON=v_json_sql_3_1,RESERVATION_VERSION=RESERVATION_VERSION+1 where RESERVATION_ID=sr.RESERVATION_ID;
end;
    RRL_STOCK_CTX_API.end_effect;
   else raise_application_error(-20869,'RESERVATION_KIND_INVALID');end if;
  end loop;
  if d.get_string('command_type')='PICK_PLAN_CANCEL' then
   if RRL_HAS_WRIGHT(p_actor,'pick_plan_cancel')!=1 then raise_application_error(-20882,'PICK_PLAN_CANCEL_FORBIDDEN');end if;
   for pt in(select PICK_TASK_ID,STATUS from RRL_PICK_TASK where PICK_PLAN_ID=v_doc order by PICK_TASK_ID for update) loop
    if pt.STATUS in('IN_PROGRESS','DONE') then raise_application_error(-20886,'PICK_PLAN_TASK_ALREADY_STARTED');end if;
   end loop;
   for task in(select w.TASK_ID,w.STATUS from RRL_WAREHOUSE_TASK w where w.TASK_SOURCE='WAVE' and (
    (w.TASK_TYPE='PICKING_MOVE' and exists(select 1 from RRL_PICK_WAVE_TASK wt join RRL_PICK_TASK pt on pt.PICK_TASK_ID=wt.PICK_TASK_ID where wt.PICK_WAVE_TASK_ID=w.SOURCE_TASK_ID and pt.PICK_PLAN_ID=v_doc))
    or (w.TASK_TYPE='REPLENISHMENT' and exists(select 1 from RRL_PICK_WAVE_REPLENISH_TASK rt join RRL_PICK_TASK pt on pt.PICK_TASK_ID=rt.PICK_TASK_ID where rt.PICK_WAVE_REPLENISH_TASK_ID=w.SOURCE_TASK_ID and pt.PICK_PLAN_ID=v_doc))) order by w.TASK_ID for update) loop
    if task.STATUS in('IN_PROGRESS','DONE') then raise_application_error(-20886,'PICK_PLAN_PHYSICAL_TASK_ALREADY_STARTED');end if;
    update RRL_WAREHOUSE_TASK set STATUS='CANCELLED' where TASK_ID=task.TASK_ID and STATUS in('PLANNED','ASSIGNED');
   end loop;
   RRL_PICKING_API.cancel_plan(v_doc,p_actor);
   update RRL_PICK_WAVE_REPLENISH_TASK set STATUS='CANCELLED',UPDATED_AT=sysdate,UPDATED_BY=p_actor where PICK_TASK_ID in(select PICK_TASK_ID from RRL_PICK_TASK where PICK_PLAN_ID=v_doc) and STATUS in('NEW','ASSIGNED','RELEASED','QUEUED','WAIT_FREE_CELL','WAIT_MINIMAX');
   update RRL_PICK_WAVE_RESERVATION set RESERVATION_STATUS='RELEASED',RELEASED_AT=sysdate,UPDATED_AT=sysdate,UPDATED_BY=p_actor where PICK_PLAN_ID=v_doc and RESERVATION_STATUS='HARD';
   update RRL_PICK_WAVE_TASK set STATUS='CANCELLED' where PICK_TASK_ID in(select PICK_TASK_ID from RRL_PICK_TASK where PICK_PLAN_ID=v_doc) and STATUS in('NEW','ASSIGNED');
  end if;
  if d.get_string('command_type') in('WAVE_CANCEL','WAVE_RELEASE') then
   for task in(select TASK_ID,STATUS from RRL_WAREHOUSE_TASK where SOURCE_DOC_TYPE='PICK_WAVE' and SOURCE_DOC_ID=v_doc order by TASK_ID for update) loop
    if task.STATUS in('IN_PROGRESS','DONE') then raise_application_error(-20886,'WAVE_PHYSICAL_TASK_ALREADY_STARTED');end if;
    update RRL_WAREHOUSE_TASK set STATUS='CANCELLED' where TASK_ID=task.TASK_ID and STATUS in('PLANNED','ASSIGNED');
   end loop;
  end if;
  if d.get_string('command_type')='WAVE_CANCEL' then
   if RRL_HAS_WRIGHT(p_actor,'pick_wave_cancel')!=1 then raise_application_error(-20882,'WAVE_CANCEL_FORBIDDEN');end if;
   RRL_PICK_WAVE_META.cancel_wave(v_doc,d.get_object('metadata').get_string('reason'),p_actor);
  elsif d.get_string('command_type')='WAVE_RELEASE' then
   if RRL_HAS_WRIGHT(p_actor,'pick_wave_release_reserves')!=1 then raise_application_error(-20882,'WAVE_RELEASE_FORBIDDEN');end if;
   RRL_PICK_WAVE_META.release_reservations(v_doc,p_actor);
  end if;
  j.put('operation_id',d.get_string('operation_id'));j.put('document_type',v_type);j.put('document_id',v_doc);j.put('released_count',a.get_size);p_result:=j.to_clob;
 end;
end;
/
