create or replace package RRL_IW_GROUP_REC authid definer accessible by(package RRL_STOCK_INTERWARE_REC)as
 procedure describe_source(p_request clob,p_actor varchar2,p_domain out json_object_t);
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure assert_fresh(p_request clob,p_actor varchar2,p_domain json_object_t);
end;
/
create or replace package body RRL_IW_GROUP_REC as
 procedure describe_source(p_request clob,p_actor varchar2,p_domain out json_object_t)is
 d json_object_t:=json_object_t.parse(p_request);m json_object_t:=d.get_object('metadata');v_plan varchar2(100):=d.get_object('source').get_string('plan_operation_id');
 plan RRL_IW_GROUP_PLAN%rowtype;source_value json_object_t;wire clob;lots json_array_t;nodes json_array_t;links json_array_t;
 nested_value json_object_t:=json_object_t();containers json_array_t:=json_array_t();nested_links json_array_t:=json_array_t();
 legs json_array_t:=json_array_t();item json_object_t;x json_object_t;manifest json_object_t;leg json_object_t;
 v_kind varchar2(80):=d.get_string('command_type');v_vehicle varchar2(60);v_cell varchar2(60);v_unload varchar2(100);
 v_uid varchar2(200);v_article varchar2(160);v_uom varchar2(20);v_barcode_article varchar2(160);v_barcode_uom varchar2(20);v_qty number;v_version number;
 n number;unit_count number;total_units number:=0;requested json_array_t;seen_count number;first_uid varchar2(200);
 begin
 select *into plan from RRL_IW_GROUP_PLAN where OPERATION_ID=v_plan;
 select count(*)into n from RUSERS where ID=p_actor and nvl(DELETED,0)=0 and RRL_HAS_WRIGHT(ID,'interwarehouse_receive')=1 and(WARE_ID=plan.TARGET_WARE_ID or upper(trim(USER_GROUP))='GLOBAL_ADMIN');
 if n!=1 then raise_application_error(-20882,'INTERWARE_GROUP_TARGET_RECEIVER_REQUIRED');end if;
 wire:=RRL_IW_GROUP_ARCHIVE.snapshot_json(plan.SOURCE_LOAD_OPERATION_ID);
 if dbms_lob.compare(wire,plan.SOURCE_JSON)!=0 then raise_application_error(-20886,'INTERWARE_GROUP_SOURCE_CHANGED');end if;
 source_value:=json_object_t.parse(wire);lots:=source_value.get_array('lots');nodes:=source_value.get_object('source_composition').get_array('nodes');links:=source_value.get_object('source_composition').get_array('links');
 select count(*)into n from RRL_IW_GROUP_RECEIPT where PLAN_OPERATION_ID=v_plan;if n!=0 then raise_application_error(-20886,'INTERWARE_GROUP_ALREADY_RECEIVED');end if;
 select TRANSPORT into v_vehicle from RRL_TRANSPORT_TASK where ID=plan.SOURCE_TT_ID;
 if m.get_string('scan_pallet')is null or m.get_string('scan_pallet')!=plan.ROOT_UID then raise_application_error(-20886,'INTERWARE_GROUP_TOP_SCAN_REQUIRED');end if;
 select count(*)into n from RRL_TT_DOCK where DOCK=plan.INBOUND_DOCK and WARE_ID=plan.TARGET_WARE_ID and nvl(DOCK_IS_BLOCKED,0)=0;
 if n!=1 then raise_application_error(-20886,'INTERWARE_GROUP_DOCK_UNAVAILABLE');end if;
 p_domain:=json_object_t();p_domain.put('group_receipt',true);p_domain.put('plan_operation_id',v_plan);p_domain.put('source_load_operation_id',plan.SOURCE_LOAD_OPERATION_ID);
 p_domain.put('uid',plan.ROOT_UID);p_domain.put('warehouse_id',plan.TARGET_WARE_ID);p_domain.put('lots',lots);p_domain.put('vehicle_number',v_vehicle);p_domain.put('inbound_dock',plan.INBOUND_DOCK);
 if v_kind='INTERWARE_UNLOAD'then
  select count(*)into n from RRL_IW_GROUP_UNLOAD where PLAN_OPERATION_ID=v_plan;
  if n!=0 or m.get_string('scan_vehicle')is null or m.get_string('scan_vehicle')!=v_vehicle or m.get_string('scan_dock')is null or m.get_string('scan_dock')!=plan.INBOUND_DOCK then raise_application_error(-20886,'INTERWARE_GROUP_EXACT_UNLOAD_REQUIRED');end if;
  return;
 end if;
 select OPERATION_ID into v_unload from RRL_IW_GROUP_UNLOAD where PLAN_OPERATION_ID=v_plan;
 v_cell:=m.get_string('scan_cell');
 select count(*)into n from RRL_CELLS where CELL=v_cell and WARE_ID=plan.TARGET_WARE_ID and nvl(BLOCKED_FOR_ACCEPT,0)=0 and BLOCKED_FOR_REMAINS=1 and BLOCKED_FOR_POPOLNENIE=1;
 if n!=1 or m.has('partial_receipt')or m.has('aggregation_scans')then raise_application_error(-20886,'INTERWARE_GROUP_WHOLE_UNIT_RECEIPT_REQUIRED');end if;
 requested:=m.get_array('items');if requested is null or requested.get_size!=lots.get_size then raise_application_error(-20886,'INTERWARE_GROUP_ALL_ITEMS_REQUIRED');end if;
 for i in 0..lots.get_size-1 loop
  item:=treat(lots.get(i)as json_object_t);v_uid:=item.get_string('uid');v_article:=item.get_string('article');v_uom:=item.get_string('base_uom');v_qty:=RRL_STOCK_MATH.quantity(item.get_string('quantity'));manifest:=item.get_object('issued_manifest');total_units:=total_units+manifest.get_number('physical_unit_count');
 if total_units>10000 then raise_application_error(-20881,'INTERWARE_GROUP_UNIT_BOUND_10000');end if;
  if first_uid is null then first_uid:=v_uid;end if;
  seen_count:=0;
  for j in 0..requested.get_size-1 loop
   x:=treat(requested.get(j)as json_object_t);
   if x.get_string('uid')=v_uid then
    seen_count:=seen_count+1;
    if x.get_string('article')is null or x.get_string('article')!=v_article or x.get_string('base_uom')is null or x.get_string('base_uom')!=v_uom or x.get_string('quantity')is null or RRL_STOCK_MATH.quantity(x.get_string('quantity'))!=v_qty then raise_application_error(-20886,'INTERWARE_GROUP_EXACT_ITEM_REQUIRED');end if;
    RRL_STOCK_QC_ITEM.resolve_barcode(x.get_string('scan_article'),v_barcode_article,v_barcode_uom);
    if v_barcode_article!=v_article then raise_application_error(-20886,'INTERWARE_GROUP_FOREIGN_ITEM_BARCODE');end if;
   end if;
  end loop;
  if seen_count!=1 then raise_application_error(-20886,'INTERWARE_GROUP_DISTINCT_ALL_ITEMS_REQUIRED');end if;
  RRL_IW_GROUP_THERMAL.assert_cell(plan.TARGET_WARE_ID,v_article,v_cell);
  select max(POLICY_VERSION)into v_version from RRL_STOCK_UOM_CONVERSION where ARTICUL=v_article and INPUT_UOM=v_uom and BASE_UOM=v_uom and NUMERATOR=DENOMINATOR;
  if v_version is null then raise_application_error(-20886,'INTERWARE_GROUP_BASE_UOM_REQUIRED');end if;
  select count(*)into n from RRL_SKU_RECEIPT_PROFILE where ARTICUL=v_article;
  if n>0 then
   declare matched number;begin
    select count(*)into matched from RRL_WMS_RECEIPT_UNIT u join RRL_WMS_RECEIPT_CODE code on code.UID_PALLET=u.UID_PALLET and code.UNIT_ID=u.UNIT_ID
    join RRL_SKU_RECEIPT_PROFILE card on card.ARTICUL=v_article and card.SYSTEM_CODE=code.SYSTEM_CODE,
    json_table(code.PROFILES_JSON,'$[*]'columns(CODE_PROFILE varchar2(80)path '$.profile',CODE_VERSION varchar2(40)path '$.version'))decoded
    where u.CURRENT_UID=v_uid and u.STOCK_STATUS='ISSUED'and card.PROFILE_CODE=decoded.CODE_PROFILE and card.PROFILE_VERSION=decoded.CODE_VERSION;
    if matched!=n*manifest.get_number('physical_unit_count')then raise_application_error(-20886,'INTERWARE_GROUP_CURRENT_CODE_PROFILE_VERSION_REQUIRED');end if;
   end;
  end if;
  item.put('uom_version',v_version);lots.put(i,item,true);
  leg:=json_object_t();leg.put('uid',v_uid);leg.put('article',v_article);leg.put('quantity',item.get_string('quantity'));leg.put('base_uom',v_uom);leg.put('cell',manifest.get_string('source_cell'));legs.append(leg);
 end loop;
 declare scan_domain json_object_t:=json_object_t();begin
  scan_domain.put('legs',legs);
  if RRL_INTERWARE_MARK_SCAN.required_for_plan(scan_domain.to_clob)=1 then RRL_INTERWARE_MARK_SCAN.validate_scan(scan_domain.to_clob,m.to_clob,unit_count);
  elsif m.has('unit_scans')and m.get_array('unit_scans').get_size>0 then raise_application_error(-20886,'INTERWARE_GROUP_UNEXPECTED_UNIT_SCANS');end if;
 end;
 for i in 0..nodes.get_size-1 loop
  x:=treat(nodes.get(i)as json_object_t);
  if x.get_string('kind')='CONTAINER'then
   item:=json_object_t();item.put('uid',x.get_string('uid'));item.put('version',x.get_number('version')+1);item.put('type',x.get_string('type'));item.put('tare',x.get_string('tare_weight_kg'));containers.append(item);
  end if;
 end loop;
 for i in 0..links.get_size-1 loop x:=treat(links.get(i)as json_object_t);x.put('version',x.get_number('version')+1);nested_links.append(x);end loop;
 nested_value.put('stock_uid',first_uid);nested_value.put('place_uid',plan.ROOT_UID);nested_value.put('source_load_operation_id',plan.SOURCE_LOAD_OPERATION_ID);nested_value.put('containers',containers);nested_value.put('links',nested_links);
 p_domain.put('nested_source',nested_value);p_domain.put('lots',lots);p_domain.put('receive_cell',v_cell);p_domain.put('unload_operation_id',v_unload);p_domain.put('legs',legs);
 exception when no_data_found then raise_application_error(-20886,'INTERWARE_GROUP_PLAN_UNLOAD_REQUIRED');
 end;
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob)is
 d json_object_t:=json_object_t.parse(p_request);v json_object_t;f json_array_t:=json_array_t();r json_array_t:=json_array_t();lots json_array_t;item json_object_t;
 units json_array_t;x json_object_t;nested_value json_object_t;links json_array_t;containers json_array_t;new_id number;
 begin
 describe_source(p_request,d.get_string('actor'),v);
 RRL_STOCK_PLAN_HELPER.fence(f,'RELEASE','STOCK');RRL_STOCK_PLAN_HELPER.fence(f,'CONFIG','WAREHOUSE');
 RRL_STOCK_PLAN_HELPER.anchor(r,10,'OP',p_operation);RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','STOCK.OUTBOX:'||rawtohex(sys.dbms_crypto.hash(utl_i18n.string_to_raw(p_operation,'AL32UTF8'),sys.dbms_crypto.hash_sh256)));
 RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_IW_GROUP_PLAN',v.get_string('plan_operation_id'));
 RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_IW_GROUP_UNLOAD',nvl(v.get_string('unload_operation_id'),p_operation));RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_IW_GROUP_RECEIPT',p_operation);
 lots:=v.get_array('lots');
 for i in 0..lots.get_size-1 loop item:=treat(lots.get(i)as json_object_t);
  RRL_STOCK_PLAN_HELPER.stock_closure(f,r,item.get_string('uid'),item.get_string('article'),null,v.get_string('receive_cell'));
  RRL_STOCK_PLAN_HELPER.anchor(r,30,'HU',item.get_string('uid'));
  units:=item.get_object('issued_manifest').get_array('units');
  for j in 0..units.get_size-1 loop x:=treat(units.get(j)as json_object_t);RRL_STOCK_PLAN_HELPER.anchor(r,60,'UNIT',x.get_string('key'));end loop;
 end loop;
 if v.has('nested_source')then
  nested_value:=v.get_object('nested_source');containers:=nested_value.get_array('containers');links:=nested_value.get_array('links');
  for i in 0..containers.get_size-1 loop x:=treat(containers.get(i)as json_object_t);RRL_STOCK_PLAN_HELPER.anchor(r,30,'HU',x.get_string('uid'));RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_PALLETS',x.get_string('uid'));end loop;
  for i in 0..links.get_size-1 loop x:=treat(links.get(i)as json_object_t);select RRL_WMS_HU_LINK_SQ.nextval into new_id from dual;x.put('new_id',new_id);links.put(i,x,true);
   RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_WMS_HU_LINK',RRL_STOCK_PLAN_HELPER.decimal_text(x.get_number('id')));RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_WMS_HU_LINK',RRL_STOCK_PLAN_HELPER.decimal_text(new_id));
  end loop;
  nested_value.put('links',links);v.put('nested_source',nested_value);
 end if;
 p_policies:=f.to_clob;p_resources:=r.to_clob;p_domain:=v.to_clob;
 end;
 procedure assert_fresh(p_request clob,p_actor varchar2,p_domain json_object_t)is
 fresh json_object_t;cached json_object_t:=p_domain.clone();nested_value json_object_t;links json_array_t;x json_object_t;new_id number;n number;fresh_wire clob;cached_wire clob;equal_count number;
 type seen_set is table of boolean index by varchar2(80);seen seen_set;
 begin
 describe_source(p_request,p_actor,fresh);
 if cached.has('nested_source')then
  nested_value:=cached.get_object('nested_source');links:=nested_value.get_array('links');
  for i in 0..links.get_size-1 loop
   x:=treat(links.get(i)as json_object_t);new_id:=x.get_number('new_id');
   if new_id is null or seen.exists(to_char(new_id))then raise_application_error(-20886,'INTERWARE_GROUP_RESERVED_LINK_REQUIRED');end if;seen(to_char(new_id)):=true;
   select count(*)into n from RRL_WMS_HU_LINK where HU_LINK_ID=new_id;if n!=0 then raise_application_error(-20886,'INTERWARE_GROUP_LINK_ALREADY_USED');end if;
   x.remove('new_id');links.put(i,x,true);
  end loop;
  nested_value.put('links',links);cached.put('nested_source',nested_value);
 end if;
 fresh_wire:=fresh.to_clob;cached_wire:=cached.to_clob;select count(*)into equal_count from dual where json_equal(fresh_wire,cached_wire);
 if equal_count!=1 then raise_application_error(-20886,'INTERWARE_GROUP_SOURCE_CHANGED_AFTER_LOCK');end if;
 end;
end;
/
