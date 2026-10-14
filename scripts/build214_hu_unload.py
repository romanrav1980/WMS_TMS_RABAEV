from pathlib import Path
import json
f=Path("db/migrations/2026-10-11_ni052_unload_hu");out={}
out["wiki/database/nicora_ni052_unload_hu_design_20261011.md"]="""# NI05.2: выгрузка матрёшки целиком
214 extends same native UNLOAD_SHIPMENT, CASE-only complete HU sub-scenario. Frozen original HU_SHIP tree/shipments and every original leaf required; no per-child partial unloading. Original links remain inactive shipped history, new native append-only links point to same containers/CASE. Current container epoch original+1/null cell/shipped original load; each CASE version original+1/shipped same load/wave LAUNCHED; no foreign active edges/claims/tasks or transferred tare. Original CASE HELD bookings retained under owner/balance row locks. Exact units restore213 applies each leaf. Original root cell/current warehouse/not quarantined. Slotted storage is explicitly refused until bounded existing placement-owner integration; this slice supports existing unslotted expedition/system cell, no fictitious slot claim. Whole P/H/units/new links/CASE/QC/FF/load/member/unload/outbox in root TX. New unload journal supports exclusive root CASE or real container UID; old facts stay valid. Monotonic epochs, no original link reactivation. Current wrong WARE before replay/after mutex.
"""
out[str(f/"001_schema.sql")]="""alter table RRL_TT_UNLOAD_FACT modify(CASE_PICK_TASK_ID null);
alter table RRL_TT_UNLOAD_FACT add(ROOT_UID varchar2(150) references RRL_PALLETS(UID_PALLET));
alter table RRL_TT_UNLOAD_FACT add constraint RRL_TT_UNLOAD_ROOT_CK check((CASE_PICK_TASK_ID is not null and ROOT_UID is null)or(CASE_PICK_TASK_ID is null and ROOT_UID is not null));
"""
s=(f/"000_before_unload.sql").read_text(encoding="utf-8")
start=s.index(" procedure source_state");end=s.index(" procedure compile_command",start)
source=""" procedure source_state(p_load varchar2,p_metadata json_object_t,p_lf out RRL_TT_HU_LOAD_FACT%rowtype,p_domain out json_object_t)is
  wire clob;kind_name varchar2(80);state_name varchar2(20);ct RRL_CASE_PICK_TASK%rowtype;tree json_object_t;root_node json_object_t;n number;trip RRL_TRANSPORT_TASK%rowtype;cell_ware number;blocked number;cell_text varchar2(60);
  original json_object_t;plans json_array_t;sub json_object_t;members json_array_t:=json_array_t();legs json_array_t:=json_array_t();a json_array_t;x json_object_t;y json_object_t;uid_text varchar2(150);version_no number;shipped_op varchar2(100);current_cell varchar2(60);
 begin
  select *into p_lf from RRL_TT_HU_LOAD_FACT where LOAD_OPERATION_ID=p_load;
  if p_lf.STATUS!='LOADED'or p_lf.DEPARTURE_OPERATION_ID is not null or p_lf.DEPARTED_AT is not null or p_lf.CUSTODY_RELEASE_OPERATION_ID is not null then raise_application_error(-20886,'UNLOAD_PREDEPARTURE_LOADED_REQUIRED');end if;
  select COMMAND_TYPE,STATE,RESOLVED_PLAN_JSON into kind_name,state_name,wire from RRL_STOCK_OPERATION where OPERATION_ID=p_load;
  if state_name!='APPLIED'or kind_name not in('LOAD_SHIPMENT','HU_SHIP')then raise_application_error(-20886,'UNLOAD_NATIVE_ORIGINAL_LOAD_REQUIRED');end if;
  original:=json_object_t.parse(wire).get_object('domain');tree:=json_object_t.parse(p_lf.COMPOSITION_JSON);root_node:=treat(tree.get_array('nodes').get(0)as json_object_t);
  if tree.get_array('ancestors').get_size!=0 then raise_application_error(-20886,'UNLOAD_WHOLE_TOP_PLACE_REQUIRED');end if;
  plans:=json_array_t();
  if kind_name='LOAD_SHIPMENT'and p_lf.ROOT_CASE_TASK_ID is not null and p_lf.ROOT_UID is null and root_node.get_string('kind')='CASE'then plans.append(original.get_object('shipment'));
  elsif kind_name='HU_SHIP'and p_lf.ROOT_UID is not null and p_lf.ROOT_CASE_TASK_ID is null and root_node.get_string('kind')='CONTAINER'then plans:=original.get_array('shipments');
  else raise_application_error(-20886,'UNLOAD_CASE_OR_CASE_HU_REQUIRED');end if;
  if plans.get_size<1 or plans.get_size>200 then raise_application_error(-20881,'UNLOAD_MEMBER_BOUND_1_200');end if;
  for i in 0..plans.get_size-1 loop
   sub:=treat(plans.get(i)as json_object_t).get_object('domain');
   if sub.has('interwarehouse_onward_source')or sub.has('supplier_return_source')or sub.get_number('case_task')is null then raise_application_error(-20886,'UNLOAD_SPECIAL_CUSTODY_DECISION_REQUIRED');end if;
   select *into ct from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=sub.get_number('case_task');
   if ct.STATUS!='SHIPPED'or ct.SHIPPED_OPERATION!=p_load or ct.WARE_ID!=p_lf.WARE_ID or ct.CONTENT_VERSION!=sub.get_number('case_version')+1 then raise_application_error(-20886,'UNLOAD_ORIGINAL_CASE_STATE_REQUIRED');end if;
   select count(*)into n from RRL_PICK_WAVE where PICK_WAVE_ID=ct.PICK_WAVE_ID and STATUS='LAUNCHED';
   if n!=1 then raise_application_error(-20886,'UNLOAD_ACTIVE_CASE_WAVE_REQUIRED');end if;
   select count(*)into n from RRL_TT_HU_LOAD_ST where LOAD_OPERATION_ID=p_load and ACTIVE_FLAG=1 and SBORKA_PALLET_ID=ct.LEGACY_SBORKA_PALLET_ID;
   if n!=1 or ct.LEGACY_SBORKA_PALLET_ID!=sub.get_number('document_id')then raise_application_error(-20886,'UNLOAD_ORIGINAL_ACTIVE_ST_REQUIRED');end if;
   x:=json_object_t();x.put('case_id',ct.CASE_PICK_TASK_ID);x.put('shipment_id',ct.LEGACY_SBORKA_PALLET_ID);x.put('case_version',ct.CONTENT_VERSION);members.append(x);
   a:=sub.get_array('legs');for k in 0..a.get_size-1 loop legs.append(a.get(k));end loop;
  end loop;
  select count(*)into n from RRL_TT_HU_LOAD_ST where LOAD_OPERATION_ID=p_load and ACTIVE_FLAG=1;
  if n!=members.get_size then raise_application_error(-20886,'UNLOAD_ALL_ORIGINAL_MEMBERS_REQUIRED');end if;
  if p_metadata.get_number('expected_version')is null or p_metadata.get_number('expected_version')!=p_lf.CONTENT_VERSION
   or p_metadata.get_string('scan_container')is null or(p_metadata.get_string('scan_container')!=root_node.get_string('uid')and(root_node.get_string('sscc')is null or p_metadata.get_string('scan_container')!=root_node.get_string('sscc')))
   or p_metadata.get_string('scan_cell')is null or p_metadata.get_string('scan_cell')!=tree.get_string('cell')
   or p_metadata.get_string('scan_vehicle')is null or p_metadata.get_string('scan_vehicle')!=p_lf.VEHICLE_NUMBER
   or p_metadata.get_string('scan_dock')is null or p_metadata.get_string('scan_dock')!=p_lf.DOCK
   or trim(p_metadata.get_string('reason'))is null or length(p_metadata.get_string('reason'))>1000 then raise_application_error(-20886,'UNLOAD_ORIGINAL_PLACE_VEHICLE_DOCK_CELL_SCAN_REQUIRED');end if;
  select *into trip from RRL_TRANSPORT_TASK where ID=p_lf.TT_ID;
  if trip.CONDITION='Отгружен'or nvl(trip.DELETED,0)!=0 or nvl(trip.PAY_ORDER_ID,0)!=0 or trip.TRANSPORT!=p_lf.VEHICLE_NUMBER or trip.DOCK!=p_lf.DOCK then raise_application_error(-20886,'UNLOAD_CURRENT_UNDEPARTED_TRIP_REQUIRED');end if;
  cell_text:=tree.get_string('cell');
  select WARE_ID,nvl(BLOCKED_FOR_REMAINS,0)into cell_ware,blocked from RRL_CELLS where CELL=cell_text;
  if cell_ware!=p_lf.WARE_ID or blocked!=0 then raise_application_error(-20886,'UNLOAD_ORIGINAL_CELL_CURRENTLY_BLOCKED');end if;
  select count(*)into n from RRL_TARE_OFFER_BOOK where LOAD_OPERATION_ID=p_load;
  if n>0 then raise_application_error(-20886,'UNLOAD_TARE_HANDOVER_DECISION_REQUIRED');end if;
  if kind_name='HU_SHIP'then
   select count(*)into n from RRL_TOPOLOGY_CELL_SLOT sl join RRL_TOPOLOGY_CELL tc on tc.TOPOLOGY_CELL_ID=sl.TOPOLOGY_CELL_ID where tc.LEGACY_CELL_CODE=cell_text and tc.WARE_ID=p_lf.WARE_ID and tc.ACTIVE=1 and sl.ACTIVE=1 and sl.SLOT_KIND='STORAGE_SLOT';
   if n>0 then raise_application_error(-20886,'UNLOAD_STORAGE_SLOT_PLACEMENT_REQUIRED');end if;
   a:=tree.get_array('nodes');
   for i in 0..a.get_size-1 loop
    x:=treat(a.get(i)as json_object_t);uid_text:=x.get_string('uid');
    if x.get_string('kind')='CONTAINER'then
     select HU_CONTENT_VERSION,HU_SHIPPED_OPERATION,HU_CURRENT_CELL into version_no,shipped_op,current_cell from RRL_PALLETS where UID_PALLET=uid_text and HU_KIND='CONTAINER';
     if version_no!=x.get_number('version')+1 or shipped_op!=p_load or current_cell is not null then raise_application_error(-20886,'UNLOAD_ORIGINAL_CONTAINER_EPOCH_REQUIRED');end if;
    end if;
    select count(*)into n from RRL_WMS_HU_LINK where ACTIVE_FLAG=1 and(PARENT_UID=uid_text or CHILD_PALLET_UID=uid_text or CHILD_CASE_TASK_ID=x.get_number('case_task_id'));
    if n>0 then raise_application_error(-20886,'UNLOAD_ORIGINAL_TREE_ALREADY_REUSED');end if;
   end loop;
   a:=tree.get_array('links');
   for i in 0..a.get_size-1 loop
    x:=treat(a.get(i)as json_object_t);
    if x.get_number('id')is not null then
     select count(*)into n from RRL_WMS_HU_LINK where HU_LINK_ID=x.get_number('id')and PARENT_UID=x.get_string('parent')and ACTIVE_FLAG=0 and UNLINKED_OPERATION_ID=p_load and LINK_VERSION=x.get_number('version')+1 and nvl(CHILD_PALLET_UID,'CASE:'||RRL_STOCK_PLAN_HELPER.decimal_text(CHILD_CASE_TASK_ID))=x.get_string('child');
     if n!=1 then raise_application_error(-20886,'UNLOAD_ORIGINAL_LINK_HISTORY_REQUIRED');end if;
    end if;
   end loop;
  end if;
  p_domain:=json_object_t();p_domain.put('members',members);p_domain.put('legs',legs);
 end;
"""
# PL JSON member access in SQL must first become local scalar.
source=source.replace("current_cell varchar2(60);","current_cell varchar2(60);case_value number;old_link_id number;parent_value varchar2(150);child_value varchar2(200);expected_link_version number;")
source=source.replace("   select *into ct from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=sub.get_number('case_task');","   case_value:=sub.get_number('case_task');select *into ct from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=case_value;")
source=source.replace("    select count(*)into n from RRL_WMS_HU_LINK where ACTIVE_FLAG=1","    case_value:=x.get_number('case_task_id');select count(*)into n from RRL_WMS_HU_LINK where ACTIVE_FLAG=1").replace("CHILD_CASE_TASK_ID=x.get_number('case_task_id')","CHILD_CASE_TASK_ID=case_value")
source=source.replace("     select count(*)into n from RRL_WMS_HU_LINK where HU_LINK_ID=x.get_number('id')and PARENT_UID=x.get_string('parent')","     old_link_id:=x.get_number('id');parent_value:=x.get_string('parent');child_value:=x.get_string('child');expected_link_version:=x.get_number('version');\n     select count(*)into n from RRL_WMS_HU_LINK where HU_LINK_ID=old_link_id and PARENT_UID=parent_value").replace("LINK_VERSION=x.get_number('version')+1","LINK_VERSION=expected_link_version+1").replace("=x.get_string('child');","=child_value;")
source=source.replace("parent_valueand","parent_value and").replace("child_value:=child_value;","child_value:=x.get_string(\'child\');")
s=s[:start]+source+s[end:]
s=s.replace("unit_obj json_object_t;","unit_obj json_object_t;members json_array_t;tree json_object_t;nodes json_array_t;links json_array_t;recover_links json_array_t:=json_array_t();new_link number;",1)
s=s.replace("case_id:=lf.ROOT_CASE_TASK_ID;sid:=sd.get_number('document_id');","case_id:=lf.ROOT_CASE_TASK_ID;members:=sd.get_array('members');tree:=json_object_t.parse(lf.COMPOSITION_JSON);",1)
start=s.index("  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_TT_HU_LOAD_ST'")
end=s.index("  for i in 0..legs.get_size-1 loop",start)
compile_members="""  for member_index in 0..members.get_size-1 loop
   x:=treat(members.get(member_index)as json_object_t);sid:=x.get_number('shipment_id');case_id:=x.get_number('case_id');
   RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_TT_HU_LOAD_ST',load_id||':'||RRL_STOCK_PLAN_HELPER.decimal_text(sid));
   RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_SBORKA_PALLETS',RRL_STOCK_PLAN_HELPER.decimal_text(sid));
   RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_CASE_PICK_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(case_id));
   n:=0;
   for ff in(select FULFILLMENT_ID,CUSTOMER_ORDER_ID,PICKED_CASE_TASK_ID from RRL_CUSTOMER_ORDER_FULFILLMENT where LEGACY_SBORKA_PALLET_ID=sid and STATUS='SHIPPED'and SHIPPED_OPERATION_ID=load_id order by FULFILLMENT_ID)loop
    n:=n+1;if n>1 or ff.PICKED_CASE_TASK_ID!=case_id then raise_application_error(-20886,'UNLOAD_ORIGINAL_FULFILLMENT_REQUIRED');end if;
    RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_CUSTOMER_ORDER_FULFILLMENT',RRL_STOCK_PLAN_HELPER.decimal_text(ff.FULFILLMENT_ID));
    RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_CUSTOMER_ORDER',RRL_STOCK_PLAN_HELPER.decimal_text(ff.CUSTOMER_ORDER_ID));
   end loop;
   if n!=1 then raise_application_error(-20886,'UNLOAD_ORIGINAL_FULFILLMENT_REQUIRED');end if;
  end loop;
  nodes:=tree.get_array('nodes');
  for node_index in 0..nodes.get_size-1 loop
   x:=treat(nodes.get(node_index)as json_object_t);uid_text:=x.get_string('uid');
   RRL_STOCK_PLAN_HELPER.anchor(r,30,'HU',uid_text);
   if x.get_string('kind')='CONTAINER'then RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_PALLETS',uid_text);end if;
   for book in(select OPERATION_ID,BALANCE_KEY,OWNER_WARE_ID from RRL_TARE_BOOK where STATUS='HELD'and((PLACE_KIND='HU'and PLACE_ID=uid_text)or(PLACE_KIND='CASE'and 'CASE:'||PLACE_ID=uid_text)))loop
    if book.OWNER_WARE_ID!=lf.WARE_ID then raise_application_error(-20886,'UNLOAD_TARE_BOOK_WARE_CONFLICT');end if;
    RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_TARE_BOOK',book.OPERATION_ID);RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_TARE_BALANCE',rawtohex(book.BALANCE_KEY));
   end loop;
  end loop;
  links:=tree.get_array('links');
  for link_index in 0..links.get_size-1 loop
   x:=treat(links.get(link_index)as json_object_t);
   if x.get_number('id')is not null then
    select RRL_WMS_HU_LINK_SQ.nextval into new_link from dual;
    RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_WMS_HU_LINK',RRL_STOCK_PLAN_HELPER.decimal_text(x.get_number('id')));
    RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_WMS_HU_LINK',RRL_STOCK_PLAN_HELPER.decimal_text(new_link));
    y:=x.clone();y.put('new_id',new_link);recover_links.append(y);
   end if;
  end loop;
"""
s=s[:start]+compile_members+s[end:]
s=s.replace("v.put('case_id',case_id);v.put('shipment_id',sid);","v.put('case_id',lf.ROOT_CASE_TASK_ID);v.put('root_uid',lf.ROOT_UID);v.put('members',members);v.put('recover_links',recover_links);",1)
s=s.replace("v.put('original_case_version',lf.CONTENT_VERSION+1);","",1)
# Generalized execute; same quantity/unit restoration loop reused.
s=s.replace("fresh_units clob;j json_object_t","fresh_units clob;members json_array_t;nodes json_array_t;links json_array_t;node_wire clob;member_wire clob;root_uid varchar2(150);child_uid varchar2(150);child_case number;new_link number;parent_uid varchar2(150);j json_object_t",1)
s=s.replace("sid:=v.get_number('shipment_id');","members:=v.get_array('members');root_uid:=v.get_string('root_uid');member_wire:=members.to_clob;node_wire:=v.get_object('snapshot').get_array('nodes').to_clob;",1)
start=s.index("  select ID into n from RRL_SBORKA_PALLETS where ID=sid for update;")
end=s.index("  a:=v.get_array('legs');",start)
s=s[:start]+"""  for owner in(select ID from RRL_SBORKA_PALLETS where ID in(select SID from json_table(member_wire,'$[*]'columns(SID number path '$.shipment_id')))order by ID)loop select ID into n from RRL_SBORKA_PALLETS where ID=owner.ID for update;end loop;
  for owner in(select CASE_PICK_TASK_ID from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID in(select C from json_table(member_wire,'$[*]'columns(C number path '$.case_id')))order by CASE_PICK_TASK_ID)loop select CASE_PICK_TASK_ID into n from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=owner.CASE_PICK_TASK_ID for update;end loop;
  source_state(load_id,m,lf,sd);
  if lf.TT_ID!=trip_id or nvl(lf.ROOT_CASE_TASK_ID,-1)!=nvl(case_id,-1)or nvl(lf.ROOT_UID,'~')!=nvl(root_uid,'~')or lf.WARE_ID!=ware or dbms_lob.compare(sd.get_array('members').to_clob,member_wire)!=0 then raise_application_error(-20890,'CLOSURE_CHANGED: unload owners');end if;
"""+s[end:]
start=s.index("  update RRL_CASE_PICK_TASK set STATUS='WAIT_CONTROL'")
end=s.index("  j.put('operation_id'",start)
tail="""  nodes:=v.get_object('snapshot').get_array('nodes');
  for node_index in 0..nodes.get_size-1 loop
   x:=treat(nodes.get(node_index)as json_object_t);uid_text:=x.get_string('uid');
   if x.get_string('kind')='CONTAINER'then
    update RRL_PALLETS set HU_SHIPPED_OPERATION=null,HU_CURRENT_CELL=cell_text,HU_CONTENT_VERSION=HU_CONTENT_VERSION+1 where UID_PALLET=uid_text and HU_SHIPPED_OPERATION=load_id;
    if sql%rowcount!=1 then raise_application_error(-20890,'CLOSURE_CHANGED: unload container');end if;
   end if;
  end loop;
  for member_index in 0..members.get_size-1 loop
   x:=treat(members.get(member_index)as json_object_t);case_id:=x.get_number('case_id');sid:=x.get_number('shipment_id');
   update RRL_CASE_PICK_TASK set STATUS='WAIT_CONTROL',SHIPPED_OPERATION=null,CONTENT_VERSION=CONTENT_VERSION+1,CURRENT_CELL=cell_text,DONE_AT=null,UPDATED_AT=systimestamp,UPDATED_BY=p_actor where CASE_PICK_TASK_ID=case_id;
   RRL_STOCK_FULFILLMENT_FACT.project_unload(sid,load_id,case_id,p_actor);
   update RRL_SBORKA_PALLETS set CONDITION=0,PROOVED=0,SCAN_MARK_PROVED=0,SCAN_PHYSICAL_UNIT_COUNT=0,SCAN_ITEM_PROVED=0,TRIAL_WEIGHT=0,WOOD_WEIGHT=0,PROOVED_BY_SCAN=0,SCAN_CONTENT_SIGNATURE=null,WEIGHT_CONTENT_SIGNATURE=null,SCAN_QC_OPERATION_ID=null,WEIGHT_QC_OPERATION_ID=null,QC_RESCAN_REQUIRED=1 where ID=sid;
  end loop;
  links:=v.get_array('recover_links');
  for link_index in 0..links.get_size-1 loop
   x:=treat(links.get(link_index)as json_object_t);parent_uid:=x.get_string('parent');uid_text:=x.get_string('child');new_link:=x.get_number('new_id');child_uid:=null;child_case:=null;
   if substr(uid_text,1,5)='CASE:'then child_case:=to_number(substr(uid_text,6));else child_uid:=uid_text;end if;
   insert into RRL_WMS_HU_LINK(HU_LINK_ID,PARENT_UID,CHILD_PALLET_UID,CHILD_CASE_TASK_ID,ACTIVE_FLAG,LINK_VERSION,LINKED_OPERATION_ID,LINKED_BY)values(new_link,parent_uid,child_uid,child_case,1,0,op,p_actor);
  end loop;
  insert into RRL_TT_UNLOAD_FACT(OPERATION_ID,LOAD_OPERATION_ID,TT_ID,CASE_PICK_TASK_ID,ROOT_UID,WARE_ID,CELL_CODE,COMPOSITION_JSON,REASON,CREATED_BY)
   values(op,load_id,trip_id,lf.ROOT_CASE_TASK_ID,lf.ROOT_UID,ware,cell_text,lf.COMPOSITION_JSON,reason_text,p_actor);
  update RRL_TT_HU_LOAD_FACT set STATUS='UNLOADED'where LOAD_OPERATION_ID=load_id;
  update RRL_TT_HU_LOAD_ST set ACTIVE_FLAG=0 where LOAD_OPERATION_ID=load_id and ACTIVE_FLAG=1;
  if sql%rowcount!=members.get_size then raise_application_error(-20890,'CLOSURE_CHANGED: unload active members');end if;
"""
s=s[:start]+tail+s[end:]
s=s.replace("j.put('case_task_id',case_id);j.put('shipment_id',sid);","j.put('case_task_id',lf.ROOT_CASE_TASK_ID);j.put('root_uid',lf.ROOT_UID);j.put('members',members);",1)
out[str(f/"002_unload.sql")]=s
print(json.dumps(out,ensure_ascii=True))


