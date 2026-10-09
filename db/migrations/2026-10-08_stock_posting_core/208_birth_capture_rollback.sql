declare n number;begin select count(*) into n from RRL_STOCK_OPERATION; if n>0 then raise_application_error(-20808,'POSTED_OPERATIONS_PREVENT_CODE_ROLLBACK');end if;end;
/
create or replace package RRL_STOCK_POSTING_API authid definer as
 procedure prepare_command(p_request clob,p_actor varchar2,p_replay out clob,p_hints clob default null);
 procedure execute_prepared(p_result out clob);
 procedure reset_connection;
end;
/

create or replace package RRL_STOCK_INVENTORY_BIRTH authid definer
 accessible by(package RRL_STOCK_POSTING_API) as
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
end;
/

create or replace package RRL_STOCK_UNIT_CORE authid definer
 accessible by(package RRL_STOCK_CASE_SHORT_CMD,package RRL_STOCK_RECEIPT_REVERSE,package RRL_STOCK_WAVE_LAUNCH_CMD,package RRL_STOCK_INVENTORY_CMD,package RRL_STOCK_MES_CANCEL_CMD,package RRL_STOCK_MES_SUPPLY_CMD,package RRL_STOCK_DOC_RESERVE_CMD,package RRL_STOCK_WAVE_CMD,package RRL_STOCK_MES_MOVEMENT_CORE,package RRL_STOCK_INVARIANT_CORE,package RRL_STOCK_RESERVATION_CMD,package RRL_STOCK_TRANSFER_CORE,
 package RRL_STOCK_EFFECT_CORE,package RRL_STOCK_RECEIPT_CORE) as
 function automatic_units(p_uid varchar2,p_cell varchar2,p_qty number) return clob;
 procedure admit_captured(p_uid varchar2,p_cell varchar2);
 procedure assert_composition(p_uid varchar2,p_cell varchar2);
 procedure issue_free_units(p_uid varchar2,p_cell varchar2,p_qty number,p_units clob);
 procedure reserve_units(p_uid varchar2,p_cell varchar2,p_id number,p_qty number,p_units clob);
 procedure release_units(p_id number,p_qty number,p_units clob,p_issue number default 0);
end;
/

