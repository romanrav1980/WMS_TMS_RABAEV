from pathlib import Path
import json
f=Path("db/migrations/2026-10-11_ni052_unload_slot");out={}
out["wiki/database/nicora_ni052_unload_slot_design_20261011.md"]="""# NI05.2: выгрузка с фактически занятым слотом
215 extends214/NS45 with existing RRL_STOCK_HU_SLOT.target_json and RRL_STOCK_HU_PLACEMENT_CORE.record_place; no duplicate capacity/placement logic. Optional target_slot_id/scanned_to_slot_code; slotted current original cell requires explicit scan. Original load canonical mass/dimensions archived unchanged, restored exact composition changes only monotonically increasing epochs/QC state. SLOT40 plus CELL_X fence/current topology/placement task-sync-claim ownership declared before all effects; former balance/reserve owners retained. Existing target_json rechecks capacity/occupied/reserved/planned arrival/current topology/temp/location at execution; late refusal rolls back unload completely. Native record_place creates actual DONE PUTAWAY/SYNCED/OCCUPIED measured owner fact, new HARD coverage same selected slot. API excludes null fields to preserve prior request/replay identity. Unload rights authorize scoped physical reversal/placement, no independent general move endpoint rights granted. Recovery forward repair with actual placement history.
"""
for stem,sql in [("slot","001_slot.sql"),("placement","002_placement.sql")]:
 s=(f/("000_before_"+stem+".sql")).read_text(encoding="utf-8").replace("accessible by(","accessible by(package RRL_STOCK_UNLOAD_CMD,",1)
 out[str(f/sql)]=s
