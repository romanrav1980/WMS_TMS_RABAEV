create or replace package RRL_STOCK_POSTING_API authid definer as
 procedure prepare_command(p_request clob,p_actor varchar2,p_replay out clob,p_hints clob default null);
 procedure execute_prepared(p_result out clob);
 procedure stage_birth(p_uid varchar2);
 procedure finish_birth_capture;
 procedure reset_connection;
end;
/

create or replace package body RRL_STOCK_POSTING_API as
 g_request clob;g_resolution clob;g_change_before clob;g_actor varchar2(50);g_operation varchar2(100);g_kind varchar2(80);g_tx varchar2(100);g_prepared boolean:=false;
 procedure assert_actor_active(p_actor varchar2) is v_n number;
 begin
  select count(*)into v_n from RUSERS where ID=p_actor and nvl(DELETED,0)=0;
  if v_n!=1 then raise_application_error(-20882,'STOCK_CURRENT_ACTOR_REQUIRED');end if;
 end;
 procedure assert_case_slot_actor(p_request clob,p_actor varchar2)is d json_object_t:=json_object_t.parse(p_request);m json_object_t;v_case number;begin
  if d.get_string('command_type')not in('HU_RELOCATE_SLOT','HU_ATTACH','HU_DETACH','HU_UNPACK','HU_REPACK_SLOT')then return;end if;
  m:=d.get_object('metadata');
  if d.get_string('command_type')='HU_RELOCATE_SLOT'then v_case:=m.get_number('case_task_id');
  else v_case:=m.get_number('child_case_task_id');end if;
  if substr(d.get_object('source').get_string('uid'),1,5)='CASE:'and v_case is null then raise_application_error(-20886,'CASE_SLOT_TASK_ID_REQUIRED');end if;
  if v_case is null then return;end if;
  if RRL_HAS_WRIGHT(p_actor,'warehouse_task_execute')!=1 then raise_application_error(-20882,'CASE_SLOT_EXECUTION_FORBIDDEN');end if;
  RRL_CASE_TASK_ACCESS.assert_scope(v_case,p_actor,'case_move');
 end;
 procedure assert_repack_actor(p_request clob,p_actor varchar2)is
  d json_object_t:=json_object_t.parse(p_request);uid varchar2(200);ware number;user_ware number;grp varchar2(100);
 begin
  if d.get_string('command_type')!='HU_REPACK_SLOT'then return;end if;uid:=d.get_object('source').get_string('uid');
  select c.WARE_ID into ware from RRL_PALLETS p join RRL_CELLS c on c.CELL=p.HU_CURRENT_CELL where p.UID_PALLET=uid;
  select WARE_ID,USER_GROUP into user_ware,grp from RUSERS where ID=p_actor and nvl(DELETED,0)=0;
  if ware is null or ware<1 then raise_application_error(-20886,'HU_REPACK_WARE_REQUIRED');end if;
  if RRL_HAS_WRIGHT(p_actor,'warehouse_task_execute')!=1 or(nvl(upper(trim(grp)),'-')!='GLOBAL_ADMIN'and(user_ware is null or user_ware!=ware))then raise_application_error(-20882,'HU_REPACK_CURRENT_WARE_EXECUTOR_REQUIRED');end if;
 exception when no_data_found then raise_application_error(-20886,'HU_REPACK_CURRENT_SOURCE_REQUIRED');end;
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
  assert_actor_active(p_actor);
  if g_kind in('INTERWARE_UNLOAD','INTERWARE_RECEIVE')then declare doc json_object_t:=json_object_t.parse(p_request);begin RRL_STOCK_INTERWARE_REC.assert_scope(doc.get_object('source').get_string('plan_operation_id'),p_actor);end;end if;
  if g_kind='LOAD_SHIPMENT'then declare doc json_object_t:=json_object_t.parse(p_request);begin RRL_STOCK_LOADING_READ.assert_scope(doc.get_object('source').get_string('pallet_identifier'),p_actor);end;end if;
  if g_kind='TARE_OFFER_CANCEL'then RRL_STOCK_TARE_CANCEL_CMD.assert_scope(p_request,p_actor);end if;
  if g_kind='TARE_BOOK'then RRL_TARE_LOAD_RECOVERY_API.assert_scope(p_request,p_actor);end if;assert_case_slot_actor(p_request,p_actor);assert_repack_actor(p_request,p_actor);
  if g_kind='UNLOAD_SHIPMENT'then declare doc json_object_t:=json_object_t.parse(p_request);begin RRL_STOCK_UNLOAD_CMD.assert_scope(doc.get_object('source').get_string('load_operation_id'),p_actor);end;end if;
  if g_kind in('TASK_COMPLETE','HU_TASK_COMPLETE') then RRL_WAREHOUSE_TASK_ACCESS.assert_completion(p_request,p_actor);end if;
  if g_kind='OUTGOING_PALLET_CHECK'then RRL_OUTGOING_QC_ACCESS.assert_identifier(json_object_t.parse(p_request).get_object('source').get_string('pallet_identifier'),p_actor);end if;
  if g_kind in('CASE_PICK_CONFIRM','CASE_CARRIER_MOVE','CASE_CARRIER_RETURN','CASE_SHORT_APPROVE')then RRL_CASE_TASK_ACCESS.assert_command(p_request,p_actor);end if;
  if g_kind='WAVE_EXECUTION_FINISH'then RRL_WAVE_EXEC_ACCESS.assert_command(p_request,p_actor);end if;
  -- Immutable committed replay is considered before any mutable article/cell/UOM validation.
  select count(*) into v_exists from RRL_STOCK_OPERATION where OPERATION_ID=g_operation;
  if v_exists!=0 then
   v_entry.put('key_hex',rawtohex(RRL_STOCK_LOCK_API.resource_key('RELEASE','STOCK')));v_entry.put('mode',4);v_plan.append(v_entry);
   v_entry:=json_object_t();v_entry.put('rank',10);
   v_entry.put('key_hex',rawtohex(RRL_STOCK_LOCK_API.resource_key('OP',g_operation)));v_resources_json.append(v_entry);
   v_policies:=v_plan.to_clob;v_resources:=v_resources_json.to_clob;
  else
   begin
   if g_kind in('INTERWARE_UNLOAD','INTERWARE_RECEIVE') then RRL_STOCK_INTERWARE_REC.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);
   elsif g_kind in('MANUAL_MOVE','COMPAT_MANUAL_MOVE') then RRL_STOCK_COMMAND_PLAN.compile_move(p_request,g_operation,v_policies,v_resources);
   elsif g_kind ='INTERWARE_PUTAWAY_PLAN' then RRL_STOCK_INTERWARE_PUT.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);
   elsif g_kind ='INTERWARE_CUSTODY_RELEASE' then RRL_STOCK_INTERWARE_CUSTODY.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);
   elsif g_kind='RESERVATION_ALLOCATE_POOL' then RRL_STOCK_POOL_CMD.compile_command(p_request,g_operation,p_hints,v_policies,v_resources,v_domain);
   elsif g_kind='PICK_PALLET_BIND_SHIPMENT' then RRL_STOCK_FULLPAL_BIND_CMD.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);
  elsif g_kind in('HU_PLAN_MOVE','HU_TASK_COMPLETE') then RRL_STOCK_HU_TASK.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);
  elsif g_kind='HU_RELOCATE_SLOT' then RRL_STOCK_HU_SLOT_MOVE_CMD.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);
  elsif g_kind='HU_REPACK_SLOT'then RRL_STOCK_HU_REPACK_CMD.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);
  elsif g_kind='HU_UNPACK' then RRL_STOCK_HU_UNPACK_CMD.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);
  elsif g_kind in('TARE_LOSS_REPORT','TARE_LOSS_DECIDE') then RRL_STOCK_TARE_LOSS.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);
  elsif g_kind in('TARE_BOOK','TARE_BOOK_CANCEL') then RRL_STOCK_TARE_BOOK_CMD.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);
  elsif g_kind in('TARE_DAMAGE','TARE_WRITE_OFF') then RRL_STOCK_TARE_RESOLVE.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);
  elsif g_kind='TARE_OFFER_CANCEL'then RRL_STOCK_TARE_CANCEL_CMD.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);
  elsif g_kind in('TARE_COUNT','TARE_OFFER','TARE_ACCEPT') then RRL_STOCK_TARE_CMD.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);
  elsif g_kind='STORE_RETURN_PUTAWAY_PLAN' then RRL_STOCK_STORE_RETURN_PUT.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);
  elsif g_kind='STORE_RETURN_RECEIVE' then RRL_STOCK_STORE_RETURN_REC_CMD.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);
  elsif g_kind in('STORE_RETURN_HANDOVER','STORE_RETURN_PICKUP') then RRL_STOCK_STORE_RETURN_CUST_CMD.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);
  elsif g_kind='STORE_RETURN_TRANSPORT_PLAN' then RRL_STOCK_STORE_RETURN_TR_CMD.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);
  elsif g_kind='STORE_RETURN_SAP_BIND' then RRL_STOCK_STORE_RETURN_SAP_CMD.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);
  elsif g_kind='STORE_RETURN_APPROVE' then RRL_STOCK_STORE_RETURN_CMD.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);
  elsif g_kind='STORE_CASE_WORK' then RRL_STOCK_STORE_CASE_CMD.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);
  elsif g_kind='STORE_RECEIPT' then RRL_STOCK_STORE_RECEIPT_CMD.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);
  elsif g_kind='RECONCILE_HU_LOAD' then RRL_STOCK_LOAD_RECONCILE_CMD.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);
  elsif g_kind='UNLOAD_SHIPMENT' then RRL_STOCK_UNLOAD_CMD.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);
  
  elsif g_kind='LOAD_SHIPMENT' then RRL_STOCK_SINGLE_LOAD_CMD.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);
  elsif g_kind='TRIP_DEPART' then RRL_STOCK_TRIP_DEPART_CMD.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);
  elsif g_kind='HU_SHIP' then RRL_STOCK_HU_SHIP_CMD.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);
  elsif g_kind in('HU_CREATE','HU_ATTACH','HU_DETACH','HU_MOVE') then RRL_STOCK_HU_CMD.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);
  elsif g_kind='WAVE_EXECUTION_FINISH' then RRL_STOCK_WAVE_FINISH_CMD.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);
  elsif g_kind='WAVE_PICK_RELEASE' then RRL_STOCK_WAVE_PICK_CMD.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);
   elsif g_kind='WAVE_LAUNCH' then RRL_STOCK_WAVE_LAUNCH_CMD.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);
   elsif g_kind='OUTGOING_PALLET_CHECK' then RRL_STOCK_PALLET_QC_CMD.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);
   elsif g_kind='CASE_SHORT_APPROVE' then RRL_STOCK_CASE_SHORT_CMD.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);
   elsif g_kind='CASE_CARRIER_RETURN' then RRL_STOCK_CASE_RETURN_CMD.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);
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
  if v_domain is not null and p_hints is not null and g_kind in('INVENTORY_REGISTER_LOT','MES_MOVEMENTS') then
   declare h json_object_t:=json_object_t.parse(p_hints);a json_array_t;b json_object_t;u json_object_t;
    rr json_array_t:=json_array_t.parse(v_resources);dom json_object_t:=json_object_t.parse(v_domain);
    uid varchar2(150);qty varchar2(30);base varchar2(20);cell varchar2(60);expected_article varchar2(160);found boolean;total number;
   begin
    a:=h.get_array('births');if a.get_size>200 then raise_application_error(-20881,'BIRTH_CAPTURE_BOUND');end if;
    for i in 0..a.get_size-1 loop
     b:=treat(a.get(i) as json_object_t);uid:=b.get_string('uid');found:=false;
     if g_kind='INVENTORY_REGISTER_LOT' and dom.get_string('uid')=uid then
      found:=true;qty:=dom.get_string('quantity');base:=dom.get_string('base');cell:=dom.get_string('cell');expected_article:=dom.get_string('article');
     elsif g_kind='MES_MOVEMENTS' then
      for z in 0..dom.get_array('movements').get_size-1 loop
       u:=treat(dom.get_array('movements').get(z) as json_object_t);
       if u.get_string('physical_uid')=uid and u.get_number('movement_id')=b.get_number('movement_id') then
        declare m RRL_MES_MOVEMENT%rowtype;mid number:=u.get_number('movement_id');begin
         select * into m from RRL_MES_MOVEMENT where MOVEMENT_ID=mid;
         if m.MOVEMENT_TYPE!='FG_PALLET_RELEASE' then raise_application_error(-20884,'NOT_A_BIRTH_MOVEMENT');end if;
         found:=true;qty:=u.get_string('base_quantity');base:=u.get_string('base_uom');cell:=m.TARGET_LOCATION;expected_article:=u.get_string('article');
        end;
       end if;
      end loop;
     end if;
     if not found or RRL_STOCK_MATH.quantity(b.get_string('quantity'))!=RRL_STOCK_MATH.quantity(qty) or b.get_string('article')!=expected_article or b.get_string('base')!=base or b.get_string('cell')!=cell
      then raise_application_error(-20890,'CLOSURE_CHANGED: birth capture');end if;
     total:=0;
     if b.get_array('unit_bindings').get_size<1 or b.get_array('unit_bindings').get_size>10000 then raise_application_error(-20881,'BIRTH_UNIT_BOUND');end if;
     for z in 0..b.get_array('unit_bindings').get_size-1 loop
      u:=treat(b.get_array('unit_bindings').get(z) as json_object_t);
      total:=total+RRL_STOCK_MATH.quantity(u.get_string('quantity'));
      RRL_STOCK_PLAN_HELPER.anchor(rr,60,'UNIT',u.get_string('key'));
     end loop;
     if total!=RRL_STOCK_MATH.quantity(qty) then raise_application_error(-20884,'BIRTH_UNIT_QUANTITY_CONFLICT');end if;
     for z in 0..b.get_array('aliases').get_size-1 loop
      u:=treat(b.get_array('aliases').get(z) as json_object_t);
      RRL_STOCK_PLAN_HELPER.anchor(rr,70,'UNIQUE','MARK:'||u.get_string('system')||':'||u.get_string('hash'));
     end loop;
    end loop;
    v_resources:=rr.to_clob;v_resolution.put('births',a);
   end;
  end if;
  -- A composition update is a predeclared part of the same command, never a late lock.
  declare rr json_array_t:=json_array_t.parse(v_resources);uid_value varchar2(200);raw_resources clob:=v_resources;begin
   for k in(select distinct KEY_HEX from json_table(raw_resources,'$[*]' columns(RANK_NO number path '$.rank',KEY_HEX varchar2(2000) path '$.key_hex')) where RANK_NO=50) loop
    uid_value:=RRL_STOCK_INVARIANT_CORE.stock_uid(hextoraw(k.KEY_HEX));
    RRL_STOCK_PLAN_HELPER.row_key(rr,'RRL_PALLETS',uid_value);
    for ct in(select CASE_PICK_TASK_ID,LEGACY_SBORKA_PALLET_ID from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID in(select CASE_PICK_TASK_ID from RRL_CASE_CARRIER_LOT where LOT_UID=uid_value)) loop
     RRL_STOCK_PLAN_HELPER.row_key(rr,'RRL_CASE_PICK_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(ct.CASE_PICK_TASK_ID));
     if ct.LEGACY_SBORKA_PALLET_ID is not null then RRL_STOCK_PLAN_HELPER.row_key(rr,'RRL_SBORKA_PALLETS',RRL_STOCK_PLAN_HELPER.decimal_text(ct.LEGACY_SBORKA_PALLET_ID));end if;
    end loop;
    for st in(select distinct LEGACY_SBORKA_PALLET_ID from RRL_CUSTOMER_ORDER_FULFILLMENT where PICKED_PALLET_UID=uid_value and LEGACY_SBORKA_PALLET_ID is not null) loop
     RRL_STOCK_PLAN_HELPER.row_key(rr,'RRL_SBORKA_PALLETS',RRL_STOCK_PLAN_HELPER.decimal_text(st.LEGACY_SBORKA_PALLET_ID));
    end loop;
   end loop;v_resources:=rr.to_clob;
  end;
  RRL_STOCK_LOCK_API.begin_plan;
  RRL_STOCK_LOCK_API.acquire_policies(v_policies);
  RRL_STOCK_LOCK_API.acquire_resources(v_resources);
  assert_actor_active(p_actor);
  if g_kind in('INTERWARE_UNLOAD','INTERWARE_RECEIVE')then declare doc json_object_t:=json_object_t.parse(p_request);begin RRL_STOCK_INTERWARE_REC.assert_scope(doc.get_object('source').get_string('plan_operation_id'),p_actor);end;end if;
  if g_kind='LOAD_SHIPMENT'then declare doc json_object_t:=json_object_t.parse(p_request);begin RRL_STOCK_LOADING_READ.assert_scope(doc.get_object('source').get_string('pallet_identifier'),p_actor);end;end if;
  if g_kind='TARE_OFFER_CANCEL'then RRL_STOCK_TARE_CANCEL_CMD.assert_scope(p_request,p_actor);end if;
  if g_kind='TARE_BOOK'then RRL_TARE_LOAD_RECOVERY_API.assert_scope(p_request,p_actor);end if;assert_case_slot_actor(p_request,p_actor);assert_repack_actor(p_request,p_actor);
  if g_kind='UNLOAD_SHIPMENT'then declare doc json_object_t:=json_object_t.parse(p_request);begin RRL_STOCK_UNLOAD_CMD.assert_scope(doc.get_object('source').get_string('load_operation_id'),p_actor);end;end if;
  select STATE into v_release from RRL_STOCK_RELEASE where RELEASE_ID=1;
  if v_release!='ACTIVE' then raise_application_error(-20860,'STOCK_RELEASE_NOT_ACTIVE'); end if;
  if v_domain is not null then v_resolution.put('domain',json_object_t.parse(v_domain));end if;
  v_resolution.put('stock_before',json_array_t.parse(RRL_STOCK_INVARIANT_CORE.snapshot_stock(v_resources)));
  v_resolution.put('physical_before',json_array_t.parse(RRL_STOCK_COMPOSITION_CORE.snapshot_before(v_resources)));
  v_resolution.put('resources',json_array_t.parse(v_resources));
  v_resolution.put('policies',json_array_t.parse(v_policies));
  if g_kind in('TASK_COMPLETE','HU_TASK_COMPLETE') then RRL_WAREHOUSE_TASK_ACCESS.assert_completion(p_request,p_actor);end if;
  if g_kind='OUTGOING_PALLET_CHECK'then RRL_OUTGOING_QC_ACCESS.assert_identifier(json_object_t.parse(p_request).get_object('source').get_string('pallet_identifier'),p_actor);end if;
  if g_kind in('CASE_PICK_CONFIRM','CASE_CARRIER_MOVE','CASE_CARRIER_RETURN','CASE_SHORT_APPROVE')then RRL_CASE_TASK_ACCESS.assert_command(p_request,p_actor);end if;
  if g_kind='WAVE_EXECUTION_FINISH'then RRL_WAVE_EXEC_ACCESS.assert_command(p_request,p_actor);end if;
  RRL_STOCK_OPERATION_CORE.begin_operation(p_request,p_actor,g_operation,g_kind,p_replay,v_resolution.to_clob);
  if p_replay is not null then return; end if;
  g_change_before:=RRL_STOCK_CHANGE_AUDIT.snapshot(v_resources);
  g_request:=p_request;g_resolution:=v_resolution.to_clob;g_actor:=p_actor;g_tx:=dbms_transaction.local_transaction_id(false);g_prepared:=true;
  if g_kind='SAP_RECEIPT' then RRL_STOCK_CTX_API.begin_staging(v_resolution.get_object('domain').get_string('uid'),v_resolution.get_object('domain').get_string('receive_cell'));end if;
 end;
 procedure stage_birth(p_uid varchar2) is
  d json_object_t:=json_object_t.parse(g_resolution);b json_object_t;v json_object_t;a json_array_t;
  n number;policy number;capture_required number;found boolean:=false;uid varchar2(150);article varchar2(160);cell varchar2(60);qty number;
  doc number;expiry date;price number;mid number;m RRL_MES_MOVEMENT%rowtype;
 begin
  if not g_prepared or g_tx is null or g_tx!=dbms_transaction.local_transaction_id(false)
   or g_kind not in('INVENTORY_REGISTER_LOT','MES_MOVEMENTS') then raise_application_error(-20850,'WRITE_PLAN_VIOLATION');end if;
  if RRL_HAS_WRIGHT(g_actor,case when g_kind='INVENTORY_REGISTER_LOT' then 'stock_inventory_count' else 'mes_wms_bridge_apply' end)!=1
   then raise_application_error(-20882,'BIRTH_CAPTURE_FORBIDDEN');end if;
  a:=d.get_array('births');
  for i in 0..a.get_size-1 loop
   b:=treat(a.get(i) as json_object_t);
   if b.get_string('uid')=p_uid then found:=true;exit;end if;
  end loop;
  if not found then raise_application_error(-20884,'BIRTH_CAPTURE_NOT_PLANNED');end if;
  uid:=b.get_string('uid');article:=b.get_string('article');cell:=b.get_string('cell');qty:=RRL_STOCK_MATH.quantity(b.get_string('quantity'));
  select POLICY_VERSION,greatest(MARKING_REQUIRED,SERIALIZED_WEIGHT_BOXES)into policy,capture_required from RRL_SKU_RECEIPT_POLICY where ARTICUL=article;
  if capture_required!=1 or policy!=b.get_number('policy_version') then raise_application_error(-20890,'CLOSURE_CHANGED: birth marking policy');end if;
  RRL_STOCK_LOCK_API.assert_held(30,RRL_STOCK_LOCK_API.resource_key('HU',uid));
  select count(*) into n from RRL_REMAINS where UID_POLETA=uid and REMAIN>0;
  if n>0 then raise_application_error(-20886,'BIRTH_STOCK_ALREADY_EXISTS');end if;
  select count(*) into n from RRL_PALLETS where UID_PALLET=uid;
  if n=0 then
   if g_kind='INVENTORY_REGISTER_LOT' then
    v:=d.get_object('domain');doc:=v.get_number('document');expiry:=to_date(v.get_string('expiry_date'),'FXYYYY-MM-DD');price:=v.get_number('price');
    insert into RRL_PALLETS(UID_PALLET,ARTICUL,CREATION_DATE,EXPIRY_DATE,UNIT_COUNT,PRICE,PRIHOD_NAKLAD_ID,STOCK_ORIGIN_UID,CREATED_BY_STOCK_OP)
     values(uid,article,systimestamp,expiry,qty,price,-doc,uid,g_operation);
   else
    mid:=b.get_number('movement_id');select * into m from RRL_MES_MOVEMENT where MOVEMENT_ID=mid;
    insert into RRL_PALLETS(UID_PALLET,ARTICUL,UNIT_COUNT,PRIHOD_NAKLAD_ID,PROD_BATCH_ID,SSCC,QUALITY_STATUS,CREATED_BY_STOCK_OP)
     values(uid,article,qty,0,m.PROD_BATCH_ID,m.SSCC,'RELEASED',g_operation);
   end if;
  end if;
  RRL_STOCK_CTX_API.begin_staging(uid,cell);
 end;
 procedure finish_birth_capture is
 begin
  if not g_prepared or g_tx!=dbms_transaction.local_transaction_id(false) then raise_application_error(-20850,'WRITE_PLAN_VIOLATION');end if;
  RRL_STOCK_CTX_API.end_effect;
 end;
 procedure execute_prepared(p_result out clob) is
  v_outbox number;v_existing number;v_key varchar2(100);v_json json_object_t;v_resolved json_object_t;v_event json_object_t;v_changes clob;v_resources clob;v_after clob;v_composition json_object_t;v_unit_changes json_array_t;v_unit_change json_object_t;v_old_unit json_object_t;v_new_unit json_object_t;v_repacking boolean:=false;
 begin
  if not g_prepared or g_tx is null or dbms_transaction.local_transaction_id(false) is null
   or g_tx!=dbms_transaction.local_transaction_id(false) then raise_application_error(-20850,'WRITE_PLAN_VIOLATION'); end if;
  if g_kind='SAP_RECEIPT' then RRL_STOCK_CTX_API.end_effect;end if;
  if g_kind in('MANUAL_MOVE','COMPAT_MANUAL_MOVE') then RRL_STOCK_MOVE_CORE.manual_whole(g_request,g_actor,p_result);
  elsif g_kind='PICK_PALLET_BIND_SHIPMENT' then RRL_STOCK_FULLPAL_BIND_CMD.execute_command(g_request,g_actor,p_result);
  elsif g_kind in('HU_PLAN_MOVE','HU_TASK_COMPLETE') then RRL_STOCK_HU_TASK.execute_command(g_request,g_actor,p_result);
  elsif g_kind='HU_RELOCATE_SLOT' then RRL_STOCK_HU_SLOT_MOVE_CMD.execute_command(g_request,g_actor,p_result);
  elsif g_kind='HU_REPACK_SLOT'then RRL_STOCK_HU_REPACK_CMD.execute_command(g_request,g_actor,p_result);
  elsif g_kind='HU_UNPACK' then RRL_STOCK_HU_UNPACK_CMD.execute_command(g_request,g_actor,p_result);
  elsif g_kind in('TARE_LOSS_REPORT','TARE_LOSS_DECIDE') then RRL_STOCK_TARE_LOSS.execute_command(g_request,g_actor,p_result);
  elsif g_kind in('TARE_BOOK','TARE_BOOK_CANCEL') then RRL_STOCK_TARE_BOOK_CMD.execute_command(g_request,g_actor,p_result);
  elsif g_kind in('TARE_DAMAGE','TARE_WRITE_OFF') then RRL_STOCK_TARE_RESOLVE.execute_command(g_request,g_actor,p_result);
  elsif g_kind='TARE_OFFER_CANCEL'then RRL_STOCK_TARE_CANCEL_CMD.execute_command(g_request,g_actor,p_result);
  elsif g_kind in('TARE_COUNT','TARE_OFFER','TARE_ACCEPT') then RRL_STOCK_TARE_CMD.execute_command(g_request,g_actor,p_result);
  elsif g_kind='STORE_RETURN_PUTAWAY_PLAN' then RRL_STOCK_STORE_RETURN_PUT.execute_command(g_request,g_actor,p_result);
  elsif g_kind='STORE_RETURN_RECEIVE' then RRL_STOCK_STORE_RETURN_REC_CMD.execute_command(g_request,g_actor,p_result);
  elsif g_kind in('STORE_RETURN_HANDOVER','STORE_RETURN_PICKUP') then RRL_STOCK_STORE_RETURN_CUST_CMD.execute_command(g_request,g_actor,p_result);
  elsif g_kind='STORE_RETURN_TRANSPORT_PLAN' then RRL_STOCK_STORE_RETURN_TR_CMD.execute_command(g_request,g_actor,p_result);
  elsif g_kind='STORE_RETURN_SAP_BIND' then RRL_STOCK_STORE_RETURN_SAP_CMD.execute_command(g_request,g_actor,p_result);
  elsif g_kind='STORE_RETURN_APPROVE' then RRL_STOCK_STORE_RETURN_CMD.execute_command(g_request,g_actor,p_result);
  elsif g_kind='STORE_CASE_WORK' then RRL_STOCK_STORE_CASE_CMD.execute_command(g_request,g_actor,p_result);
  elsif g_kind='STORE_RECEIPT' then RRL_STOCK_STORE_RECEIPT_CMD.execute_command(g_request,g_actor,p_result);
  elsif g_kind='RECONCILE_HU_LOAD' then RRL_STOCK_LOAD_RECONCILE_CMD.execute_command(g_request,g_actor,p_result);
  elsif g_kind='UNLOAD_SHIPMENT' then RRL_STOCK_UNLOAD_CMD.execute_command(g_request,g_actor,p_result);
  elsif g_kind in('INTERWARE_UNLOAD','INTERWARE_RECEIVE') then RRL_STOCK_INTERWARE_REC.execute_command(g_request,g_actor,p_result);
  elsif g_kind ='INTERWARE_PUTAWAY_PLAN' then RRL_STOCK_INTERWARE_PUT.execute_command(g_request,g_actor,p_result);
  elsif g_kind ='INTERWARE_CUSTODY_RELEASE' then RRL_STOCK_INTERWARE_CUSTODY.execute_command(g_request,g_actor,p_result);
  elsif g_kind='LOAD_SHIPMENT' then RRL_STOCK_SINGLE_LOAD_CMD.execute_command(g_request,g_actor,p_result);
  elsif g_kind='TRIP_DEPART' then RRL_STOCK_TRIP_DEPART_CMD.execute_command(g_request,g_actor,p_result);
  elsif g_kind='HU_SHIP' then RRL_STOCK_HU_SHIP_CMD.execute_command(g_request,g_actor,p_result);
  elsif g_kind in('HU_CREATE','HU_ATTACH','HU_DETACH','HU_MOVE') then RRL_STOCK_HU_CMD.execute_command(g_request,g_actor,p_result);
  elsif g_kind='WAVE_EXECUTION_FINISH' then RRL_STOCK_WAVE_FINISH_CMD.execute_command(g_request,g_actor,p_result);
  elsif g_kind='WAVE_PICK_RELEASE' then RRL_STOCK_WAVE_PICK_CMD.execute_command(g_request,g_actor,p_result);
  elsif g_kind='WAVE_LAUNCH' then RRL_STOCK_WAVE_LAUNCH_CMD.execute_command(g_request,g_actor,p_result);
   elsif g_kind='OUTGOING_PALLET_CHECK' then RRL_STOCK_PALLET_QC_CMD.execute_command(g_request,g_actor,p_result);
   elsif g_kind='CASE_SHORT_APPROVE' then RRL_STOCK_CASE_SHORT_CMD.execute_command(g_request,g_actor,p_result);
  elsif g_kind='CASE_CARRIER_RETURN' then RRL_STOCK_CASE_RETURN_CMD.execute_command(g_request,g_actor,p_result);
   elsif g_kind='CASE_CARRIER_MOVE' then RRL_STOCK_CASE_MOVE_CMD.execute_command(g_request,g_actor,p_result);
   elsif g_kind='CASE_PICK_CONFIRM' then RRL_STOCK_CASE_PICK_CMD.execute_command(g_request,g_actor,p_result);
   elsif g_kind='RECEIPT_REVERSE' then RRL_STOCK_RECEIPT_REVERSE.execute_command(g_request,g_actor,p_result);
   elsif g_kind='INVENTORY_REGISTER_LOT' then RRL_STOCK_INVENTORY_BIRTH.execute_command(g_request,g_actor,p_result);
   elsif g_kind='INVENTORY_COUNT' then RRL_STOCK_INVENTORY_CMD.execute_count(g_request,g_actor,p_result);
   elsif g_kind='MES_RAW_TASK_CANCEL' then RRL_STOCK_MES_CANCEL_CMD.execute_command(g_request,g_actor,p_result);
   elsif g_kind in('MES_RELEASE_TO_PRODUCTION','MES_CALCULATE_SUPPLY') then RRL_STOCK_MES_SUPPLY_CMD.execute_command(g_request,g_actor,p_result);
   elsif g_kind in('DOCUMENT_RELEASE_RESERVATIONS','WAVE_CANCEL','WAVE_RELEASE','PICK_PLAN_CANCEL') then RRL_STOCK_DOC_RESERVE_CMD.execute_release(g_request,g_actor,p_result);
  elsif g_kind='RESERVATION_ALLOCATE_POOL' then RRL_STOCK_POOL_CMD.execute_command(g_request,g_actor,p_result);
  elsif g_kind='WAVE_RESERVE_SOURCES' then RRL_STOCK_WAVE_CMD.execute_reserve(g_request,g_actor,p_result);
  elsif g_kind in('SHIP_DOCUMENT','SHIP_PALLET') then RRL_STOCK_SHIPPING_CORE.execute_shipment(g_request,g_actor,p_result);
  elsif g_kind in('INTERNAL_MOVE','MOVE_QUARANTINE') then RRL_STOCK_INTERNAL_CMD.execute_move(g_request,g_actor,p_result);
  elsif g_kind='MES_MOVEMENTS' then RRL_STOCK_MES_MOVEMENT_CORE.execute_movements(g_request,g_actor,p_result);
  elsif g_kind='SAP_RECEIPT' then RRL_STOCK_RECEIPT_CORE.execute_receipt(g_request,g_actor,p_result);
  elsif g_kind='TASK_COMPLETE' then RRL_STOCK_TASK_CORE.execute_task(g_request,g_actor,p_result);
  elsif g_kind in('RESERVATION_CREATE','RESERVATION_PROMOTE','RESERVATION_RELEASE','RESERVATION_CANCEL','RESERVATION_CONSUME') then RRL_STOCK_RESERVATION_CMD.execute_command(g_request,g_actor,p_result);
  else raise_application_error(-20888,'COMMAND_HANDLER_NOT_INSTALLED'); end if;
  v_resolved:=json_object_t.parse(g_resolution);
  RRL_STOCK_COMPOSITION_CORE.finish_changes(v_resolved.get_array('physical_before').to_clob);
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