create or replace package body RRL_STOCK_POSTING_API as
 g_request clob;g_resolution clob;g_change_before clob;g_actor varchar2(50);g_operation varchar2(100);g_kind varchar2(80);g_tx varchar2(100);g_prepared boolean:=false;
 procedure reset_connection is
 begin
  RRL_STOCK_CTX_API.clear_operation;RRL_STOCK_LOCK_API.clear_plan;
  g_request:=null;g_resolution:=null;g_change_before:=null;g_actor:=null;g_operation:=null;g_kind:=null;g_tx:=null;g_prepared:=false;
 end;
 procedure prepare_command(p_request clob,p_actor varchar2,p_replay out clob,p_hints clob default null) is
  v_doc json_object_t;v_policies clob;v_resources clob;v_exists number;v_release varchar2(20);v_domain clob;v_resolution json_object_t:=json_object_t();
  v_plan json_array_t:=json_array_t();v_entry json_object_t:=json_object_t();v_resources_json json_array_t:=json_array_t();
 begin
  p_replay:=null;
  if g_prepared or sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID') is not null then
   raise_application_error(-20862,'POSTING_ALREADY_ENTERED');
  end if;
  if p_request is null or dbms_lob.getlength(p_request)>4194304 then raise_application_error(-20871,'OPERATION_CONTRACT_INVALID'); end if;
  v_doc:=json_object_t.parse(p_request);v_doc.on_error(1);
  g_operation:=v_doc.get_string('operation_id');g_kind:=v_doc.get_string('command_type');
  if v_doc.get_number('contract_version') is null or v_doc.get_number('contract_version')!=2 or v_doc.get_string('actor') is null
   or v_doc.get_string('actor')!=p_actor or p_actor is null or length(p_actor)>50
   or g_operation is null or length(g_operation)>100 or g_kind is null then
   raise_application_error(-20871,'OPERATION_CONTRACT_INVALID');
  end if;
  -- Immutable committed replay is considered before any mutable article/cell/UOM validation.
  select count(*) into v_exists from RRL_STOCK_OPERATION where OPERATION_ID=g_operation;
  if v_exists!=0 then
   v_entry.put('key_hex',rawtohex(RRL_STOCK_LOCK_API.resource_key('RELEASE','STOCK')));v_entry.put('mode',4);v_plan.append(v_entry);
   v_entry:=json_object_t();v_entry.put('rank',10);
   v_entry.put('key_hex',rawtohex(RRL_STOCK_LOCK_API.resource_key('OP',g_operation)));v_resources_json.append(v_entry);
   v_policies:=v_plan.to_clob;v_resources:=v_resources_json.to_clob;
  else
   begin
   if g_kind in('MANUAL_MOVE','COMPAT_MANUAL_MOVE') then RRL_STOCK_COMMAND_PLAN.compile_move(p_request,g_operation,v_policies,v_resources);
   elsif g_kind='WAVE_LAUNCH' then RRL_STOCK_WAVE_LAUNCH_CMD.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);
   elsif g_kind='OUTGOING_PALLET_CHECK' then RRL_STOCK_PALLET_QC_CMD.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);
   elsif g_kind='CASE_SHORT_APPROVE' then RRL_STOCK_CASE_SHORT_CMD.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);
   elsif g_kind='CASE_CARRIER_MOVE' then RRL_STOCK_CASE_MOVE_CMD.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);
   elsif g_kind='CASE_PICK_CONFIRM' then RRL_STOCK_CASE_PICK_CMD.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);
   elsif g_kind='RECEIPT_REVERSE' then RRL_STOCK_RECEIPT_REVERSE.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);
   elsif g_kind='INVENTORY_REGISTER_LOT' then RRL_STOCK_INVENTORY_BIRTH.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);
   elsif g_kind='INVENTORY_COUNT' then RRL_STOCK_INVENTORY_CMD.compile_count(p_request,g_operation,v_policies,v_resources,v_domain);
   elsif g_kind='MES_RAW_TASK_CANCEL' then RRL_STOCK_MES_CANCEL_CMD.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);
   elsif g_kind in('MES_RELEASE_TO_PRODUCTION','MES_CALCULATE_SUPPLY') then RRL_STOCK_MES_SUPPLY_CMD.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);
   elsif g_kind in('DOCUMENT_RELEASE_RESERVATIONS','WAVE_CANCEL','WAVE_RELEASE','PICK_PLAN_CANCEL') then RRL_STOCK_DOC_RESERVE_CMD.compile_release(p_request,g_operation,v_policies,v_resources,v_domain);
   elsif g_kind='WAVE_RESERVE_SOURCES' then RRL_STOCK_WAVE_CMD.compile_reserve(p_request,g_operation,v_policies,v_resources,v_domain);
   elsif g_kind in('SHIP_DOCUMENT','SHIP_PALLET') then RRL_STOCK_SHIPPING_CORE.compile_shipment(p_request,g_operation,v_policies,v_resources,v_domain);
   elsif g_kind in('INTERNAL_MOVE','MOVE_QUARANTINE') then RRL_STOCK_INTERNAL_CMD.compile_move(p_request,g_operation,v_policies,v_resources,v_domain);
   elsif g_kind='MES_MOVEMENTS' then RRL_STOCK_MES_MOVEMENT_PLAN.compile_movements(p_request,g_operation,v_policies,v_resources,v_domain);
   elsif g_kind='SAP_RECEIPT' then RRL_STOCK_RECEIPT_PLAN.compile_receipt(p_request,g_operation,p_hints,v_policies,v_resources,v_domain);
   elsif g_kind='TASK_COMPLETE' then RRL_STOCK_TASK_PLAN.compile_task(p_request,g_operation,v_policies,v_resources,v_domain);
   elsif g_kind in('RESERVATION_CREATE','RESERVATION_PROMOTE','RESERVATION_RELEASE','RESERVATION_CANCEL','RESERVATION_CONSUME') then RRL_STOCK_RESERVATION_CMD.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);
   else raise_application_error(-20888,'COMMAND_HANDLER_NOT_INSTALLED');end if;
   exception when others then
    -- A concurrent identical command may have committed while this planner read mutable stock.
    -- Rebuild only the existing replay lock plan; never take OP before the full resource plan.
    select count(*) into v_exists from RRL_STOCK_OPERATION where OPERATION_ID=g_operation;
    if v_exists=0 then raise;end if;
    v_domain:=null;v_plan:=json_array_t();v_resources_json:=json_array_t();
    v_entry:=json_object_t();v_entry.put('key_hex',rawtohex(RRL_STOCK_LOCK_API.resource_key('RELEASE','STOCK')));v_entry.put('mode',4);v_plan.append(v_entry);
    v_entry:=json_object_t();v_entry.put('rank',10);v_entry.put('key_hex',rawtohex(RRL_STOCK_LOCK_API.resource_key('OP',g_operation)));v_resources_json.append(v_entry);
    v_policies:=v_plan.to_clob;v_resources:=v_resources_json.to_clob;
   end;
  end if;
  RRL_STOCK_LOCK_API.begin_plan;
  RRL_STOCK_LOCK_API.acquire_policies(v_policies);
  RRL_STOCK_LOCK_API.acquire_resources(v_resources);
  select STATE into v_release from RRL_STOCK_RELEASE where RELEASE_ID=1;
  if v_release!='ACTIVE' then raise_application_error(-20860,'STOCK_RELEASE_NOT_ACTIVE'); end if;
  if v_domain is not null then v_resolution.put('domain',json_object_t.parse(v_domain));end if;
  v_resolution.put('stock_before',json_array_t.parse(RRL_STOCK_INVARIANT_CORE.snapshot_stock(v_resources)));
  v_resolution.put('resources',json_array_t.parse(v_resources));
  v_resolution.put('policies',json_array_t.parse(v_policies));
  RRL_STOCK_OPERATION_CORE.begin_operation(p_request,p_actor,g_operation,g_kind,p_replay,v_resolution.to_clob);
  if p_replay is not null then return; end if;
  g_change_before:=RRL_STOCK_CHANGE_AUDIT.snapshot(v_resources);
  g_request:=p_request;g_resolution:=v_resolution.to_clob;g_actor:=p_actor;g_tx:=dbms_transaction.local_transaction_id(false);g_prepared:=true;
  if g_kind='SAP_RECEIPT' then RRL_STOCK_CTX_API.begin_staging(v_resolution.get_object('domain').get_string('uid'),v_resolution.get_object('domain').get_string('receive_cell'));end if;
 end;
 procedure execute_prepared(p_result out clob) is
  v_outbox number;v_existing number;v_key varchar2(100);v_json json_object_t;v_resolved json_object_t;v_event json_object_t;v_changes clob;v_resources clob;v_after clob;v_composition json_object_t;v_unit_changes json_array_t;v_unit_change json_object_t;v_old_unit json_object_t;v_new_unit json_object_t;v_repacking boolean:=false;
 begin
  if not g_prepared or g_tx is null or dbms_transaction.local_transaction_id(false) is null
   or g_tx!=dbms_transaction.local_transaction_id(false) then raise_application_error(-20850,'WRITE_PLAN_VIOLATION'); end if;
  if g_kind='SAP_RECEIPT' then RRL_STOCK_CTX_API.end_effect;end if;
  if g_kind in('MANUAL_MOVE','COMPAT_MANUAL_MOVE') then RRL_STOCK_MOVE_CORE.manual_whole(g_request,g_actor,p_result);
  elsif g_kind='WAVE_LAUNCH' then RRL_STOCK_WAVE_LAUNCH_CMD.execute_command(g_request,g_actor,p_result);
   elsif g_kind='OUTGOING_PALLET_CHECK' then RRL_STOCK_PALLET_QC_CMD.execute_command(g_request,g_actor,p_result);
   elsif g_kind='CASE_SHORT_APPROVE' then RRL_STOCK_CASE_SHORT_CMD.execute_command(g_request,g_actor,p_result);
  elsif g_kind='CASE_CARRIER_MOVE' then RRL_STOCK_CASE_MOVE_CMD.execute_command(g_request,g_actor,p_result);
   elsif g_kind='CASE_PICK_CONFIRM' then RRL_STOCK_CASE_PICK_CMD.execute_command(g_request,g_actor,p_result);
   elsif g_kind='RECEIPT_REVERSE' then RRL_STOCK_RECEIPT_REVERSE.execute_command(g_request,g_actor,p_result);
   elsif g_kind='INVENTORY_REGISTER_LOT' then RRL_STOCK_INVENTORY_BIRTH.execute_command(g_request,g_actor,p_result);
   elsif g_kind='INVENTORY_COUNT' then RRL_STOCK_INVENTORY_CMD.execute_count(g_request,g_actor,p_result);
   elsif g_kind='MES_RAW_TASK_CANCEL' then RRL_STOCK_MES_CANCEL_CMD.execute_command(g_request,g_actor,p_result);
   elsif g_kind in('MES_RELEASE_TO_PRODUCTION','MES_CALCULATE_SUPPLY') then RRL_STOCK_MES_SUPPLY_CMD.execute_command(g_request,g_actor,p_result);
   elsif g_kind in('DOCUMENT_RELEASE_RESERVATIONS','WAVE_CANCEL','WAVE_RELEASE','PICK_PLAN_CANCEL') then RRL_STOCK_DOC_RESERVE_CMD.execute_release(g_request,g_actor,p_result);
  elsif g_kind='WAVE_RESERVE_SOURCES' then RRL_STOCK_WAVE_CMD.execute_reserve(g_request,g_actor,p_result);
  elsif g_kind in('SHIP_DOCUMENT','SHIP_PALLET') then RRL_STOCK_SHIPPING_CORE.execute_shipment(g_request,g_actor,p_result);
  elsif g_kind in('INTERNAL_MOVE','MOVE_QUARANTINE') then RRL_STOCK_INTERNAL_CMD.execute_move(g_request,g_actor,p_result);
  elsif g_kind='MES_MOVEMENTS' then RRL_STOCK_MES_MOVEMENT_CORE.execute_movements(g_request,g_actor,p_result);
  elsif g_kind='SAP_RECEIPT' then RRL_STOCK_RECEIPT_CORE.execute_receipt(g_request,g_actor,p_result);
  elsif g_kind='TASK_COMPLETE' then RRL_STOCK_TASK_CORE.execute_task(g_request,g_actor,p_result);
  elsif g_kind in('RESERVATION_CREATE','RESERVATION_PROMOTE','RESERVATION_RELEASE','RESERVATION_CANCEL','RESERVATION_CONSUME') then RRL_STOCK_RESERVATION_CMD.execute_command(g_request,g_actor,p_result);
  else raise_application_error(-20888,'COMMAND_HANDLER_NOT_INSTALLED'); end if;
  v_resolved:=json_object_t.parse(g_resolution);
  RRL_STOCK_INVARIANT_CORE.verify_posting(v_resolved.get_array('resources').to_clob,v_resolved.get_array('stock_before').to_clob,g_operation);
  v_key:='STOCK:'||rawtohex(sys.dbms_crypto.hash(utl_i18n.string_to_raw(g_operation,'AL32UTF8'),sys.dbms_crypto.hash_sh256));
  RRL_STOCK_LOCK_API.assert_held(70,RRL_STOCK_LOCK_API.resource_key('UNIQUE','STOCK.OUTBOX:'||substr(v_key,7)));
  select count(*) into v_existing from RRL_EVENT_OUTBOX where IDEMPOTENCY_KEY=v_key;
  if v_existing!=0 then raise_application_error(-20889,'OUTBOX_IDENTITY_CONFLICT'); end if;
  v_resources:=v_resolved.get_array('resources').to_clob;
  v_after:=RRL_STOCK_CHANGE_AUDIT.snapshot(v_resources);v_changes:=RRL_STOCK_CHANGE_AUDIT.differences(g_change_before,v_after);
  v_event:=json_object_t();v_event.put('contract_version',3);v_event.put('operation_id',g_operation);v_event.put('command_type',g_kind);
  v_event.put('source',json_object_t.parse(g_request).get_object('source'));v_event.put('result',json_object_t.parse(p_result));
  v_event.put('stock_before',v_resolved.get_array('stock_before'));
  v_event.put('stock_after',json_array_t.parse(RRL_STOCK_INVARIANT_CORE.snapshot_stock(v_resources)));
  v_composition:=json_object_t.parse(v_changes);v_unit_changes:=v_composition.get_array('units');
  for i in 0..v_unit_changes.get_size-1 loop
   v_unit_change:=treat(v_unit_changes.get(i) as json_object_t);
   if not v_unit_change.get('before').is_null and not v_unit_change.get('after').is_null then
    v_old_unit:=v_unit_change.get_object('before');v_new_unit:=v_unit_change.get_object('after');
    if v_old_unit.get_string('uid')!=v_new_unit.get_string('uid') then v_repacking:=true;end if;
   end if;
  end loop;
  v_event.put('composition_changes',v_composition);
  if v_repacking then
   v_event.put('regulatory_composition_status','PENDING');
   v_event.put('regulatory_action','PHYSICAL_REPACK_PROPOSED');
  end if;
  v_event.put('immutable_request_reference',g_operation);
  v_outbox:=RRL_TRACEABILITY_API.enqueue_event('STOCK_POSTED','STOCK_OPERATION',g_operation,v_key,v_event.to_clob,'WMS',g_operation);
  v_json:=json_object_t.parse(p_result);v_json.put('outbox_id',v_outbox);
  if v_repacking then v_json.put('regulatory_composition_status','PENDING');end if;
  p_result:=v_json.to_clob;
  RRL_STOCK_OPERATION_CORE.finish_operation(g_operation,p_result);
  g_prepared:=false;
 end;
