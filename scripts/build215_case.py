from pathlib import Path
import json
s=Path("scripts/ni052_whole_hu_unload_case.py").read_text(encoding="utf-8").replace("214","215")
anchor='  unloader="UL215"'
idx=s.index(anchor)
extra="""  topo=seq("RRL_WH_TOPOLOGY_SQ");topocell=seq("RRL_TOPOLOGY_CELL_SQ");slots=[]
  meta("insert into RRL_WAREHOUSE_TOPOLOGY(TOPOLOGY_ID,WARE_ID,TOPOLOGY_CODE,STATUS)values(:p_id,:p_ware,:p_code,'PUBLISHED')",p_id=topo,p_ware=ware,p_code="UNLOAD215:"+tag)
  meta("insert into RRL_TOPOLOGY_CELL(TOPOLOGY_CELL_ID,TOPOLOGY_ID,WARE_ID,CELL_CODE,LEGACY_CELL_CODE,SLOT_LAYER_KIND,MAX_WEIGHT_KG,MAX_VOLUME_M3)values(:p_id,:p_topo,:p_ware,:p_cell,:p_cell,'STORAGE_SLOT',100,4)",p_id=topocell,p_topo=topo,p_ware=ware,p_cell=case_cell)
  for slot_index in range(3):
   slot_id=seq("RRL_TOPO_CELL_SLOT_SQ");slot_code="UL215:"+tag+":"+str(slot_index)
   meta("insert into RRL_TOPOLOGY_CELL_SLOT(CELL_SLOT_ID,TOPOLOGY_ID,TOPOLOGY_CELL_ID,PARENT_SLOT_LAYER_KIND,SLOT_KIND,SLOT_CODE,CAPACITY_QTY,CAPACITY_WEIGHT_KG,CAPACITY_VOLUME_M3,WIDTH_M,DEPTH_M,HEIGHT_M,SUB_COLUMN_NO)values(:p_id,:p_topo,:p_cell,'STORAGE_SLOT','STORAGE_SLOT',:p_code,1,100,3,1.2,1.2,2,:p_index)",p_id=slot_id,p_topo=topo,p_cell=topocell,p_code=slot_code,p_index=slot_index+1);slots.append((slot_id,slot_code))
"""
s=s[:idx]+extra+s[idx:]
s=s.replace('"reason":"Own215 physically unloaded before departure"}','"reason":"Own215 physically unloaded before departure","target_slot_id":slots[0][0],"scanned_to_slot_code":slots[0][1]}')
anchor='  canonical=StockCommand(operation_id=body["operation_id"],command_type="UNLOAD_SHIPMENT"'
idx=s.index(anchor)
extra="""  no_slot={k:v for k,v in body.items()if k not in("target_slot_id","scanned_to_slot_code")}
  assert unloading.post(base+uri,json=no_slot).status_code==409
  meta("update RRL_TOPOLOGY_CELL_SLOT set CAPACITY_WEIGHT_KG=1 where CELL_SLOT_ID=:p_slot",p_slot=slots[0][0])
  late=unloading.post(base+uri,json=body);assert late.status_code==409 and "HU_SLOT_WEIGHT_VOLUME_OR_DIMENSIONS_EXCEEDED"in late.text,(late.status_code,late.text[:1700])
  q.execute("select count(*)from RRL_TT_UNLOAD_FACT where LOAD_OPERATION_ID=:p_load",p_load=load_id);assert q.fetchone()[0]==0
  q.execute("select count(*)from RRL_RECEIPT_SLOT_CLAIM where CELL_SLOT_ID=:p_slot",p_slot=slots[0][0]);assert q.fetchone()[0]==0
  meta("update RRL_TOPOLOGY_CELL_SLOT set CAPACITY_WEIGHT_KG=100 where CELL_SLOT_ID=:p_slot",p_slot=slots[0][0])
"""
s=s[:idx]+extra+s[idx:]
anchor='  assert not quality.status(identifier)["ready"]'
idx=s.rfind(anchor)
extra="""
  q.execute("select TASK_ID,UID_PALLET,HU_GROSS_WEIGHT_KG,HU_BOUNDING_VOLUME_M3 from RRL_RECEIPT_SLOT_CLAIM where CELL_SLOT_ID=:p_slot and STATUS='OCCUPIED'",p_slot=slots[0][0]);placed=q.fetchone();assert placed[1]==outer and Decimal(str(placed[2]))==Decimal("2.45")and Decimal(str(placed[3]))==Decimal(".125")
  q.execute("select STATUS from RRL_WAREHOUSE_TASK where TASK_ID=:p_task",p_task=placed[0]);assert q.fetchone()[0]=="DONE"
  q.execute("select SYNC_STATUS from RRL_WAREHOUSE_TASK_SYNC where TASK_ID=:p_task",p_task=placed[0]);assert q.fetchone()[0]=="SYNCED"
  q.execute("select distinct CELL_SLOT_ID from RRL_STOCK_RESERVATION where SOURCE_DOC_TYPE='PICK_WAVE'and SOURCE_DOC_ID=:p_wave and BASE_QTY>0",p_wave=wave);assert q.fetchall()==[(slots[0][0],)]
  print("PASS215 original2.45kg/.125m3 real occupied slot/actual DONE PUTAWAY/SYNCED/same HARD owner slot/late capacity refusal restores complete original load",flush=True)
"""
s=s[:idx]+s[idx:].replace(anchor,anchor+extra,1)
start=s.index('  if "outer"in locals()and not shipped:')
end=s.index("  if wave is not None and not shipped:",start)
cleanup="""  def measures(version,mass):
   return {"origin":"MANUAL_CONFIRMED","content_version":version,"gross_weight_kg":mass,"width_m":"0.5","depth_m":"0.5","height_m":"0.5"}
  if "slots"in locals()and not shipped:
   if any(e.get("child")==inner for e in tree_for(outer)["links"]):
    post("HU_UNPACK",{"uid":outer},{"child_uid":inner,"expected_version":tree_for(outer)["nodes"][0]["version"],"expected_child_version":tree_for(inner)["nodes"][0]["version"],"scan_container":outer,"scan_child":inner,"scan_cell":case_cell,"scan_parent_slot":slots[0][1],"scan_child_slot":slots[1][1],"child_slot_id":slots[1][0],"reason":"Own215 explicit native physical unpack","parent_measurements":measures(tree_for(outer)["nodes"][0]["version"],"1"),"child_measurements":measures(tree_for(inner)["nodes"][0]["version"],"1.45")})
   if any(e.get("child")=="CASE:"+str(case)for e in tree_for(inner)["links"]):
    post("HU_UNPACK",{"uid":inner},{"child_case_task_id":case,"expected_version":tree_for(inner)["nodes"][0]["version"],"expected_child_version":case_version(),"scan_container":inner,"scan_child":carrier,"scan_cell":case_cell,"scan_parent_slot":slots[1][1],"scan_child_slot":slots[2][1],"child_slot_id":slots[2][0],"reason":"Own215 explicit native CASE unpack","parent_measurements":measures(tree_for(inner)["nodes"][0]["version"],"1"),"child_measurements":measures(case_version(),"0.45")})
  elif parent is not None and not shipped:
   q.execute("select CHILD_CASE_TASK_ID from RRL_WMS_HU_LINK where PARENT_UID=:p_uid and ACTIVE_FLAG=1",p_uid=parent)
   for(nested_case,)in q.fetchall():packing("HU_DETACH","SMALL215.CLEANUP.UNPACK:"+tag)
"""
s=s[:start]+cleanup+s[end:]
print(json.dumps({"scripts/ni052_slotted_hu_unload_case.py":s},ensure_ascii=True))
