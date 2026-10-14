raise SystemExit("Retired authoring draft: use checked-in final SQL/fixture sources; do not regenerate over verified fixes.")
from pathlib import Path
import json,re
f=Path("db/migrations/2026-10-11_ni052_unload");out={}
out[str(f/"001_schema.sql")]="""create table RRL_TT_UNLOAD_FACT(
 OPERATION_ID varchar2(100)primary key references RRL_STOCK_OPERATION(OPERATION_ID),
 LOAD_OPERATION_ID varchar2(100)not null unique references RRL_TT_HU_LOAD_FACT(LOAD_OPERATION_ID),
 TT_ID number not null references RRL_TRANSPORT_TASK(ID),
 CASE_PICK_TASK_ID number not null references RRL_CASE_PICK_TASK(CASE_PICK_TASK_ID),
 WARE_ID number not null references RRL_WARES(ID),
 CELL_CODE varchar2(60)not null,
 COMPOSITION_JSON clob not null check(COMPOSITION_JSON is json),
 REASON varchar2(1000)not null,
 CREATED_BY varchar2(50)not null,CREATED_AT timestamp with time zone default systimestamp not null);
"""
out[str(f/"002_command.sql")]="""create or replace package RRL_STOCK_UNLOAD_CMD authid definer accessible by(package RRL_STOCK_POSTING_API) as
 procedure assert_scope(p_load varchar2,p_actor varchar2);
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
end;
/
create or replace package body RRL_STOCK_UNLOAD_CMD as
 procedure assert_scope(p_load varchar2,p_actor varchar2)is n number;
 begin
  select count(*)into n from RRL_TT_HU_LOAD_FACT lf join RUSERS u on u.ID=p_actor
   where lf.LOAD_OPERATION_ID=p_load and nvl(u.DELETED,0)=0 and RRL_HAS_WRIGHT(u.ID,'stock_posting_shipping')=1
    and(upper(trim(u.USER_GROUP))='GLOBAL_ADMIN'or u.WARE_ID=lf.WARE_ID);
  if n!=1 then raise_application_error(-20882,'UNLOAD_CURRENT_WARE_ACTOR_REQUIRED');end if;
 end;
 procedure source_state(p_load varchar2,p_metadata json_object_t,p_lf out RRL_TT_HU_LOAD_FACT%rowtype,p_domain out json_object_t)is
  wire clob;kind_name varchar2(80);state_name varchar2(20);ct RRL_CASE_PICK_TASK%rowtype;tree json_object_t;root_node json_object_t;n number;trip RRL_TRANSPORT_TASK%rowtype;cell_ware number;blocked number;
 begin
  select *into p_lf from RRL_TT_HU_LOAD_FACT where LOAD_OPERATION_ID=p_load;
  if p_lf.STATUS!='LOADED'or p_lf.DEPARTURE_OPERATION_ID is not null or p_lf.DEPARTED_AT is not null or p_lf.CUSTODY_RELEASE_OPERATION_ID is not null then raise_application_error(-20886,'UNLOAD_PREDEPARTURE_LOADED_REQUIRED');end if;
  select COMMAND_TYPE,STATE,RESOLVED_PLAN_JSON into kind_name,state_name,wire from RRL_STOCK_OPERATION where OPERATION_ID=p_load;
  if kind_name!='LOAD_SHIPMENT'or state_name!='APPLIED'or p_lf.ROOT_CASE_TASK_ID is null or p_lf.ROOT_UID is not null then raise_application_error(-20886,'UNLOAD_STANDALONE_CASE_REQUIRED');end if;
  p_domain:=json_object_t.parse(wire).get_object('domain').get_object('shipment').get_object('domain');
  if p_domain.has('interwarehouse_onward_source')or p_domain.has('supplier_return_source')then raise_application_error(-20886,'UNLOAD_SPECIAL_CUSTODY_DECISION_REQUIRED');end if;
  tree:=json_object_t.parse(p_lf.COMPOSITION_JSON);root_node:=treat(tree.get_array('nodes').get(0)as json_object_t);
  if root_node.get_string('kind')!='CASE'or tree.get_array('links').get_size!=0 or p_domain.get_number('case_task')!=p_lf.ROOT_CASE_TASK_ID then raise_application_error(-20886,'UNLOAD_STANDALONE_CASE_REQUIRED');end if;
  select *into ct from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=p_lf.ROOT_CASE_TASK_ID;
  if ct.STATUS!='SHIPPED'or ct.SHIPPED_OPERATION!=p_load or ct.WARE_ID!=p_lf.WARE_ID or ct.CONTENT_VERSION!=p_lf.CONTENT_VERSION+1 then raise_application_error(-20886,'UNLOAD_ORIGINAL_CASE_STATE_REQUIRED');end if;
  if p_metadata.get_number('expected_version')is null or p_metadata.get_number('expected_version')!=p_lf.CONTENT_VERSION
    or p_metadata.get_string('scan_container')is null or p_metadata.get_string('scan_container')!=root_node.get_string('sscc')
    or p_metadata.get_string('scan_cell')is null or p_metadata.get_string('scan_cell')!=tree.get_string('cell')
    or p_metadata.get_string('scan_vehicle')is null or p_metadata.get_string('scan_vehicle')!=p_lf.VEHICLE_NUMBER
    or p_metadata.get_string('scan_dock')is null or p_metadata.get_string('scan_dock')!=p_lf.DOCK
    or trim(p_metadata.get_string('reason'))is null or length(p_metadata.get_string('reason'))>1000 then raise_application_error(-20886,'UNLOAD_ORIGINAL_PLACE_VEHICLE_DOCK_CELL_SCAN_REQUIRED');end if;
  select *into trip from RRL_TRANSPORT_TASK where ID=p_lf.TT_ID;
  if trip.CONDITION=unistr('\041E\0442\0433\0440\0443\0436\0435\043D')or nvl(trip.DELETED,0)!=0 or trip.PAY_ORDER_ID is not null or trip.TRANSPORT!=p_lf.VEHICLE_NUMBER or trip.DOCK!=p_lf.DOCK then raise_application_error(-20886,'UNLOAD_CURRENT_UNDEPARTED_TRIP_REQUIRED');end if;
  select WARE_ID,nvl(BLOCKED_FOR_REMAINS,0)into cell_ware,blocked from RRL_CELLS where CELL=tree.get_string('cell');
  if cell_ware!=p_lf.WARE_ID or blocked!=0 then raise_application_error(-20886,'UNLOAD_ORIGINAL_CELL_CURRENTLY_BLOCKED');end if;
  select count(*)into n from RRL_PICK_WAVE where PICK_WAVE_ID=ct.PICK_WAVE_ID and STATUS='LAUNCHED';
  if n!=1 then raise_application_error(-20886,'UNLOAD_ACTIVE_CASE_WAVE_REQUIRED');end if;
  select count(*)into n from RRL_TARE_OFFER_BOOK where LOAD_OPERATION_ID=p_load;
  if n>0 then raise_application_error(-20886,'UNLOAD_TARE_HANDOVER_DECISION_REQUIRED');end if;
  select count(*)into n from RRL_TT_HU_LOAD_ST where LOAD_OPERATION_ID=p_load and ACTIVE_FLAG=1 and SBORKA_PALLET_ID=ct.LEGACY_SBORKA_PALLET_ID;
  if n!=1 then raise_application_error(-20886,'UNLOAD_ORIGINAL_ACTIVE_ST_REQUIRED');end if;
 end;
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob)is
  d json_object_t:=json_object_t.parse(p_request);m json_object_t:=d.get_object('metadata');v json_object_t:=json_object_t();sd json_object_t;
  lf RRL_TT_HU_LOAD_FACT%rowtype;legs json_array_t;restored json_array_t:=json_array_t();x json_object_t;y json_object_t;
  f json_array_t:=json_array_t();r json_array_t:=json_array_t();load_id varchar2(100):=d.get_object('source').get_string('load_operation_id');
  uid_text varchar2(150);cell_text varchar2(60);qty number;physical number;held number;version_no number;new_res number;n number;signed_total number;sid number;case_id number;
 begin
  assert_scope(load_id,d.get_string('actor'));source_state(load_id,m,lf,sd);legs:=sd.get_array('legs');case_id:=lf.ROOT_CASE_TASK_ID;sid:=sd.get_number('document_id');
  if legs.get_size<1 or legs.get_size>200 then raise_application_error(-20881,'UNLOAD_LEG_BOUND_1_200');end if;
  RRL_STOCK_PLAN_HELPER.fence(f,'RELEASE','STOCK');RRL_STOCK_PLAN_HELPER.fence(f,'CONFIG','WAREHOUSE');
  RRL_STOCK_PLAN_HELPER.anchor(r,10,'OP',p_operation);
  RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','UNLOAD.LOAD:'||load_id);
  RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','STOCK.OUTBOX:'||rawtohex(sys.dbms_crypto.hash(utl_i18n.string_to_raw(p_operation,'AL32UTF8'),sys.dbms_crypto.hash_sh256)));
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_TRANSPORT_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(lf.TT_ID));
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_TT_HU_LOAD_FACT',load_id);
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_TT_UNLOAD_FACT',p_operation);
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_TT_HU_LOAD_ST',load_id||':'||RRL_STOCK_PLAN_HELPER.decimal_text(sid));
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_SBORKA_PALLETS',RRL_STOCK_PLAN_HELPER.decimal_text(sid));
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_CASE_PICK_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(case_id));
  RRL_STOCK_PLAN_HELPER.anchor(r,30,'HU','CASE:'||RRL_STOCK_PLAN_HELPER.decimal_text(case_id));
  for ff in(select FULFILLMENT_ID,CUSTOMER_ORDER_ID,PICKED_CASE_TASK_ID from RRL_CUSTOMER_ORDER_FULFILLMENT where LEGACY_SBORKA_PALLET_ID=sid and STATUS='SHIPPED'and SHIPPED_OPERATION_ID=load_id order by FULFILLMENT_ID)loop
   n:=nvl(n,0)+1;if n>1 or ff.PICKED_CASE_TASK_ID!=case_id then raise_application_error(-20886,'UNLOAD_ORIGINAL_FULFILLMENT_REQUIRED');end if;
   RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_CUSTOMER_ORDER_FULFILLMENT',RRL_STOCK_PLAN_HELPER.decimal_text(ff.FULFILLMENT_ID));
   RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_CUSTOMER_ORDER',RRL_STOCK_PLAN_HELPER.decimal_text(ff.CUSTOMER_ORDER_ID));
  end loop;
  if nvl(n,0)!=1 then raise_application_error(-20886,'UNLOAD_ORIGINAL_FULFILLMENT_REQUIRED');end if;
  for i in 0..legs.get_size-1 loop
   x:=treat(legs.get(i)as json_object_t);uid_text:=x.get_string('uid');cell_text:=x.get_string('cell');qty:=RRL_STOCK_MATH.quantity(x.get_string('quantity'));
   if cell_text!=m.get_string('scan_cell')or x.get_number('reservation_id')is null then raise_application_error(-20886,'UNLOAD_ORIGINAL_RESERVED_CASE_LEAF_REQUIRED');end if;
   select REMAIN,HARD_RESERVED_BASE,STOCK_VERSION into physical,held,version_no from RRL_REMAINS where UID_POLETA=uid_text and CELL=cell_text;
   if physical!=0 or held!=0 then raise_application_error(-20886,'UNLOAD_ORIGINAL_LEAF_NOT_EMPTY');end if;
   select count(*)into n from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=uid_text;
   if n>0 then raise_application_error(-20886,'UNLOAD_CAPTURED_UNIT_RECOVERY_REQUIRED');end if;
   select count(*)into n from RRL_SKU_RECEIPT_POLICY where ARTICUL=x.get_string('article')and(MARKING_REQUIRED=1 or SERIALIZED_WEIGHT_BOXES=1);
   if n>0 then raise_application_error(-20886,'UNLOAD_CAPTURED_UNIT_RECOVERY_REQUIRED');end if;
   select nvl(sum(BASE_QTY),0)into signed_total from RRL_EVENTS where OPERATION_ID=load_id and UID_POLETA=uid_text;
   if signed_total!=-qty then raise_application_error(-20886,'UNLOAD_ORIGINAL_SIGNED_SHIP_JOURNAL_REQUIRED');end if;
   select RRL_STOCK_RESERVATION_SQ.nextval into new_res from dual;
   RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_STOCK_RESERVATION',RRL_STOCK_PLAN_HELPER.decimal_text(new_res));
   RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_STOCK_RESERVATION',RRL_STOCK_PLAN_HELPER.decimal_text(x.get_number('reservation_id')));
   RRL_STOCK_PLAN_HELPER.stock_closure(f,r,uid_text,x.get_string('article'),cell_text,cell_text);
   y:=x.clone();y.put('new_reservation',new_res);y.put('current_stock_version',version_no);restored.append(y);
  end loop;
  v.put('load_id',load_id);v.put('trip_id',lf.TT_ID);v.put('case_id',case_id);v.put('shipment_id',sid);v.put('warehouse',lf.WARE_ID);
  v.put('snapshot',json_object_t.parse(lf.COMPOSITION_JSON));v.put('legs',restored);v.put('original_case_version',lf.CONTENT_VERSION+1);
  p_domain:=v.to_clob;p_policies:=f.to_clob;p_resources:=r.to_clob;
 end;
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob)is
  d json_object_t:=json_object_t.parse(p_request);m json_object_t:=d.get_object('metadata');wire clob;v json_object_t;sd json_object_t;lf RRL_TT_HU_LOAD_FACT%rowtype;
  op varchar2(100):=d.get_string('operation_id');load_id varchar2(100);case_id number;sid number;trip_id number;ware number;cell_text varchar2(60);
  a json_array_t;x json_object_t;history RRL_STOCK_RESERVATION%rowtype;details json_object_t;uid_text varchar2(150);qty number;version_no number;physical number;held number;event_id number;n number;new_id number;uom_version number;uom_text varchar2(20);j json_object_t:=json_object_t();
 begin
  select RESOLVED_PLAN_JSON into wire from RRL_STOCK_OPERATION where OPERATION_ID=op;v:=json_object_t.parse(wire).get_object('domain');
  load_id:=v.get_string('load_id');case_id:=v.get_number('case_id');sid:=v.get_number('shipment_id');trip_id:=v.get_number('trip_id');ware:=v.get_number('warehouse');cell_text:=m.get_string('scan_cell');
  assert_scope(load_id,p_actor);
  select ID into n from RRL_TRANSPORT_TASK where ID=trip_id for update;
  select TT_ID into n from RRL_TT_HU_LOAD_FACT where LOAD_OPERATION_ID=load_id for update;
  select ID into n from RRL_SBORKA_PALLETS where ID=sid for update;
  select CASE_PICK_TASK_ID into n from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=case_id for update;
  source_state(load_id,m,lf,sd);
  if lf.TT_ID!=trip_id or lf.ROOT_CASE_TASK_ID!=case_id or sd.get_number('document_id')!=sid or lf.WARE_ID!=ware then raise_application_error(-20890,'CLOSURE_CHANGED: unload owner');end if;
  a:=v.get_array('legs');
  for i in 0..a.get_size-1 loop
   x:=treat(a.get(i)as json_object_t);uid_text:=x.get_string('uid');new_id:=x.get_number('new_reservation');qty:=RRL_STOCK_MATH.quantity(x.get_string('quantity'));uom_text:=x.get_string('base_uom');uom_version:=x.get_number('uom_version');
   select REMAIN,HARD_RESERVED_BASE,STOCK_VERSION into physical,held,version_no from RRL_REMAINS where UID_POLETA=uid_text and CELL=cell_text for update;
   if physical!=0 or held!=0 or version_no!=x.get_number('current_stock_version')then raise_application_error(-20890,'CLOSURE_CHANGED: unload physical stock');end if;
   declare old_id number:=x.get_number('reservation_id');begin select *into history from RRL_STOCK_RESERVATION where RESERVATION_ID=old_id;end;
   if history.UID_PALLET!=uid_text or history.CELL!=cell_text or history.STATUS!='CONSUMED'or history.BASE_QTY!=0 or history.SOURCE_DOC_TYPE!='PICK_WAVE'or history.RESERVATION_DOMAIN!='PICKING'then raise_application_error(-20886,'UNLOAD_ORIGINAL_CONSUMED_RESERVATION_REQUIRED');end if;
   RRL_STOCK_BALANCE_CORE.apply_delta(uid_text,cell_text,qty,0,uom_text,uom_version,version_no);
   RRL_STOCK_BALANCE_CORE.write_leg(uid_text,null,cell_text,qty,uom_text,uom_version,i+1,1,1,p_actor,event_id);
   details:=json_object_t();details.put('reservation_scope',history.RESERVATION_SCOPE);details.put('customer_order_id',history.CUSTOMER_ORDER_ID);details.put('customer_id',history.CUSTOMER_ID);details.put('pick_plan_id',history.PICK_PLAN_ID);details.put('pick_plan_line_id',history.PICK_PLAN_LINE_ID);details.put('restores_load_operation',load_id);
   RRL_STOCK_RESERVE_CORE.create_hard(new_id,uid_text,cell_text,qty,uom_text,uom_version,history.SOURCE_DOC_TYPE,history.SOURCE_DOC_ID,history.SOURCE_LINE_ID,history.RESERVATION_DOMAIN,p_actor,details.to_clob);
  end loop;
  update RRL_CASE_PICK_TASK set STATUS='WAIT_CONTROL',SHIPPED_OPERATION=null,CONTENT_VERSION=CONTENT_VERSION+1,CURRENT_CELL=cell_text,DONE_AT=null,UPDATED_AT=systimestamp,UPDATED_BY=p_actor where CASE_PICK_TASK_ID=case_id;
  RRL_STOCK_FULFILLMENT_FACT.project_unload(sid,load_id,case_id,p_actor);
  update RRL_SBORKA_PALLETS set CONDITION=0,PROOVED=0,PROOVED_BY=null,SCAN_MARK_PROVED=0,SCAN_PHYSICAL_UNIT_COUNT=0,SCAN_ITEM_PROVED=0,TRIAL_WEIGHT=0,WOOD_WEIGHT=0,QUANTITY_SCAN=0,SCAN_CONTENT_SIGNATURE=null,WEIGHT_CONTENT_SIGNATURE=null,SCAN_QC_OPERATION_ID=null,WEIGHT_QC_OPERATION_ID=null,QC_RESCAN_REQUIRED=1 where ID=sid;
  insert into RRL_TT_UNLOAD_FACT(OPERATION_ID,LOAD_OPERATION_ID,TT_ID,CASE_PICK_TASK_ID,WARE_ID,CELL_CODE,COMPOSITION_JSON,REASON,CREATED_BY)
   values(op,load_id,trip_id,case_id,ware,cell_text,lf.COMPOSITION_JSON,m.get_string('reason'),p_actor);
  update RRL_TT_HU_LOAD_FACT set STATUS='UNLOADED'where LOAD_OPERATION_ID=load_id;
  update RRL_TT_HU_LOAD_ST set ACTIVE_FLAG=0 where LOAD_OPERATION_ID=load_id and SBORKA_PALLET_ID=sid and ACTIVE_FLAG=1;
  if sql%rowcount!=1 then raise_application_error(-20890,'CLOSURE_CHANGED: unload active member');end if;
  j.put('operation_id',op);j.put('status','UNLOADED');j.put('load_operation_id',load_id);j.put('case_task_id',case_id);j.put('shipment_id',sid);j.put('cell',cell_text);j.put('restored_lines',a);j.put('quality_control_required',true);j.put('original_ship_history_preserved',true);p_result:=j.to_clob;
 end;
end;
/
"""
# Scalarize every JSON method used inside SQL; never rely on SQL resolving PL object methods.
s=out[str(f/"002_command.sql")]
s=s.replace("CELL=tree.get_string('cell')","CELL=cell_text").replace("blocked number;","blocked number;cell_text varchar2(60);")
s=s.replace("  select WARE_ID,nvl(BLOCKED_FOR_REMAINS,0)","  cell_text:=tree.get_string('cell');\n  select WARE_ID,nvl(BLOCKED_FOR_REMAINS,0)")
s=s.replace("new_res number;n number;signed_total","new_res number;article_text varchar2(160);n number;signed_total")
s=s.replace("   select count(*)into n from RRL_SKU_RECEIPT_POLICY where ARTICUL=x.get_string('article')","   article_text:=x.get_string('article');\n   select count(*)into n from RRL_SKU_RECEIPT_POLICY where ARTICUL=article_text")
s=s.replace("COMPOSITION_JSON,m.get_string('reason'),p_actor","COMPOSITION_JSON,reason_text,p_actor")
s=s.replace("op varchar2(100):=d.get_string('operation_id');load_id","reason_text varchar2(1000):=m.get_string('reason');op varchar2(100):=d.get_string('operation_id');load_id")
out[str(f/"002_command.sql")]=s
for stem,target in [("balance","003_balance.sql"),("reserve","004_reserve.sql")]:
 s=(f/("000_before_"+stem+".sql")).read_text(encoding="utf-8")
 # Add this narrow caller to the actual existing specification ACL.
 s=s.replace("accessible by(","accessible by(package RRL_STOCK_UNLOAD_CMD,",1)
 out[str(f/target)]=s