end;
/

create or replace package body RRL_STOCK_INVENTORY_BIRTH as
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob) is
  d json_object_t:=json_object_t.parse(p_request);m json_object_t:=d.get_object('metadata');v json_object_t:=json_object_t();
  f json_array_t:=json_array_t();r json_array_t:=json_array_t();doc number;ware number;uid varchar2(200);cell varchar2(60);article varchar2(160);
  base varchar2(20);other_base varchar2(20);qty number;version number;scale number;expiry date;price number;legacy json_object_t;legacy_doc number;legacy_owner number;v_mod_id number;gross number;net number;boxes number;defect number;
 begin
  doc:=d.get_object('source').get_number('revision_id');uid:=m.get_string('uid');cell:=m.get_string('cell');article:=m.get_string('article');
  if doc is null or uid is null or lengthb(uid)>150 or cell is null or article is null or trim(m.get_string('reason')) is null then raise_application_error(-20871,'INVENTORY_BIRTH_IDENTITY_REQUIRED');end if;
  select WARE_ID into ware from RRL_REVIZION where ID=doc;
  select min(BASE_UOM),max(BASE_UOM) into base,other_base from RRL_STOCK_UOM_CONVERSION where ARTICUL=article and INPUT_UOM=BASE_UOM and NUMERATOR=1 and DENOMINATOR=1;
  if base is null or base!=other_base then raise_application_error(-20868,'INVENTORY_BASE_POLICY_AMBIGUOUS');end if;
  select max(POLICY_VERSION) into version from RRL_STOCK_UOM_CONVERSION where ARTICUL=article and INPUT_UOM=base and BASE_UOM=base and NUMERATOR=1 and DENOMINATOR=1;
  select BASE_SCALE into scale from RRL_STOCK_UOM_CONVERSION where ARTICUL=article and INPUT_UOM=base and POLICY_VERSION=version;
  qty:=RRL_STOCK_MATH.quantity(m.get_string('quantity'));RRL_STOCK_MATH.assert_base(qty,scale);
  expiry:=to_date(m.get_string('expiry_date'),'FXYYYY-MM-DD');price:=m.get_number('price');
  if expiry is null or price<0 then raise_application_error(-20871,'INVENTORY_LOT_DATA_REQUIRED');end if;
  if m.has('legacy_facts') then
   legacy:=m.get_object('legacy_facts');legacy.on_error(1);legacy_doc:=legacy.get_number('receipt_document_id');
   select REV_NAKLAD_ID into legacy_owner from RRL_REVIZION where ID=doc;
   if legacy_doc is null or legacy_owner is null or legacy_doc!=legacy_owner then raise_application_error(-20887,'INVENTORY_SOURCE_DOCUMENT_CONFLICT');end if;
   v_mod_id:=nvl(legacy.get_number('mod_id'),0);gross:=legacy.get_number('gross_weight');net:=legacy.get_number('net_weight');
   boxes:=legacy.get_number('box_count');defect:=legacy.get_number('defect_percent');
   if gross is null or gross<0 or net is null or net<0 or (gross>0 and net>gross) or boxes is null or boxes<0
    or defect is null or defect<0 or defect>100 or v_mod_id<0 then raise_application_error(-20871,'INVENTORY_PALLET_FACTS_INVALID');end if;
   if v_mod_id>0 then select ID into v_mod_id from RRL_ARTICUL_MODS where ID=v_mod_id and ARTICUL=article;end if;
  end if;
  RRL_STOCK_PLAN_HELPER.fence(f,'RELEASE','STOCK');RRL_STOCK_PLAN_HELPER.fence(f,'CONFIG','WAREHOUSE');
  RRL_STOCK_PLAN_HELPER.anchor(r,10,'OP',p_operation);RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_REVIZION',RRL_STOCK_PLAN_HELPER.decimal_text(doc));
  RRL_STOCK_PLAN_HELPER.stock_closure(f,r,uid,article,cell,null);
  RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','PALLET:'||uid);
  RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','STOCK.OUTBOX:'||rawtohex(sys.dbms_crypto.hash(utl_i18n.string_to_raw(p_operation,'AL32UTF8'),sys.dbms_crypto.hash_sh256)));
  if legacy_doc is not null then RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_PRIHOD_NAKLAD',RRL_STOCK_PLAN_HELPER.decimal_text(legacy_doc));end if;
  v.put('document',doc);v.put('warehouse',ware);v.put('uid',uid);v.put('cell',cell);v.put('article',article);
  v.put('quantity',RRL_STOCK_PLAN_HELPER.decimal_text(qty));v.put('base',base);v.put('version',version);v.put('expiry_date',to_char(expiry,'YYYY-MM-DD'));v.put('price',price);
  p_policies:=f.to_clob;p_resources:=r.to_clob;p_domain:=v.to_clob;
 end;
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob) is
  d json_object_t:=json_object_t.parse(p_request);v json_object_t;j json_object_t:=json_object_t();plan clob;
  doc number;ware number;cond number;uid varchar2(200);cell varchar2(60);article varchar2(160);base varchar2(20);version number;
  qty number;expiry date;price number;n number;eventid number;marked number;current_version number;v_count_cell varchar2(60);legacy json_object_t;legacy_doc number;legacy_owner number;v_mod_id number;gross number;net number;boxes number;defect number;
 begin
  if RRL_HAS_WRIGHT(p_actor,'stock_inventory_count')!=1 then raise_application_error(-20882,'INVENTORY_BIRTH_FORBIDDEN');end if;
  uid:=d.get_string('operation_id');select RESOLVED_PLAN_JSON into plan from RRL_STOCK_OPERATION where OPERATION_ID=uid;
  v:=json_object_t.parse(plan).get_object('domain');doc:=v.get_number('document');uid:=v.get_string('uid');cell:=v.get_string('cell');
  article:=v.get_string('article');base:=v.get_string('base');version:=v.get_number('version');qty:=RRL_STOCK_MATH.quantity(v.get_string('quantity'));
  expiry:=to_date(v.get_string('expiry_date'),'FXYYYY-MM-DD');price:=v.get_number('price');
  select WARE_ID,CONDITION into ware,cond from RRL_REVIZION where ID=doc for update;
  if ware!=v.get_number('warehouse') or cond is null or cond not in(0,1) then raise_application_error(-20886,'INVENTORY_DOCUMENT_NOT_OPEN');end if;
  if d.get_object('metadata').has('legacy_facts') then
   legacy:=d.get_object('metadata').get_object('legacy_facts');legacy_doc:=legacy.get_number('receipt_document_id');
   select REV_NAKLAD_ID into legacy_owner from RRL_REVIZION where ID=doc;
   if legacy_owner is null or legacy_owner!=legacy_doc then raise_application_error(-20890,'CLOSURE_CHANGED: inventory source document');end if;
   v_mod_id:=nvl(legacy.get_number('mod_id'),0);gross:=legacy.get_number('gross_weight');net:=legacy.get_number('net_weight');
   boxes:=legacy.get_number('box_count');defect:=legacy.get_number('defect_percent');
   if v_mod_id>0 then select ID into v_mod_id from RRL_ARTICUL_MODS where ID=v_mod_id and ARTICUL=article;end if;
  end if;
  RRL_STOCK_LOCATION_CORE.assert_quarantine(cell,ware);
  select max(POLICY_VERSION) into current_version from RRL_STOCK_UOM_CONVERSION where ARTICUL=article and INPUT_UOM=base and BASE_UOM=base and NUMERATOR=1 and DENOMINATOR=1;
  if current_version!=version then raise_application_error(-20890,'CLOSURE_CHANGED: inventory birth policy');end if;
  select greatest(nvl((select MARKING_REQUIRED from RRL_SKU_RECEIPT_POLICY where ARTICUL=article),0),
    nvl((select CRPT_REQUIRED from RRL_FINISHED_GOODS_SKU where ARTICUL=article),0),
    case when exists(select 1 from RRL_SKU_RECEIPT_PROFILE where ARTICUL=article) then 1 else 0 end) into marked from dual;
  if marked!=0 then raise_application_error(-20884,'MARKED_INVENTORY_CAPTURE_REQUIRED');end if;
  select count(*) into n from RRL_PALLETS where UID_PALLET=uid;
  if n>0 then raise_application_error(-20887,'INVENTORY_PALLET_ALREADY_EXISTS: use measured count for existing identity');end if;
  -- The planned CELL fence serializes birth against existing-lot movements.
  -- A changed input file must not add measured inventory on top of live stock.
  v_count_cell:=cell;
  select count(*) into n from RRL_REMAINS s join RRL_PALLETS p on p.UID_PALLET=s.UID_POLETA
   where s.CELL=v_count_cell and p.ARTICUL=article and s.REMAIN>0;
  if n>0 then
   if legacy is null then raise_application_error(-20887,'INVENTORY_CELL_HAS_STOCK: count existing lots');end if;
   -- Different explicitly identified pallets may be measured within one revision.
   -- A new revision/file must not load inventory over unrelated existing stock.
   select count(*) into n from RRL_REMAINS s join RRL_PALLETS p on p.UID_PALLET=s.UID_POLETA
    where s.CELL=v_count_cell and p.ARTICUL=article and s.REMAIN>0 and not exists(
     select 1 from RRL_STOCK_OPERATION o where o.OPERATION_ID=p.CREATED_BY_STOCK_OP and o.STATE='APPLIED'
      and o.COMMAND_TYPE='INVENTORY_REGISTER_LOT' and json_value(o.CANONICAL_REQUEST,'$.source.revision_id' returning number)=doc);
   if n>0 then raise_application_error(-20887,'INVENTORY_CELL_HAS_OTHER_STOCK: count existing lots');end if;
  end if;
  declare
 v_json_sql_1_1 varchar2(32767):=d.get_string('operation_id');
