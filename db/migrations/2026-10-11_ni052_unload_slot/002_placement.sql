create or replace package RRL_STOCK_HU_PLACEMENT_CORE authid definer
 accessible by(package RRL_STOCK_UNLOAD_CMD,package RRL_STOCK_HU_UNPACK_CMD,package RRL_STOCK_HU_SLOT_MOVE_CMD,package RRL_STOCK_CASE_MOVE_CMD,package RRL_STOCK_CASE_RETURN_CMD,package RRL_STOCK_SHIPPING_CORE,package RRL_STOCK_HU_REPACK_CMD) as
 procedure declare_existing_case(r in out nocopy json_array_t,p_case number);
 procedure release_case(p_case number,p_cell varchar2);
 procedure declare_place(r in out nocopy json_array_t,p_task number,p_sync number);
 procedure record_place(p_request clob,p_actor varchar2,p_uid varchar2,p_warehouse number,p_cell varchar2,p_task number,p_slot number,p_sync number,p_placement clob,p_case_task number default null);
end;
/

create or replace package body RRL_STOCK_HU_PLACEMENT_CORE as
 function sync_key(p_task number) return varchar2 is begin return 'WT:'||RRL_STOCK_PLAN_HELPER.decimal_text(p_task)||':MANUAL:PUTAWAY:'||RRL_STOCK_PLAN_HELPER.decimal_text(p_task)||':';end;
 procedure declare_place(r in out nocopy json_array_t,p_task number,p_sync number) is
 begin
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_WAREHOUSE_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(p_task));
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_RECEIPT_SLOT_CLAIM',RRL_STOCK_PLAN_HELPER.decimal_text(p_task));
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_WAREHOUSE_TASK_SYNC',RRL_STOCK_PLAN_HELPER.decimal_text(p_sync));
  RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','TASK.SYNC:'||sync_key(p_task));
 end;
 procedure declare_existing_case(r in out nocopy json_array_t,p_case number) is
 begin
  for cl in(select TASK_ID,CELL_SLOT_ID from RRL_RECEIPT_SLOT_CLAIM where HU_CASE_TASK_ID=p_case and STATUS in('RESERVED','OCCUPIED') order by TASK_ID) loop
   RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_RECEIPT_SLOT_CLAIM',RRL_STOCK_PLAN_HELPER.decimal_text(cl.TASK_ID));
   RRL_STOCK_PLAN_HELPER.anchor(r,40,'SLOT',RRL_STOCK_PLAN_HELPER.decimal_text(cl.CELL_SLOT_ID));
  end loop;
 end;
 procedure release_case(p_case number,p_cell varchar2) is
 begin
  for cl in(select TASK_ID,CELL_SLOT_ID from RRL_RECEIPT_SLOT_CLAIM where HU_CASE_TASK_ID=p_case and CELL=p_cell and STATUS='OCCUPIED') loop
   RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_RECEIPT_SLOT_CLAIM',RRL_STOCK_PLAN_HELPER.decimal_text(cl.TASK_ID)));
   RRL_STOCK_LOCK_API.assert_held(40,RRL_STOCK_LOCK_API.resource_key('SLOT',RRL_STOCK_PLAN_HELPER.decimal_text(cl.CELL_SLOT_ID)));
   delete from RRL_RECEIPT_SLOT_CLAIM where TASK_ID=cl.TASK_ID and HU_CASE_TASK_ID=p_case;
  end loop;
 end;
 procedure record_place(p_request clob,p_actor varchar2,p_uid varchar2,p_warehouse number,p_cell varchar2,p_task number,p_slot number,p_sync number,p_placement clob,p_case_task number default null) is
  placement_json json_object_t:=json_object_t.parse(p_placement);measures json_object_t;version_no number;mass_no number;volume_no number;measurement_json clob;completion_hash varchar2(64);key_text varchar2(255);kind_name varchar2(20);stock_version number;physical_version number;unit_sig varchar2(64);unit_count number;actual_cell varchar2(60);
 begin
  RRL_STOCK_LOCK_API.assert_held(30,RRL_STOCK_LOCK_API.resource_key('HU',p_uid));
  RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_WAREHOUSE_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(p_task)));
  RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_RECEIPT_SLOT_CLAIM',RRL_STOCK_PLAN_HELPER.decimal_text(p_task)));
  RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_WAREHOUSE_TASK_SYNC',RRL_STOCK_PLAN_HELPER.decimal_text(p_sync)));
  RRL_STOCK_LOCK_API.assert_held(40,RRL_STOCK_LOCK_API.resource_key('SLOT',RRL_STOCK_PLAN_HELPER.decimal_text(p_slot)));
  if p_case_task is not null then
   if p_uid!='CASE:'||RRL_STOCK_PLAN_HELPER.decimal_text(p_case_task) then raise_application_error(-20886,'PLACEMENT_CASE_IDENTITY_CONFLICT');end if;
   select CONTENT_VERSION,CURRENT_CELL into version_no,actual_cell from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=p_case_task and STATUS in('WAIT_CONTROL','CONTROL_IN_PROGRESS','CONTROLLED','READY_TO_SHIP');
   RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_CASE_PICK_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(p_case_task)));
   if actual_cell is null or actual_cell!=p_cell then raise_application_error(-20890,'PLACEMENT_CASE_CELL_CHANGED');end if;
  else
  select HU_CONTENT_VERSION,HU_KIND,STOCK_COMPOSITION_VERSION,HU_CURRENT_CELL into version_no,kind_name,stock_version,actual_cell from RRL_PALLETS where UID_PALLET=p_uid and HU_SHIPPED_OPERATION is null;
  if kind_name='CONTAINER' then
   if actual_cell is null or actual_cell!=p_cell then raise_application_error(-20890,'PLACEMENT_CONTAINER_CELL_CHANGED');end if;
   stock_version:=null;
  elsif kind_name='STOCK' then
   RRL_STOCK_LOCK_API.assert_held(50,RRL_STOCK_LOCK_API.resource_key('STOCK',p_uid));
   select PHYSICAL_VERSION into physical_version from RRL_REMAINS where UID_POLETA=p_uid and CELL=p_cell and REMAIN>0;
   RRL_STOCK_HU_UNIT_SIGNATURE.describe_units(p_uid,null,unit_sig,unit_count);
  else raise_application_error(-20886,'PLACEMENT_OWNER_KIND_INVALID');end if;
  end if;
  measures:=placement_json.get_object('measurements');mass_no:=RRL_STOCK_MATH.quantity(measures.get_string('gross_weight_kg'));volume_no:=RRL_STOCK_MATH.quantity(measures.get_string('bounding_volume_m3'));
  measures.put('content_version',version_no);measurement_json:=measures.to_clob;completion_hash:=rawtohex(sys.dbms_crypto.hash(p_request,sys.dbms_crypto.hash_sh256));
  insert into RRL_WAREHOUSE_TASK(TASK_ID,TASK_TYPE,TASK_SOURCE,SOURCE_TASK_ID,SOURCE_DOC_TYPE,UID_PALLET,FROM_WARE_ID,FROM_CELL,TO_WARE_ID,TO_CELL,QTY,FACT_QTY,UNIT_CODE,QTY_MODE,STATUS,CREATED_BY,ASSIGNED_TO,FINISHED_AT,HU_CONTENT_VERSION,TO_CELL_SLOT_ID,HU_MEASUREMENTS_JSON,COMPLETION_HASH,COMPLETION_JSON)
   values(p_task,'PUTAWAY','MANUAL',p_task,'WAREHOUSE_HU',p_uid,p_warehouse,p_cell,p_warehouse,p_cell,1,1,'HU','PALLET','DONE',p_actor,p_actor,systimestamp,version_no,p_slot,measurement_json,completion_hash,p_request);
  insert into RRL_RECEIPT_SLOT_CLAIM(TASK_ID,UID_PALLET,CELL,CELL_SLOT_ID,STATUS,HU_GROSS_WEIGHT_KG,HU_BOUNDING_VOLUME_M3,HU_COMPOSITION_VERSION,HU_STOCK_COMPOSITION_VERSION,HU_PHYSICAL_VERSION,HU_UNIT_SIGNATURE,HU_CASE_TASK_ID)
   values(p_task,p_uid,p_cell,p_slot,'OCCUPIED',mass_no,volume_no,version_no,stock_version,physical_version,unit_sig,p_case_task);
  key_text:=sync_key(p_task);
  insert into RRL_WAREHOUSE_TASK_SYNC(SYNC_ID,TASK_ID,TASK_SOURCE,TASK_TYPE,SOURCE_DOC_TYPE,SOURCE_TASK_ID,SYNC_KEY,SYNC_STATUS,SYNC_ATTEMPT,CREATED_AT,UPDATED_AT,SYNCED_AT,UPDATED_BY)
   values(p_sync,p_task,'MANUAL','PUTAWAY','WAREHOUSE_HU',p_task,key_text,'SYNCED',1,systimestamp,systimestamp,systimestamp,p_actor);
 end;
end;
/
