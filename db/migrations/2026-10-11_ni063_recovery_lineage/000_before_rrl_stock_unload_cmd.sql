create or replace package RRL_STOCK_UNLOAD_CMD authid definer accessible by(package RRL_STOCK_POSTING_API) as
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
 function issued_units(p_load varchar2,p_uid varchar2,p_cell varchar2,p_qty number)return clob is
  wire clob;expected_sig varchar2(64);sig varchar2(64);a json_array_t:=json_array_t();plain json_array_t:=json_array_t();x json_object_t;j json_object_t:=json_object_t();n number:=0;total number:=0;original_count number;
 begin
  select RESOLVED_PLAN_JSON into wire from RRL_STOCK_OPERATION where OPERATION_ID=p_load;
  select count(*),max(S)into original_count,expected_sig from json_table(wire,'$.physical_before[*]'columns(U varchar2(150)path '$.uid',S varchar2(64)path '$.unit_signature'))where U=p_uid;
  if original_count!=1 or expected_sig is null then raise_application_error(-20884,'UNLOAD_ORIGINAL_UNIT_PROOF_REQUIRED');end if;
  for u in(select PHYSICAL_UNIT_KEY,BASE_QTY,BASE_UOM,UNIT_VERSION,STOCK_STATUS,HARD_RESERVATION_ID from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=p_uid and CURRENT_CELL=p_cell order by PHYSICAL_UNIT_KEY fetch first 10001 rows only)loop
   n:=n+1;if n>10000 or u.PHYSICAL_UNIT_KEY is null or u.BASE_QTY<=0 or u.BASE_UOM is null or u.UNIT_VERSION is null or u.STOCK_STATUS!='ISSUED'or u.HARD_RESERVATION_ID is not null then raise_application_error(-20884,'UNLOAD_EXACT_ORIGINAL_ISSUED_SET_REQUIRED');end if;
   x:=json_object_t();x.put('key',u.PHYSICAL_UNIT_KEY);x.put('quantity',RRL_STOCK_PLAN_HELPER.decimal_text(u.BASE_QTY));x.put('base_uom',u.BASE_UOM);plain.append(x.clone());x.put('version',u.UNIT_VERSION);a.append(x);total:=total+u.BASE_QTY;
  end loop;
  j.put('units',plain);sig:=rawtohex(sys.dbms_crypto.hash(j.to_clob,sys.dbms_crypto.hash_sh256));
  if sig!=expected_sig or(n>0 and total!=p_qty)then raise_application_error(-20884,'UNLOAD_ORIGINAL_UNIT_FINGERPRINT_CONFLICT');end if;
  if n=0 then
   select count(*)into n from RRL_PALLETS p where p.UID_PALLET=p_uid and(exists(select 1 from RRL_SKU_RECEIPT_POLICY sp where sp.ARTICUL=p.ARTICUL and(sp.MARKING_REQUIRED=1 or sp.SERIALIZED_WEIGHT_BOXES=1))or exists(select 1 from RRL_SKU_RECEIPT_PROFILE profile where profile.ARTICUL=p.ARTICUL)or exists(select 1 from RRL_FINISHED_GOODS_SKU fg where fg.ARTICUL=p.ARTICUL and fg.CRPT_REQUIRED=1));
   if n>0 then raise_application_error(-20884,'UNLOAD_ORIGINAL_MARKED_CAPTURE_REQUIRED');end if;
  end if;
  return a.to_clob;
 end;
 procedure source_state(p_load varchar2,p_metadata json_object_t,p_lf out RRL_TT_HU_LOAD_FACT%rowtype,p_domain out json_object_t)is
  wire clob;kind_name varchar2(80);state_name varchar2(20);ct RRL_CASE_PICK_TASK%rowtype;tree json_object_t;root_node json_object_t;n number;trip RRL_TRANSPORT_TASK%rowtype;cell_ware number;blocked number;cell_text varchar2(60);
  original json_object_t;plans json_array_t;sub json_object_t;members json_array_t:=json_array_t();legs json_array_t:=json_array_t();a json_array_t;x json_object_t;y json_object_t;uid_text varchar2(150);version_no number;shipped_op varchar2(100);current_cell varchar2(60);case_value number;old_link_id number;parent_value varchar2(150);child_value varchar2(200);expected_link_version number;sid number;physical_uid varchar2(150);wave_value number;full_task number;physical_total number;held_total number;
 begin
  select *into p_lf from RRL_TT_HU_LOAD_FACT where LOAD_OPERATION_ID=p_load;
  if p_lf.STATUS!='LOADED'or p_lf.DEPARTURE_OPERATION_ID is not null or p_lf.DEPARTED_AT is not null or p_lf.CUSTODY_RELEASE_OPERATION_ID is not null then raise_application_error(-20886,'UNLOAD_PREDEPARTURE_LOADED_REQUIRED');end if;
  select COMMAND_TYPE,STATE,RESOLVED_PLAN_JSON into kind_name,state_name,wire from RRL_STOCK_OPERATION where OPERATION_ID=p_load;
  if state_name!='APPLIED'or kind_name not in('LOAD_SHIPMENT','HU_SHIP')then raise_application_error(-20886,'UNLOAD_NATIVE_ORIGINAL_LOAD_REQUIRED');end if;
  original:=json_object_t.parse(wire).get_object('domain');tree:=json_object_t.parse(p_lf.COMPOSITION_JSON);root_node:=treat(tree.get_array('nodes').get(0)as json_object_t);
  if tree.get_array('ancestors').get_size!=0 then raise_application_error(-20886,'UNLOAD_WHOLE_TOP_PLACE_REQUIRED');end if;
  plans:=json_array_t();
  if kind_name='LOAD_SHIPMENT'and p_lf.ROOT_CASE_TASK_ID is not null and p_lf.ROOT_UID is null and root_node.get_string('kind')='CASE'then plans.append(original.get_object('shipment'));
  elsif kind_name='LOAD_SHIPMENT'and p_lf.ROOT_CASE_TASK_ID is null and p_lf.ROOT_UID is not null and root_node.get_string('kind')='STOCK'then plans.append(original.get_object('shipment'));
  elsif kind_name='HU_SHIP'and p_lf.ROOT_UID is not null and p_lf.ROOT_CASE_TASK_ID is null and root_node.get_string('kind')='CONTAINER'then plans:=original.get_array('shipments');
  else raise_application_error(-20886,'UNLOAD_CASE_OR_CASE_HU_REQUIRED');end if;
  if plans.get_size<1 or plans.get_size>200 then raise_application_error(-20881,'UNLOAD_MEMBER_BOUND_1_200');end if;
  for i in 0..plans.get_size-1 loop
   sub:=treat(plans.get(i)as json_object_t).get_object('domain');
   if sub.has('interwarehouse_onward_source')or sub.has('supplier_return_source')then raise_application_error(-20886,'UNLOAD_SPECIAL_CUSTODY_DECISION_REQUIRED');end if;
   if sub.get_number('case_task')is not null then
   case_value:=sub.get_number('case_task');select *into ct from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=case_value;
   if ct.STATUS!='SHIPPED'or ct.SHIPPED_OPERATION!=p_load or ct.WARE_ID!=p_lf.WARE_ID or ct.CONTENT_VERSION!=sub.get_number('case_version')+1 then raise_application_error(-20886,'UNLOAD_ORIGINAL_CASE_STATE_REQUIRED');end if;
   select count(*)into n from RRL_PICK_WAVE where PICK_WAVE_ID=ct.PICK_WAVE_ID and STATUS='LAUNCHED';
   if n!=1 then raise_application_error(-20886,'UNLOAD_ACTIVE_CASE_WAVE_REQUIRED');end if;
   select count(*)into n from RRL_TT_HU_LOAD_ST where LOAD_OPERATION_ID=p_load and ACTIVE_FLAG=1 and SBORKA_PALLET_ID=ct.LEGACY_SBORKA_PALLET_ID;
   if n!=1 or ct.LEGACY_SBORKA_PALLET_ID!=sub.get_number('document_id')then raise_application_error(-20886,'UNLOAD_ORIGINAL_ACTIVE_ST_REQUIRED');end if;
   x:=json_object_t();x.put('case_id',ct.CASE_PICK_TASK_ID);x.put('shipment_id',ct.LEGACY_SBORKA_PALLET_ID);x.put('case_version',ct.CONTENT_VERSION);x.put_null('physical_uid');members.append(x);
   else
    physical_uid:=sub.get_string('bound_physical_uid');sid:=sub.get_number('document_id');
    if physical_uid is null or sub.get_number('bound_stock_version')is null then raise_application_error(-20886,'UNLOAD_ORIGINAL_BOUND_FULLPAL_REQUIRED');end if;
    select nvl(sum(REMAIN),0),nvl(sum(HARD_RESERVED_BASE),0)into physical_total,held_total from RRL_REMAINS where UID_POLETA=physical_uid;
    if physical_total!=0 or held_total!=0 then raise_application_error(-20886,'UNLOAD_WHOLE_ORIGINAL_FULLPAL_NOT_EMPTY');end if;
    select count(*),max(PICKED_WAREHOUSE_TASK_ID)into n,full_task from RRL_CUSTOMER_ORDER_FULFILLMENT where LEGACY_SBORKA_PALLET_ID=sid and STATUS='SHIPPED'and SHIPPED_OPERATION_ID=p_load and PICKED_CASE_TASK_ID is null and PICKED_PALLET_UID=physical_uid;
    if n!=1 or full_task is null then raise_application_error(-20886,'UNLOAD_ORIGINAL_FULLPAL_FULFILLMENT_REQUIRED');end if;
    select count(*)into n from RRL_WAREHOUSE_TASK where TASK_ID=full_task and STATUS='DONE'and TASK_TYPE='PICKING_MOVE'and UID_PALLET=physical_uid and TO_WARE_ID=p_lf.WARE_ID;
    if n!=1 then raise_application_error(-20886,'UNLOAD_ORIGINAL_FULLPAL_COMPLETED_TASK_REQUIRED');end if;
    a:=sub.get_array('legs');
    if a.get_size!=1 then raise_application_error(-20886,'UNLOAD_WHOLE_SINGLE_FULLPAL_LEAF_REQUIRED');end if;
    y:=treat(a.get(0)as json_object_t);wave_value:=y.get_number('owner_id');
    if y.get_string('uid')!=physical_uid or y.get_string('owner_type')!='PICK_WAVE'then raise_application_error(-20886,'UNLOAD_ORIGINAL_FULLPAL_WAVE_OWNER_REQUIRED');end if;
    select count(*)into n from RRL_PICK_WAVE where PICK_WAVE_ID=wave_value and STATUS='LAUNCHED';
    if n!=1 then raise_application_error(-20886,'UNLOAD_ACTIVE_FULLPAL_WAVE_REQUIRED');end if;
    select count(*)into n from RRL_TT_HU_LOAD_ST where LOAD_OPERATION_ID=p_load and ACTIVE_FLAG=1 and SBORKA_PALLET_ID=sid;
    if n!=1 then raise_application_error(-20886,'UNLOAD_ORIGINAL_ACTIVE_ST_REQUIRED');end if;
    x:=json_object_t();x.put_null('case_id');x.put('shipment_id',sid);x.put_null('case_version');x.put('physical_uid',physical_uid);x.put('wave_id',wave_value);x.put('fullpal_task_id',full_task);members.append(x);
   end if;
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
  select count(*)into n from RRL_TARE_OFFER_BOOK old_offer where LOAD_OPERATION_ID=p_load and not exists(select 1 from RRL_TARE_OFFER_CANCEL cancelled where cancelled.OFFER_OPERATION_ID=old_offer.OFFER_OPERATION_ID)and not exists(
   select 1 from RRL_TARE_LOAD_RECOVERY recovery join RRL_TARE_BOOK replacement on replacement.OPERATION_ID=recovery.OPERATION_ID
    where recovery.LOAD_OPERATION_ID=p_load and recovery.ORIGINAL_BOOK_OPERATION_ID=old_offer.BOOK_OPERATION_ID and replacement.STATUS='HELD');
  if n>0 then raise_application_error(-20886,'UNLOAD_TARE_HANDOVER_DECISION_REQUIRED');end if;
  if kind_name='HU_SHIP'then
   select count(*)into n from RRL_TOPOLOGY_CELL_SLOT sl join RRL_TOPOLOGY_CELL tc on tc.TOPOLOGY_CELL_ID=sl.TOPOLOGY_CELL_ID where tc.LEGACY_CELL_CODE=cell_text and tc.WARE_ID=p_lf.WARE_ID and tc.ACTIVE=1 and sl.ACTIVE=1 and sl.SLOT_KIND='STORAGE_SLOT';
   if n>0 and p_metadata.get_number('target_slot_id')is null then raise_application_error(-20886,'UNLOAD_STORAGE_SLOT_PLACEMENT_REQUIRED');end if;
   a:=tree.get_array('nodes');
   for i in 0..a.get_size-1 loop
    x:=treat(a.get(i)as json_object_t);uid_text:=x.get_string('uid');
    if x.get_string('kind')='CONTAINER'then
     select HU_CONTENT_VERSION,HU_SHIPPED_OPERATION,HU_CURRENT_CELL into version_no,shipped_op,current_cell from RRL_PALLETS where UID_PALLET=uid_text and HU_KIND='CONTAINER';
     if version_no!=x.get_number('version')+1 or shipped_op!=p_load or current_cell is not null then raise_application_error(-20886,'UNLOAD_ORIGINAL_CONTAINER_EPOCH_REQUIRED');end if;
    end if;
    case_value:=x.get_number('case_task_id');select count(*)into n from RRL_WMS_HU_LINK where ACTIVE_FLAG=1 and(PARENT_UID=uid_text or CHILD_PALLET_UID=uid_text or CHILD_CASE_TASK_ID=case_value);
    if n>0 then raise_application_error(-20886,'UNLOAD_ORIGINAL_TREE_ALREADY_REUSED');end if;
   end loop;
   a:=tree.get_array('links');
   for i in 0..a.get_size-1 loop
    x:=treat(a.get(i)as json_object_t);
    if x.get_number('id')is not null then
     old_link_id:=x.get_number('id');parent_value:=x.get_string('parent');child_value:=x.get_string('child');expected_link_version:=x.get_number('version');
     select count(*)into n from RRL_WMS_HU_LINK where HU_LINK_ID=old_link_id and PARENT_UID=parent_value and ACTIVE_FLAG=0 and UNLINKED_OPERATION_ID=p_load and LINK_VERSION=expected_link_version+1 and nvl(CHILD_PALLET_UID,'CASE:'||RRL_STOCK_PLAN_HELPER.decimal_text(CHILD_CASE_TASK_ID))=child_value;
     if n!=1 then raise_application_error(-20886,'UNLOAD_ORIGINAL_LINK_HISTORY_REQUIRED');end if;
    end if;
   end loop;
  end if;
  p_domain:=json_object_t();p_domain.put('members',members);p_domain.put('legs',legs);
 end;
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob)is
  d json_object_t:=json_object_t.parse(p_request);m json_object_t:=d.get_object('metadata');v json_object_t:=json_object_t();sd json_object_t;
  lf RRL_TT_HU_LOAD_FACT%rowtype;legs json_array_t;restored json_array_t:=json_array_t();x json_object_t;y json_object_t;
  f json_array_t:=json_array_t();r json_array_t:=json_array_t();load_id varchar2(100):=d.get_object('source').get_string('load_operation_id');
  uid_text varchar2(150);cell_text varchar2(60);qty number;physical number;held number;version_no number;new_res number;article_text varchar2(160);n number;signed_total number;sid number;case_id number;unit_wire clob;unit_array json_array_t;unit_obj json_object_t;members json_array_t;tree json_object_t;nodes json_array_t;links json_array_t;recover_links json_array_t:=json_array_t();new_link number;physical_uid varchar2(150);full_task number;wave_value number;actual_article varchar2(160);actual_uom varchar2(20);target_slot number;placement_task number;placement_sync number;request_wire clob;original_measures json_object_t;slot_code varchar2(100);
 begin
  assert_scope(load_id,d.get_string('actor'));source_state(load_id,m,lf,sd);legs:=sd.get_array('legs');case_id:=lf.ROOT_CASE_TASK_ID;members:=sd.get_array('members');tree:=json_object_t.parse(lf.COMPOSITION_JSON);
  if legs.get_size<1 or legs.get_size>200 then raise_application_error(-20881,'UNLOAD_LEG_BOUND_1_200');end if;
  RRL_STOCK_PLAN_HELPER.fence(f,'RELEASE','STOCK');RRL_STOCK_PLAN_HELPER.fence(f,'CONFIG','WAREHOUSE');
  RRL_STOCK_PLAN_HELPER.anchor(r,10,'OP',p_operation);
  RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','UNLOAD.LOAD:'||load_id);
  RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','STOCK.OUTBOX:'||rawtohex(sys.dbms_crypto.hash(utl_i18n.string_to_raw(p_operation,'AL32UTF8'),sys.dbms_crypto.hash_sh256)));
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_TRANSPORT_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(lf.TT_ID));
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_TT_HU_LOAD_FACT',load_id);
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_TT_UNLOAD_FACT',p_operation);
  for member_index in 0..members.get_size-1 loop
   x:=treat(members.get(member_index)as json_object_t);sid:=x.get_number('shipment_id');case_id:=x.get_number('case_id');physical_uid:=x.get_string('physical_uid');
   RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_TT_HU_LOAD_ST',load_id||':'||RRL_STOCK_PLAN_HELPER.decimal_text(sid));
   RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_SBORKA_PALLETS',RRL_STOCK_PLAN_HELPER.decimal_text(sid));
   if case_id is not null then
    RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_CASE_PICK_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(case_id));
    select PICK_WAVE_ID into wave_value from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=case_id;
   else
    RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_WAREHOUSE_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(x.get_number('fullpal_task_id')));
    wave_value:=x.get_number('wave_id');
   end if;
   RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_PICK_WAVE',RRL_STOCK_PLAN_HELPER.decimal_text(wave_value));
   n:=0;
   for ff in(select FULFILLMENT_ID,CUSTOMER_ORDER_ID,PICKED_CASE_TASK_ID,PICKED_PALLET_UID from RRL_CUSTOMER_ORDER_FULFILLMENT where LEGACY_SBORKA_PALLET_ID=sid and STATUS='SHIPPED'and SHIPPED_OPERATION_ID=load_id order by FULFILLMENT_ID)loop
    n:=n+1;if n>1 or nvl(ff.PICKED_CASE_TASK_ID,-1)!=nvl(case_id,-1)or(case_id is null and ff.PICKED_PALLET_UID!=physical_uid)then raise_application_error(-20886,'UNLOAD_ORIGINAL_FULFILLMENT_REQUIRED');end if;
    RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_CUSTOMER_ORDER_FULFILLMENT',RRL_STOCK_PLAN_HELPER.decimal_text(ff.FULFILLMENT_ID));
    RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_CUSTOMER_ORDER',RRL_STOCK_PLAN_HELPER.decimal_text(ff.CUSTOMER_ORDER_ID));
   end loop;
   if n!=1 then raise_application_error(-20886,'UNLOAD_ORIGINAL_FULFILLMENT_REQUIRED');end if;
  end loop;
  for association in(select ob.OFFER_OPERATION_ID,c.OPERATION_ID CANCEL_ID from RRL_TARE_OFFER_BOOK ob left join RRL_TARE_OFFER_CANCEL c on c.OFFER_OPERATION_ID=ob.OFFER_OPERATION_ID where ob.LOAD_OPERATION_ID=load_id order by ob.OFFER_OPERATION_ID)loop
   RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_TARE_OFFER',association.OFFER_OPERATION_ID);
   if association.CANCEL_ID is not null then RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_TARE_OFFER_CANCEL',association.CANCEL_ID);end if;
  end loop;
  for proof in(select OPERATION_ID,ORIGINAL_BOOK_OPERATION_ID,RETURN_OFFER_OPERATION_ID,RETURN_ACCEPT_OPERATION_ID from RRL_TARE_LOAD_RECOVERY where LOAD_OPERATION_ID=load_id order by OPERATION_ID)loop
   RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_TARE_LOAD_RECOVERY',proof.OPERATION_ID);
   RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_TARE_BOOK',proof.ORIGINAL_BOOK_OPERATION_ID);
   RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_TARE_OFFER',proof.RETURN_OFFER_OPERATION_ID);
   RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_TARE_ACCEPT',proof.RETURN_ACCEPT_OPERATION_ID);
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
  target_slot:=m.get_number('target_slot_id');
  if target_slot is not null then
   if target_slot<1 or target_slot!=trunc(target_slot)or m.get_string('scanned_to_slot_code')is null then raise_application_error(-20886,'UNLOAD_SLOT_SCAN_REQUIRED');end if;
   cell_text:=m.get_string('scan_cell');select sl.SLOT_CODE into slot_code from RRL_TOPOLOGY_CELL_SLOT sl join RRL_TOPOLOGY_CELL tc on tc.TOPOLOGY_CELL_ID=sl.TOPOLOGY_CELL_ID
    where sl.CELL_SLOT_ID=target_slot and sl.ACTIVE=1 and sl.SLOT_KIND='STORAGE_SLOT'and tc.ACTIVE=1 and tc.LEGACY_CELL_CODE=cell_text and tc.WARE_ID=lf.WARE_ID;
   if slot_code!=m.get_string('scanned_to_slot_code')then raise_application_error(-20886,'UNLOAD_SLOT_SCAN_REQUIRED');end if;
   select CANONICAL_REQUEST into request_wire from RRL_STOCK_OPERATION where OPERATION_ID=load_id;
   original_measures:=json_object_t.parse(request_wire).get_object('metadata').get_object('loading_context').get_object('measurements');
   RRL_STOCK_PLAN_HELPER.fence(f,'CELL',m.get_string('scan_cell'),6);
   RRL_STOCK_PLAN_HELPER.anchor(r,40,'SLOT',RRL_STOCK_PLAN_HELPER.decimal_text(target_slot));
   placement_task:=RRL_WAREHOUSE_TASK_SQ.nextval;placement_sync:=RRL_WH_TASK_SYNC_SQ.nextval;
   RRL_STOCK_HU_PLACEMENT_CORE.declare_place(r,placement_task,placement_sync);
   v.put('placement_slot',target_slot);v.put('placement_task',placement_task);v.put('placement_sync',placement_sync);v.put('original_measures',original_measures);
  elsif m.get_string('scanned_to_slot_code')is not null then raise_application_error(-20886,'UNLOAD_SLOT_SCAN_REQUIRED');end if;
  for i in 0..legs.get_size-1 loop
   x:=treat(legs.get(i)as json_object_t);uid_text:=x.get_string('uid');cell_text:=x.get_string('cell');qty:=RRL_STOCK_MATH.quantity(x.get_string('quantity'));
   if cell_text!=m.get_string('scan_cell')or x.get_number('reservation_id')is null then raise_application_error(-20886,'UNLOAD_ORIGINAL_RESERVED_CASE_LEAF_REQUIRED');end if;
   select REMAIN,HARD_RESERVED_BASE,STOCK_VERSION into physical,held,version_no from RRL_REMAINS where UID_POLETA=uid_text and CELL=cell_text;
   if physical!=0 or held!=0 then raise_application_error(-20886,'UNLOAD_ORIGINAL_LEAF_NOT_EMPTY');end if;
   select p.ARTICUL,rem.BASE_UOM into actual_article,actual_uom from RRL_PALLETS p join RRL_REMAINS rem on rem.UID_POLETA=p.UID_PALLET where p.UID_PALLET=uid_text and rem.CELL=cell_text;
   if actual_article!=x.get_string('article')or actual_uom!=x.get_string('base_uom')then raise_application_error(-20886,'UNLOAD_ORIGINAL_ARTICLE_UOM_REQUIRED');end if;
   unit_wire:=issued_units(load_id,uid_text,cell_text,qty);unit_array:=json_array_t.parse(unit_wire);
   if unit_array.get_size>0 then
    for unit_index in 0..unit_array.get_size-1 loop
     unit_obj:=treat(unit_array.get(unit_index)as json_object_t);RRL_STOCK_PLAN_HELPER.anchor(r,60,'UNIT',unit_obj.get_string('key'));
    end loop;
   end if;
   select nvl(sum(BASE_QTY),0)into signed_total from RRL_EVENTS where OPERATION_ID=load_id and UID_POLETA=uid_text;
   if signed_total!=-qty then raise_application_error(-20886,'UNLOAD_ORIGINAL_SIGNED_SHIP_JOURNAL_REQUIRED');end if;
   select RRL_STOCK_RESERVATION_SQ.nextval into new_res from dual;
   RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_STOCK_RESERVATION',RRL_STOCK_PLAN_HELPER.decimal_text(new_res));
   RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_STOCK_RESERVATION',RRL_STOCK_PLAN_HELPER.decimal_text(x.get_number('reservation_id')));
   RRL_STOCK_PLAN_HELPER.stock_closure(f,r,uid_text,x.get_string('article'),cell_text,cell_text);
   y:=x.clone();y.put('restored_units',unit_array);y.put('new_reservation',new_res);y.put('current_stock_version',version_no);restored.append(y);
  end loop;
  v.put('load_id',load_id);v.put('trip_id',lf.TT_ID);v.put('case_id',lf.ROOT_CASE_TASK_ID);v.put('root_uid',lf.ROOT_UID);v.put('members',members);v.put('recover_links',recover_links);v.put('warehouse',lf.WARE_ID);
  v.put('snapshot',json_object_t.parse(lf.COMPOSITION_JSON));v.put('legs',restored);
  p_domain:=v.to_clob;p_policies:=f.to_clob;p_resources:=r.to_clob;
 end;
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob)is
  d json_object_t:=json_object_t.parse(p_request);m json_object_t:=d.get_object('metadata');wire clob;v json_object_t;sd json_object_t;lf RRL_TT_HU_LOAD_FACT%rowtype;
  reason_text varchar2(1000):=m.get_string('reason');op varchar2(100):=d.get_string('operation_id');load_id varchar2(100);case_id number;sid number;trip_id number;ware number;cell_text varchar2(60);
  a json_array_t;x json_object_t;history RRL_STOCK_RESERVATION%rowtype;details json_object_t;uid_text varchar2(150);qty number;version_no number;physical number;held number;event_id number;n number;new_id number;uom_version number;uom_text varchar2(20);unit_wire clob;fresh_units clob;members json_array_t;nodes json_array_t;links json_array_t;node_wire clob;member_wire clob;root_uid varchar2(150);child_uid varchar2(150);child_case number;new_link number;parent_uid varchar2(150);placement_metadata json_object_t;placement_tree json_object_t;measures json_object_t;placement_wire clob;placement_root varchar2(150);new_coverage number;j json_object_t:=json_object_t();
 begin
  select RESOLVED_PLAN_JSON into wire from RRL_STOCK_OPERATION where OPERATION_ID=op;v:=json_object_t.parse(wire).get_object('domain');
  load_id:=v.get_string('load_id');case_id:=v.get_number('case_id');members:=v.get_array('members');root_uid:=v.get_string('root_uid');member_wire:=members.to_clob;node_wire:=v.get_object('snapshot').get_array('nodes').to_clob;trip_id:=v.get_number('trip_id');ware:=v.get_number('warehouse');cell_text:=m.get_string('scan_cell');
  assert_scope(load_id,p_actor);
  select ID into n from RRL_TRANSPORT_TASK where ID=trip_id for update;
  select TT_ID into n from RRL_TT_HU_LOAD_FACT where LOAD_OPERATION_ID=load_id for update;
  for owner in(select ID from RRL_SBORKA_PALLETS where ID in(select SID from json_table(member_wire,'$[*]'columns(SID number path '$.shipment_id')))order by ID)loop select ID into n from RRL_SBORKA_PALLETS where ID=owner.ID for update;end loop;
  for owner in(select CASE_PICK_TASK_ID from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID in(select C from json_table(member_wire,'$[*]'columns(C number path '$.case_id')))order by CASE_PICK_TASK_ID)loop select CASE_PICK_TASK_ID into n from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=owner.CASE_PICK_TASK_ID for update;end loop;
  source_state(load_id,m,lf,sd);
  if lf.TT_ID!=trip_id or nvl(lf.ROOT_CASE_TASK_ID,-1)!=nvl(case_id,-1)or nvl(lf.ROOT_UID,'~')!=nvl(root_uid,'~')or lf.WARE_ID!=ware or dbms_lob.compare(sd.get_array('members').to_clob,member_wire)!=0 then raise_application_error(-20890,'CLOSURE_CHANGED: unload owners');end if;
  a:=v.get_array('legs');
  for i in 0..a.get_size-1 loop
   x:=treat(a.get(i)as json_object_t);uid_text:=x.get_string('uid');new_id:=x.get_number('new_reservation');qty:=RRL_STOCK_MATH.quantity(x.get_string('quantity'));uom_text:=x.get_string('base_uom');uom_version:=x.get_number('uom_version');
   select REMAIN,HARD_RESERVED_BASE,STOCK_VERSION into physical,held,version_no from RRL_REMAINS where UID_POLETA=uid_text and CELL=cell_text for update;
   if physical!=0 or held!=0 or version_no!=x.get_number('current_stock_version')then raise_application_error(-20890,'CLOSURE_CHANGED: unload physical stock');end if;
   declare old_id number:=x.get_number('reservation_id');begin select *into history from RRL_STOCK_RESERVATION where RESERVATION_ID=old_id;end;
   if history.UID_PALLET!=uid_text or history.CELL!=cell_text or history.STATUS!='CONSUMED'or history.BASE_QTY!=0 or history.SOURCE_DOC_TYPE!='PICK_WAVE'or history.RESERVATION_DOMAIN!='PICKING'then raise_application_error(-20886,'UNLOAD_ORIGINAL_CONSUMED_RESERVATION_REQUIRED');end if;
   unit_wire:=x.get_array('restored_units').to_clob;fresh_units:=issued_units(load_id,uid_text,cell_text,qty);
   if dbms_lob.compare(unit_wire,fresh_units)!=0 then raise_application_error(-20890,'CLOSURE_CHANGED: unload original units');end if;
   RRL_STOCK_BALANCE_CORE.apply_delta(uid_text,cell_text,qty,0,uom_text,uom_version,version_no);
   RRL_STOCK_BALANCE_CORE.write_leg(uid_text,null,cell_text,qty,uom_text,uom_version,i+1,1,1,p_actor,event_id);
   details:=json_object_t();details.put('reservation_scope',history.RESERVATION_SCOPE);details.put('customer_order_id',history.CUSTOMER_ORDER_ID);details.put('customer_id',history.CUSTOMER_ID);details.put('pick_plan_id',history.PICK_PLAN_ID);details.put('pick_plan_line_id',history.PICK_PLAN_LINE_ID);details.put('restores_load_operation',load_id);
   RRL_STOCK_RESERVE_CORE.restore_consumed(history.RESERVATION_ID,new_id,qty,uom_version,p_actor);
   if x.get_array('restored_units').get_size>0 then RRL_STOCK_UNIT_CORE.restore_issued(uid_text,cell_text,new_id,qty,unit_wire);end if;
  end loop;
  nodes:=v.get_object('snapshot').get_array('nodes');
  for node_index in 0..nodes.get_size-1 loop
   x:=treat(nodes.get(node_index)as json_object_t);uid_text:=x.get_string('uid');
   if x.get_string('kind')='CONTAINER'then
    update RRL_PALLETS set HU_SHIPPED_OPERATION=null,HU_CURRENT_CELL=cell_text,HU_CONTENT_VERSION=HU_CONTENT_VERSION+1 where UID_PALLET=uid_text and HU_SHIPPED_OPERATION=load_id;
    if sql%rowcount!=1 then raise_application_error(-20890,'CLOSURE_CHANGED: unload container');end if;
   end if;
  end loop;
  for member_index in 0..members.get_size-1 loop
   x:=treat(members.get(member_index)as json_object_t);case_id:=x.get_number('case_id');sid:=x.get_number('shipment_id');
   if case_id is not null then
   update RRL_CASE_PICK_TASK set STATUS='WAIT_CONTROL',SHIPPED_OPERATION=null,CONTENT_VERSION=CONTENT_VERSION+1,CURRENT_CELL=cell_text,DONE_AT=null,UPDATED_AT=systimestamp,UPDATED_BY=p_actor where CASE_PICK_TASK_ID=case_id;
   RRL_STOCK_FULFILLMENT_FACT.project_unload(sid,load_id,case_id,p_actor);
   else
    RRL_STOCK_FULFILLMENT_FACT.project_unload_pallet(sid,load_id,x.get_string('physical_uid'),p_actor);
   end if;
   update RRL_SBORKA_PALLETS set CONDITION=0,PROOVED=0,SCAN_MARK_PROVED=0,SCAN_PHYSICAL_UNIT_COUNT=0,SCAN_ITEM_PROVED=0,TRIAL_WEIGHT=0,WOOD_WEIGHT=0,PROOVED_BY_SCAN=0,SCAN_CONTENT_SIGNATURE=null,WEIGHT_CONTENT_SIGNATURE=null,SCAN_QC_OPERATION_ID=null,WEIGHT_QC_OPERATION_ID=null,QC_RESCAN_REQUIRED=1 where ID=sid;
  end loop;
  links:=v.get_array('recover_links');
  for link_index in 0..links.get_size-1 loop
   x:=treat(links.get(link_index)as json_object_t);parent_uid:=x.get_string('parent');uid_text:=x.get_string('child');new_link:=x.get_number('new_id');child_uid:=null;child_case:=null;
   if substr(uid_text,1,5)='CASE:'then child_case:=to_number(substr(uid_text,6));else child_uid:=uid_text;end if;
   insert into RRL_WMS_HU_LINK(HU_LINK_ID,PARENT_UID,CHILD_PALLET_UID,CHILD_CASE_TASK_ID,ACTIVE_FLAG,LINK_VERSION,LINKED_OPERATION_ID,LINKED_BY)values(new_link,parent_uid,child_uid,child_case,1,0,op,p_actor);
  end loop;
  if v.get_number('placement_slot')is not null then
   placement_root:=nvl(lf.ROOT_UID,'CASE:'||RRL_STOCK_PLAN_HELPER.decimal_text(lf.ROOT_CASE_TASK_ID));
   if lf.ROOT_CASE_TASK_ID is null then placement_tree:=json_object_t.parse(RRL_STOCK_HU_READ.snapshot_json(placement_root));
   else placement_tree:=json_object_t.parse(RRL_STOCK_HU_READ.case_snapshot_json(lf.ROOT_CASE_TASK_ID));end if;
   measures:=v.get_object('original_measures').clone();measures.put('content_version',treat(placement_tree.get_array('nodes').get(0)as json_object_t).get_number('version'));
   placement_metadata:=m.clone();placement_metadata.put('target_cell',cell_text);placement_metadata.put('planned_physical_task_id',v.get_number('placement_task'));placement_metadata.put('measurements',measures);
   placement_wire:=RRL_STOCK_HU_SLOT.target_json(placement_tree.to_clob,placement_metadata.to_clob,null,placement_root);
   RRL_STOCK_HU_PLACEMENT_CORE.record_place(p_request,p_actor,placement_root,ware,cell_text,v.get_number('placement_task'),v.get_number('placement_slot'),v.get_number('placement_sync'),placement_wire,lf.ROOT_CASE_TASK_ID);
   for leg_index in 0..a.get_size-1 loop
    x:=treat(a.get(leg_index)as json_object_t);qty:=RRL_STOCK_MATH.quantity(x.get_string('quantity'));new_id:=x.get_number('new_reservation');
    RRL_STOCK_RESERVE_CORE.move_coverage(new_id,new_id,x.get_string('uid'),cell_text,ware,qty,v.get_number('placement_slot'),p_actor,new_coverage);
    if new_coverage!=new_id then raise_application_error(-20869,'UNLOAD_RESERVATION_IDENTITY_CHANGED');end if;
   end loop;
   j.put('placement_task',v.get_number('placement_task'));j.put('placement_slot',v.get_number('placement_slot'));
  end if;
  insert into RRL_TT_UNLOAD_FACT(OPERATION_ID,LOAD_OPERATION_ID,TT_ID,CASE_PICK_TASK_ID,ROOT_UID,WARE_ID,CELL_CODE,COMPOSITION_JSON,REASON,CREATED_BY)
   values(op,load_id,trip_id,lf.ROOT_CASE_TASK_ID,lf.ROOT_UID,ware,cell_text,lf.COMPOSITION_JSON,reason_text,p_actor);
  update RRL_TT_HU_LOAD_FACT set STATUS='UNLOADED'where LOAD_OPERATION_ID=load_id;
  update RRL_TT_HU_LOAD_ST set ACTIVE_FLAG=0 where LOAD_OPERATION_ID=load_id and ACTIVE_FLAG=1;
  if sql%rowcount!=members.get_size then raise_application_error(-20890,'CLOSURE_CHANGED: unload active members');end if;
  j.put('operation_id',op);j.put('status','UNLOADED');j.put('load_operation_id',load_id);j.put('case_task_id',lf.ROOT_CASE_TASK_ID);j.put('root_uid',lf.ROOT_UID);j.put('members',members);j.put('cell',cell_text);j.put('restored_lines',a);j.put('quality_control_required',true);j.put('original_ship_history_preserved',true);p_result:=j.to_clob;
 end;
end;
/