begin
insert into RRL_PALLETS(UID_PALLET,ARTICUL,CREATION_DATE,EXPIRY_DATE,UNIT_COUNT,PRICE,PRIHOD_NAKLAD_ID,STOCK_ORIGIN_UID,CREATED_BY_STOCK_OP)
   values(uid,article,systimestamp,expiry,qty,price,-doc,uid,v_json_sql_1_1);
end;
  if legacy is not null then
   update RRL_PALLETS set MOD_ID=v_mod_id,WEIGHT_BRUTTO=gross,WEIGHT_TN=net,COUNT_KOR=boxes,DEFECT_PERC=defect where UID_PALLET=uid;
  end if;
  RRL_STOCK_BALANCE_CORE.apply_delta(uid,cell,qty,0,base,version,0);
  RRL_STOCK_BALANCE_CORE.write_leg(uid,null,cell,qty,base,version,1,1,1,p_actor,eventid);
  j.put('operation_id',d.get_string('operation_id'));j.put('revision_id',doc);j.put('uid',uid);j.put('cell',cell);j.put('article',article);
  j.put('quantity',RRL_STOCK_PLAN_HELPER.decimal_text(qty));j.put('unit',base);j.put('event_id',eventid);j.put('lot_source','INVENTORY');
  p_result:=j.to_clob;
 end;
