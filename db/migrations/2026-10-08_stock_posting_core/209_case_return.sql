create or replace package RRL_STOCK_CASE_RETURN_CMD authid definer accessible by(package RRL_STOCK_POSTING_API) as
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
end;
/
create or replace package body RRL_STOCK_CASE_RETURN_CMD as
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob) is
  d json_object_t:=json_object_t.parse(p_request);m json_object_t:=d.get_object('metadata');v json_object_t:=json_object_t();
  f json_array_t:=json_array_t();r json_array_t:=json_array_t();a json_array_t;x json_object_t;
  ct RRL_CASE_PICK_TASK%rowtype;tid number;target varchar2(60);lid number;uid varchar2(150);ids json_array_t;
 begin
  tid:=d.get_object('source').get_number('case_task_id');select * into ct from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=tid;
  RRL_STOCK_PLAN_HELPER.fence(f,'RELEASE','STOCK');RRL_STOCK_PLAN_HELPER.fence(f,'CONFIG','WAREHOUSE');
  RRL_STOCK_PLAN_HELPER.anchor(r,10,'OP',p_operation);
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_CASE_PICK_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(tid));
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_PICK_WAVE',RRL_STOCK_PLAN_HELPER.decimal_text(ct.PICK_WAVE_ID));
  RRL_STOCK_PLAN_HELPER.anchor(r,30,'HU','CASE:'||RRL_STOCK_PLAN_HELPER.decimal_text(tid));
  if ct.LEGACY_SBORKA_PALLET_ID is not null then RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_SBORKA_PALLETS',RRL_STOCK_PLAN_HELPER.decimal_text(ct.LEGACY_SBORKA_PALLET_ID));end if;
  a:=json_array_t.parse(RRL_STOCK_CASE_PICK_CMD.carrier_rows(tid));
  if a.get_size=0 then raise_application_error(-20886,'CASE_RETURN_EMPTY_CARRIER');end if;
  if m.get_object('destinations').get_size!=a.get_size then raise_application_error(-20871,'CASE_RETURN_ALL_LOTS_REQUIRED');end if;
  for i in 0..a.get_size-1 loop
   x:=treat(a.get(i) as json_object_t);uid:=x.get_string('uid');lid:=x.get_number('case_line');
   select CELL_CODE into target from RRL_CASE_PICK_LINE where CASE_PICK_LINE_ID=lid;
   if m.get_object('destinations').get_string(uid) is null or m.get_object('destinations').get_string(uid)!=target then raise_application_error(-20886,'CASE_RETURN_SCAN_ORIGINAL_CELL_REQUIRED');end if;
   x.put('target',target);ids:=json_array_t();
   RRL_STOCK_PLAN_HELPER.stock_closure(f,r,uid,x.get_string('article'),x.get_string('cell'),target);
   RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_CASE_PICK_LINE',RRL_STOCK_PLAN_HELPER.decimal_text(lid));
   for l in(select PICK_TASK_ID,PICK_WAVE_TASK_ID from RRL_CASE_PICK_LINE where CASE_PICK_LINE_ID=lid) loop
    RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_PICK_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(l.PICK_TASK_ID));
    RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_PICK_WAVE_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(l.PICK_WAVE_TASK_ID));
   end loop;
   for h in(select RESERVATION_ID from RRL_STOCK_RESERVATION where UID_PALLET=uid and RESERVATION_KIND='HARD'
    and STATUS in('ACTIVE','ALLOCATED','PICKING') and BASE_QTY>0 order by RESERVATION_ID) loop
    ids.append(h.RESERVATION_ID);RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_STOCK_RESERVATION',RRL_STOCK_PLAN_HELPER.decimal_text(h.RESERVATION_ID));
   end loop;
   x.put('reservations',ids);a.put(i,x);
  end loop;
  for l in(select CASE_PICK_LINE_ID,PICK_TASK_ID,PICK_WAVE_TASK_ID from RRL_CASE_PICK_LINE where CASE_PICK_TASK_ID=tid order by CASE_PICK_LINE_ID) loop
   RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_CASE_PICK_LINE',RRL_STOCK_PLAN_HELPER.decimal_text(l.CASE_PICK_LINE_ID));
   RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_PICK_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(l.PICK_TASK_ID));
   RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_PICK_WAVE_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(l.PICK_WAVE_TASK_ID));
  end loop;
  RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','STOCK.OUTBOX:'||rawtohex(sys.dbms_crypto.hash(utl_i18n.string_to_raw(p_operation,'AL32UTF8'),sys.dbms_crypto.hash_sh256)));
  v.put('task',tid);v.put('version',ct.CONTENT_VERSION);v.put('carrier',ct.SSCC);v.put('warehouse',ct.WARE_ID);v.put('stocks',a);
  v.put('before',json_array_t.parse(RRL_STOCK_CASE_PICK_CMD.carrier_rows(tid)));
  declare unused json_array_t:=json_array_t();item json_object_t;begin
   for h in(select sr.RESERVATION_ID,sr.UID_PALLET,sr.CELL,sr.BASE_UOM,sr.BASE_QTY,p.ARTICUL
    from RRL_STOCK_RESERVATION sr join RRL_PALLETS p on p.UID_PALLET=sr.UID_PALLET
    where sr.SOURCE_DOC_TYPE='PICK_WAVE' and sr.SOURCE_DOC_ID=ct.PICK_WAVE_ID
     and sr.RESERVATION_KIND='HARD' and sr.STATUS in('ACTIVE','ALLOCATED','PICKING') and sr.BASE_QTY>0
     and exists(select 1 from RRL_CASE_PICK_LINE l where l.CASE_PICK_TASK_ID=tid and l.PICK_TASK_ID=sr.SOURCE_LINE_ID)
     and not exists(select 1 from RRL_CASE_CARRIER_LOT cl where cl.LOT_UID=sr.UID_PALLET)
    order by sr.RESERVATION_ID fetch first 201 rows only) loop
    if unused.get_size=200 then raise_application_error(-20881,'CASE_RETURN_UNUSED_RESERVE_BOUND');end if;
    RRL_STOCK_PLAN_HELPER.stock_closure(f,r,h.UID_PALLET,h.ARTICUL,h.CELL,null);
    RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_STOCK_RESERVATION',RRL_STOCK_PLAN_HELPER.decimal_text(h.RESERVATION_ID));
    item:=json_object_t();item.put('id',h.RESERVATION_ID);item.put('uid',h.UID_PALLET);item.put('article',h.ARTICUL);item.put('base',h.BASE_UOM);item.put('cell',h.CELL);
    unused.append(item);
   end loop;
   for sh in(select CASE_PICK_SHORT_ID from RRL_CASE_PICK_SHORT where CASE_PICK_TASK_ID=tid order by CASE_PICK_SHORT_ID) loop
    RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_CASE_PICK_SHORT',RRL_STOCK_PLAN_HELPER.decimal_text(sh.CASE_PICK_SHORT_ID));
   end loop;
   v.put('unused',unused);
  end;
  p_policies:=f.to_clob;p_resources:=r.to_clob;p_domain:=v.to_clob;
 end;
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob) is
  d json_object_t:=json_object_t.parse(p_request);m json_object_t:=d.get_object('metadata');v json_object_t;
  ct RRL_CASE_PICK_TASK%rowtype;sr RRL_STOCK_RESERVATION%rowtype;plan clob;current_rows clob;previous_rows clob;
  tid number;sid number;uid varchar2(150);target varchar2(60);cell varchar2(60);article varchar2(160);base varchar2(20);version number;
  op varchar2(100);a json_array_t;ids json_array_t;x json_object_t;pt number;wave number;n number;qc number;
 begin
  if RRL_HAS_WRIGHT(p_actor,'case_pick_manage')!=1 then raise_application_error(-20882,'CASE_RETURN_FORBIDDEN');end if;
  op:=d.get_string('operation_id');select RESOLVED_PLAN_JSON into plan from RRL_STOCK_OPERATION where OPERATION_ID=op;
  v:=json_object_t.parse(plan).get_object('domain');tid:=v.get_number('task');
  select * into ct from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=tid for update;
  if ct.CONTENT_VERSION!=v.get_number('version') or ct.CONTENT_VERSION!=m.get_number('expected_content_version')
   or ct.SSCC!=m.get_string('scan_container') or m.get_string('scan_container') is null
   or ct.STATUS in('SHIPPED','CANCELLED','FAILED') then raise_application_error(-20886,'CASE_RETURN_STATE_SCAN_VERSION_CONFLICT');end if;
  current_rows:=RRL_STOCK_CASE_PICK_CMD.carrier_rows(tid);previous_rows:=v.get_array('before').to_clob;
  if dbms_lob.compare(current_rows,previous_rows)!=0 then raise_application_error(-20890,'CLOSURE_CHANGED: CASE return contents');end if;
  if ct.LEGACY_SBORKA_PALLET_ID is not null then
   select CONDITION into qc from RRL_SBORKA_PALLETS where ID=ct.LEGACY_SBORKA_PALLET_ID for update;
   if nvl(qc,0)>=2 then raise_application_error(-20886,'CASE_RETURN_SHIPMENT_ALREADY_POSTED');end if;
   update RRL_SBORKA_PALLETS set PROOVED=0,PROOVED_BY_SCAN=0 where ID=ct.LEGACY_SBORKA_PALLET_ID;
  end if;
  a:=v.get_array('stocks');wave:=ct.PICK_WAVE_ID;
  for i in 0..a.get_size-1 loop
   x:=treat(a.get(i) as json_object_t);uid:=x.get_string('uid');cell:=x.get_string('cell');target:=x.get_string('target');article:=x.get_string('article');base:=x.get_string('base');
   select max(POLICY_VERSION) into version from RRL_STOCK_UOM_CONVERSION where ARTICUL=article and INPUT_UOM=base and BASE_UOM=base and NUMERATOR=1 and DENOMINATOR=1;
   if version is null then raise_application_error(-20868,'CASE_RETURN_BASE_POLICY_REQUIRED');end if;
   declare lid number:=x.get_number('case_line');begin select PICK_TASK_ID into pt from RRL_CASE_PICK_LINE where CASE_PICK_LINE_ID=lid;end;
   ids:=x.get_array('reservations');
   for z in 0..ids.get_size-1 loop
    sid:=ids.get_number(z);select * into sr from RRL_STOCK_RESERVATION where RESERVATION_ID=sid for update;
    if sr.SOURCE_DOC_TYPE!='PICK_WAVE' or sr.SOURCE_DOC_ID!=wave or sr.SOURCE_LINE_ID!=pt or sr.UID_PALLET!=uid or sr.CELL!=cell
     or sr.STATUS not in('ACTIVE','ALLOCATED','PICKING') then raise_application_error(-20869,'CASE_RETURN_FOREIGN_RESERVE');end if;
    RRL_STOCK_UNIT_CORE.release_units(sid,sr.BASE_QTY,null,0);
    RRL_STOCK_RESERVE_CORE.release_hard(sid,sr.BASE_QTY,version,'PICK_WAVE',wave,p_actor);
   end loop;
   RRL_STOCK_TRANSFER_CORE.move(uid,uid,cell,target,RRL_STOCK_MATH.quantity(x.get_string('quantity')),base,version,ct.WARE_ID,p_actor,i+1,
    null,null,null,null,null,case when cell='CPT_'||RRL_STOCK_PLAN_HELPER.decimal_text(ct.WARE_ID) then 'CASE_EXIT' else 'ORDINARY' end);
   delete from RRL_CASE_CARRIER_LOT where LOT_UID=uid and CASE_PICK_TASK_ID=tid;
  end loop;
  ids:=v.get_array('unused');
  for i in 0..ids.get_size-1 loop
   x:=treat(ids.get(i) as json_object_t);sid:=x.get_number('id');
   select * into sr from RRL_STOCK_RESERVATION where RESERVATION_ID=sid for update;
   if sr.SOURCE_DOC_TYPE!='PICK_WAVE' or sr.SOURCE_DOC_ID!=wave or sr.UID_PALLET!=x.get_string('uid') or sr.CELL!=x.get_string('cell')
    or sr.STATUS not in('ACTIVE','ALLOCATED','PICKING') then raise_application_error(-20890,'CLOSURE_CHANGED: CASE unused reserve');end if;
   article:=x.get_string('article');base:=x.get_string('base');
   select max(POLICY_VERSION) into version from RRL_STOCK_UOM_CONVERSION where ARTICUL=article and INPUT_UOM=base and BASE_UOM=base and NUMERATOR=1 and DENOMINATOR=1;
   if version is null then raise_application_error(-20868,'CASE_RETURN_BASE_POLICY_REQUIRED');end if;
   RRL_STOCK_UNIT_CORE.release_units(sid,sr.BASE_QTY,null,0);
   RRL_STOCK_RESERVE_CORE.release_hard(sid,sr.BASE_QTY,version,'PICK_WAVE',wave,p_actor);
  end loop;
  update RRL_CASE_PICK_SHORT set STATUS='CANCELLED',CANCELLED_AT=systimestamp,CANCELLED_BY=p_actor
   where CASE_PICK_TASK_ID=tid and STATUS in('CREATED','PENDING_APPROVAL');
  for l in(select CASE_PICK_LINE_ID,PICK_TASK_ID,PICK_WAVE_TASK_ID from RRL_CASE_PICK_LINE where CASE_PICK_TASK_ID=tid) loop
   update RRL_CASE_PICK_LINE set STATUS='CANCELLED',UPDATED_AT=systimestamp,UPDATED_BY=p_actor where CASE_PICK_LINE_ID=l.CASE_PICK_LINE_ID;
   update RRL_PICK_TASK set STATUS='CANCELLED',UPDATED_AT=sysdate,UPDATED_BY=p_actor where PICK_TASK_ID=l.PICK_TASK_ID;
   update RRL_PICK_WAVE_TASK set STATUS='CANCELLED',UPDATED_AT=sysdate,UPDATED_BY=p_actor where PICK_WAVE_TASK_ID=l.PICK_WAVE_TASK_ID;
  end loop;
  update RRL_CASE_PICK_TASK set STATUS='CANCELLED',LEGACY_SBORKA_PALLET_ID=null,CURRENT_CELL=null,
   CONTENT_VERSION=CONTENT_VERSION+1,UPDATED_AT=systimestamp,UPDATED_BY=p_actor where CASE_PICK_TASK_ID=tid;
  v.put('operation_id',op);v.put('status','RETURNED');p_result:=v.to_clob;
 end;
end;
/
