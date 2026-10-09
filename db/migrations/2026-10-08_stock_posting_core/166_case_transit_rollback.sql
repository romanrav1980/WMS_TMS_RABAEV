declare n number;begin select count(*) into n from RRL_STOCK_OPERATION; if n>0 then raise_application_error(-20808,'POSTED_OPERATIONS_PREVENT_CODE_ROLLBACK');end if;end;
/
create or replace package RRL_STOCK_CASE_PICK_CMD authid definer
 accessible by(package RRL_STOCK_POSTING_API) as
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
end;
/

create or replace package RRL_STOCK_TRANSFER_CORE authid definer
 accessible by(package RRL_STOCK_CASE_PICK_CMD,package RRL_STOCK_INTERNAL_CMD,package RRL_STOCK_POSTING_API,package RRL_STOCK_TASK_CORE,
 package RRL_STOCK_MES_MOVEMENT_CORE,package RRL_STOCK_RECEIPT_CORE,package RRL_STOCK_MOVE_CORE,package RRL_STOCK_MES_CORE) as
 procedure move(p_uid varchar2,p_target_uid varchar2,p_from varchar2,p_to varchar2,p_qty number,
  p_uom varchar2,p_uom_version number,p_warehouse number,p_actor varchar2,p_line number,
  p_reservation number default null,p_units clob default null,p_new_reservation number default null,p_target_slot number default null,p_source_warehouse number default null,p_location_mode varchar2 default 'ORDINARY');
end;
/

