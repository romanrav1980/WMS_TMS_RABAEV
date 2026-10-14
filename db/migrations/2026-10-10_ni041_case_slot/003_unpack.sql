create or replace package RRL_STOCK_HU_UNPACK_CMD authid definer accessible by(package RRL_STOCK_POSTING_API) as
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
end;
/
create or replace package body RRL_STOCK_HU_UNPACK_CMD as
 function proxy(p_request clob) return clob is d json_object_t:=json_object_t.parse(p_request);begin d.put('command_type','HU_DETACH');return d.to_clob;end;
 function placement(tree json_object_t,measures json_object_t,slot_no number,task_no number,root_uid varchar2,extra json_object_t) return json_object_t is
  m json_object_t:=json_object_t();w number;vol number;
 begin
  m.put('target_cell',tree.get_string('cell'));m.put('target_slot_id',slot_no);m.put('planned_physical_task_id',task_no);m.put('measurements',measures);
  w:=RRL_STOCK_MATH.quantity(extra.get_string('gross_weight_kg'));
  vol:=ceil(RRL_STOCK_MATH.quantity(extra.get_string('width_m'))*RRL_STOCK_MATH.quantity(extra.get_string('depth_m'))*RRL_STOCK_MATH.quantity(extra.get_string('height_m'))*1000000000)/1000000000;
  return json_object_t.parse(RRL_STOCK_HU_SLOT.target_json(tree.to_clob,m.to_clob,null,root_uid,w,vol));
 end;
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob) is
  d json_object_t:=json_object_t.parse(p_request);m json_object_t:=d.get_object('metadata');v json_object_t;p json_object_t;c json_object_t;x json_object_t;
  f json_array_t;r json_array_t;nodes json_array_t;remain_nodes json_array_t:=json_array_t();child_nodes json_array_t;pr json_object_t;cr json_object_t;
  type keys is table of number index by varchar2(200);removed keys;
  dom clob;v_uid varchar2(200):=d.get_object('source').get_string('uid');child_uid varchar2(200):=m.get_string('child_uid');old_task number;old_slot number;new_slot number:=m.get_number('child_slot_id');
  parent_task number;child_task number;parent_sync number;child_sync number;sync_key varchar2(255);leaf_count number:=0;n number;cell_name varchar2(60);
 begin
  if (child_uid is null and m.get_number('child_case_task_id') is null) or(child_uid is not null and m.get_number('child_case_task_id') is not null) or new_slot is null then raise_application_error(-20886,'HU_UNPACK_CONTAINER_AND_SLOT_REQUIRED');end if;
  RRL_STOCK_HU_CMD.compile_command(proxy(p_request),p_operation,p_policies,p_resources,dom,true);v:=json_object_t.parse(dom);
  p:=v.get_object('parent_snapshot');c:=v.get_object('child_snapshot');cell_name:=p.get_string('cell');child_uid:=c.get_string('root');
  if p.get_array('ancestors').get_size>0 or treat(c.get_array('nodes').get(0) as json_object_t).get_string('kind') not in('CONTAINER','STOCK','CASE') then raise_application_error(-20886,'HU_UNPACK_TOP_PARENT_CONTAINER_CHILD_REQUIRED');end if;
  begin select TASK_ID,CELL_SLOT_ID into old_task,old_slot from RRL_RECEIPT_SLOT_CLAIM where UID_PALLET=v_uid and CELL=cell_name and STATUS='OCCUPIED';
  exception when no_data_found then raise_application_error(-20886,'HU_UNPACK_EXISTING_PARENT_SLOT_REQUIRED');end;
  if old_slot=new_slot then raise_application_error(-20886,'HU_UNPACK_SEPARATE_CHILD_SLOT_REQUIRED');end if;
  child_nodes:=c.get_array('nodes');
  for i in 0..child_nodes.get_size-1 loop x:=treat(child_nodes.get(i) as json_object_t);removed(x.get_string('uid')):=1;end loop;
  nodes:=p.get_array('nodes');
  for i in 0..nodes.get_size-1 loop x:=treat(nodes.get(i) as json_object_t);
   if not removed.exists(x.get_string('uid')) then remain_nodes.append(x);if x.get_string('kind')='STOCK' then leaf_count:=leaf_count+1;end if;end if;
  end loop;
  pr:=json_object_t.parse(p.to_clob);pr.put('nodes',remain_nodes);pr.put('leaf_count',leaf_count);
  parent_task:=RRL_WAREHOUSE_TASK_SQ.nextval;child_task:=RRL_WAREHOUSE_TASK_SQ.nextval;
  if not m.has('parent_measurements') or not m.has('child_measurements') then raise_application_error(-20886,'HU_UNPACK_BOTH_FRESH_MEASUREMENTS_REQUIRED');end if;
  cr:=placement(c,m.get_object('child_measurements'),new_slot,child_task,v_uid,m.get_object('parent_measurements'));
  v.put('child_placement',cr);
  cr:=placement(pr,m.get_object('parent_measurements'),old_slot,parent_task,v_uid,m.get_object('child_measurements'));
  v.put('parent_placement',cr);v.put('remaining_parent_snapshot',pr);
  v.put('old_claim_task',old_task);v.put('parent_slot',old_slot);v.put('child_slot',new_slot);v.put('parent_placement_task',parent_task);v.put('child_placement_task',child_task);
  f:=json_array_t.parse(p_policies);r:=json_array_t.parse(p_resources);RRL_STOCK_PLAN_HELPER.fence(f,'CELL',cell_name,6);
  RRL_STOCK_PLAN_HELPER.anchor(r,40,'SLOT',RRL_STOCK_PLAN_HELPER.decimal_text(old_slot));
  RRL_STOCK_PLAN_HELPER.anchor(r,40,'SLOT',RRL_STOCK_PLAN_HELPER.decimal_text(new_slot));
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_RECEIPT_SLOT_CLAIM',RRL_STOCK_PLAN_HELPER.decimal_text(old_task));
  for i in 1..2 loop n:=case i when 1 then parent_task else child_task end;
   RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_WAREHOUSE_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(n));
   RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_RECEIPT_SLOT_CLAIM',RRL_STOCK_PLAN_HELPER.decimal_text(n));
  end loop;
  parent_sync:=RRL_WH_TASK_SYNC_SQ.nextval;child_sync:=RRL_WH_TASK_SYNC_SQ.nextval;
  v.put('parent_sync',parent_sync);v.put('child_sync',child_sync);
  for i in 1..2 loop n:=case i when 1 then parent_task else child_task end;
   sync_key:='WT:'||RRL_STOCK_PLAN_HELPER.decimal_text(n)||':MANUAL:PUTAWAY:'||RRL_STOCK_PLAN_HELPER.decimal_text(n)||':';
   RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_WAREHOUSE_TASK_SYNC',RRL_STOCK_PLAN_HELPER.decimal_text(case i when 1 then parent_sync else child_sync end));
   RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','TASK.SYNC:'||sync_key);
  end loop;
  p_policies:=f.to_clob;p_resources:=r.to_clob;p_domain:=v.to_clob;
 end;
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob) is
  d json_object_t:=json_object_t.parse(p_request);m json_object_t:=d.get_object('metadata');op varchar2(100):=d.get_string('operation_id');plan clob;unused_result clob;
  v json_object_t;x json_object_t;actual json_object_t;placement_now json_object_t;measures json_object_t;j json_object_t:=json_object_t();children clob;
  v_uid varchar2(200);child_uid varchar2(200);cell_name varchar2(60);ware number;old_task number;old_slot number;child_slot number;rid number;
 begin
  if RRL_HAS_WRIGHT(p_actor,'warehouse_task_execute')!=1 then raise_application_error(-20882,'HU_EXECUTION_FORBIDDEN');end if;
  select RESOLVED_PLAN_JSON into plan from RRL_STOCK_OPERATION where OPERATION_ID=op;v:=json_object_t.parse(plan).get_object('domain');
  v_uid:=v.get_string('uid');child_uid:=v.get_object('child_snapshot').get_string('root');cell_name:=v.get_object('parent_snapshot').get_string('cell');ware:=v.get_object('parent_snapshot').get_number('warehouse');
  old_task:=v.get_number('old_claim_task');old_slot:=v.get_number('parent_slot');child_slot:=v.get_number('child_slot');
  if m.get_string('scan_cell') is null or m.get_string('scan_cell')!=cell_name or m.get_string('scan_parent_slot') is null or m.get_string('scan_child_slot') is null then raise_application_error(-20886,'HU_UNPACK_CELL_AND_SLOTS_SCAN_REQUIRED');end if;
  declare code varchar2(100);begin
   select SLOT_CODE into code from RRL_TOPOLOGY_CELL_SLOT where CELL_SLOT_ID=old_slot;
   if code!=m.get_string('scan_parent_slot') then raise_application_error(-20886,'HU_UNPACK_PARENT_SLOT_SCAN_REQUIRED');end if;
   select SLOT_CODE into code from RRL_TOPOLOGY_CELL_SLOT where CELL_SLOT_ID=child_slot;
   if code!=m.get_string('scan_child_slot') then raise_application_error(-20886,'HU_UNPACK_CHILD_SLOT_SCAN_REQUIRED');end if;
  end;
  placement_now:=placement(v.get_object('child_snapshot'),m.get_object('child_measurements'),child_slot,v.get_number('child_placement_task'),v_uid,m.get_object('parent_measurements'));
  if dbms_lob.compare(placement_now.to_clob,v.get_object('child_placement').to_clob)!=0 then raise_application_error(-20890,'CLOSURE_CHANGED: child placement');end if;
  placement_now:=placement(v.get_object('remaining_parent_snapshot'),m.get_object('parent_measurements'),old_slot,v.get_number('parent_placement_task'),v_uid,m.get_object('child_measurements'));
  if dbms_lob.compare(placement_now.to_clob,v.get_object('parent_placement').to_clob)!=0 then raise_application_error(-20890,'CLOSURE_CHANGED: parent placement');end if;
  RRL_STOCK_HU_CMD.execute_command(proxy(p_request),p_actor,unused_result);
  delete from RRL_RECEIPT_SLOT_CLAIM where TASK_ID=old_task and UID_PALLET=v_uid and CELL_SLOT_ID=old_slot and STATUS='OCCUPIED';
  if sql%rowcount!=1 then raise_application_error(-20890,'CLOSURE_CHANGED: parent placement claim');end if;
  RRL_STOCK_HU_PLACEMENT_CORE.record_place(p_request,p_actor,v_uid,ware,cell_name,v.get_number('parent_placement_task'),old_slot,v.get_number('parent_sync'),v.get_object('parent_placement').to_clob);
  RRL_STOCK_HU_PLACEMENT_CORE.record_place(p_request,p_actor,child_uid,ware,cell_name,v.get_number('child_placement_task'),child_slot,v.get_number('child_sync'),v.get_object('child_placement').to_clob,v.get_number('child_case_task_id'));
  children:=v.get_object('child_snapshot').get_array('nodes').to_clob;
  for rr in(select RESERVATION_ID,UID_PALLET,CELL,BASE_QTY from RRL_STOCK_RESERVATION where UID_PALLET in(
   select U from json_table(children,'$[*]' columns(U varchar2(200) path '$.uid',K varchar2(20) path '$.kind')) where K='STOCK')
   and CELL=cell_name and RESERVATION_KIND='HARD' and STATUS in('ACTIVE','ALLOCATED','PICKING') and BASE_QTY>0 order by RESERVATION_ID) loop
   RRL_STOCK_RESERVE_CORE.move_coverage(rr.RESERVATION_ID,rr.RESERVATION_ID,rr.UID_PALLET,rr.CELL,ware,rr.BASE_QTY,child_slot,p_actor,rid);
   if rid!=rr.RESERVATION_ID then raise_application_error(-20869,'HU_UNPACK_RESERVATION_IDENTITY_CHANGED');end if;
  end loop;
  j.put('operation_id',op);j.put('command','HU_UNPACK');j.put('parent',json_object_t.parse(RRL_STOCK_HU_READ.snapshot_json(v_uid)));
  if v.get_number('child_case_task_id') is null then j.put('child',json_object_t.parse(RRL_STOCK_HU_READ.snapshot_json(child_uid)));else j.put('child',json_object_t.parse(RRL_STOCK_HU_READ.case_snapshot_json(v.get_number('child_case_task_id'))));end if;j.put('parent_task_id',v.get_number('parent_placement_task'));j.put('child_task_id',v.get_number('child_placement_task'));j.put('quantity_unchanged',true);
  p_result:=j.to_clob;
 end;
end;
/
