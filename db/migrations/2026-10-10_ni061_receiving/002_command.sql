create or replace package RRL_STOCK_INTERWARE_REC authid definer accessible by(package RRL_STOCK_POSTING_API) as
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
end;
/
create or replace package body RRL_STOCK_INTERWARE_REC as
 procedure describe_source(p_request clob,p_actor varchar2,p_domain out json_object_t) is
 d json_object_t:=json_object_t.parse(p_request);m json_object_t:=d.get_object('metadata');v_plan varchar2(100):=d.get_object('source').get_string('plan_operation_id');
 plan RRL_INTERWARE_PLAN%rowtype;cargo RRL_TT_HU_LOAD_FACT%rowtype;lot RRL_PALLETS%rowtype;nodes json_array_t;leaf json_object_t;
 v_kind varchar2(80):=d.get_string('command_type');v_unload varchar2(100);v_vehicle varchar2(60);v_cell varchar2(60);v_uom varchar2(20);v_qty number;v_version number;v_scan_article varchar2(160);v_scan_uom varchar2(20);n number;
 begin
 select * into plan from RRL_INTERWARE_PLAN where OPERATION_ID=v_plan;
 select count(*)into n from RUSERS u where ID=p_actor and nvl(DELETED,0)=0 and(WARE_ID=plan.TARGET_WARE_ID or upper(trim(USER_GROUP))='GLOBAL_ADMIN')and RRL_HAS_WRIGHT(u.ID,'interwarehouse_receive')=1;
 if n!=1 then raise_application_error(-20882,'INTERWARE_TARGET_RECEIVER_REQUIRED');end if;
 select * into cargo from RRL_TT_HU_LOAD_FACT where LOAD_OPERATION_ID=plan.SOURCE_LOAD_OPERATION_ID;
 if cargo.STATUS!='DEPARTED' or dbms_lob.compare(cargo.COMPOSITION_JSON,plan.SOURCE_COMPOSITION_JSON)!=0 then raise_application_error(-20886,'INTERWARE_ORIGINAL_DEPARTURE_CHANGED');end if;
 select * into lot from RRL_PALLETS where UID_PALLET=plan.ROOT_UID;
 nodes:=json_object_t.parse(plan.SOURCE_COMPOSITION_JSON).get_array('nodes');
 if nodes.get_size!=1 then raise_application_error(-20886,'INTERWARE_SINGLE_STOCK_NODE_REQUIRED');end if;
 leaf:=treat(nodes.get(0)as json_object_t);
 if leaf.get_string('uid')!=plan.ROOT_UID or leaf.get_string('article')!=lot.ARTICUL or leaf.get_string('kind')!='STOCK' then raise_application_error(-20886,'INTERWARE_ORIGINAL_LOT_CHANGED');end if;
 v_qty:=RRL_STOCK_MATH.quantity(leaf.get_string('quantity'));v_uom:=leaf.get_string('base_uom');
 select count(*)into n from dual where exists(select 1 from RRL_SKU_RECEIPT_PROFILE where ARTICUL=lot.ARTICUL)or exists(select 1 from RRL_SKU_RECEIPT_POLICY where ARTICUL=lot.ARTICUL and MARKING_REQUIRED=1)or exists(select 1 from RRL_FINISHED_GOODS_SKU where ARTICUL=lot.ARTICUL and CRPT_REQUIRED=1);
 if n!=0 then raise_application_error(-20886,'INTERWARE_MARKED_UNIT_FLOW_REQUIRED');end if;
 select count(*)into n from RRL_REMAINS where UID_POLETA=plan.ROOT_UID and(nvl(REMAIN,0)!=0 or nvl(HARD_RESERVED_BASE,0)!=0);
 if n!=0 then raise_application_error(-20886,'INTERWARE_SOURCE_ALREADY_IN_STOCK');end if;
 select count(*)into n from RRL_INTERWARE_RECEIPT where PLAN_OPERATION_ID=v_plan;
 if n!=0 then raise_application_error(-20886,'INTERWARE_PLAN_ALREADY_RECEIVED');end if;
 select TRANSPORT into v_vehicle from RRL_TRANSPORT_TASK where ID=plan.SOURCE_TT_ID;
 if m.get_string('scan_pallet') is null or m.get_string('scan_pallet')!=plan.ROOT_UID then raise_application_error(-20886,'INTERWARE_PALLET_SCAN_REQUIRED');end if;
 select count(*)into n from RRL_TT_DOCK where DOCK=plan.INBOUND_DOCK and WARE_ID=plan.TARGET_WARE_ID and nvl(DOCK_IS_BLOCKED,0)=0;
 if n!=1 then raise_application_error(-20886,'INTERWARE_INBOUND_DOCK_UNAVAILABLE');end if;
 p_domain:=json_object_t();p_domain.put('plan_operation_id',v_plan);p_domain.put('source_load_operation_id',plan.SOURCE_LOAD_OPERATION_ID);p_domain.put('source_st_id',plan.SOURCE_ST_ID);
 p_domain.put('uid',plan.ROOT_UID);p_domain.put('warehouse_id',plan.TARGET_WARE_ID);p_domain.put('article',lot.ARTICUL);p_domain.put('quantity',RRL_STOCK_PLAN_HELPER.decimal_text(v_qty));p_domain.put('base_uom',v_uom);p_domain.put('vehicle_number',v_vehicle);p_domain.put('inbound_dock',plan.INBOUND_DOCK);
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
  p_domain.put('unload_operation_id',v_unload);p_domain.put('receive_cell',v_cell);p_domain.put('uom_version',v_version);
 end if;
 exception when no_data_found then raise_application_error(-20886,'INTERWARE_PLAN_DEPARTURE_UNLOAD_OR_LOT_REQUIRED');
 end;
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob) is
 d json_object_t:=json_object_t.parse(p_request);v json_object_t;f json_array_t:=json_array_t();r json_array_t:=json_array_t();
 begin
 describe_source(p_request,d.get_string('actor'),v);
 RRL_STOCK_PLAN_HELPER.fence(f,'RELEASE','STOCK');RRL_STOCK_PLAN_HELPER.fence(f,'CONFIG','WAREHOUSE');RRL_STOCK_PLAN_HELPER.anchor(r,10,'OP',p_operation);
 RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','STOCK.OUTBOX:'||rawtohex(sys.dbms_crypto.hash(utl_i18n.string_to_raw(p_operation,'AL32UTF8'),sys.dbms_crypto.hash_sh256)));
 RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_INTERWARE_PLAN',v.get_string('plan_operation_id'));
 RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_INTERWARE_UNLOAD',nvl(v.get_string('unload_operation_id'),p_operation));
 RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_INTERWARE_RECEIPT',p_operation);
 RRL_STOCK_PLAN_HELPER.stock_closure(f,r,v.get_string('uid'),v.get_string('article'),null,v.get_string('receive_cell'));
 p_policies:=f.to_clob;p_resources:=r.to_clob;p_domain:=v.to_clob;
 end;
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob) is
 d json_object_t:=json_object_t.parse(p_request);op varchar2(100):=d.get_string('operation_id');v_kind varchar2(80):=d.get_string('command_type');resolved clob;v json_object_t;fresh json_object_t;j json_object_t:=json_object_t();
 v_plan varchar2(100);v_uid varchar2(200);v_source varchar2(100);v_unload varchar2(100);v_ware number;v_article varchar2(160);v_cell varchar2(60);v_uom varchar2(20);v_qty number;v_ver number;v_event number;v_vehicle varchar2(60);v_dock varchar2(60);v_payload clob;
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
  RRL_STOCK_BALANCE_CORE.apply_delta(v_uid,v_cell,v_qty,0,v_uom,v_ver,0);
  RRL_STOCK_BALANCE_CORE.write_leg(v_uid,null,v_cell,v_qty,v_uom,v_ver,1,1,1,p_actor,v_event);
  insert into RRL_INTERWARE_RECEIPT(OPERATION_ID,PLAN_OPERATION_ID,UNLOAD_OPERATION_ID,ROOT_UID,WARE_ID,RECEIVE_CELL,ARTICLE,BASE_QTY,BASE_UOM,SOURCE_LOAD_OPERATION_ID,STOCK_EVENT_ID,ACTOR)
  values(op,v_plan,v_unload,v_uid,v_ware,v_cell,v_article,v_qty,v_uom,v_source,v_event,p_actor);
  j.put('status','RECEIVED_PENDING_PLACEMENT');j.put('stock_changed',true);j.put('quantity',v.get_string('quantity'));j.put('base_uom',v_uom);j.put('cell',v_cell);j.put('event_id',v_event);j.put('external_sap_ack',false);
  v_payload:=j.to_clob;
  insert into RRL_SAP_RECEIPT_OUTBOX(EVENT_ID,EVENT_TYPE,PAYLOAD_JSON)values('INTERWARE:'||rawtohex(sys.dbms_crypto.hash(utl_i18n.string_to_raw(op,'AL32UTF8'),sys.dbms_crypto.hash_sh256)),'INTERWAREHOUSE_RECEIVED',v_payload);
 end if;
 p_result:=j.to_clob;
 end;
end;
/