create or replace package body RRL_STOCK_CASE_PICK_CMD as
 function carrier_rows(p_task number) return clob is
  a json_array_t:=json_array_t();x json_object_t;
 begin
  for r in(select h.LOT_UID,s.CELL,s.REMAIN,s.STOCK_VERSION,s.BASE_UOM,p.ARTICUL,h.CASE_PICK_LINE_ID
   from RRL_CASE_CARRIER_LOT h join RRL_REMAINS s on s.UID_POLETA=h.LOT_UID join RRL_PALLETS p on p.UID_PALLET=h.LOT_UID
   where h.CASE_PICK_TASK_ID=p_task and s.REMAIN>0 order by h.LOT_UID,s.CELL fetch first 201 rows only) loop
   if a.get_size=200 then raise_application_error(-20881,'CASE_CARRIER_LOT_BOUND');end if;
   x:=json_object_t();x.put('uid',r.LOT_UID);x.put('cell',r.CELL);x.put('quantity',RRL_STOCK_PLAN_HELPER.decimal_text(r.REMAIN));
   x.put('version',r.STOCK_VERSION);x.put('base',r.BASE_UOM);x.put('article',r.ARTICUL);x.put('case_line',r.CASE_PICK_LINE_ID);a.append(x);
  end loop;
  return a.to_clob;
 end;
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob) is
  d json_object_t:=json_object_t.parse(p_request);m json_object_t:=d.get_object('metadata');v json_object_t:=json_object_t();
  f json_array_t:=json_array_t();r json_array_t:=json_array_t();a json_array_t;chunks json_array_t:=json_array_t();x json_object_t;selected_wire clob;
  ct RRL_CASE_PICK_TASK%rowtype;l RRL_CASE_PICK_LINE%rowtype;pt RRL_PICK_TASK%rowtype;
  task_id number;line_id number;fact number;remaining number;q number;basever number;newres number;target varchar2(150);n number:=0;v_cell varchar2(60);
  type source_numbers is table of number index by varchar2(150);consumed source_numbers;steps source_numbers;
 begin
  task_id:=d.get_object('source').get_number('case_task_id');line_id:=d.get_object('source').get_number('case_line_id');
  select * into ct from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=task_id;
  select * into l from RRL_CASE_PICK_LINE where CASE_PICK_LINE_ID=line_id and CASE_PICK_TASK_ID=task_id;
  select * into pt from RRL_PICK_TASK where PICK_TASK_ID=l.PICK_TASK_ID;
  if ct.WARE_ID is null or ct.WARE_ID<1 or ct.SSCC is null or l.CELL_CODE is null or l.ARTICUL is null or l.PICK_TASK_ID is null or l.PICK_WAVE_TASK_ID is null or l.CUSTOMER_ORDER_ID is null then raise_application_error(-20887,'CASE_TASK_IDENTITY_REQUIRED');end if;
  fact:=RRL_STOCK_MATH.quantity(m.get_string('fact_qty'));remaining:=fact-nvl(l.PICKED_QTY,0);v_cell:=l.CELL_CODE;
  if remaining<=0 or fact>l.PLANNED_QTY then raise_application_error(-20886,'CASE_PICK_FACT_NOT_INCREASING_OR_EXCEEDS_PLAN');end if;
  RRL_STOCK_PLAN_HELPER.fence(f,'RELEASE','STOCK');RRL_STOCK_PLAN_HELPER.fence(f,'CONFIG','WAREHOUSE');
  RRL_STOCK_PLAN_HELPER.anchor(r,10,'OP',p_operation);
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_CASE_PICK_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(task_id));
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_CASE_PICK_LINE',RRL_STOCK_PLAN_HELPER.decimal_text(line_id));
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_PICK_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(l.PICK_TASK_ID));
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_PICK_WAVE_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(l.PICK_WAVE_TASK_ID));
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_PICK_WAVE',RRL_STOCK_PLAN_HELPER.decimal_text(l.PICK_WAVE_ID));
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_CUSTOMER_ORDER',RRL_STOCK_PLAN_HELPER.decimal_text(l.CUSTOMER_ORDER_ID));
  RRL_STOCK_PLAN_HELPER.anchor(r,30,'HU','CASE:'||RRL_STOCK_PLAN_HELPER.decimal_text(task_id));
  a:=json_array_t.parse(carrier_rows(task_id));
  for i in 0..a.get_size-1 loop
   x:=treat(a.get(i) as json_object_t);
   RRL_STOCK_PLAN_HELPER.stock_closure(f,r,x.get_string('uid'),x.get_string('article'),x.get_string('cell'),v_cell);
  end loop;
  selected_wire:=d.get_array('units').to_clob;
  for sr in(select sr.RESERVATION_ID,sr.UID_PALLET,sr.CELL,sr.BASE_QTY,sr.BASE_UOM,s.REMAIN,s.STOCK_VERSION,p.EXPIRY_DATE
   from RRL_STOCK_RESERVATION sr join RRL_REMAINS s on s.UID_POLETA=sr.UID_PALLET and s.CELL=sr.CELL
    join RRL_PALLETS p on p.UID_PALLET=sr.UID_PALLET
   where sr.SOURCE_DOC_TYPE='PICK_WAVE' and sr.SOURCE_DOC_ID=l.PICK_WAVE_ID and sr.SOURCE_LINE_ID=l.PICK_TASK_ID
    and sr.RESERVATION_KIND='HARD' and sr.STATUS in('ACTIVE','ALLOCATED','PICKING') and sr.CELL=v_cell
    and p.ARTICUL=l.ARTICUL and not exists(select 1 from RRL_CASE_CARRIER_LOT h where h.LOT_UID=sr.UID_PALLET)
   order by p.EXPIRY_DATE nulls last,sr.UID_PALLET,sr.RESERVATION_ID fetch first 201 rows only) loop
   exit when remaining=0;n:=n+1;
   if n>200 or sr.BASE_QTY is null or sr.BASE_QTY<=0 then raise_application_error(-20881,'CASE_SOURCE_RESERVATION_BOUND_OR_INVALID');end if;
   if d.get_array('units').get_size>0 then
    select nvl(sum(u.BASE_QTY),0) into q from RRL_WMS_RECEIPT_UNIT u
     join json_table(selected_wire,'$[*]' columns(K varchar2(64) path '$'))j on j.K=u.PHYSICAL_UNIT_KEY
     where u.CURRENT_UID=sr.UID_PALLET and u.CURRENT_CELL=v_cell and u.HARD_RESERVATION_ID=sr.RESERVATION_ID and u.STOCK_STATUS!='ISSUED';
    if q=0 then continue;end if;
    if q>remaining or q>sr.BASE_QTY then raise_application_error(-20884,'CASE_SCANNED_UNIT_QUANTITY_CONFLICT');end if;
   else q:=least(remaining,sr.BASE_QTY);end if;
   remaining:=remaining-q;
   select max(POLICY_VERSION) into basever from RRL_STOCK_UOM_CONVERSION where ARTICUL=l.ARTICUL and INPUT_UOM=sr.BASE_UOM and BASE_UOM=sr.BASE_UOM and NUMERATOR=1 and DENOMINATOR=1;
   if basever is null then raise_application_error(-20868,'CASE_BASE_POLICY_REQUIRED');end if;
   target:='CASELOT:'||rawtohex(sys.dbms_crypto.hash(utl_i18n.string_to_raw(p_operation,'AL32UTF8'),sys.dbms_crypto.hash_sh256))||':'||RRL_STOCK_PLAN_HELPER.decimal_text(n);
   select RRL_STOCK_RESERVATION_SQ.nextval into newres from dual;
   RRL_STOCK_PLAN_HELPER.stock_closure(f,r,sr.UID_PALLET,l.ARTICUL,v_cell,v_cell);
   RRL_STOCK_PLAN_HELPER.anchor(r,30,'HU',target);RRL_STOCK_PLAN_HELPER.anchor(r,50,'STOCK',target);
   RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_STOCK_RESERVATION',RRL_STOCK_PLAN_HELPER.decimal_text(newres));
   RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','PALLET:'||target);
   x:=json_object_t();x.put('source_uid',sr.UID_PALLET);x.put('target_uid',target);x.put('reservation',sr.RESERVATION_ID);x.put('new_reservation',newres);
   x.put('quantity',RRL_STOCK_PLAN_HELPER.decimal_text(q));x.put('base',sr.BASE_UOM);x.put('policy',basever);
   if not consumed.exists(sr.UID_PALLET) then consumed(sr.UID_PALLET):=0;steps(sr.UID_PALLET):=0;end if;
   x.put('stock_version',sr.STOCK_VERSION+steps(sr.UID_PALLET));x.put('source_p',RRL_STOCK_PLAN_HELPER.decimal_text(sr.REMAIN-consumed(sr.UID_PALLET)));
   consumed(sr.UID_PALLET):=consumed(sr.UID_PALLET)+q;steps(sr.UID_PALLET):=steps(sr.UID_PALLET)+1;chunks.append(x);
  end loop;
  if remaining!=0 then raise_application_error(-20869,'CASE_OWN_HARD_IN_PICK_CELL_INSUFFICIENT');end if;
  RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','STOCK.OUTBOX:'||rawtohex(sys.dbms_crypto.hash(utl_i18n.string_to_raw(p_operation,'AL32UTF8'),sys.dbms_crypto.hash_sh256)));
  v.put('task_id',task_id);v.put('line_id',line_id);v.put('pick_task',l.PICK_TASK_ID);v.put('wave_task',l.PICK_WAVE_TASK_ID);
  v.put('wave_id',l.PICK_WAVE_ID);v.put('customer_order',l.CUSTOMER_ORDER_ID);v.put('warehouse',ct.WARE_ID);v.put('cell',v_cell);v.put('article',l.ARTICUL);
  v.put('previous_qty',RRL_STOCK_PLAN_HELPER.decimal_text(nvl(l.PICKED_QTY,0)));v.put('planned_qty',RRL_STOCK_PLAN_HELPER.decimal_text(l.PLANNED_QTY));
  v.put('content_version',ct.CONTENT_VERSION);v.put('carrier_identifier',ct.SSCC);v.put('carrier',a);v.put('chunks',chunks);
  p_policies:=f.to_clob;p_resources:=r.to_clob;p_domain:=v.to_clob;
 end;
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob) is
  d json_object_t:=json_object_t.parse(p_request);m json_object_t:=d.get_object('metadata');v json_object_t;x json_object_t;
  a json_array_t;chunks json_array_t;facts json_array_t:=json_array_t();factx json_object_t;keys json_array_t;selected json_array_t;keyx json_element_t;unit_wire clob;
  ct RRL_CASE_PICK_TASK%rowtype;l RRL_CASE_PICK_LINE%rowtype;pt RRL_PICK_TASK%rowtype;p RRL_PALLETS%rowtype;
  plan clob;nowrows clob;oldrows clob;op varchar2(100);task_id number;line_id number;ware number;v_cell varchar2(60);article varchar2(160);
  qty number;fact number;before_qty number;ver number;stockver number;physical number;owned number;base varchar2(20);uid varchar2(150);target varchar2(150);sid number;new_sid number;
  wave_status varchar2(40);n number;posted number;line_no number:=0;unit_key varchar2(64);matched number;scan_product varchar2(4000);newstatus varchar2(20);eventid number;offline varchar2(100);
 begin
  if RRL_HAS_WRIGHT(p_actor,'case_pick_execute')!=1 then raise_application_error(-20882,'CASE_PICK_FORBIDDEN');end if;
  op:=d.get_string('operation_id');select RESOLVED_PLAN_JSON into plan from RRL_STOCK_OPERATION where OPERATION_ID=op;v:=json_object_t.parse(plan).get_object('domain');
  task_id:=v.get_number('task_id');line_id:=v.get_number('line_id');ware:=v.get_number('warehouse');v_cell:=v.get_string('cell');article:=v.get_string('article');
  declare
 v_json_sql_1_1 number:=v.get_number('wave_id');
