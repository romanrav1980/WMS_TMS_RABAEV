create or replace package body RRL_STOCK_INTERWARE_REC as
 procedure assert_scope(p_plan varchar2,p_actor varchar2)is n number;
 begin
  select count(*)into n from RRL_INTERWARE_PLAN p join RUSERS u on u.ID=p_actor where p.OPERATION_ID=p_plan and nvl(u.DELETED,0)=0 and RRL_HAS_WRIGHT(u.ID,'interwarehouse_receive')=1 and(u.WARE_ID=p.TARGET_WARE_ID or upper(trim(u.USER_GROUP))='GLOBAL_ADMIN');
  if n!=1 then raise_application_error(-20882,'INTERWARE_TARGET_RECEIVER_REQUIRED');end if;
 end;
 procedure describe_source(p_request clob,p_actor varchar2,p_domain out json_object_t) is
 d json_object_t:=json_object_t.parse(p_request);m json_object_t:=d.get_object('metadata');v_plan varchar2(100):=d.get_object('source').get_string('plan_operation_id');
 plan RRL_INTERWARE_PLAN%rowtype;cargo RRL_TT_HU_LOAD_FACT%rowtype;lot RRL_PALLETS%rowtype;nodes json_array_t;leaf json_object_t;
 v_kind varchar2(80):=d.get_string('command_type');v_unload varchar2(100);v_vehicle varchar2(60);v_cell varchar2(60);v_uom varchar2(20);v_qty number;v_version number;v_scan_article varchar2(160);v_scan_uom varchar2(20);n number;manifest clob;source_units json_object_t;scan_domain json_object_t;scan_legs json_array_t;scan_leg json_object_t;unit_count number;
 begin
 select * into plan from RRL_INTERWARE_PLAN where OPERATION_ID=v_plan;
 plan:=RRL_INTERWARE_ROUTING.resolved(plan);
 select count(*)into n from RUSERS u where ID=p_actor and nvl(DELETED,0)=0 and(WARE_ID=plan.TARGET_WARE_ID or upper(trim(USER_GROUP))='GLOBAL_ADMIN')and RRL_HAS_WRIGHT(u.ID,'interwarehouse_receive')=1;
 if n!=1 then raise_application_error(-20882,'INTERWARE_TARGET_RECEIVER_REQUIRED');end if;
 select * into cargo from RRL_TT_HU_LOAD_FACT where LOAD_OPERATION_ID=plan.SOURCE_LOAD_OPERATION_ID;
 if cargo.STATUS!='DEPARTED' or dbms_lob.compare(cargo.COMPOSITION_JSON,plan.SOURCE_COMPOSITION_JSON)!=0 then raise_application_error(-20886,'INTERWARE_ORIGINAL_DEPARTURE_CHANGED');end if;
 select * into lot from RRL_PALLETS where UID_PALLET=plan.ROOT_UID;
 nodes:=json_object_t.parse(plan.SOURCE_COMPOSITION_JSON).get_array('nodes');
 if nodes.get_size<1 or nodes.get_size>200 then raise_application_error(-20886,'INTERWARE_STOCK_NODE_BOUND');end if;
 leaf:=null;
 for i in 0..nodes.get_size-1 loop
  declare candidate json_object_t:=treat(nodes.get(i)as json_object_t);begin
   if candidate.get_string('kind')='STOCK'then
    if leaf is not null then raise_application_error(-20886,'INTERWARE_ONE_STOCK_NODE_REQUIRED');end if;leaf:=candidate;
   elsif candidate.get_string('kind')!='CONTAINER'then raise_application_error(-20886,'INTERWARE_STOCK_CONTAINER_ONLY');end if;
  end;
 end loop;
 if leaf is null then raise_application_error(-20886,'INTERWARE_STOCK_NODE_REQUIRED');end if;
 RRL_IW_HU_SOURCE.assert_context(plan.SOURCE_LOAD_OPERATION_ID,plan.SOURCE_HU_JSON);

 if leaf.get_string('uid')!=plan.ROOT_UID or leaf.get_string('article')!=lot.ARTICUL or leaf.get_string('kind')!='STOCK' then raise_application_error(-20886,'INTERWARE_ORIGINAL_LOT_CHANGED');end if;
 v_qty:=RRL_STOCK_MATH.quantity(leaf.get_string('quantity'));v_uom:=leaf.get_string('base_uom');
 select count(*)into n from dual where exists(select 1 from RRL_SKU_RECEIPT_PROFILE where ARTICUL=lot.ARTICUL)or exists(select 1 from RRL_SKU_RECEIPT_POLICY where ARTICUL=lot.ARTICUL and MARKING_REQUIRED=1)or exists(select 1 from RRL_FINISHED_GOODS_SKU where ARTICUL=lot.ARTICUL and CRPT_REQUIRED=1);
 manifest:=RRL_INTERWARE_UNIT_SOURCE.issued_manifest(plan.SOURCE_LOAD_OPERATION_ID,plan.ROOT_UID,plan.SOURCE_COMPOSITION_JSON);
 source_units:=json_object_t.parse(manifest);
 if source_units.get_number('physical_unit_count')>0 then
  select MANIFEST_JSON into manifest from RRL_INTERWARE_UNIT_MANIFEST where PLAN_OPERATION_ID=v_plan;
  if dbms_lob.compare(manifest,source_units.to_clob)!=0 then raise_application_error(-20886,'INTERWARE_FROZEN_UNIT_SOURCE_CHANGED');end if;
 end if;
 select count(*)into n from RRL_REMAINS where UID_POLETA=plan.ROOT_UID and(nvl(REMAIN,0)!=0 or nvl(HARD_RESERVED_BASE,0)!=0);
 if n!=0 then raise_application_error(-20886,'INTERWARE_SOURCE_ALREADY_IN_STOCK');end if;
 select count(*)into n from RRL_INTERWARE_RECEIPT where PLAN_OPERATION_ID=v_plan;
 if n!=0 then raise_application_error(-20886,'INTERWARE_PLAN_ALREADY_RECEIVED');end if;
 select TRANSPORT into v_vehicle from RRL_TRANSPORT_TASK where ID=plan.SOURCE_TT_ID;
 if m.get_string('scan_pallet') is null or m.get_string('scan_pallet')!=nvl(plan.SOURCE_PLACE_UID,plan.ROOT_UID) then raise_application_error(-20886,'INTERWARE_PALLET_SCAN_REQUIRED');end if;
 select count(*)into n from RRL_TT_DOCK where DOCK=plan.INBOUND_DOCK and WARE_ID=plan.TARGET_WARE_ID and nvl(DOCK_IS_BLOCKED,0)=0;
 if n!=1 then raise_application_error(-20886,'INTERWARE_INBOUND_DOCK_UNAVAILABLE');end if;
 p_domain:=json_object_t();p_domain.put('plan_operation_id',v_plan);p_domain.put('source_load_operation_id',plan.SOURCE_LOAD_OPERATION_ID);p_domain.put('source_st_id',plan.SOURCE_ST_ID);
 p_domain.put('uid',plan.ROOT_UID);p_domain.put('warehouse_id',plan.TARGET_WARE_ID);p_domain.put('article',lot.ARTICUL);p_domain.put('quantity',RRL_STOCK_PLAN_HELPER.decimal_text(v_qty));p_domain.put('base_uom',v_uom);p_domain.put('vehicle_number',v_vehicle);p_domain.put('inbound_dock',plan.INBOUND_DOCK);
 if plan.SOURCE_HU_JSON is not null then p_domain.put('nested_source',json_object_t.parse(plan.SOURCE_HU_JSON));end if;
 if source_units.get_number('physical_unit_count')>0 then
  p_domain.put('source_units',source_units.get_array('units'));p_domain.put('source_cell',source_units.get_string('source_cell'));p_domain.put('original_unit_signature',source_units.get_string('unit_signature'));
 end if;
 if m.get_boolean('partial_receipt')then
  if plan.SOURCE_HU_JSON is not null then raise_application_error(-20886,'INTERWARE_NESTED_WHOLE_RECEIPT_REQUIRED');end if;
  if v_kind!='INTERWARE_RECEIVE'then raise_application_error(-20886,'INTERWARE_PARTIAL_RECEIPT_ONLY');end if;
  RRL_STOCK_INTERWARE_PART.describe_partial(m,plan.ROOT_UID,v_qty,v_uom,lot.ARTICUL,p_domain);
  v_qty:=RRL_STOCK_MATH.quantity(p_domain.get_string('quantity'));
  RRL_STOCK_INTERWARE_PART.describe_selected_units(m,p_domain);
 end if;
 if v_kind='INTERWARE_UNLOAD' then
  select count(*)into n from RRL_INTERWARE_UNLOAD where PLAN_OPERATION_ID=v_plan;if n!=0 then raise_application_error(-20886,'INTERWARE_PLAN_ALREADY_UNLOADED');end if;
  if m.get_string('scan_vehicle') is null or m.get_string('scan_vehicle')!=v_vehicle or m.get_string('scan_dock') is null or m.get_string('scan_dock')!=plan.INBOUND_DOCK then raise_application_error(-20886,'INTERWARE_VEHICLE_DOCK_SCAN_REQUIRED');end if;
 else
  select OPERATION_ID into v_unload from RRL_INTERWARE_UNLOAD where PLAN_OPERATION_ID=v_plan;
  v_cell:=m.get_string('scan_cell');
  select count(*)into n from RRL_CELLS where CELL=v_cell and WARE_ID=plan.TARGET_WARE_ID and nvl(BLOCKED_FOR_ACCEPT,0)=0 and BLOCKED_FOR_REMAINS=1 and BLOCKED_FOR_POPOLNENIE=1;
  if n!=1 then raise_application_error(-20886,'INTERWARE_TARGET_RECEIVE_CELL_REQUIRED');end if;
  if m.get_string('article') is null or m.get_string('article')!=lot.ARTICUL or m.get_string('base_uom') is null or m.get_string('base_uom')!=v_uom or RRL_STOCK_MATH.quantity(m.get_string('quantity'))!=v_qty then raise_application_error(-20886,'INTERWARE_EXACT_ORIGINAL_QUANTITY_REQUIRED');end if;
  RRL_STOCK_QC_ITEM.resolve_barcode(m.get_string('scan_article'),v_scan_article,v_scan_uom);
  if v_scan_article!=lot.ARTICUL then raise_application_error(-20886,'INTERWARE_FOREIGN_ARTICLE_BARCODE');end if;
  select max(POLICY_VERSION)into v_version from RRL_STOCK_UOM_CONVERSION where ARTICUL=lot.ARTICUL and INPUT_UOM=v_uom and BASE_UOM=v_uom and NUMERATOR=DENOMINATOR;
  if v_version is null then raise_application_error(-20886,'INTERWARE_BASE_UOM_REQUIRED');end if;
  if source_units.get_number('physical_unit_count')>0 then
   scan_leg:=json_object_t();scan_leg.put('article',lot.ARTICUL);scan_leg.put('uid',plan.ROOT_UID);scan_leg.put('cell',source_units.get_string('source_cell'));scan_leg.put('base_uom',v_uom);scan_leg.put('quantity',RRL_STOCK_PLAN_HELPER.decimal_text(v_qty));
   if p_domain.has('partial_receipt')then
    scan_leg.put('uid',plan.ROOT_UID);scan_leg.put('selected_unit_keys',p_domain.get_array('selected_unit_keys'));
   end if;
   scan_legs:=json_array_t();scan_legs.append(scan_leg);scan_domain:=json_object_t();scan_domain.put('legs',scan_legs);
   if RRL_INTERWARE_MARK_SCAN.required_for_article(lot.ARTICUL)=1 then RRL_INTERWARE_MARK_SCAN.validate_scan(scan_domain.to_clob,m.to_clob,unit_count);end if;
  elsif m.has('unit_scans') and m.get_array('unit_scans').get_size>0 then raise_application_error(-20886,'INTERWARE_UNEXPECTED_UNIT_SCANS');end if;
  p_domain.put('unload_operation_id',v_unload);p_domain.put('receive_cell',v_cell);p_domain.put('uom_version',v_version);
 end if;
 exception when no_data_found then raise_application_error(-20886,'INTERWARE_PLAN_DEPARTURE_UNLOAD_OR_LOT_REQUIRED');
 end;
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob) is
 d json_object_t:=json_object_t.parse(p_request);v json_object_t;f json_array_t:=json_array_t();r json_array_t:=json_array_t();units json_array_t;unit_value json_object_t;
 begin
 describe_source(p_request,d.get_string('actor'),v);
 RRL_IW_HU_REC_CORE.declare_rows(v,p_operation,r);
 RRL_STOCK_PLAN_HELPER.fence(f,'RELEASE','STOCK');RRL_STOCK_PLAN_HELPER.fence(f,'CONFIG','WAREHOUSE');RRL_STOCK_PLAN_HELPER.anchor(r,10,'OP',p_operation);
 RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','STOCK.OUTBOX:'||rawtohex(sys.dbms_crypto.hash(utl_i18n.string_to_raw(p_operation,'AL32UTF8'),sys.dbms_crypto.hash_sh256)));
 RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_INTERWARE_PLAN',v.get_string('plan_operation_id'));
 RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_INTERWARE_UNLOAD',nvl(v.get_string('unload_operation_id'),p_operation));
 RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_INTERWARE_RECEIPT',p_operation);
 RRL_STOCK_PLAN_HELPER.stock_closure(f,r,v.get_string('uid'),v.get_string('article'),null,v.get_string('receive_cell'));

 if v.has('partial_receipt')then
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_PALLETS',v.get_string('uid'));
  RRL_STOCK_PLAN_HELPER.stock_closure(f,r,v.get_string('original_root_uid'),v.get_string('article'),null,null);
  RRL_STOCK_PLAN_HELPER.anchor(r,50,'STOCK',v.get_string('source_origin_uid'));
 end if;
 if v.has('source_units')then
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_INTERWARE_UNIT_MANIFEST',v.get_string('plan_operation_id'));
  units:=v.get_array('source_units');
  for i in 0..units.get_size-1 loop unit_value:=treat(units.get(i)as json_object_t);RRL_STOCK_PLAN_HELPER.anchor(r,60,'UNIT',unit_value.get_string('key'));end loop;
 end if;
 p_policies:=f.to_clob;p_resources:=r.to_clob;p_domain:=v.to_clob;
 end;
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob) is
 d json_object_t:=json_object_t.parse(p_request);op varchar2(100):=d.get_string('operation_id');v_kind varchar2(80):=d.get_string('command_type');resolved clob;v json_object_t;fresh json_object_t;j json_object_t:=json_object_t();
 v_plan varchar2(100);v_uid varchar2(200);v_source varchar2(100);v_unload varchar2(100);v_ware number;v_article varchar2(160);v_cell varchar2(60);v_uom varchar2(20);v_qty number;v_ver number;v_event number;v_vehicle varchar2(60);v_dock varchar2(60);v_payload clob;v_original_root varchar2(200);v_expected_qty number;v_short_reason varchar2(4000);v_short_ref varchar2(2000);
 begin
 select RESOLVED_PLAN_JSON into resolved from RRL_STOCK_OPERATION where OPERATION_ID=op;v:=json_object_t.parse(resolved).get_object('domain');
 describe_source(p_request,p_actor,fresh);if dbms_lob.compare(v.to_clob,fresh.to_clob)!=0 then raise_application_error(-20886,'INTERWARE_RECEIVING_SOURCE_CHANGED');end if;
 v_plan:=v.get_string('plan_operation_id');v_uid:=v.get_string('uid');v_ware:=v.get_number('warehouse_id');v_article:=v.get_string('article');v_source:=v.get_string('source_load_operation_id');v_vehicle:=v.get_string('vehicle_number');v_dock:=v.get_string('inbound_dock');
 j.put('operation_id',op);j.put('plan_operation_id',v_plan);j.put('pallet_identifier',v_uid);j.put('warehouse_id',v_ware);j.put('source_load_operation_id',v_source);j.put('source_st_id',v.get_number('source_st_id'));j.put('customer_fulfillment_repeated',false);
 if v_kind='INTERWARE_UNLOAD' then
  insert into RRL_INTERWARE_UNLOAD(OPERATION_ID,PLAN_OPERATION_ID,ROOT_UID,WARE_ID,VEHICLE_NUMBER,INBOUND_DOCK,ACTOR)values(op,v_plan,v_uid,v_ware,v_vehicle,v_dock,p_actor);
  j.put('status','UNLOADED_PENDING_RECEIPT');j.put('stock_changed',false);
 else
  v_cell:=v.get_string('receive_cell');v_unload:=v.get_string('unload_operation_id');v_uom:=v.get_string('base_uom');v_qty:=RRL_STOCK_MATH.quantity(v.get_string('quantity'));v_ver:=v.get_number('uom_version');
  RRL_STOCK_LOCATION_CORE.assert_receiving(v_cell,v_ware);
  if v.has('partial_receipt')then RRL_STOCK_INTERWARE_PART.create_pallet(v,op);end if;
  RRL_STOCK_BALANCE_CORE.apply_delta(v_uid,v_cell,v_qty,0,v_uom,v_ver,0);
  RRL_STOCK_BALANCE_CORE.write_leg(v_uid,null,v_cell,v_qty,v_uom,v_ver,1,1,1,p_actor,v_event);
  if v.has('source_units')then
   if v.has('partial_receipt')then
    RRL_STOCK_UNIT_CORE.receive_partial_issued(v.get_string('original_root_uid'),v.get_string('source_cell'),v_uid,v_cell,v_qty,v.get_array('source_units').to_clob);
   else
   RRL_STOCK_UNIT_CORE.receive_issued(v_uid,v.get_string('source_cell'),v_cell,v_qty,v.get_array('source_units').to_clob);
   end if;
   j.put('physical_unit_count',v.get_array('source_units').get_size);j.put('original_unit_signature',v.get_string('original_unit_signature'));j.put('regulatory_ack_verified',false);
  end if;
  if v.has('nested_source')then
   RRL_IW_HU_REC_CORE.restore(v,op,p_actor);
   j.put('physical_place_identifier',v.get_object('nested_source').get_string('place_uid'));
   j.put('physical_tree_restored',true);j.put('physical_place_count',1);
  end if;
  v_original_root:=v.get_string('original_root_uid');v_expected_qty:=v.get_number('expected_quantity');
  v_short_reason:=v.get_string('discrepancy_reason');v_short_ref:=v.get_string('discrepancy_reference');
  insert into RRL_INTERWARE_RECEIPT(OPERATION_ID,PLAN_OPERATION_ID,UNLOAD_OPERATION_ID,ROOT_UID,WARE_ID,RECEIVE_CELL,ARTICLE,BASE_QTY,BASE_UOM,SOURCE_LOAD_OPERATION_ID,STOCK_EVENT_ID,ACTOR,ORIGINAL_ROOT_UID,EXPECTED_BASE_QTY,DISCREPANCY_REASON,DISCREPANCY_REFERENCE)
  values(op,v_plan,v_unload,v_uid,v_ware,v_cell,v_article,v_qty,v_uom,v_source,v_event,p_actor,v_original_root,v_expected_qty,v_short_reason,v_short_ref);
  j.put('status','RECEIVED_PENDING_PLACEMENT');j.put('stock_changed',true);j.put('quantity',v.get_string('quantity'));j.put('base_uom',v_uom);j.put('cell',v_cell);j.put('event_id',v_event);j.put('external_sap_ack',false);
  if v.has('partial_receipt')then
   j.put('status','RECEIVED_PARTIAL_PENDING_PLACEMENT');j.put('original_pallet_identifier',v.get_string('original_root_uid'));
   j.put('expected_quantity',v.get_string('expected_quantity'));j.put('short_quantity',v.get_string('short_quantity'));
   j.put('carrier_shortage_resolved',false);j.put('discrepancy_reason',v.get_string('discrepancy_reason'));j.put('discrepancy_reference',v.get_string('discrepancy_reference'));
  end if;
  v_payload:=j.to_clob;
  insert into RRL_SAP_RECEIPT_OUTBOX(EVENT_ID,EVENT_TYPE,PAYLOAD_JSON)values('INTERWARE:'||rawtohex(sys.dbms_crypto.hash(utl_i18n.string_to_raw(op,'AL32UTF8'),sys.dbms_crypto.hash_sh256)),'INTERWAREHOUSE_RECEIVED',v_payload);
 end if;
 p_result:=j.to_clob;
 end;
end;
/