s=(f/"000_before_unload.sql").read_text(encoding="utf-8")
s=s.replace("if n>0 then raise_application_error(-20886,'UNLOAD_STORAGE_SLOT_PLACEMENT_REQUIRED');end if;","if n>0 and p_metadata.get_number('target_slot_id')is null then raise_application_error(-20886,'UNLOAD_STORAGE_SLOT_PLACEMENT_REQUIRED');end if;")
s=s.replace("new_link number;\n begin","new_link number;target_slot number;placement_task number;placement_sync number;request_wire clob;original_measures json_object_t;slot_code varchar2(100);\n begin",1)
anchor="  for i in 0..legs.get_size-1 loop"
idx=s.index(anchor)
insert="""  target_slot:=m.get_number('target_slot_id');
  if target_slot is not null then
   if target_slot<1 or target_slot!=trunc(target_slot)or m.get_string('scanned_to_slot_code')is null then raise_application_error(-20886,'UNLOAD_SLOT_SCAN_REQUIRED');end if;
   select sl.SLOT_CODE into slot_code from RRL_TOPOLOGY_CELL_SLOT sl join RRL_TOPOLOGY_CELL tc on tc.TOPOLOGY_CELL_ID=sl.TOPOLOGY_CELL_ID
    where sl.CELL_SLOT_ID=target_slot and sl.ACTIVE=1 and sl.SLOT_KIND='STORAGE_SLOT'and tc.ACTIVE=1 and tc.LEGACY_CELL_CODE=m.get_string('scan_cell')and tc.WARE_ID=lf.WARE_ID;
   if slot_code!=m.get_string('scanned_to_slot_code')then raise_application_error(-20886,'UNLOAD_SLOT_SCAN_REQUIRED');end if;
   select CANONICAL_REQUEST into request_wire from RRL_STOCK_OPERATION where OPERATION_ID=load_id;
   original_measures:=json_object_t.parse(request_wire).get_object('metadata').get_object('loading_context').get_object('measurements');
   RRL_STOCK_PLAN_HELPER.fence(f,'CELL',m.get_string('scan_cell'),6);
   RRL_STOCK_PLAN_HELPER.anchor(r,40,'SLOT',RRL_STOCK_PLAN_HELPER.decimal_text(target_slot));
   placement_task:=RRL_WAREHOUSE_TASK_SQ.nextval;placement_sync:=RRL_WH_TASK_SYNC_SQ.nextval;
   RRL_STOCK_HU_PLACEMENT_CORE.declare_place(r,placement_task,placement_sync);
   v.put('placement_slot',target_slot);v.put('placement_task',placement_task);v.put('placement_sync',placement_sync);v.put('original_measures',original_measures);
  elsif m.get_string('scanned_to_slot_code')is not null then raise_application_error(-20886,'UNLOAD_SLOT_SCAN_REQUIRED');end if;
"""
# Scalars for PL JSON SQL operands.
insert=insert.replace("   select sl.SLOT_CODE","   cell_text:=m.get_string('scan_cell');select sl.SLOT_CODE").replace("tc.LEGACY_CELL_CODE=m.get_string('scan_cell')","tc.LEGACY_CELL_CODE=cell_text")
insert=insert.replace("cell_textand","cell_text and")
s=s[:idx]+insert+s[idx:]
s=s.replace("parent_uid varchar2(150);j json_object_t","parent_uid varchar2(150);placement_metadata json_object_t;placement_tree json_object_t;measures json_object_t;placement_wire clob;placement_root varchar2(150);new_coverage number;j json_object_t",1)
anchor="  insert into RRL_TT_UNLOAD_FACT"
idx=s.index(anchor)
insert="""  if v.get_number('placement_slot')is not null then
   placement_root:=nvl(lf.ROOT_UID,'CASE:'||RRL_STOCK_PLAN_HELPER.decimal_text(lf.ROOT_CASE_TASK_ID));
   if lf.ROOT_CASE_TASK_ID is null then placement_tree:=json_object_t.parse(RRL_STOCK_HU_READ.snapshot_json(placement_root));
   else placement_tree:=json_object_t.parse(RRL_STOCK_HU_READ.case_snapshot_json(lf.ROOT_CASE_TASK_ID));end if;
   measures:=v.get_object('original_measures').clone();measures.put('content_version',treat(placement_tree.get_array('nodes').get(0)as json_object_t).get_number('version'));
   placement_metadata:=m.clone();placement_metadata.put('target_cell',cell_text);placement_metadata.put('planned_physical_task_id',v.get_number('placement_task'));placement_metadata.put('measurements',measures);
   placement_wire:=RRL_STOCK_HU_SLOT.target_json(placement_tree.to_clob,placement_metadata.to_clob,null,placement_root);
   RRL_STOCK_HU_PLACEMENT_CORE.record_place(p_request,p_actor,placement_root,ware,cell_text,v.get_number('placement_task'),v.get_number('placement_slot'),v.get_number('placement_sync'),placement_wire,lf.ROOT_CASE_TASK_ID);
   for leg_index in 0..a.get_size-1 loop
    x:=treat(a.get(leg_index)as json_object_t);qty:=RRL_STOCK_MATH.quantity(x.get_string('quantity'));new_id:=x.get_number('new_reservation');
    RRL_STOCK_RESERVE_CORE.move_coverage(new_id,new_id,x.get_string('uid'),cell_text,ware,qty,v.get_number('placement_slot'),p_actor,new_coverage);
    if new_coverage!=new_id then raise_application_error(-20869,'UNLOAD_RESERVATION_IDENTITY_CHANGED');end if;
   end loop;
   j.put('placement_task',v.get_number('placement_task'));j.put('placement_slot',v.get_number('placement_slot'));
  end if;
"""
s=s[:idx]+insert+s[idx:]
out[str(f/"003_unload.sql")]=s
for stem,sql,var in [("rrl_hu_task_plan_guard","004_task_guard.sql","v_kind"),("rrl_hu_claim_measure_guard","005_claim_guard.sql","kind")]:
 s=(f/("000_before_"+stem+".sql")).read_text(encoding="utf-8")
 s=s.replace("'HU_RELOCATE_SLOT','HU_REPACK_SLOT'","'HU_RELOCATE_SLOT','HU_REPACK_SLOT','UNLOAD_SHIPMENT'")
 # Exact authoritative placement-plan proof before original row-lock/measurement validations.
 anchor="  RRL_STOCK_LOCK_API.assert_held(20"if var=="v_kind"else" if :new.HU_CASE_TASK_ID is not null then"
 idx=s.index(anchor)
 taskfield="TASK_ID"
 insert=f""" if {var}='UNLOAD_SHIPMENT'then
  declare wire clob;state_name varchar2(20);domain_json json_object_t;expected_uid varchar2(150);begin
   select STATE,RESOLVED_PLAN_JSON into state_name,wire from RRL_STOCK_OPERATION where OPERATION_ID=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID');
   domain_json:=json_object_t.parse(wire).get_object('domain');expected_uid:=nvl(domain_json.get_string('root_uid'),'CASE:'||RRL_STOCK_PLAN_HELPER.decimal_text(domain_json.get_number('case_id')));
   if state_name!='IN_FLIGHT'or domain_json.get_number('placement_task')is null or domain_json.get_number('placement_task')!=:new.TASK_ID or domain_json.get_number('placement_slot')is null or domain_json.get_number('placement_slot')!=:new.{('TO_CELL_SLOT_ID'if var=='v_kind'else'CELL_SLOT_ID')} or expected_uid!=:new.UID_PALLET then raise_application_error(-20863,'UNLOAD_EXACT_PLACEMENT_PLAN_REQUIRED');end if;
  end;
 end if;
"""
 s=s[:idx]+insert+s[idx:];out[str(f/sql)]=s
out[str(f/"apply.sql")]="".join("@@"+name+"\n"for name in ["001_slot.sql","002_placement.sql","003_unload.sql","004_task_guard.sql","005_claim_guard.sql"])
out[str(f/"rollback.sql")]="""declare n number;begin select count(*)into n from RRL_STOCK_OPERATION where COMMAND_TYPE='UNLOAD_SHIPMENT'and STATE='APPLIED'and json_exists(RESOLVED_PLAN_JSON,'$.domain.placement_task');if n>0 then raise_application_error(-20863,'UNLOAD_PLACEMENT_HISTORY_FORWARD_REPAIR_REQUIRED');end if;end;
/
@@000_before_unload.sql
@@000_before_rrl_hu_task_plan_guard.sql
@@000_before_rrl_hu_claim_measure_guard.sql
@@000_before_slot.sql
@@000_before_placement.sql
"""
p=Path("api/wms_api_server/app/modules/transport/api/unloading_routes.py");s=p.read_text(encoding="utf-8").replace("    reason: str = Field","    target_slot_id: int | None = Field(default=None, strict=True, ge=1)\n    scanned_to_slot_code: str | None = Field(default=None, strict=True, min_length=1, max_length=100)\n    reason: str = Field").replace('body.model_dump(exclude={"operation_id", "load_operation_id"})','body.model_dump(exclude={"operation_id", "load_operation_id"}, exclude_none=True)')
out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))