begin
select STATUS into wave_status from RRL_PICK_WAVE where PICK_WAVE_ID=v_json_sql_1_1 for update;
end;
  if wave_status in('CANCELLED','CLOSED','DRAFT','PREVIEW') or wave_status is null then raise_application_error(-20886,'CASE_WAVE_STATE_CONFLICT');end if;
  select * into ct from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=task_id for update;
  select * into l from RRL_CASE_PICK_LINE where CASE_PICK_LINE_ID=line_id for update;
  select * into pt from RRL_PICK_TASK where PICK_TASK_ID=l.PICK_TASK_ID for update;
  if ct.WARE_ID!=ware or ct.CONTENT_VERSION!=v.get_number('content_version') or ct.SSCC!=v.get_string('carrier_identifier')
   or l.CASE_PICK_TASK_ID!=task_id or l.PICK_TASK_ID!=v.get_number('pick_task') or l.PICK_WAVE_TASK_ID!=v.get_number('wave_task')
   or l.PICK_WAVE_ID!=v.get_number('wave_id') or l.CUSTOMER_ORDER_ID!=v.get_number('customer_order') or l.CELL_CODE!=v_cell or l.ARTICUL!=article
   or RRL_STOCK_PLAN_HELPER.decimal_text(l.PLANNED_QTY)!=v.get_string('planned_qty')
   or RRL_STOCK_PLAN_HELPER.decimal_text(nvl(l.PICKED_QTY,0))!=v.get_string('previous_qty') then raise_application_error(-20890,'CLOSURE_CHANGED: case task identity');end if;
  if ct.STATUS is null or ct.STATUS not in('IN_PROGRESS','PARTIAL','WAIT_REPLENISHMENT') or l.STATUS is null or l.STATUS not in('NEW','IN_PROGRESS','PARTIAL','WAIT_REPLENISHMENT')
   or pt.TASK_TYPE is null or pt.TASK_TYPE!='CASE_PICK' or pt.STATUS is null or pt.STATUS in('DONE','CANCELLED','FAILED') or pt.CUSTOMER_ORDER_ID!=l.CUSTOMER_ORDER_ID or pt.ARTICUL!=article then raise_application_error(-20886,'CASE_TASK_LINE_STATE_CONFLICT');end if;
  if ct.ASSIGNED_TO is not null and ct.ASSIGNED_TO!=p_actor and RRL_HAS_WRIGHT(p_actor,'case_pick_manage')!=1 then raise_application_error(-20882,'CASE_TASK_ACTOR_CONFLICT');end if;
  if m.get_string('scan_cell') is null or upper(m.get_string('scan_cell'))!=upper(v_cell)
   or m.get_string('scan_container') is null or m.get_string('scan_container')!=ct.SSCC then raise_application_error(-20886,'CASE_CELL_CARRIER_SCAN_REQUIRED');end if;
  scan_product:=m.get_string('scan_product');
  select count(*) into n from RRL_ARTICULS where ACTICUL=article and scan_product in(ACTICUL,BARCODE_SHT,BARCODE_KOR,BARCODE_BL);
  if n!=1 and d.get_array('units').get_size=0 then raise_application_error(-20886,'CASE_PRODUCT_SCAN_CONFLICT');end if;
  nowrows:=carrier_rows(task_id);a:=v.get_array('carrier');oldrows:=a.to_clob;
  if dbms_lob.compare(nowrows,oldrows)!=0 then raise_application_error(-20890,'CLOSURE_CHANGED: case carrier stock');end if;
  before_qty:=nvl(l.PICKED_QTY,0);posted:=0;
  for i in 0..a.get_size-1 loop
   x:=treat(a.get(i) as json_object_t);
   if x.get_number('case_line')=line_id then posted:=posted+RRL_STOCK_MATH.quantity(x.get_string('quantity'));end if;
  end loop;
  if posted!=before_qty then raise_application_error(-20886,'CASE_PRIOR_FACT_WITHOUT_PHYSICAL_POSTING');end if;
  fact:=RRL_STOCK_MATH.quantity(m.get_string('fact_qty'));
  if fact<=before_qty or fact>l.PLANNED_QTY then raise_application_error(-20886,'CASE_PICK_FACT_CONFLICT');end if;
  keys:=d.get_array('units');unit_wire:=keys.to_clob;matched:=0;
  -- Move already picked contents with their carrier to the newly scanned pick v_cell.
  for i in 0..a.get_size-1 loop
   x:=treat(a.get(i) as json_object_t);uid:=x.get_string('uid');
   if ct.CURRENT_CELL is null or ct.CURRENT_CELL!=x.get_string('cell') then raise_application_error(-20887,'CASE_CARRIER_LOCATION_CONFLICT');end if;
   if x.get_string('cell')!=v_cell then
    base:=x.get_string('base');
    declare
 v_json_sql_2_1 varchar2(32767):=x.get_string('article');
