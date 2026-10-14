create or replace package body RRL_STOCK_INTERWARE_PUT as
 procedure assert_scope(p_receipt varchar2,p_actor varchar2,p_superseded number default null)is n number;
 begin
  select count(*)into n from RRL_INTERWARE_RECEIPT r join RUSERS u on u.ID=p_actor where r.OPERATION_ID=p_receipt and nvl(u.DELETED,0)=0 and RRL_HAS_WRIGHT(u.ID,'interwarehouse_receive')=1 and(u.WARE_ID=r.WARE_ID or upper(trim(u.USER_GROUP))='GLOBAL_ADMIN');
  if n!=1 then raise_application_error(-20882,'INTERWARE_PLACEMENT_ACTOR_REQUIRED');end if;
  if p_superseded is not null and nvl(RRL_HAS_WRIGHT(p_actor,'warehouse_task_edit'),0)!=1 then raise_application_error(-20882,'INTERWARE_REPLAN_TASK_EDIT_REQUIRED');end if;
 end;
 procedure describe_current(p_receipt varchar2,p_actor varchar2,p_task number,p_domain out json_object_t,p_replacing boolean default false) is
 receipt RRL_INTERWARE_RECEIPT%rowtype;plan RRL_INTERWARE_PLAN%rowtype;
 v_target varchar2(60);v_p number;v_h number;v_unit varchar2(20);v_ver number;v_capacity number;v_height number;v_weight number;v_unknown number;v_gross number;n number;unit_wire clob;unit_snapshot clob;unit_count number;unit_total number;unit_distinct number;thermal json_object_t;stored_thermal varchar2(100);stored_lo number;stored_hi number;hu_tree json_object_t;hu_nodes json_array_t;hu_node json_object_t;hu_stock number:=0;
 begin
 select *into receipt from RRL_INTERWARE_RECEIPT where OPERATION_ID=p_receipt;
 select *into plan from RRL_INTERWARE_PLAN where OPERATION_ID=receipt.PLAN_OPERATION_ID;
 plan:=RRL_INTERWARE_ROUTING.resolved(plan);
 select count(*)into n from RUSERS u where ID=p_actor and nvl(DELETED,0)=0 and(WARE_ID=receipt.WARE_ID or upper(trim(USER_GROUP))='GLOBAL_ADMIN')and RRL_HAS_WRIGHT(u.ID,'interwarehouse_receive')=1;
 if n!=1 then raise_application_error(-20882,'INTERWARE_PLACEMENT_ACTOR_REQUIRED');end if;
 RRL_INTERWARE_THERMAL.assert_release(plan.OPERATION_ID);
 thermal:=json_object_t.parse(RRL_INTERWARE_THERMAL.mode_json(plan.OPERATION_ID));
 if p_task is not null and not p_replacing then
  select TEMP_DECISION_OPERATION_ID,TASK_TEMP_MIN,TASK_TEMP_MAX into stored_thermal,stored_lo,stored_hi from RRL_INTERWARE_PUT_PLAN where TASK_ID=p_task;
  if nvl(stored_lo,-1000)!=nvl(thermal.get_number('task_temp_min'),-1000)or nvl(stored_hi,-1000)!=nvl(thermal.get_number('task_temp_max'),-1000)then raise_application_error(-20886,'INTERWARE_TASK_TEMPERATURE_REPLAN_REQUIRED');end if;
  thermal.put('task_decision_operation_id',stored_thermal);
 end if;
 v_target:=plan.OUTBOUND_DOCK;
 RRL_INTERWARE_THERMAL.assert_cell(thermal.to_clob,receipt.WARE_ID,v_target);
 select count(*)into n from RRL_TRANSPORT_TASK t join RRL_TT_DOCK d on d.DOCK=t.DOCK where t.ID=plan.TARGET_TT_ID and t.DOCK=v_target and d.WARE_ID=receipt.WARE_ID and nvl(d.DOCK_IS_BLOCKED,0)=0 and t.CONDITION='Спланирован'and nvl(t.DELETED,0)=0;
 if n!=1 then raise_application_error(-20886,'INTERWARE_ORIGINAL_TARGET_TRIP_UNAVAILABLE');end if;
 select count(*)into n from RRL_INTERWARE_PLACEMENT where RECEIPT_OPERATION_ID=p_receipt;if n!=0 then raise_application_error(-20886,'INTERWARE_ALREADY_PLACED');end if;
 select count(*)into n from RRL_INTERWARE_PUT_PLAN p join RRL_WAREHOUSE_TASK wt on wt.TASK_ID=p.TASK_ID where p.RECEIPT_OPERATION_ID=p_receipt and wt.STATUS!='CANCELLED'and(p_task is null or wt.TASK_ID!=p_task);
 if n!=0 then raise_application_error(-20886,'INTERWARE_ACTIVE_PLACEMENT_EXISTS');end if;
 select REMAIN,HARD_RESERVED_BASE,BASE_UOM,STOCK_VERSION into v_p,v_h,v_unit,v_ver from RRL_REMAINS where UID_POLETA=receipt.ROOT_UID and CELL=receipt.RECEIVE_CELL;
 if v_p!=receipt.BASE_QTY or v_h!=0 or v_unit!=receipt.BASE_UOM then raise_application_error(-20886,'INTERWARE_WHOLE_UNRESERVED_RECEIPT_REQUIRED');end if;
 select count(*)into n from RRL_REMAINS where UID_POLETA=receipt.ROOT_UID and CELL!=receipt.RECEIVE_CELL and(REMAIN!=0 or HARD_RESERVED_BASE!=0);if n!=0 then raise_application_error(-20886,'INTERWARE_MULTIPLE_STOCK_CELLS_DENIED');end if;
 select count(*)into n from dual where exists(select 1 from RRL_SKU_RECEIPT_PROFILE where ARTICUL=receipt.ARTICLE)or exists(select 1 from RRL_SKU_RECEIPT_POLICY where ARTICUL=receipt.ARTICLE and MARKING_REQUIRED=1)or exists(select 1 from RRL_FINISHED_GOODS_SKU where ARTICUL=receipt.ARTICLE and CRPT_REQUIRED=1);
 select count(*)into unit_count from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=receipt.ROOT_UID;
 if n>0 or unit_count>0 then
  if receipt.ORIGINAL_ROOT_UID is not null then
   select json_query(RESOLVED_PLAN_JSON,'$.domain.source_units' returning clob)into unit_wire from RRL_STOCK_OPERATION where OPERATION_ID=receipt.OPERATION_ID and STATE='APPLIED';
   declare envelope json_object_t:=json_object_t();a json_array_t:=json_array_t.parse(unit_wire);begin
    envelope.put('units',a);envelope.put('physical_unit_count',a.get_size);unit_wire:=envelope.to_clob;
   end;
  else
  select MANIFEST_JSON into unit_wire from RRL_INTERWARE_UNIT_MANIFEST where PLAN_OPERATION_ID=receipt.PLAN_OPERATION_ID;
  end if;
  select count(*),sum(u.BASE_QTY),count(distinct u.PHYSICAL_UNIT_KEY),
   json_arrayagg(json_object('key'value u.PHYSICAL_UNIT_KEY,'quantity'value RRL_STOCK_PLAN_HELPER.decimal_text(u.BASE_QTY),'base_uom'value u.BASE_UOM,'version'value u.UNIT_VERSION)order by u.PHYSICAL_UNIT_KEY returning clob)
   into n,unit_total,unit_distinct,unit_snapshot
   from RRL_WMS_RECEIPT_UNIT u join json_table(unit_wire,'$.units[*]'columns(K varchar2(64)path '$.key',Q varchar2(60)path '$.quantity',B varchar2(20)path '$.base_uom'))j on j.K=u.PHYSICAL_UNIT_KEY
   where u.CURRENT_UID=receipt.ROOT_UID and u.CURRENT_CELL=receipt.RECEIVE_CELL and u.STOCK_STATUS='AVAILABLE'and u.HARD_RESERVATION_ID is null and u.BASE_QTY=RRL_STOCK_MATH.quantity(j.Q)and u.BASE_UOM=j.B and u.BASE_UOM=receipt.BASE_UOM;
  if unit_count<1 or unit_count>10000 or n!=unit_count or unit_distinct!=unit_count or unit_total!=receipt.BASE_QTY or json_object_t.parse(unit_wire).get_number('physical_unit_count')!=unit_count then raise_application_error(-20884,'INTERWARE_ORIGINAL_AVAILABLE_UNITS_REQUIRED');end if;
 end if;
 if receipt.ORIGINAL_ROOT_UID is not null then
  select WEIGHT_BRUTTO into v_gross from RRL_PALLETS where UID_PALLET=receipt.ROOT_UID;
 else
 select GROSS_WEIGHT_KG into v_gross from RRL_TT_HU_LOAD_FACT where LOAD_OPERATION_ID=receipt.SOURCE_LOAD_OPERATION_ID;
 end if;
 RRL_STOCK_IW_PUT_CELL.assert_target(receipt.WARE_ID,receipt.ROOT_UID,receipt.RECEIVE_CELL,v_target,v_gross,p_task);
 p_domain:=json_object_t();p_domain.put('temperature',thermal);if unit_snapshot is not null then p_domain.put('physical_units',json_array_t.parse(unit_snapshot));end if;p_domain.put('receipt_operation_id',p_receipt);p_domain.put('plan_operation_id',receipt.PLAN_OPERATION_ID);p_domain.put('warehouse_id',receipt.WARE_ID);p_domain.put('uid',receipt.ROOT_UID);p_domain.put('article',receipt.ARTICLE);
 p_domain.put('from_cell',receipt.RECEIVE_CELL);p_domain.put('target_cell',v_target);p_domain.put('quantity',RRL_STOCK_PLAN_HELPER.decimal_text(receipt.BASE_QTY));p_domain.put('base_uom',receipt.BASE_UOM);p_domain.put('stock_version',v_ver);p_domain.put('target_trip_id',plan.TARGET_TT_ID);
 if plan.SOURCE_PLACE_UID is not null then
 hu_tree:=json_object_t.parse(RRL_STOCK_HU_READ.snapshot_json(plan.SOURCE_PLACE_UID,p_task));hu_nodes:=hu_tree.get_array('nodes');
 if hu_tree.get_string('cell')!=receipt.RECEIVE_CELL or hu_tree.get_number('warehouse')!=receipt.WARE_ID or hu_tree.get_number('leaf_count')!=1 or hu_tree.get_array('ancestors').get_size!=0 then raise_application_error(-20886,'INTERWARE_WHOLE_RECEIVED_HU_REQUIRED');end if;
 for i in 0..hu_nodes.get_size-1 loop hu_node:=treat(hu_nodes.get(i)as json_object_t);
 if hu_node.get_number('open_task_count')>0 then raise_application_error(-20886,'INTERWARE_HU_OTHER_PHYSICAL_TASK_OPEN');end if;
 if hu_node.get_string('kind')='STOCK'then
  hu_stock:=hu_stock+1;
  if hu_node.get_string('uid')!=receipt.ROOT_UID or RRL_STOCK_MATH.quantity(hu_node.get_string('quantity'))!=receipt.BASE_QTY then raise_application_error(-20886,'INTERWARE_HU_ORIGINAL_STOCK_LEAF_REQUIRED');end if;
 elsif hu_node.get_string('kind')!='CONTAINER'then raise_application_error(-20886,'INTERWARE_HU_STOCK_CONTAINER_ONLY');end if;
 end loop;
 if hu_stock!=1 then raise_application_error(-20886,'INTERWARE_HU_ONE_STOCK_REQUIRED');end if;
 p_domain.put('physical_place_uid',plan.SOURCE_PLACE_UID);p_domain.put('hu_version',treat(hu_nodes.get(0)as json_object_t).get_number('version'));
 p_domain.put('hu_snapshot',hu_tree);
 end if;

 exception when no_data_found then raise_application_error(-20886,'INTERWARE_RECEIPT_OUTBOUND_CELL_REQUIRED');
 end;
 procedure describe_plan(p_request clob,p_actor varchar2,p_domain out json_object_t)is
  d json_object_t:=json_object_t.parse(p_request);m json_object_t:=d.get_object('metadata');
  receipt_id varchar2(100):=d.get_object('source').get_string('receipt_operation_id');old_task number:=m.get_number('superseded_task_id');
  t RRL_WAREHOUSE_TASK%rowtype;p RRL_INTERWARE_PUT_PLAN%rowtype;reason nvarchar2(500):=m.get_string('replan_reason');n number;
 begin
  assert_scope(receipt_id,p_actor,old_task);
  if old_task is not null then
   if old_task<=0 or old_task!=trunc(old_task)or trim(reason)is null then raise_application_error(-20871,'INTERWARE_REPLAN_OLD_TASK_REASON_REQUIRED');end if;
   select *into p from RRL_INTERWARE_PUT_PLAN where TASK_ID=old_task;
   select *into t from RRL_WAREHOUSE_TASK where TASK_ID=old_task;
   if p.RECEIPT_OPERATION_ID!=receipt_id or t.STATUS is null or t.STATUS!='PLANNED'or nvl(t.TASK_TYPE,'~')!='PUTAWAY'or nvl(t.TASK_SOURCE,'~')!='MANUAL'or nvl(t.SOURCE_DOC_TYPE,'~')!='INTERWARE'or t.SOURCE_DOC_ID is null or t.SOURCE_DOC_ID!=t.TASK_ID or t.STARTED_AT is not null or t.STARTED_AT_INSTANT is not null or t.FACT_QTY is not null or t.RESOURCE_ID is not null or t.RESOURCE_SESSION_ID is not null or t.EQUIPMENT_ID is not null then raise_application_error(-20886,'INTERWARE_REPLAN_UNSTARTED_UNASSIGNED_ORIGINAL_TASK_REQUIRED');end if;
   select count(*)into n from RRL_STOCK_OPERATION where OPERATION_ID=p.OPERATION_ID and STATE='APPLIED'and COMMAND_TYPE='INTERWARE_PUTAWAY_PLAN';if n!=1 then raise_application_error(-20886,'INTERWARE_REPLAN_ORIGINAL_APPLIED_PLAN_REQUIRED');end if;
   describe_current(receipt_id,p_actor,old_task,p_domain,true);
   if p_domain.has('physical_place_uid')then raise_application_error(-20886,'INTERWARE_HU_REPLAN_EXPLICIT_CANCEL_REQUIRED');end if;
   if t.UID_PALLET!=p_domain.get_string('uid')or t.FROM_CELL!=p_domain.get_string('from_cell')or t.QTY!=RRL_STOCK_MATH.quantity(p_domain.get_string('quantity'))or t.UNIT_CODE!=p_domain.get_string('base_uom')or t.QTY_MODE!='PALLET'then raise_application_error(-20886,'INTERWARE_REPLAN_ORIGINAL_TASK_IDENTITY_REQUIRED');end if;
   p_domain.put('superseded_task_id',old_task);p_domain.put('superseded_plan_operation_id',p.OPERATION_ID);p_domain.put('replan_reason',reason);
  else
   if m.has('replan_reason')then raise_application_error(-20871,'INTERWARE_REPLAN_SUPERSEDED_TASK_REQUIRED');end if;
   describe_current(receipt_id,p_actor,null,p_domain);
  end if;
 exception when no_data_found then raise_application_error(-20886,'INTERWARE_REPLAN_ORIGINAL_TASK_REQUIRED');
 end;
 procedure declare_rows(p_domain json_object_t,p_resources in out nocopy json_array_t) is
 begin
 RRL_STOCK_PLAN_HELPER.row_key(p_resources,'RRL_INTERWARE_RECEIPT',p_domain.get_string('receipt_operation_id'));
 RRL_STOCK_PLAN_HELPER.row_key(p_resources,'RRL_INTERWARE_PLAN',p_domain.get_string('plan_operation_id'));
 if p_domain.has('superseded_task_id')then
  RRL_STOCK_PLAN_HELPER.row_key(p_resources,'RRL_WAREHOUSE_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(p_domain.get_number('superseded_task_id')));
  RRL_STOCK_PLAN_HELPER.row_key(p_resources,'RRL_INTERWARE_PUT_PLAN',p_domain.get_string('superseded_plan_operation_id'));
 end if;
 end;
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob) is
 d json_object_t:=json_object_t.parse(p_request);v json_object_t;f json_array_t:=json_array_t();r json_array_t:=json_array_t();v_task number;
 begin
 describe_plan(p_request,d.get_string('actor'),v);
 select RRL_WAREHOUSE_TASK_SQ.nextval into v_task from dual;v.put('task_id',v_task);
 RRL_STOCK_PLAN_HELPER.fence(f,'RELEASE','STOCK');RRL_STOCK_PLAN_HELPER.fence(f,'CONFIG','WAREHOUSE');RRL_STOCK_PLAN_HELPER.anchor(r,10,'OP',p_operation);
 RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','STOCK.OUTBOX:'||rawtohex(sys.dbms_crypto.hash(utl_i18n.string_to_raw(p_operation,'AL32UTF8'),sys.dbms_crypto.hash_sh256)));
 declare_rows(v,r);RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_INTERWARE_PUT_PLAN',p_operation);RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_WAREHOUSE_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(v_task));
 RRL_STOCK_PLAN_HELPER.stock_closure(f,r,v.get_string('uid'),v.get_string('article'),v.get_string('from_cell'),v.get_string('target_cell'));
 if v.has('hu_snapshot')then
 declare nodes json_array_t:=v.get_object('hu_snapshot').get_array('nodes');links json_array_t:=v.get_object('hu_snapshot').get_array('links');item json_object_t;begin
 for i in 0..nodes.get_size-1 loop item:=treat(nodes.get(i)as json_object_t);
 RRL_STOCK_PLAN_HELPER.anchor(r,30,'HU',item.get_string('uid'));RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_PALLETS',item.get_string('uid'));end loop;
 for i in 0..links.get_size-1 loop item:=treat(links.get(i)as json_object_t);RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_WMS_HU_LINK',RRL_STOCK_PLAN_HELPER.decimal_text(item.get_number('id')));end loop;
 end;
 end if;

 p_policies:=f.to_clob;p_resources:=r.to_clob;p_domain:=v.to_clob;
 end;
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob) is
 d json_object_t:=json_object_t.parse(p_request);op varchar2(100):=d.get_string('operation_id');resolved clob;v json_object_t;fresh json_object_t;j json_object_t:=json_object_t();
 v_receipt varchar2(100);v_task number;v_ware number;v_uid varchar2(200);v_article varchar2(160);v_from varchar2(60);v_to varchar2(60);v_unit varchar2(20);v_qty number;temp_op varchar2(100);temp_lo number;temp_hi number;old_task number;reason nvarchar2(500);
 begin
 select RESOLVED_PLAN_JSON into resolved from RRL_STOCK_OPERATION where OPERATION_ID=op;v:=json_object_t.parse(resolved).get_object('domain');v_receipt:=v.get_string('receipt_operation_id');v_task:=v.get_number('task_id');
 describe_plan(p_request,p_actor,fresh);fresh.put('task_id',v_task);
 if dbms_lob.compare(v.to_clob,fresh.to_clob)!=0 then raise_application_error(-20886,'INTERWARE_PLACEMENT_PLAN_CHANGED');end if;
 v_ware:=v.get_number('warehouse_id');v_uid:=v.get_string('uid');v_article:=v.get_string('article');v_from:=v.get_string('from_cell');v_to:=v.get_string('target_cell');v_unit:=v.get_string('base_uom');v_qty:=RRL_STOCK_MATH.quantity(v.get_string('quantity'));
 if v.has('superseded_task_id')then
  old_task:=v.get_number('superseded_task_id');reason:=v.get_string('replan_reason');
  update RRL_WAREHOUSE_TASK set STATUS='CANCELLED',CANCELLED_AT=systimestamp,CANCELLED_BY=p_actor,LAST_ERROR=reason where TASK_ID=old_task and STATUS='PLANNED'and STARTED_AT is null and STARTED_AT_INSTANT is null and RESOURCE_ID is null and RESOURCE_SESSION_ID is null and EQUIPMENT_ID is null;
  if sql%rowcount!=1 then raise_application_error(-20890,'CLOSURE_CHANGED: superseded interwarehouse task');end if;
  j.put('superseded_task_id',old_task);j.put('replan_reason',reason);
 end if;
 if v.has('physical_place_uid')then
 declare place_id varchar2(200):=v.get_string('physical_place_uid');version_no number:=v.get_number('hu_version');begin
 insert into RRL_WAREHOUSE_TASK(TASK_ID,TASK_TYPE,TASK_SOURCE,SOURCE_TASK_ID,SOURCE_DOC_TYPE,SOURCE_DOC_ID,UID_PALLET,TARGET_ARTICUL,FROM_CELL,TO_CELL,FROM_WARE_ID,TO_WARE_ID,QTY,UNIT_CODE,QTY_MODE,STATUS,CREATED_BY,HU_CONTENT_VERSION)
 values(v_task,'PUTAWAY','MANUAL',v_task,'WAREHOUSE_HU',v_task,place_id,v_article,v_from,v_to,v_ware,v_ware,1,'HU','PALLET','PLANNED',p_actor,version_no);
 j.put('physical_place_identifier',place_id);j.put('task_quantity','1');j.put('task_unit','HU');
 end;
 else
 insert into RRL_WAREHOUSE_TASK(TASK_ID,TASK_TYPE,TASK_SOURCE,SOURCE_TASK_ID,SOURCE_DOC_TYPE,SOURCE_DOC_ID,UID_PALLET,TARGET_ARTICUL,FROM_CELL,TO_CELL,FROM_WARE_ID,TO_WARE_ID,QTY,UNIT_CODE,QTY_MODE,STATUS,CREATED_BY)
 values(v_task,'PUTAWAY','MANUAL',v_task,'INTERWARE',v_task,v_uid,v_article,v_from,v_to,v_ware,v_ware,v_qty,v_unit,'PALLET','PLANNED',p_actor);
 end if;
 temp_op:=v.get_object('temperature').get_string('decision_operation_id');temp_lo:=v.get_object('temperature').get_number('task_temp_min');temp_hi:=v.get_object('temperature').get_number('task_temp_max');
 insert into RRL_INTERWARE_PUT_PLAN(OPERATION_ID,RECEIPT_OPERATION_ID,TASK_ID,TARGET_CELL,ACTOR,TEMP_DECISION_OPERATION_ID,TASK_TEMP_MIN,TASK_TEMP_MAX)values(op,v_receipt,v_task,v_to,p_actor,temp_op,temp_lo,temp_hi);
 j.put('temperature',v.get_object('temperature'));j.put('operation_id',op);j.put('task_id',v_task);j.put('receipt_operation_id',v_receipt);j.put('from_cell',v_from);j.put('to_cell',v_to);j.put('quantity',v.get_string('quantity'));j.put('base_uom',v_unit);j.put('stock_changed',false);p_result:=j.to_clob;
 end;
 procedure plan_task(p_task RRL_WAREHOUSE_TASK%rowtype,p_actor varchar2,p_resources in out nocopy json_array_t,p_domain in out nocopy json_object_t) is
 v_receipt varchar2(100);v_target varchar2(60);v json_object_t;
 begin
 select RECEIPT_OPERATION_ID,TARGET_CELL into v_receipt,v_target from RRL_INTERWARE_PUT_PLAN where TASK_ID=p_task.TASK_ID;
 describe_current(v_receipt,p_actor,p_task.TASK_ID,v);
 if v.has('physical_place_uid')then
 if p_task.TASK_SOURCE!='MANUAL'or p_task.TASK_TYPE!='PUTAWAY'or p_task.SOURCE_DOC_TYPE!='WAREHOUSE_HU'or p_task.SOURCE_DOC_ID!=p_task.TASK_ID or p_task.UID_PALLET!=v.get_string('physical_place_uid')or p_task.HU_CONTENT_VERSION!=v.get_number('hu_version')or p_task.FROM_CELL!=v.get_string('from_cell')or p_task.TO_CELL!=v.get_string('target_cell')or p_task.UNIT_CODE!='HU'or p_task.QTY!=1 or p_task.QTY_MODE!='PALLET'or v_target!=p_task.TO_CELL then raise_application_error(-20886,'INTERWARE_ORIGINAL_HU_TASK_REQUIRED');end if;
 else
 if p_task.TASK_SOURCE!='MANUAL' or p_task.TASK_TYPE!='PUTAWAY' or p_task.SOURCE_DOC_TYPE!='INTERWARE' or p_task.SOURCE_DOC_ID!=p_task.TASK_ID or p_task.UID_PALLET!=v.get_string('uid') or p_task.FROM_CELL!=v.get_string('from_cell') or p_task.TO_CELL!=v.get_string('target_cell') or p_task.UNIT_CODE!=v.get_string('base_uom') or p_task.QTY!=RRL_STOCK_MATH.quantity(v.get_string('quantity')) or p_task.QTY_MODE!='PALLET' or v_target!=p_task.TO_CELL then raise_application_error(-20886,'INTERWARE_ORIGINAL_TASK_REQUIRED');end if;
 end if;
 declare_rows(v,p_resources);RRL_STOCK_PLAN_HELPER.row_key(p_resources,'RRL_INTERWARE_PLACEMENT',RRL_STOCK_PLAN_HELPER.decimal_text(p_task.TASK_ID));
 p_domain.put('interwarehouse_placement',v);
 end;
 procedure validate_task(p_task RRL_WAREHOUSE_TASK%rowtype,p_actor varchar2,p_frozen json_object_t) is
 resources json_array_t:=json_array_t();domain json_object_t:=json_object_t();
 begin
 plan_task(p_task,p_actor,resources,domain);
 if dbms_lob.compare(p_frozen.to_clob,domain.get_object('interwarehouse_placement').to_clob)!=0 then raise_application_error(-20886,'INTERWARE_TASK_SOURCE_CHANGED');end if;
 end;
 procedure complete_task(p_task RRL_WAREHOUSE_TASK%rowtype,p_quantity number,p_target_uid varchar2,p_actor varchar2) is
 v_receipt varchar2(100);receipt RRL_INTERWARE_RECEIPT%rowtype;op varchar2(100):=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID');v_json clob;
 begin
 select RECEIPT_OPERATION_ID into v_receipt from RRL_INTERWARE_PUT_PLAN where TASK_ID=p_task.TASK_ID;select *into receipt from RRL_INTERWARE_RECEIPT where OPERATION_ID=v_receipt;
 if p_quantity!=receipt.BASE_QTY or p_target_uid!=receipt.ROOT_UID then raise_application_error(-20886,'INTERWARE_WHOLE_PLACEMENT_REQUIRED');end if;
 insert into RRL_INTERWARE_PLACEMENT(TASK_ID,RECEIPT_OPERATION_ID,OPERATION_ID,ROOT_UID,WARE_ID,TARGET_CELL,BASE_QTY,BASE_UOM,ACTOR)values(p_task.TASK_ID,v_receipt,op,receipt.ROOT_UID,receipt.WARE_ID,p_task.TO_CELL,receipt.BASE_QTY,receipt.BASE_UOM,p_actor);
 end;
end;

/
