create or replace package RRL_STOCK_HU_SLOT_MOVE_CMD authid definer accessible by(package RRL_STOCK_POSTING_API) as
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
end;
/
create or replace package body RRL_STOCK_HU_SLOT_MOVE_CMD as
 function digest(s clob) return varchar2 is begin return rawtohex(sys.dbms_crypto.hash(s,sys.dbms_crypto.hash_sh256));end;
 function placement(p_tree clob,p_metadata clob,p_uid varchar2,p_task number) return clob is
  m json_object_t:=json_object_t.parse(p_metadata);tree json_object_t:=json_object_t.parse(p_tree);
 begin
  m.put('target_cell',tree.get_string('cell'));m.put('planned_physical_task_id',p_task);
  return RRL_STOCK_HU_SLOT.target_json(p_tree,m.to_clob,null,p_uid);
 end;
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob) is
  d json_object_t:=json_object_t.parse(p_request);m json_object_t:=d.get_object('metadata');v json_object_t:=json_object_t();tree json_object_t;
  f json_array_t:=json_array_t();r json_array_t:=json_array_t();s clob;v_uid varchar2(200):=d.get_object('source').get_string('uid');
  v_old_task number;v_old_slot number;v_slot number:=m.get_number('target_slot_id');v_task number;v_sync number;v_cell varchar2(60);v_placement clob;
 begin
  s:=RRL_STOCK_HU_READ.snapshot_json(v_uid);tree:=json_object_t.parse(s);v_cell:=tree.get_string('cell');
  if tree.get_array('ancestors').get_size>0 or treat(tree.get_array('nodes').get(0) as json_object_t).get_string('kind') not in('CONTAINER','STOCK') then raise_application_error(-20886,'HU_SLOT_MOVE_TOP_CONTAINER_WITH_STOCK_REQUIRED');end if;
  if m.get_number('expected_version') is null or m.get_number('expected_version')!=treat(tree.get_array('nodes').get(0) as json_object_t).get_number('version') then raise_application_error(-20890,'CLOSURE_CHANGED: HU slot movement version');end if;
  begin select TASK_ID,CELL_SLOT_ID into v_old_task,v_old_slot from RRL_RECEIPT_SLOT_CLAIM where UID_PALLET=v_uid and CELL=v_cell and STATUS='OCCUPIED';
  exception when no_data_found then raise_application_error(-20886,'HU_SLOT_MOVE_EXISTING_PLACEMENT_REQUIRED');end;
  if v_slot is null or v_slot=v_old_slot then raise_application_error(-20886,'HU_SLOT_MOVE_DIFFERENT_SLOT_REQUIRED');end if;
  v_task:=RRL_WAREHOUSE_TASK_SQ.nextval;v_sync:=RRL_WH_TASK_SYNC_SQ.nextval;
  v_placement:=placement(s,m.to_clob,v_uid,v_task);
  RRL_STOCK_PLAN_HELPER.fence(f,'RELEASE','STOCK');RRL_STOCK_PLAN_HELPER.fence(f,'CONFIG','WAREHOUSE');RRL_STOCK_PLAN_HELPER.fence(f,'CELL',v_cell,6);
  RRL_STOCK_PLAN_HELPER.anchor(r,10,'OP',p_operation);RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','STOCK.OUTBOX:'||digest(to_clob(p_operation)));
  RRL_STOCK_HU_CMD.declare_tree(f,r,s);
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_RECEIPT_SLOT_CLAIM',RRL_STOCK_PLAN_HELPER.decimal_text(v_old_task));
  RRL_STOCK_PLAN_HELPER.anchor(r,40,'SLOT',RRL_STOCK_PLAN_HELPER.decimal_text(v_old_slot));
  RRL_STOCK_PLAN_HELPER.anchor(r,40,'SLOT',RRL_STOCK_PLAN_HELPER.decimal_text(v_slot));
  RRL_STOCK_HU_PLACEMENT_CORE.declare_place(r,v_task,v_sync);
  v.put('uid',v_uid);v.put('snapshot',tree);v.put('signature',digest(s));v.put('placement',json_object_t.parse(v_placement));
  v.put('old_claim_task',v_old_task);v.put('old_slot',v_old_slot);v.put('slot',v_slot);v.put('task',v_task);v.put('sync',v_sync);
  p_domain:=v.to_clob;p_resources:=r.to_clob;p_policies:=f.to_clob;
 end;
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob) is
  d json_object_t:=json_object_t.parse(p_request);m json_object_t:=d.get_object('metadata');op varchar2(100):=d.get_string('operation_id');
  plan clob;v json_object_t;tree json_object_t;s clob;new_placement clob;nodes clob;j json_object_t:=json_object_t();
  v_uid varchar2(200);v_cell varchar2(60);alias varchar2(32);code varchar2(100);old_task number;old_slot number;target_slot number;v_ware number;rid number;
 begin
  if RRL_HAS_WRIGHT(p_actor,'warehouse_task_execute')!=1 then raise_application_error(-20882,'HU_EXECUTION_FORBIDDEN');end if;
  select RESOLVED_PLAN_JSON into plan from RRL_STOCK_OPERATION where OPERATION_ID=op;v:=json_object_t.parse(plan).get_object('domain');
  v_uid:=v.get_string('uid');tree:=v.get_object('snapshot');v_cell:=tree.get_string('cell');v_ware:=tree.get_number('warehouse');old_task:=v.get_number('old_claim_task');old_slot:=v.get_number('old_slot');target_slot:=v.get_number('slot');
  select SSCC into alias from RRL_PALLETS where UID_PALLET=v_uid;
  if m.get_string('scan_container') is null or(m.get_string('scan_container')!=v_uid and(alias is null or m.get_string('scan_container')!=alias))
   or m.get_string('scan_cell') is null or m.get_string('scan_cell')!=v_cell then raise_application_error(-20886,'HU_SLOT_MOVE_CONTAINER_CELL_SCAN_REQUIRED');end if;
  select SLOT_CODE into code from RRL_TOPOLOGY_CELL_SLOT where CELL_SLOT_ID=old_slot;
  if m.get_string('scan_from_slot') is null or m.get_string('scan_from_slot')!=code then raise_application_error(-20886,'HU_SLOT_MOVE_FROM_SLOT_SCAN_REQUIRED');end if;
  select SLOT_CODE into code from RRL_TOPOLOGY_CELL_SLOT where CELL_SLOT_ID=target_slot;
  if m.get_string('scan_to_slot') is null or m.get_string('scan_to_slot')!=code then raise_application_error(-20886,'HU_SLOT_MOVE_TO_SLOT_SCAN_REQUIRED');end if;
  s:=RRL_STOCK_HU_READ.snapshot_json(v_uid);
  if digest(s)!=v.get_string('signature') then raise_application_error(-20890,'CLOSURE_CHANGED: HU slot composition');end if;
  new_placement:=placement(s,m.to_clob,v_uid,v.get_number('task'));
  if dbms_lob.compare(new_placement,v.get_object('placement').to_clob)!=0 then raise_application_error(-20890,'CLOSURE_CHANGED: HU target slot');end if;
  delete from RRL_RECEIPT_SLOT_CLAIM where TASK_ID=old_task and UID_PALLET=v_uid and CELL_SLOT_ID=old_slot and STATUS='OCCUPIED';
  if sql%rowcount!=1 then raise_application_error(-20890,'CLOSURE_CHANGED: HU source claim');end if;
  update RRL_PALLETS set HU_CONTENT_VERSION=HU_CONTENT_VERSION+1 where UID_PALLET=v_uid and HU_SHIPPED_OPERATION is null;
  if sql%rowcount!=1 then raise_application_error(-20890,'CLOSURE_CHANGED: HU active placement');end if;
  RRL_STOCK_HU_PLACEMENT_CORE.record_place(p_request,p_actor,v_uid,v_ware,v_cell,v.get_number('task'),target_slot,v.get_number('sync'),new_placement);
  nodes:=tree.get_array('nodes').to_clob;
  for rr in(select RESERVATION_ID,UID_PALLET,CELL,BASE_QTY from RRL_STOCK_RESERVATION where UID_PALLET in(
   select U from json_table(nodes,'$[*]' columns(U varchar2(200) path '$.uid',K varchar2(20) path '$.kind')) where K='STOCK')
   and CELL=v_cell and RESERVATION_KIND='HARD' and STATUS in('ACTIVE','ALLOCATED','PICKING') and BASE_QTY>0 order by RESERVATION_ID) loop
   RRL_STOCK_RESERVE_CORE.move_coverage(rr.RESERVATION_ID,rr.RESERVATION_ID,rr.UID_PALLET,rr.CELL,v_ware,rr.BASE_QTY,target_slot,p_actor,rid);
   if rid!=rr.RESERVATION_ID then raise_application_error(-20869,'HU_SLOT_MOVE_RESERVATION_IDENTITY_CHANGED');end if;
  end loop;
  j:=json_object_t.parse(RRL_STOCK_HU_READ.snapshot_json(v_uid));j.put('operation_id',op);j.put('command','HU_RELOCATE_SLOT');j.put('task_id',v.get_number('task'));j.put('pallet_identifier',v_uid);j.put('slot_id',target_slot);j.put('quantity_unchanged',true);
  p_result:=j.to_clob;
 end;
end;
/