begin
select max(POLICY_VERSION) into ver from RRL_STOCK_UOM_CONVERSION where ARTICUL=v_json_sql_2_1 and INPUT_UOM=base and BASE_UOM=base and NUMERATOR=1 and DENOMINATOR=1;
end;
    line_no:=line_no+1;
    RRL_STOCK_TRANSFER_CORE.move(uid,uid,x.get_string('cell'),v_cell,RRL_STOCK_MATH.quantity(x.get_string('quantity')),base,ver,ware,p_actor,line_no);
   end if;
  end loop;
  chunks:=v.get_array('chunks');
  for i in 0..chunks.get_size-1 loop
   x:=treat(chunks.get(i) as json_object_t);uid:=x.get_string('source_uid');target:=x.get_string('target_uid');
   qty:=RRL_STOCK_MATH.quantity(x.get_string('quantity'));base:=x.get_string('base');sid:=x.get_number('reservation');new_sid:=x.get_number('new_reservation');
   select REMAIN,STOCK_VERSION into physical,stockver from RRL_REMAINS where UID_POLETA=uid and CELL=v_cell;
   if stockver!=x.get_number('stock_version') or RRL_STOCK_PLAN_HELPER.decimal_text(physical)!=x.get_string('source_p') then raise_application_error(-20890,'CLOSURE_CHANGED: case source stock');end if;
   select BASE_QTY into owned from RRL_STOCK_RESERVATION where RESERVATION_ID=sid and UID_PALLET=uid and CELL=v_cell
    and SOURCE_DOC_TYPE='PICK_WAVE' and SOURCE_DOC_ID=l.PICK_WAVE_ID and SOURCE_LINE_ID=l.PICK_TASK_ID
    and RESERVATION_KIND='HARD' and STATUS in('ACTIVE','ALLOCATED','PICKING');
   if owned<qty then raise_application_error(-20869,'CASE_OWN_HARD_INSUFFICIENT');end if;
   select max(POLICY_VERSION) into ver from RRL_STOCK_UOM_CONVERSION where ARTICUL=article and INPUT_UOM=base and BASE_UOM=base and NUMERATOR=1 and DENOMINATOR=1;
   if ver is null or ver!=x.get_number('policy') then raise_application_error(-20890,'CLOSURE_CHANGED: case UOM policy');end if;
   selected:=json_array_t();
   for selected_unit in(select u.PHYSICAL_UNIT_KEY from RRL_WMS_RECEIPT_UNIT u
    join json_table(unit_wire,'$[*]' columns(K varchar2(64) path '$'))j on j.K=u.PHYSICAL_UNIT_KEY
    where u.CURRENT_UID=uid and u.CURRENT_CELL=v_cell and u.HARD_RESERVATION_ID=sid and u.STOCK_STATUS!='ISSUED'
    order by u.PHYSICAL_UNIT_KEY) loop
    selected.append(selected_unit.PHYSICAL_UNIT_KEY);matched:=matched+1;
   end loop;
   select count(*) into n from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=uid and CURRENT_CELL=v_cell and STOCK_STATUS!='ISSUED';
   if n>0 and selected.get_size=0 then raise_application_error(-20884,'CASE_MARKED_UNIT_SCANS_REQUIRED');end if;
   select * into p from RRL_PALLETS where UID_PALLET=uid;
   if p.ARTICUL!=article then raise_application_error(-20887,'CASE_LOT_ARTICLE_CONFLICT');end if;
   p.STOCK_ORIGIN_UID:=nvl(p.STOCK_ORIGIN_UID,p.UID_PALLET);p.CREATED_BY_STOCK_OP:=op;p.UID_PALLET:=target;p.SSCC:=null;p.PRINTED:=0;
   if p.WEIGHT_BRUTTO is not null then p.WEIGHT_BRUTTO:=p.WEIGHT_BRUTTO*qty/nullif(p.UNIT_COUNT,0);end if;
   p.UNIT_COUNT:=qty;insert into RRL_PALLETS values p;
   line_no:=line_no+1;
   RRL_STOCK_TRANSFER_CORE.move(uid,target,v_cell,v_cell,qty,base,ver,ware,p_actor,line_no,sid,
    case when selected.get_size>0 then selected.to_clob else null end,new_sid);
   insert into RRL_CASE_CARRIER_LOT(LOT_UID,CASE_PICK_TASK_ID,CASE_PICK_LINE_ID,CREATED_OPERATION,CREATED_BY)
    values(target,task_id,line_id,op,p_actor);
   factx:=json_object_t();factx.put('uid',target);factx.put('source_uid',uid);factx.put('quantity',x.get_string('quantity'));factx.put('unit',base);facts.append(factx);
  end loop;
  if matched!=keys.get_size then raise_application_error(-20884,'CASE_SELECTED_UNIT_NOT_OWNED');end if;
  newstatus:=case when fact=l.PLANNED_QTY then 'PICKED' else 'PARTIAL' end;offline:=m.get_string('offline_event_id');
  update RRL_CASE_PICK_LINE set PICKED_QTY=fact,STATUS=newstatus,LAST_OFFLINE_EVENT_ID=offline,
   STARTED_AT=nvl(STARTED_AT,systimestamp),DONE_AT=case when newstatus='PICKED' then systimestamp else DONE_AT end,UPDATED_AT=systimestamp,UPDATED_BY=p_actor where CASE_PICK_LINE_ID=line_id;
  update RRL_PICK_TASK set FACT_QTY=fact,STATUS=case when newstatus='PICKED' then 'DONE' else 'IN_PROGRESS' end,
   DONE_AT=case when newstatus='PICKED' then sysdate else DONE_AT end,DONE_BY=p_actor,UPDATED_AT=sysdate,UPDATED_BY=p_actor where PICK_TASK_ID=l.PICK_TASK_ID;
  update RRL_PICK_WAVE_TASK set FACT_QTY=fact,STATUS=case when newstatus='PICKED' then 'DONE' else 'IN_PROGRESS' end,
   DONE_AT=case when newstatus='PICKED' then sysdate else DONE_AT end,DONE_BY=p_actor,UPDATED_AT=sysdate,UPDATED_BY=p_actor where PICK_WAVE_TASK_ID=l.PICK_WAVE_TASK_ID;
  update RRL_CASE_PICK_TASK t set CURRENT_CELL=v_cell,CONTENT_VERSION=CONTENT_VERSION+1,
   (TOTAL_LINES,PICKED_LINES,PLANNED_QTY,PICKED_QTY)=(select count(*),nvl(sum(case when STATUS in('PICKED','SHORT_PICKED','CANCELLED') then 1 else 0 end),0),nvl(sum(PLANNED_QTY),0),nvl(sum(PICKED_QTY),0) from RRL_CASE_PICK_LINE z where z.CASE_PICK_TASK_ID=task_id),
   UPDATED_AT=systimestamp,UPDATED_BY=p_actor where t.CASE_PICK_TASK_ID=task_id;
  select RRL_CASE_PICK_EVENT_SQ.nextval into eventid from dual;
  insert into RRL_CASE_PICK_EVENT(CASE_PICK_EVENT_ID,CASE_PICK_TASK_ID,CASE_PICK_LINE_ID,EVENT_TYPE,OFFLINE_EVENT_ID,PAYLOAD_JSON,CREATED_BY)
   values(eventid,task_id,line_id,'LINE_CONFIRMED',offline,p_request,p_actor);
  v:=json_object_t();v.put('operation_id',op);v.put('case_pick_task_id',task_id);v.put('case_pick_line_id',line_id);v.put('status',newstatus);
  v.put('fact_qty',RRL_STOCK_PLAN_HELPER.decimal_text(fact));v.put('carrier_identifier',ct.SSCC);v.put('cell',v_cell);v.put('lots',facts);p_result:=v.to_clob;
 end;
