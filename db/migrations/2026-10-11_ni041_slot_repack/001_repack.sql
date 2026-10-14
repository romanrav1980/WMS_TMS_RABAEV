create or replace package RRL_STOCK_HU_REPACK_CMD authid definer accessible by(package RRL_STOCK_POSTING_API)as
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
end;
/
create or replace package body RRL_STOCK_HU_REPACK_CMD as
 function proxy(p_request clob)return clob is d json_object_t:=json_object_t.parse(p_request);begin d.put('command_type','HU_ATTACH');return d.to_clob;end;
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob)is
  d json_object_t:=json_object_t.parse(p_request);m json_object_t:=d.get_object('metadata');v json_object_t;p json_object_t;c json_object_t;
  f json_array_t;r json_array_t;dom clob;parent_uid varchar2(200);child_uid varchar2(200);cell_name varchar2(60);
  parent_claim number;child_claim number;parent_slot number;child_slot number;task_no number;sync_no number;cv number;v_saved number;v_error number;
 begin
  if trim(m.get_string('reason'))is null or length(m.get_string('reason'))>1000 then raise_application_error(-20886,'HU_REPACK_REASON_REQUIRED');end if;
  if not m.has('measurements')or m.get('measurements').is_null then raise_application_error(-20886,'HU_REPACK_COMBINED_MEASUREMENTS_REQUIRED');end if;
  RRL_STOCK_HU_CMD.compile_command(proxy(p_request),p_operation,p_policies,p_resources,dom,true);
  v:=json_object_t.parse(dom);p:=v.get_object('parent_snapshot');c:=v.get_object('child_snapshot');
  parent_uid:=p.get_string('root');child_uid:=c.get_string('root');cell_name:=p.get_string('cell');
  if p.get_array('ancestors').get_size>0 or c.get_array('ancestors').get_size>0 then raise_application_error(-20886,'HU_REPACK_TWO_TOP_PLACES_REQUIRED');end if;
  cv:=treat(p.get_array('nodes').get(0)as json_object_t).get_number('version');
  if m.get_object('measurements').get_number('content_version')is null or m.get_object('measurements').get_number('content_version')!=cv then raise_application_error(-20890,'HU_REPACK_MEASUREMENT_VERSION_CONFLICT');end if;
  begin
   select TASK_ID,CELL_SLOT_ID into parent_claim,parent_slot from RRL_RECEIPT_SLOT_CLAIM where UID_PALLET=parent_uid and CELL=cell_name and STATUS='OCCUPIED';
   select TASK_ID,CELL_SLOT_ID into child_claim,child_slot from RRL_RECEIPT_SLOT_CLAIM where UID_PALLET=child_uid and CELL=cell_name and STATUS='OCCUPIED';
  exception when no_data_found then raise_application_error(-20886,'HU_REPACK_TWO_OCCUPIED_PLACES_REQUIRED');end;
  if parent_slot is null or child_slot is null or parent_slot=child_slot then raise_application_error(-20886,'HU_REPACK_DISTINCT_SOURCE_SLOTS_REQUIRED');end if;
  f:=json_array_t.parse(p_policies);r:=json_array_t.parse(p_resources);
  RRL_STOCK_PLAN_HELPER.fence(f,'CELL',cell_name,6);
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_RECEIPT_SLOT_CLAIM',RRL_STOCK_PLAN_HELPER.decimal_text(parent_claim));
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_RECEIPT_SLOT_CLAIM',RRL_STOCK_PLAN_HELPER.decimal_text(child_claim));
  RRL_STOCK_PLAN_HELPER.anchor(r,40,'SLOT',RRL_STOCK_PLAN_HELPER.decimal_text(parent_slot));
  RRL_STOCK_PLAN_HELPER.anchor(r,40,'SLOT',RRL_STOCK_PLAN_HELPER.decimal_text(child_slot));
  task_no:=RRL_WAREHOUSE_TASK_SQ.nextval;sync_no:=RRL_WH_TASK_SYNC_SQ.nextval;
  RRL_STOCK_HU_PLACEMENT_CORE.declare_place(r,task_no,sync_no);
  v.put('parent_claim_task',parent_claim);v.put('child_claim_task',child_claim);v.put('parent_slot',parent_slot);v.put('child_slot',child_slot);
  v.put('placement_task',task_no);v.put('placement_sync',sync_no);
  p_policies:=f.to_clob;p_resources:=r.to_clob;p_domain:=v.to_clob;
 exception when others then
  v_error:=sqlcode;
  if v_error in(-20886,-20867,-20890)then
   select count(*)into v_saved from RRL_STOCK_OPERATION where OPERATION_ID=p_operation and STATE='APPLIED';
   if v_saved=1 then raise_application_error(-20890,'HU_REPACK_COMMITTED_PEER_RETRY_SAME_OPERATION');end if;
  end if;raise;
 end;
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob)is
  d json_object_t:=json_object_t.parse(p_request);m json_object_t:=d.get_object('metadata');op varchar2(100):=d.get_string('operation_id');
  plan clob;v json_object_t;tree json_object_t;placement_metadata json_object_t;measures json_object_t;placement_json clob;unused_result clob;nodes clob;
  parent_uid varchar2(200);child_uid varchar2(200);cell_name varchar2(60);parent_slot number;child_slot number;parent_claim number;child_claim number;ware number;code varchar2(100);rid number;
 begin
  if RRL_HAS_WRIGHT(p_actor,'warehouse_task_execute')!=1 then raise_application_error(-20882,'HU_EXECUTION_FORBIDDEN');end if;
  select RESOLVED_PLAN_JSON into plan from RRL_STOCK_OPERATION where OPERATION_ID=op;v:=json_object_t.parse(plan).get_object('domain');
  parent_uid:=v.get_object('parent_snapshot').get_string('root');child_uid:=v.get_object('child_snapshot').get_string('root');
  cell_name:=v.get_object('parent_snapshot').get_string('cell');ware:=v.get_object('parent_snapshot').get_number('warehouse');
  parent_slot:=v.get_number('parent_slot');child_slot:=v.get_number('child_slot');parent_claim:=v.get_number('parent_claim_task');child_claim:=v.get_number('child_claim_task');
  if m.get_string('scan_cell')is null or m.get_string('scan_cell')!=cell_name then raise_application_error(-20886,'HU_REPACK_CELL_SCAN_REQUIRED');end if;
  select SLOT_CODE into code from RRL_TOPOLOGY_CELL_SLOT where CELL_SLOT_ID=parent_slot;
  if m.get_string('scan_parent_slot')is null or m.get_string('scan_parent_slot')!=code then raise_application_error(-20886,'HU_REPACK_PARENT_SLOT_SCAN_REQUIRED');end if;
  select SLOT_CODE into code from RRL_TOPOLOGY_CELL_SLOT where CELL_SLOT_ID=child_slot;
  if m.get_string('scan_child_slot')is null or m.get_string('scan_child_slot')!=code then raise_application_error(-20886,'HU_REPACK_CHILD_SLOT_SCAN_REQUIRED');end if;
  -- Existing executor checks both locked source signatures, versions, scans, cycles and book proof.
  RRL_STOCK_HU_CMD.execute_command(proxy(p_request),p_actor,unused_result);
  delete from RRL_RECEIPT_SLOT_CLAIM where TASK_ID=parent_claim and UID_PALLET=parent_uid and CELL_SLOT_ID=parent_slot and STATUS='OCCUPIED';
  if sql%rowcount!=1 then raise_application_error(-20890,'HU_REPACK_PARENT_CLAIM_CHANGED');end if;
  delete from RRL_RECEIPT_SLOT_CLAIM where TASK_ID=child_claim and UID_PALLET=child_uid and CELL_SLOT_ID=child_slot and STATUS='OCCUPIED';
  if sql%rowcount!=1 then raise_application_error(-20890,'HU_REPACK_CHILD_CLAIM_CHANGED');end if;
  tree:=json_object_t.parse(RRL_STOCK_HU_READ.snapshot_json(parent_uid));
  placement_metadata:=json_object_t.parse(m.to_clob);measures:=json_object_t.parse(m.get_object('measurements').to_clob);
  measures.put('content_version',treat(tree.get_array('nodes').get(0)as json_object_t).get_number('version'));
  placement_metadata.put('measurements',measures);placement_metadata.put('target_cell',cell_name);placement_metadata.put('target_slot_id',parent_slot);placement_metadata.put('planned_physical_task_id',v.get_number('placement_task'));
  -- Capacity validation sees the actual merged tree and excludes the replaced root once.
  -- A late refusal rolls back links, epochs and both deleted claims with the same root transaction.
  placement_json:=RRL_STOCK_HU_SLOT.target_json(tree.to_clob,placement_metadata.to_clob,null,parent_uid);
  RRL_STOCK_HU_PLACEMENT_CORE.record_place(p_request,p_actor,parent_uid,ware,cell_name,v.get_number('placement_task'),parent_slot,v.get_number('placement_sync'),placement_json);
  nodes:=tree.get_array('nodes').to_clob;
  for rr in(select RESERVATION_ID,UID_PALLET,CELL,BASE_QTY from RRL_STOCK_RESERVATION where UID_PALLET in(
   select U from json_table(nodes,'$[*]'columns(U varchar2(200)path '$.uid',K varchar2(20)path '$.kind'))where K='STOCK')
   and CELL=cell_name and RESERVATION_KIND='HARD'and STATUS in('ACTIVE','ALLOCATED','PICKING')and BASE_QTY>0 and nvl(CELL_SLOT_ID,-1)!=parent_slot order by RESERVATION_ID)loop
   RRL_STOCK_RESERVE_CORE.move_coverage(rr.RESERVATION_ID,rr.RESERVATION_ID,rr.UID_PALLET,rr.CELL,ware,rr.BASE_QTY,parent_slot,p_actor,rid);
   if rid!=rr.RESERVATION_ID then raise_application_error(-20869,'HU_REPACK_RESERVATION_IDENTITY_CHANGED');end if;
  end loop;
  tree:=json_object_t.parse(RRL_STOCK_HU_READ.snapshot_json(parent_uid));tree.put('operation_id',op);tree.put('command','HU_REPACK_SLOT');
  tree.put('task_id',v.get_number('placement_task'));tree.put('pallet_identifier',parent_uid);tree.put('slot_id',parent_slot);tree.put('released_child_slot_id',child_slot);tree.put('quantity_unchanged',true);tree.put('tare_assets_preserved',true);
  p_result:=tree.to_clob;
 end;
end;
/
