create or replace package body RRL_STOCK_HU_TASK as

 function proxy_request(p_request clob,t RRL_WAREHOUSE_TASK%rowtype) return clob is

  d json_object_t:=json_object_t.parse(p_request);m json_object_t:=d.get_object('metadata');src json_object_t:=json_object_t();

 begin

  if d.get_string('command_type')='HU_PLAN_MOVE' then

   d.put('command_type','HU_MOVE');return d.to_clob;

  end if;

  declare v_group_receipt varchar2(100);begin

   select max(RECEIPT_OPERATION_ID)into v_group_receipt from RRL_IW_GROUP_PUT_PLAN where TASK_ID=t.TASK_ID;

   if v_group_receipt is not null then m.put('group_receipt_operation_id',v_group_receipt);

   else m.remove('group_receipt_operation_id');end if;

  end;

  src.put('uid',t.UID_PALLET);d.put('source',src);d.put('command_type','HU_TASK_COMPLETE');

  m.put('expected_version',t.HU_CONTENT_VERSION);m.put('target_cell',t.TO_CELL);m.put('physical_task_id',t.TASK_ID);

  m.put('target_slot_id',t.TO_CELL_SLOT_ID);

  if t.HU_MEASUREMENTS_JSON is not null then m.put('measurements',json_object_t.parse(t.HU_MEASUREMENTS_JSON));end if;

  m.put('scan_container',m.get_string('scanned_pallet'));d.put('metadata',m);return d.to_clob;

 end;

 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob) is

  d json_object_t:=json_object_t.parse(p_request);m json_object_t:=d.get_object('metadata');v json_object_t;ctx json_object_t;

  t RRL_WAREHOUSE_TASK%rowtype;pr clob;f json_array_t;r json_array_t;v_id number;v_sync number;v_key varchar2(400);iw_count number;

 begin

  if d.get_string('command_type')='HU_PLAN_MOVE' then

   select RRL_WAREHOUSE_TASK_SQ.nextval into v_id from dual;

   m.put('planned_physical_task_id',v_id);d.put('metadata',m);pr:=proxy_request(d.to_clob,t);

   RRL_STOCK_HU_CMD.compile_command(pr,p_operation,p_policies,p_resources,p_domain,p_defer_wait_planning=>true);

   v:=json_object_t.parse(p_domain);r:=json_array_t.parse(p_resources);

   RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_WAREHOUSE_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(v_id));

   if m.get_string('group_receipt_operation_id')is not null then

    declare group_value json_object_t;begin

     RRL_IW_GROUP_PUT.describe_receipt(m.get_string('group_receipt_operation_id'),v.get_string('target'),d.get_string('actor'),null,group_value);

     if group_value.get_string('uid')!=v.get_string('uid')then raise_application_error(-20886,'INTERWARE_GROUP_PLACEMENT_ROOT_REQUIRED');end if;

     RRL_IW_GROUP_PUT.declare_rows(group_value,p_operation,r);v.put('group_placement',group_value);

    end;

   end if;

   RRL_ST_DEFER_HU_WAIT.declare_plan(p_request,v_id,r,v);
   v.put('task_id',v_id);v.put('planning',1);p_domain:=v.to_clob;p_resources:=r.to_clob;

  else

   v_id:=d.get_object('source').get_number('task_id');

   select * into t from RRL_WAREHOUSE_TASK where TASK_ID=v_id;

   if t.HU_CONTENT_VERSION is null or t.TASK_SOURCE!='MANUAL' or t.SOURCE_DOC_TYPE!='WAREHOUSE_HU'

    or t.TASK_TYPE!='PUTAWAY' or t.UNIT_CODE!='HU' or t.QTY_MODE!='PALLET' or t.QTY!=1

    or t.STATUS not in('PLANNED','ASSIGNED','IN_PROGRESS') then raise_application_error(-20886,'HU_TASK_CONTRACT_OR_STATE_INVALID');end if;

   if m.has('fact_qty') and not m.get('fact_qty').is_null and RRL_STOCK_MATH.quantity(m.get_string('fact_qty'))!=1 then

    raise_application_error(-20886,'HU_TASK_ONE_WHOLE_PLACE_REQUIRED');end if;

   if m.get_number('scan_draft_id') is not null then raise_application_error(-20886,'HU_TASK_SEALED_TOP_SCAN_REQUIRED');end if;

   pr:=proxy_request(p_request,t);

   RRL_STOCK_HU_CMD.compile_command(pr,p_operation,p_policies,p_resources,p_domain);

   v:=json_object_t.parse(p_domain);r:=json_array_t.parse(p_resources);

   if v.get_object('parent_snapshot').get_string('cell')!=t.FROM_CELL

    or v.get_number('warehouse')!=t.FROM_WARE_ID or t.FROM_WARE_ID!=t.TO_WARE_ID then raise_application_error(-20886,'HU_TASK_SOURCE_LOCATION_CONFLICT');end if;

   ctx:=json_object_t.parse(RRL_TASK_RESOURCE_POLICY.context_json(v_id,'COMPLETE',d.get_string('actor'),d.get_string('actor'),

    m.get_number('resource_id'),m.get_number('resource_session_id'),m.get_number('equipment_id')));

   if ctx.get_number('resource_session_id') is not null then

    RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_RESOURCE_SESSION',RRL_STOCK_PLAN_HELPER.decimal_text(ctx.get_number('resource_session_id')));

    RRL_STOCK_PLAN_HELPER.row_key(r,'RUSERS',d.get_string('actor'));

   end if;

   if t.RESOURCE_SESSION_ID is not null then RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_RESOURCE_SESSION',RRL_STOCK_PLAN_HELPER.decimal_text(t.RESOURCE_SESSION_ID));end if;

   RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_WAREHOUSE_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(v_id));

   v_key:='WT:'||RRL_STOCK_PLAN_HELPER.decimal_text(v_id)||':MANUAL:PUTAWAY:'||RRL_STOCK_PLAN_HELPER.decimal_text(v_id)||':';

   begin select SYNC_ID into v_sync from RRL_WAREHOUSE_TASK_SYNC where SYNC_KEY=v_key;

   exception when no_data_found then select RRL_WH_TASK_SYNC_SQ.nextval into v_sync from dual;end;

   RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_WAREHOUSE_TASK_SYNC',RRL_STOCK_PLAN_HELPER.decimal_text(v_sync));

   RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','TASK.SYNC:'||v_key);

   v.put('task_signature',RRL_STOCK_TASK_PLAN.signature(t));v.put('hu_version',t.HU_CONTENT_VERSION);

   select count(*)into iw_count from RRL_INTERWARE_PUT_PLAN where TASK_ID=v_id;

   if iw_count=1 then RRL_STOCK_INTERWARE_PUT.plan_task(t,d.get_string('actor'),r,v);end if;

   declare group_receipt varchar2(100);group_value json_object_t;begin

    select max(RECEIPT_OPERATION_ID)into group_receipt from RRL_IW_GROUP_PUT_PLAN where TASK_ID=v_id;

    if group_receipt is not null then

     RRL_IW_GROUP_PUT.describe_receipt(group_receipt,t.TO_CELL,d.get_string('actor'),v_id,group_value);

     RRL_IW_GROUP_PUT.declare_rows(group_value,p_operation,r);v.put('group_placement',group_value);

    end if;

   end;

   RRL_ST_DEFER_HU_WAIT.declare_plan(p_request,v_id,r,v);
   v.put('resource_context',ctx);v.put('task_id',v_id);v.put('sync_id',v_sync);v.put('sync_key',v_key);v.put('planning',0);

   p_domain:=v.to_clob;p_resources:=r.to_clob;

  end if;

 end;

 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob) is

  d json_object_t:=json_object_t.parse(p_request);m json_object_t:=d.get_object('metadata');v json_object_t;j json_object_t:=json_object_t();ctx json_object_t;x json_object_t;

  t RRL_WAREHOUSE_TASK%rowtype;plan clob;s clob;pr clob;a json_array_t;v_op varchar2(100):=d.get_string('operation_id');v_id number;

  v_uid varchar2(200);v_from varchar2(60);v_to varchar2(60);v_ware number;v_version number;v_resource number;v_session number;v_equipment number;v_sync number;v_key varchar2(400);

  v_leaf_uid varchar2(200);v_qty number;v_base varchar2(20);v_sscc varchar2(32);v_slot number;v_measures clob;

 begin

  if RRL_HAS_WRIGHT(p_actor,'warehouse_task_execute')!=1 then raise_application_error(-20882,'HU_TASK_EXECUTION_FORBIDDEN');end if;

  select RESOLVED_PLAN_JSON into plan from RRL_STOCK_OPERATION where OPERATION_ID=v_op;

  v:=json_object_t.parse(plan).get_object('domain');v_id:=v.get_number('task_id');v_uid:=v.get_string('uid');

  v_from:=v.get_object('parent_snapshot').get_string('cell');v_to:=v.get_string('target');v_ware:=v.get_number('warehouse');

  if v.has('defer_wait_hu')then
   RRL_ST_DEFER_HU_WAIT.validate_plan(p_request,p_actor,v.get_object('defer_wait_hu'),case when v.get_number('planning')=1 then null else v_id end);
  end if;
  if v.has('group_placement')then RRL_IW_GROUP_PUT.validate_receipt(v.get_object('group_placement'),p_actor,case when v.get_number('planning')=1 then null else v_id end);end if;

  if v.get_number('planning')=1 then

   s:=RRL_STOCK_HU_READ.snapshot_json(v_uid);

   if rawtohex(sys.dbms_crypto.hash(s,sys.dbms_crypto.hash_sh256))!=v.get_string('parent_signature') then raise_application_error(-20890,'CLOSURE_CHANGED: HU task planning');end if;

   select SSCC into v_sscc from RRL_PALLETS where UID_PALLET=v_uid;

   if not v.has('defer_wait_hu')and(m.get_string('scan_container') is null or(m.get_string('scan_container')!=v_uid and(v_sscc is null or m.get_string('scan_container')!=v_sscc))) then raise_application_error(-20886,'HU_TASK_PLAN_TOP_SCAN_REQUIRED');end if;

   v_version:=treat(v.get_object('parent_snapshot').get_array('nodes').get(0) as json_object_t).get_number('version');

   v_slot:=v.get_object('placement').get_number('slot_id');

   if v.get_object('placement').has('measurements') then v_measures:=v.get_object('placement').get_object('measurements').to_clob;end if;

   insert into RRL_WAREHOUSE_TASK(TASK_ID,TASK_TYPE,TASK_SOURCE,SOURCE_TASK_ID,SOURCE_DOC_TYPE,UID_PALLET,

    FROM_WARE_ID,FROM_CELL,TO_WARE_ID,TO_CELL,QTY,UNIT_CODE,QTY_MODE,STATUS,CREATED_BY,HU_CONTENT_VERSION,TO_CELL_SLOT_ID,HU_MEASUREMENTS_JSON)

    values(v_id,'PUTAWAY','MANUAL',v_id,'WAREHOUSE_HU',v_uid,v_ware,v_from,v_ware,v_to,1,'HU','PALLET','PLANNED',p_actor,v_version,v_slot,v_measures);

   if v.has('group_placement')then RRL_IW_GROUP_PUT.record_plan(v_op,v_id,v.get_object('group_placement'),p_actor);end if;

   j.put('operation_id',v_op);j.put('task_id',v_id);j.put('pallet_identifier',v_uid);j.put('from_cell',v_from);j.put('cell',v_to);

   j.put('target_slot_id',v_slot);j.put('placement',v.get_object('placement'));j.put('status','PLANNED');j.put('quantity','1');j.put('unit_code','HU');j.put('content_version',v_version);p_result:=j.to_clob;
   if v.has('defer_wait_hu')then RRL_ST_DEFER_WAIT_API.record_hu_plan(p_request,v_id,v.get_object('defer_wait_hu'),p_result);end if;

  else

   select * into t from RRL_WAREHOUSE_TASK where TASK_ID=v_id for update;

   if t.HU_CONTENT_VERSION!=v.get_number('hu_version') or RRL_STOCK_TASK_PLAN.signature(t)!=v.get_string('task_signature') then raise_application_error(-20890,'CLOSURE_CHANGED: HU physical task');end if;

   if v.has('interwarehouse_placement')then RRL_STOCK_INTERWARE_PUT.validate_task(t,p_actor,v.get_object('interwarehouse_placement'));end if;

   ctx:=json_object_t.parse(RRL_TASK_RESOURCE_POLICY.context_json(v_id,'COMPLETE',p_actor,p_actor,

    m.get_number('resource_id'),m.get_number('resource_session_id'),m.get_number('equipment_id')));

   if dbms_lob.compare(ctx.to_clob,v.get_object('resource_context').to_clob)!=0 then raise_application_error(-20890,'CLOSURE_CHANGED: HU task resource context');end if;

   pr:=proxy_request(p_request,t);RRL_STOCK_HU_CMD.execute_command(pr,p_actor,s);

   v_resource:=ctx.get_number('resource_id');v_session:=ctx.get_number('resource_session_id');v_equipment:=ctx.get_number('equipment_id');

   update RRL_WAREHOUSE_TASK set STATUS='DONE',FACT_QTY=1,TARGET_UID_PALLET=v_uid,FINISHED_AT=systimestamp,

    ASSIGNED_TO=p_actor,RESOURCE_ID=v_resource,RESOURCE_SESSION_ID=v_session,EQUIPMENT_ID=v_equipment,

    COMPLETION_HASH=rawtohex(sys.dbms_crypto.hash(p_request,sys.dbms_crypto.hash_sh256)),COMPLETION_JSON=p_request,LAST_ERROR=null where TASK_ID=v_id;

   a:=v.get_object('parent_snapshot').get_array('nodes');

   for i in 0..a.get_size-1 loop x:=treat(a.get(i) as json_object_t);

    if x.get_string('kind')='STOCK' then

     v_leaf_uid:=x.get_string('uid');v_qty:=RRL_STOCK_MATH.quantity(x.get_string('quantity'));v_base:=x.get_string('base_uom');

     insert into RRL_WAREHOUSE_TASK_STOCK_MOVE(STOCK_MOVE_ID,TASK_ID,TASK_SOURCE,TASK_TYPE,SOURCE_DOC_TYPE,SOURCE_TASK_ID,

      UID_PALLET,TARGET_UID_PALLET,FROM_CELL,TO_CELL,QTY,BASE_QTY,BASE_UOM,OPERATION_ID,CREATED_AT,CREATED_BY)

      values(RRL_WH_TASK_STOCK_MOVE_SQ.nextval,v_id,'MANUAL','PUTAWAY','WAREHOUSE_HU',v_id,v_leaf_uid,v_leaf_uid,

       v_from,v_to,v_qty,v_qty,v_base,v_op,systimestamp,p_actor);

    end if;

   end loop;

   if v_resource is not null or v_session is not null or v_equipment is not null then

    insert into RRL_RESOURCE_FACT_EVENT(EVENT_ID,TASK_ID,SESSION_ID,RESOURCE_ID,EVENT_TYPE,EVENT_AT,EVENT_BY,PAYLOAD_JSON)

     values(RRL_RESOURCE_FACT_EVENT_SQ.nextval,v_id,v_session,v_resource,'COMPLETED',systimestamp,p_actor,p_request);

   end if;

   update RRL_RESOURCE_SESSION set CURRENT_TASK_ID=null where SESSION_ID in(v_session,t.RESOURCE_SESSION_ID) and CURRENT_TASK_ID=v_id;

   if v_session is not null then update RRL_RESOURCE_SESSION set LAST_CELL=v_to,LAST_POSITION_AT=systimestamp,LAST_HEARTBEAT_AT=systimestamp

    where SESSION_ID=v_session and OPERATOR_USER_ID=p_actor;end if;

   v_sync:=v.get_number('sync_id');v_key:=v.get_string('sync_key');

   merge into RRL_WAREHOUSE_TASK_SYNC dst using(select v_key SYNC_KEY from dual)src on(dst.SYNC_KEY=src.SYNC_KEY)

    when matched then update set dst.SYNC_STATUS='SYNCED',dst.SYNCED_AT=systimestamp,dst.UPDATED_AT=systimestamp,dst.UPDATED_BY=p_actor,dst.LAST_ERROR=null

    when not matched then insert(SYNC_ID,TASK_ID,TASK_SOURCE,TASK_TYPE,SOURCE_DOC_TYPE,SOURCE_TASK_ID,SYNC_KEY,SYNC_STATUS,SYNC_ATTEMPT,CREATED_AT,UPDATED_AT,SYNCED_AT,UPDATED_BY)

     values(v_sync,v_id,'MANUAL','PUTAWAY','WAREHOUSE_HU',v_id,v_key,'SYNCED',1,systimestamp,systimestamp,systimestamp,p_actor);

   if v.has('interwarehouse_placement')then

    x:=v.get_object('interwarehouse_placement');

    RRL_STOCK_INTERWARE_PUT.complete_task(t,RRL_STOCK_MATH.quantity(x.get_string('quantity')),x.get_string('uid'),p_actor);

   end if;

   if v.has('group_placement')then RRL_IW_GROUP_PUT.record_complete(v_op,v_id,v.get_object('group_placement'),p_actor);end if;

   j:=json_object_t.parse(RRL_STOCK_HU_READ.snapshot_json(v_uid));j.put('operation_id',v_op);j.put('task_id',v_id);j.put('status','DONE');

   j.put('pallet_identifier',v_uid);j.put('source_pallet_identifier',v_uid);j.put('quantity','1');j.put('unit_code','HU');j.put('remaining_quantity','0');j.put_null('residual_task_id');

   p_result:=j.to_clob;

  end if;

 end;

end;
/