end;
/

create or replace package body RRL_STOCK_TRANSFER_CORE as
 procedure require_row(p_id number) is
 begin
  begin RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_STOCK_RESERVATION',
   RRL_STOCK_PLAN_HELPER.decimal_text(p_id)));
  exception when others then
   if sqlcode=-20850 then raise_application_error(-20890,'CLOSURE_CHANGED: reservation set');else raise;end if;
  end;
 end;
 procedure move(p_uid varchar2,p_target_uid varchar2,p_from varchar2,p_to varchar2,p_qty number,
  p_uom varchar2,p_uom_version number,p_warehouse number,p_actor varchar2,p_line number,
  p_reservation number default null,p_units clob default null,p_new_reservation number default null,p_target_slot number default null,p_source_warehouse number default null,p_location_mode varchar2 default 'ORDINARY') is
  v_p number;v_h number;v_ver number;v_uom varchar2(20);v_article varchar2(160);v_sum number;
  v_hmove number:=0;v_event number;v_units number;v_unit_qty number;v_selected number;v_expected number;
  v_r RRL_STOCK_RESERVATION%rowtype;v_result_reservation number;
 begin
  if p_uid is null or p_target_uid is null or p_from is null or p_to is null or (p_from=p_to and p_uid=p_target_uid)
   or p_qty is null or p_qty<=0 then raise_application_error(-20886,'TRANSFER_CONTRACT_INVALID');end if;
  RRL_STOCK_LOCK_API.assert_held(30,RRL_STOCK_LOCK_API.resource_key('HU',p_uid));
  RRL_STOCK_LOCK_API.assert_held(50,RRL_STOCK_LOCK_API.resource_key('STOCK',p_uid));
  RRL_STOCK_LOCK_API.assert_held(30,RRL_STOCK_LOCK_API.resource_key('HU',p_target_uid));
  RRL_STOCK_LOCK_API.assert_held(50,RRL_STOCK_LOCK_API.resource_key('STOCK',p_target_uid));
  if p_location_mode='PUTAWAY' then
   RRL_STOCK_LOCATION_CORE.assert_receiving(p_from,nvl(p_source_warehouse,p_warehouse));
   RRL_STOCK_LOCATION_CORE.assert_ordinary(p_to,p_warehouse,'TARGET');
  elsif p_location_mode='QUARANTINE' then
   if RRL_HAS_WRIGHT(p_actor,'QUARANTINE_MOVE')!=1 then raise_application_error(-20882,'QUARANTINE_MOVE_FORBIDDEN');end if;
   RRL_STOCK_LOCATION_CORE.assert_quarantine(p_from,nvl(p_source_warehouse,p_warehouse));
   RRL_STOCK_LOCATION_CORE.assert_quarantine(p_to,p_warehouse);
  elsif p_location_mode='ORDINARY' then
   RRL_STOCK_LOCATION_CORE.assert_ordinary(p_from,nvl(p_source_warehouse,p_warehouse),'SOURCE');
   RRL_STOCK_LOCATION_CORE.assert_ordinary(p_to,p_warehouse,'TARGET');
  else raise_application_error(-20878,'TRANSFER_LOCATION_MODE_INVALID');end if;
  select REMAIN,HARD_RESERVED_BASE,STOCK_VERSION,BASE_UOM into v_p,v_h,v_ver,v_uom
   from RRL_REMAINS where UID_POLETA=p_uid and CELL=p_from;
  if v_uom is null or v_uom!=p_uom or p_qty>v_p then raise_application_error(-20868,'TRANSFER_STOCK_CONFLICT');end if;
  select ARTICUL into v_article from RRL_PALLETS where UID_PALLET=p_uid;
  select count(*) into v_sum from RRL_STOCK_RESERVATION where UID_PALLET=p_uid and CELL=p_from and RESERVATION_KIND='HARD' and STATUS in('ACTIVE','ALLOCATED','PICKING') and (BASE_QTY is null or BASE_QTY<=0 or BASE_UOM is null or BASE_UOM!=p_uom);
  if v_sum>0 then raise_application_error(-20869,'HARD_BASE_IDENTITY_CONFLICT');end if;
  select nvl(sum(BASE_QTY),0) into v_sum from RRL_STOCK_RESERVATION where UID_PALLET=p_uid
   and CELL=p_from and RESERVATION_KIND='HARD' and STATUS in('ACTIVE','ALLOCATED','PICKING');
  if v_sum!=v_h then raise_application_error(-20869,'HARD_MATERIALIZATION_CONFLICT');end if;
  for r in(select RESERVATION_ID from RRL_STOCK_RESERVATION where UID_PALLET=p_uid and CELL=p_from
   and RESERVATION_KIND='HARD' and STATUS in('ACTIVE','ALLOCATED','PICKING')) loop require_row(r.RESERVATION_ID);end loop;
  if p_qty=v_p then
   v_hmove:=v_h;
  elsif p_reservation is not null then
   require_row(p_reservation);
   select * into v_r from RRL_STOCK_RESERVATION where RESERVATION_ID=p_reservation;
   if v_r.UID_PALLET is null or v_r.UID_PALLET!=p_uid or v_r.CELL is null or v_r.CELL!=p_from
    or v_r.RESERVATION_KIND!='HARD' or v_r.STATUS not in('ACTIVE','ALLOCATED','PICKING')
    or v_r.BASE_QTY is null or v_r.BASE_QTY<=0 then raise_application_error(-20869,'TRANSFER_RESERVATION_CONFLICT');end if;
   v_hmove:=least(p_qty,v_r.BASE_QTY);
   if p_qty-v_hmove>v_p-v_h then raise_application_error(-20869,'TRANSFER_FREE_PORTION_INSUFFICIENT');end if;
  elsif p_qty>v_p-v_h then raise_application_error(-20869,'TRANSFER_UNRESERVED_INSUFFICIENT');end if;
  if p_target_uid!=p_uid then
   declare t RRL_PALLETS%rowtype;s RRL_PALLETS%rowtype;
   begin
    select * into s from RRL_PALLETS where UID_PALLET=p_uid;
    select * into t from RRL_PALLETS where UID_PALLET=p_target_uid;
    if t.ARTICUL!=s.ARTICUL or t.PRIHOD_NAKLAD_ID!=s.PRIHOD_NAKLAD_ID
     or (t.EXPIRY_DATE!=s.EXPIRY_DATE or (t.EXPIRY_DATE is null and s.EXPIRY_DATE is not null) or (t.EXPIRY_DATE is not null and s.EXPIRY_DATE is null)) or (t.PRODUCED_DATE!=s.PRODUCED_DATE or (t.PRODUCED_DATE is null and s.PRODUCED_DATE is not null) or (t.PRODUCED_DATE is not null and s.PRODUCED_DATE is null))
     or (t.PROD_BATCH_ID!=s.PROD_BATCH_ID or (t.PROD_BATCH_ID is null and s.PROD_BATCH_ID is not null) or (t.PROD_BATCH_ID is not null and s.PROD_BATCH_ID is null)) then raise_application_error(-20887,'TRANSFER_LOT_IDENTITY_CONFLICT');end if;
   end;
  end if;
  select count(*),nvl(sum(BASE_QTY),0) into v_units,v_unit_qty from RRL_WMS_RECEIPT_UNIT
   where CURRENT_UID=p_uid and CURRENT_CELL=p_from and STOCK_STATUS!='ISSUED';
  if v_units>0 then
   -- CURRENT_UID is the warehouse physical authority. Published regulatory
   -- aggregations are retained; the coordinator queues composition before/after
   -- in the same transaction, for asynchronous regulatory reaggregation.
   -- Birth UID/code and external acknowledgement are never rewritten here.
   if v_unit_qty!=v_p then raise_application_error(-20884,'COMPOSITION_STOCK_CONFLICT');end if;
   if p_qty!=v_p and p_units is null then raise_application_error(-20884,'PARTIAL_UNIT_SELECTION_REQUIRED');end if;
   select count(*),nvl(sum(u.BASE_QTY),0) into v_selected,v_unit_qty from RRL_WMS_RECEIPT_UNIT u
    where u.CURRENT_UID=p_uid and u.CURRENT_CELL=p_from and u.STOCK_STATUS!='ISSUED' and
     (p_units is null or exists(select 1 from json_table(p_units,'$[*]' columns(K varchar2(64) path '$'))j where j.K=u.PHYSICAL_UNIT_KEY));
   if v_unit_qty!=p_qty then raise_application_error(-20884,'SELECTED_UNIT_QUANTITY_CONFLICT');end if;
   if p_units is not null then
    select count(distinct K) into v_expected from json_table(p_units,'$[*]' columns(K varchar2(64) path '$'));
    if v_expected!=v_selected then raise_application_error(-20884,'SELECTED_UNIT_IDENTITY_CONFLICT');end if;
   end if;
   if p_qty!=v_p and p_reservation is not null then
    select nvl(sum(u.BASE_QTY),0) into v_unit_qty from RRL_WMS_RECEIPT_UNIT u
     where u.CURRENT_UID=p_uid and u.CURRENT_CELL=p_from and u.HARD_RESERVATION_ID=p_reservation and
      (p_units is null or exists(select 1 from json_table(p_units,'$[*]' columns(K varchar2(64) path '$'))j where j.K=u.PHYSICAL_UNIT_KEY));
    if v_unit_qty!=v_hmove then raise_application_error(-20869,'RESERVED_UNIT_SELECTION_CONFLICT');end if;
   end if;
   for u in(select PHYSICAL_UNIT_KEY,HARD_RESERVATION_ID from RRL_WMS_RECEIPT_UNIT
    where CURRENT_UID=p_uid and CURRENT_CELL=p_from and STOCK_STATUS!='ISSUED' and
     (p_units is null or exists(select 1 from json_table(p_units,'$[*]' columns(K varchar2(64) path '$'))j where j.K=PHYSICAL_UNIT_KEY))) loop
    begin RRL_STOCK_LOCK_API.assert_held(60,RRL_STOCK_LOCK_API.resource_key('UNIT',u.PHYSICAL_UNIT_KEY));
    exception when others then if sqlcode=-20850 then raise_application_error(-20890,'CLOSURE_CHANGED: unit set');else raise;end if;end;
    if u.HARD_RESERVATION_ID is not null and p_qty!=v_p and
      (p_reservation is null or u.HARD_RESERVATION_ID!=p_reservation) then raise_application_error(-20869,'UNIT_RESERVED_BY_OTHER_OWNER');end if;
   end loop;
  else
   select nvl(max(MARKING_REQUIRED),0) into v_expected from RRL_SKU_RECEIPT_POLICY where ARTICUL=v_article;
   if v_expected=1 then raise_application_error(-20884,'MARKED_BINDING_REQUIRED');end if;
  end if;
  RRL_STOCK_BALANCE_CORE.apply_delta(p_uid,p_from,-p_qty,-v_hmove,p_uom,p_uom_version,v_ver);
  RRL_STOCK_BALANCE_CORE.apply_delta(p_target_uid,p_to,p_qty,v_hmove,p_uom,p_uom_version);
  if p_qty=v_p then
   for c in(select TASK_ID from RRL_RECEIPT_SLOT_CLAIM where UID_PALLET=p_uid and CELL=p_from and STATUS='OCCUPIED') loop
    RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_RECEIPT_SLOT_CLAIM',RRL_STOCK_PLAN_HELPER.decimal_text(c.TASK_ID)));
    delete from RRL_RECEIPT_SLOT_CLAIM where TASK_ID=c.TASK_ID and STATUS='OCCUPIED';
   end loop;
  end if;
  if v_hmove>0 then
   for r in(select RESERVATION_ID,BASE_QTY from RRL_STOCK_RESERVATION
    where UID_PALLET=p_uid and CELL=p_from and RESERVATION_KIND='HARD' and STATUS in('ACTIVE','ALLOCATED','PICKING')
     and (p_qty=v_p or RESERVATION_ID=p_reservation)) loop
    RRL_STOCK_RESERVE_CORE.move_coverage(r.RESERVATION_ID,p_new_reservation,p_target_uid,p_to,p_warehouse,
     case when p_qty=v_p then r.BASE_QTY else v_hmove end,p_target_slot,p_actor,v_result_reservation);
    RRL_STOCK_CTX_API.begin_effect('UNIT',p_uid,p_from);
    update RRL_WMS_RECEIPT_UNIT set HARD_RESERVATION_ID=v_result_reservation,UNIT_VERSION=UNIT_VERSION+1
     where CURRENT_UID=p_uid and CURRENT_CELL=p_from and HARD_RESERVATION_ID=r.RESERVATION_ID and
      (p_units is null or exists(select 1 from json_table(p_units,'$[*]' columns(K varchar2(64) path '$'))j where j.K=PHYSICAL_UNIT_KEY));
    RRL_STOCK_CTX_API.end_effect;
   end loop;
  end if;
  RRL_STOCK_CTX_API.begin_effect('UNIT',p_uid,p_from);
  update RRL_WMS_RECEIPT_UNIT set CURRENT_UID=p_target_uid,CURRENT_CELL=p_to,UNIT_VERSION=UNIT_VERSION+1
   where CURRENT_UID=p_uid and CURRENT_CELL=p_from and STOCK_STATUS!='ISSUED' and
    (p_units is null or exists(select 1 from json_table(p_units,'$[*]' columns(K varchar2(64) path '$'))j where j.K=PHYSICAL_UNIT_KEY));
  RRL_STOCK_CTX_API.end_effect;
  if p_target_uid=p_uid then
   RRL_STOCK_BALANCE_CORE.write_move(p_uid,p_from,p_to,p_qty,p_uom,p_uom_version,p_line,p_actor,v_event);
  else
  RRL_STOCK_BALANCE_CORE.write_leg(p_uid,p_from,null,-p_qty,p_uom,p_uom_version,p_line,1,2,p_actor,v_event);
  RRL_STOCK_BALANCE_CORE.write_leg(p_target_uid,null,p_to,p_qty,p_uom,p_uom_version,p_line,2,2,p_actor,v_event);
  end if;
 end;
end;
/