s=(f/"000_before_fulfillment.sql").read_text(encoding="utf-8").replace("accessible by(","accessible by(package RRL_STOCK_UNLOAD_CMD,",1)
anchor=" procedure project_ship(p_shipment number,p_identifier varchar2,p_order number,p_operation varchar2,p_facts clob,p_actor varchar2);"
s=s.replace(anchor,anchor+"\n procedure project_unload(p_shipment number,p_load varchar2,p_case number,p_actor varchar2);")
anchor="end;\n/"
# Add owner method to the body, not to the spec.
pos=s.rfind(anchor);assert pos>0
s=s[:pos]+""" procedure project_unload(p_shipment number,p_load varchar2,p_case number,p_actor varchar2)is n number:=0;version_no number;
 begin
  select CONTENT_VERSION into version_no from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=p_case;
  for ff in(select FULFILLMENT_ID from RRL_CUSTOMER_ORDER_FULFILLMENT where LEGACY_SBORKA_PALLET_ID=p_shipment and PICKED_CASE_TASK_ID=p_case and STATUS='SHIPPED'and SHIPPED_OPERATION_ID=p_load order by FULFILLMENT_ID for update)loop
   n:=n+1;
   RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_CUSTOMER_ORDER_FULFILLMENT',RRL_STOCK_PLAN_HELPER.decimal_text(ff.FULFILLMENT_ID)));
   update RRL_CUSTOMER_ORDER_FULFILLMENT set STATUS='PICKED',SHIPPED_OPERATION_ID=null,SHIPPED_AT=null,PICKED_CONTENT_VERSION=version_no,UPDATED_AT=sysdate,UPDATED_BY=p_actor where FULFILLMENT_ID=ff.FULFILLMENT_ID;
  end loop;
  if n!=1 then raise_application_error(-20886,'UNLOAD_ORIGINAL_FULFILLMENT_REQUIRED');end if;
 end;
"""+s[pos:]
out[str(f/"005_fulfillment.sql")]=s
s=(f/"000_before_root.sql").read_text(encoding="utf-8")
anchor="  assert_actor_active(p_actor);assert_case_slot_actor(p_request,p_actor);assert_repack_actor(p_request,p_actor);"
assert s.count(anchor)==2
s=s.replace(anchor,anchor+"\n  if g_kind='UNLOAD_SHIPMENT'then declare doc json_object_t:=json_object_t.parse(p_request);begin RRL_STOCK_UNLOAD_CMD.assert_scope(doc.get_object('source').get_string('load_operation_id'),p_actor);end;end if;")
anchor="elsif g_kind='LOAD_SHIPMENT' then";assert s.count(anchor)==2
s=s.replace(anchor,"elsif g_kind='UNLOAD_SHIPMENT' then RRL_STOCK_UNLOAD_CMD.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);\n  "+anchor,1)
pos=s.index(anchor,s.index("procedure execute_prepared"))
s=s[:pos]+"elsif g_kind='UNLOAD_SHIPMENT' then RRL_STOCK_UNLOAD_CMD.execute_command(g_request,g_actor,p_result);\n  "+s[pos:]
out[str(f/"006_root.sql")]=s
out["wiki/database/nicora_ni052_unload_design_20261011.md"]="""# NI05.2: подтверждённая выгрузка до выезда
212 первый slice: существующее standalone ordinary CASE LOAD_SHIPMENT, текущая LAUNCHED wave, исходные машина/ворота/скан места/ячейка и сохранённая версия. Дополнение к реальной погрузке; STATUS UNLOADED уже есть в таблице.
Sole transaction RRL_STOCK_POSTING_API: новая неизменяемая выгрузка + обратные положительные ноги журнала через existing BALANCE owner + восстановленный P и новый HARD того же первоначального CASE заказа + исходная fulfillment projection PICKED + reset QC + load UNLOADED/member inactive + obligatory outbox. Старые shipment/box/stock events не удаляются. Повтор исходного operation_id возвращает receipt, чужой currentWARE запрещён до replay и после wait.
Logical declared locks preserve existing ranks and same TT→ST→CASE physical serialization; unique source unload prohibits duplicate restoration. Restore only exact zero original leaves and consumed original reservation, original signed load journal; before departure only. No tare handed over, no interwarehouse/supplier-return special source, no marked/weighted physical units in212; explicit refusal until their own recovery delivered. Same original staging cell, no arbitrary target/quantity input. Re-control mandatory after restoration; fresh archived scale proof cannot be forged by reusing old changed-epoch QC. Fresh checkpoint/paired rollback only without unload history; actual restoration thereafter compensated by next physical load or forward repair, no copying/deleting database.
"""
print(json.dumps(out,ensure_ascii=True))