end;
/

create or replace package body RRL_STOCK_UNIT_CORE as
 procedure require_context is
 begin
  if sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID') is null or
   sys_context('RRL_STOCK_WRITE_CTX','TX_ID') is null or
   sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false) then
   raise_application_error(-20863,'UNIT_WRITE_FORBIDDEN');end if;
 end;
 procedure own_unit(p_key varchar2) is
 begin
  if p_key is null then raise_application_error(-20884,'UNIT_BINDING_REQUIRED');end if;
  begin RRL_STOCK_LOCK_API.assert_held(60,RRL_STOCK_LOCK_API.resource_key('UNIT',p_key));
  exception when others then if sqlcode=-20850 then raise_application_error(-20890,'CLOSURE_CHANGED: units');else raise;end if;end;
 end;
 procedure assert_composition(p_uid varchar2,p_cell varchar2) is
  v_p number;v_base varchar2(20);v_total number;v_count number;v_bad number;v_article varchar2(160);v_marked number;v_scale number;
 begin
  select REMAIN,BASE_UOM into v_p,v_base from RRL_REMAINS where UID_POLETA=p_uid and CELL=p_cell;
  select ARTICUL into v_article from RRL_PALLETS where UID_PALLET=p_uid;
  select greatest(nvl((select MARKING_REQUIRED from RRL_SKU_RECEIPT_POLICY where ARTICUL=v_article),0),
   nvl((select CRPT_REQUIRED from RRL_FINISHED_GOODS_SKU where ARTICUL=v_article),0),
   case when exists(select 1 from RRL_SKU_RECEIPT_PROFILE where ARTICUL=v_article) then 1 else 0 end) into v_marked from dual;
  select count(*),nvl(sum(BASE_QTY),0),nvl(sum(case when PHYSICAL_UNIT_KEY is null or STOCK_STATUS is null or BASE_QTY<=0 or BASE_UOM is null or BASE_UOM!=v_base then 1 else 0 end),0)
   into v_count,v_total,v_bad from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=p_uid and CURRENT_CELL=p_cell and (STOCK_STATUS is null or STOCK_STATUS!='ISSUED');
  select max(BASE_SCALE) into v_scale from RRL_STOCK_UOM_CONVERSION where ARTICUL=v_article and BASE_UOM=v_base;
  if v_scale is null then raise_application_error(-20868,'COMPOSITION_BASE_POLICY_REQUIRED');end if;
  select count(*) into v_bad from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=p_uid and CURRENT_CELL=p_cell and (STOCK_STATUS is null or STOCK_STATUS!='ISSUED')
   and (STOCK_STATUS is null or BASE_QTY is null or BASE_QTY<=0 or abs(BASE_QTY)>=power(10,18) or trunc(BASE_QTY,v_scale)!=BASE_QTY or BASE_UOM is null or BASE_UOM!=v_base or PHYSICAL_UNIT_KEY is null);
  if v_bad>0 or (v_count>0 and v_total!=v_p) or (v_marked=1 and v_p>0 and v_count=0) then
   raise_application_error(-20884,'PHYSICAL_COMPOSITION_CONFLICT');end if;
 end;
 function automatic_units(p_uid varchar2,p_cell varchar2,p_qty number) return clob is
  a json_array_t:=json_array_t();v_n number;v_qty number:=0;
 begin
  require_context;assert_composition(p_uid,p_cell);
  select count(*) into v_n from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=p_uid and CURRENT_CELL=p_cell and STOCK_STATUS!='ISSUED';
  if v_n=0 then return null;end if;
  for u in(select PHYSICAL_UNIT_KEY,BASE_QTY from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=p_uid and CURRENT_CELL=p_cell and STOCK_STATUS='AVAILABLE' and HARD_RESERVATION_ID is null order by PHYSICAL_UNIT_KEY) loop
   exit when v_qty=p_qty;
   own_unit(u.PHYSICAL_UNIT_KEY);
   if v_qty+u.BASE_QTY>p_qty then raise_application_error(-20884,'PHYSICAL_UNIT_ALLOCATION_REQUIRES_SELECTION');end if;
   a.append(u.PHYSICAL_UNIT_KEY);v_qty:=v_qty+u.BASE_QTY;
   if a.get_size>10000 then raise_application_error(-20884,'UNIT_SELECTION_BOUND');end if;
  end loop;
  if v_qty!=p_qty then raise_application_error(-20884,'ADMITTED_FREE_UNITS_INSUFFICIENT');end if;
  return a.to_clob;
 end;
 procedure admit_captured(p_uid varchar2,p_cell varchar2) is
 begin
  require_context;assert_composition(p_uid,p_cell);
  for u in(select PHYSICAL_UNIT_KEY from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=p_uid and CURRENT_CELL=p_cell and STOCK_STATUS='CAPTURED') loop own_unit(u.PHYSICAL_UNIT_KEY);end loop;
  RRL_STOCK_CTX_API.begin_effect('UNIT',p_uid,p_cell);
  update RRL_WMS_RECEIPT_UNIT set STOCK_STATUS='AVAILABLE',UNIT_VERSION=UNIT_VERSION+1
   where CURRENT_UID=p_uid and CURRENT_CELL=p_cell and STOCK_STATUS='CAPTURED';
  RRL_STOCK_CTX_API.end_effect;
 end;
 procedure issue_free_units(p_uid varchar2,p_cell varchar2,p_qty number,p_units clob) is v_total number;v_count number;v_qty number;v_expected number;v_distinct number;
 begin
  require_context;assert_composition(p_uid,p_cell);
  select count(*) into v_total from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=p_uid and CURRENT_CELL=p_cell and STOCK_STATUS!='ISSUED';
  if v_total=0 then return;end if;
  select count(*),nvl(sum(BASE_QTY),0) into v_count,v_qty from RRL_WMS_RECEIPT_UNIT u
   where CURRENT_UID=p_uid and CURRENT_CELL=p_cell and STOCK_STATUS!='ISSUED'
    and (p_units is null or exists(select 1 from json_table(p_units,'$[*]' columns(K varchar2(64) path '$'))j where j.K=u.PHYSICAL_UNIT_KEY));
  if v_qty!=p_qty then raise_application_error(-20884,'ISSUE_UNIT_QUANTITY_CONFLICT');end if;
  if p_units is not null then
   select count(*),count(distinct K) into v_expected,v_distinct from json_table(p_units,'$[*]' columns(K varchar2(64) path '$'));
   if v_count!=v_expected or v_expected!=v_distinct then raise_application_error(-20884,'UNIT_SELECTION_CONFLICT');end if;
  end if;
  for r in(select PHYSICAL_UNIT_KEY,STOCK_STATUS,HARD_RESERVATION_ID from RRL_WMS_RECEIPT_UNIT u
   where CURRENT_UID=p_uid and CURRENT_CELL=p_cell and STOCK_STATUS!='ISSUED'
    and (p_units is null or exists(select 1 from json_table(p_units,'$[*]' columns(K varchar2(64) path '$'))j where j.K=u.PHYSICAL_UNIT_KEY))) loop
   own_unit(r.PHYSICAL_UNIT_KEY);
   if r.HARD_RESERVATION_ID is not null then raise_application_error(-20869,'UNIT_RESERVED_BY_OTHER_OWNER');end if;
   if r.STOCK_STATUS!='AVAILABLE' then raise_application_error(-20884,'UNIT_NOT_ADMITTED');end if;
  end loop;
  RRL_STOCK_CTX_API.begin_effect('UNIT',p_uid,p_cell);
  update RRL_WMS_RECEIPT_UNIT u set STOCK_STATUS='ISSUED',UNIT_VERSION=UNIT_VERSION+1
   where CURRENT_UID=p_uid and CURRENT_CELL=p_cell and STOCK_STATUS!='ISSUED'
    and (p_units is null or exists(select 1 from json_table(p_units,'$[*]' columns(K varchar2(64) path '$'))j where j.K=u.PHYSICAL_UNIT_KEY));
  RRL_STOCK_CTX_API.end_effect;
 end;
 procedure reserve_units(p_uid varchar2,p_cell varchar2,p_id number,p_qty number,p_units clob) is
  v_count number;v_total number;v_chosen number;v_qty number;v_expected number;
 begin
  require_context;assert_composition(p_uid,p_cell);
  RRL_STOCK_LOCK_API.assert_held(50,RRL_STOCK_LOCK_API.resource_key('STOCK',p_uid));
  select count(*),nvl(sum(BASE_QTY),0) into v_count,v_total from RRL_WMS_RECEIPT_UNIT
   where CURRENT_UID=p_uid and CURRENT_CELL=p_cell and STOCK_STATUS!='ISSUED';
  if v_count=0 then return;end if;
  select count(*),nvl(sum(BASE_QTY),0) into v_chosen,v_qty from RRL_WMS_RECEIPT_UNIT u
   where CURRENT_UID=p_uid and CURRENT_CELL=p_cell and STOCK_STATUS!='ISSUED'
    and (p_units is null or exists(select 1 from json_table(p_units,'$[*]' columns(K varchar2(64) path '$'))j where j.K=u.PHYSICAL_UNIT_KEY));
  if v_qty!=p_qty then raise_application_error(-20884,'RESERVATION_UNIT_QUANTITY_CONFLICT');end if;
  if p_units is not null then
   select count(*),count(distinct K) into v_expected,v_count from json_table(p_units,'$[*]' columns(K varchar2(64) path '$'));
   if v_expected!=v_count or v_expected!=v_chosen then raise_application_error(-20884,'UNIT_SELECTION_CONFLICT');end if;
  end if;
  for r in(select PHYSICAL_UNIT_KEY,HARD_RESERVATION_ID,STOCK_STATUS from RRL_WMS_RECEIPT_UNIT u
   where CURRENT_UID=p_uid and CURRENT_CELL=p_cell and STOCK_STATUS!='ISSUED'
    and (p_units is null or exists(select 1 from json_table(p_units,'$[*]' columns(K varchar2(64) path '$'))j where j.K=u.PHYSICAL_UNIT_KEY))) loop
   own_unit(r.PHYSICAL_UNIT_KEY);
   if r.HARD_RESERVATION_ID is not null then raise_application_error(-20869,'UNIT_ALREADY_RESERVED');end if;
   if r.STOCK_STATUS!='AVAILABLE' then raise_application_error(-20884,'UNIT_NOT_ADMITTED');end if;
  end loop;
  RRL_STOCK_CTX_API.begin_effect('UNIT',p_uid,p_cell);
  update RRL_WMS_RECEIPT_UNIT u set HARD_RESERVATION_ID=p_id,UNIT_VERSION=UNIT_VERSION+1
   where CURRENT_UID=p_uid and CURRENT_CELL=p_cell and STOCK_STATUS!='ISSUED'
    and (p_units is null or exists(select 1 from json_table(p_units,'$[*]' columns(K varchar2(64) path '$'))j where j.K=u.PHYSICAL_UNIT_KEY));
  RRL_STOCK_CTX_API.end_effect;
 end;
 procedure release_units(p_id number,p_qty number,p_units clob,p_issue number default 0) is
  v_qty number;v_count number;v_expected number;v_distinct number;v_uid varchar2(200);v_cell varchar2(60);
 begin
  require_context;
  select UID_PALLET,CELL into v_uid,v_cell from RRL_STOCK_RESERVATION where RESERVATION_ID=p_id;
  assert_composition(v_uid,v_cell);
  RRL_STOCK_LOCK_API.assert_held(50,RRL_STOCK_LOCK_API.resource_key('STOCK',v_uid));
  select count(*),nvl(sum(BASE_QTY),0) into v_count,v_qty from RRL_WMS_RECEIPT_UNIT u
   where HARD_RESERVATION_ID=p_id and STOCK_STATUS!='ISSUED'
    and (p_units is null or exists(select 1 from json_table(p_units,'$[*]' columns(K varchar2(64) path '$'))j where j.K=u.PHYSICAL_UNIT_KEY));
  if v_count=0 then
   select count(*) into v_expected from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=v_uid and CURRENT_CELL=v_cell and STOCK_STATUS!='ISSUED';
   if v_expected>0 then raise_application_error(-20869,'RESERVATION_UNIT_BINDING_REQUIRED');end if;
   return;end if;
  if v_qty!=p_qty then raise_application_error(-20884,'RESERVATION_UNIT_QUANTITY_CONFLICT');end if;
  if p_units is not null then
   select count(*),count(distinct K) into v_expected,v_distinct from json_table(p_units,'$[*]' columns(K varchar2(64) path '$'));
   if v_count!=v_expected or v_expected!=v_distinct then raise_application_error(-20884,'UNIT_SELECTION_CONFLICT');end if;
  end if;
  for r in(select PHYSICAL_UNIT_KEY,STOCK_STATUS from RRL_WMS_RECEIPT_UNIT u
   where HARD_RESERVATION_ID=p_id and STOCK_STATUS!='ISSUED'
    and (p_units is null or exists(select 1 from json_table(p_units,'$[*]' columns(K varchar2(64) path '$'))j where j.K=u.PHYSICAL_UNIT_KEY))) loop
   own_unit(r.PHYSICAL_UNIT_KEY);
   if p_issue=1 and r.STOCK_STATUS!='AVAILABLE' then raise_application_error(-20884,'UNIT_NOT_ADMITTED');end if;
  end loop;
  RRL_STOCK_CTX_API.begin_effect('UNIT',v_uid,v_cell);
  update RRL_WMS_RECEIPT_UNIT u set HARD_RESERVATION_ID=null,UNIT_VERSION=UNIT_VERSION+1,
   STOCK_STATUS=case when p_issue=1 then 'ISSUED' else STOCK_STATUS end
   where HARD_RESERVATION_ID=p_id and STOCK_STATUS!='ISSUED'
    and (p_units is null or exists(select 1 from json_table(p_units,'$[*]' columns(K varchar2(64) path '$'))j where j.K=u.PHYSICAL_UNIT_KEY));
  RRL_STOCK_CTX_API.end_effect;
 end;
end;
/
