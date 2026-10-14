from pathlib import Path
import json
s=Path("scripts/ni052_marked_case_unload_case.py").read_text(encoding="utf-8").replace("213","214")
start=s.index('  packing("HU_DETACH","SMALL214.STANDALONE:');end=s.index('  q.execute("select sum(r.REMAIN)',start)
replacement="""  inner=parent;outer="SMALL214.OUTER:"+tag
  post("HU_CREATE",{"uid":outer},{"cell":case_cell,"warehouse":ware,"container_type":"ROLL_CAGE","tare_weight_kg":1,"scan_container":outer,"scan_cell":case_cell})
  def tree_for(uid):
   q.execute("select RRL_STOCK_HU_READ.snapshot_json(:p_uid)from dual",p_uid=uid);return read_oracle_json(q.fetchone()[0])
  post("HU_ATTACH",{"uid":outer},{"child_uid":inner,"expected_version":tree_for(outer)["nodes"][0]["version"],"expected_child_version":tree_for(inner)["nodes"][0]["version"],"scan_container":outer,"scan_child":inner,"reason":"Own214 whole two-level matryoshka"})
  tree=tree_for(outer);load_version=tree["nodes"][0]["version"]
  assert len([n for n in tree["nodes"]if n["kind"]=="CONTAINER"])==2
  metadata={"expected_version":load_version,"scan_container":outer,"scan_cell":tree["cell"],"loading_context":{"transport_task_id":trip,"scan_vehicle":plate,"scan_dock":dock,"measurements":{"origin":"MANUAL_CONFIRMED","content_version":load_version,"gross_weight_kg":"2.45","width_m":"0.5","depth_m":"0.5","height_m":"0.5"}}}
  load_id="SMALL214.LOAD:"+tag
  actual=post("HU_SHIP",{"uid":outer},metadata,load_id);shipped=True
  assert post("HU_SHIP",{"uid":outer},metadata,load_id)==actual
  # The scan is the outer physical pallet identifier; quantity is server-owned.
  unload_scan=outer
"""
s=s[:start]+replacement+s[end:]
s=s.replace('"scan_container":carrier,"scan_cell":tree["cell"],"scan_vehicle":plate','"scan_container":unload_scan,"scan_cell":tree["cell"],"scan_vehicle":plate')
needle='  assert not quality.status(identifier)["ready"]'
extra="""
  restored=tree_for(outer)
  assert len([n for n in restored["nodes"]if n["kind"]=="CONTAINER"])==2
  assert len([n for n in restored["nodes"]if n["kind"]=="CASE"])==1
  assert len([edge for edge in restored["links"]if edge.get("id")is not None])==2
  q.execute("select count(*)from RRL_WMS_HU_LINK where UNLINKED_OPERATION_ID=:p_load and ACTIVE_FLAG=0",p_load=load_id);assert q.fetchone()[0]==2
  q.execute("select count(*)from RRL_WMS_HU_LINK where LINKED_OPERATION_ID=:p_op and ACTIVE_FLAG=1",p_op=body["operation_id"]);assert q.fetchone()[0]==2
  print("PASS214 two-level containers/same original CASE7+14 codes/new links2/old links2 kept/all P-H restored/no partial child unload",outer,flush=True)
"""
# needle occurs once after actual unloading.
i=s.rfind(needle);assert i>0;s=s[:i]+s[i:].replace(needle,needle+extra,1)
cleanup=' finally:\n  if parent is not None and not shipped:'
s=s.replace(cleanup,' finally:\n  if "outer"in locals()and not shipped:\n   if any(e.get("child")==inner for e in tree_for(outer)["links"]):\n    post("HU_DETACH",{"uid":outer},{"child_uid":inner,"expected_version":tree_for(outer)["nodes"][0]["version"],"expected_child_version":tree_for(inner)["nodes"][0]["version"],"scan_container":outer,"scan_child":inner,"reason":"Own214 native cleanup outer"})\n  if parent is not None and not shipped:')
print(json.dumps({"scripts/ni052_whole_hu_unload_case.py":s},ensure_ascii=True))

