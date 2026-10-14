from pathlib import Path
import json
out={}
p=Path("db/migrations/2026-10-11_ni042_small_hu/002_gate.sql");s=p.read_text(encoding="utf-8")
start=s.index(" function signature_for_plan(p_domain clob) return varchar2 is");end=s.index(" procedure assert_approved",start)
part=s[start:end]
part=part.replace("v_links number:=0;","v_links number:=0;v_signature_version number;")
part=part.replace("  j.put('version',signature_version_for_plan(p_domain));","  v_signature_version:=signature_version_for_plan(p_domain);j.put('version',v_signature_version);")
part=part.replace("if signature_version_for_plan(p_domain)=3","if v_signature_version=3").replace("if signature_version_for_plan(p_domain)=2","if v_signature_version=2")
s=s[:start]+part+s[end:];out[str(p)]=s
out["db/migrations/2026-10-11_ni042_small_hu/008_finish.sql"]="@@002_gate.sql\n@@003_admission.sql\n@@005_qc.sql\n@@006_archive.sql\n"
s=Path("scripts/ni042_final_qc_case.py").read_text(encoding="utf-8").replace("205","206")
s=s.replace("controller=None","controller=None;parent=None",1)
needle='  controller="QC206"'
pos=s.index(needle)
new="""  parent="SMALL206.HU:"+tag
  q.execute("select CURRENT_CELL from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:p_id",p_id=case);case_cell=q.fetchone()[0]
  post("HU_CREATE",{"uid":parent},{"cell":case_cell,"warehouse":ware,"container_type":"ROLL_CAGE","tare_weight_kg":1,"scan_container":parent,"scan_cell":case_cell})
  def hu_tree():
   q.execute("select RRL_STOCK_HU_READ.snapshot_json(:p_uid)from dual",p_uid=parent);return read_oracle_json(q.fetchone()[0])
  def case_version():
   q.execute("select CONTENT_VERSION from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:p_id",p_id=case);return int(q.fetchone()[0])
  def packing(kind,op):
   return post(kind,{"uid":parent},{"child_case_task_id":int(case),"expected_version":hu_tree()["nodes"][0]["version"],"expected_child_version":case_version(),"scan_container":parent,"scan_child":carrier,"retained_tare_booking_operation_id":book,"reason":"Own206 physical layout"},op)
  # A parent exemption cannot approve an unweighed child; old GROSS command version remains stale.
  packing("HU_ATTACH","SMALL206.UNCONTROLLED.PACK:"+tag)
  assert not quality.status(identifier)["ready"]
  packing("HU_DETACH","SMALL206.UNCONTROLLED.UNPACK:"+tag)
  assert not quality.status(identifier)["ready"]
  new_packet=final_packet("FINAL_GROSS","0.400",case_version(),tare_capture["capture_key"]);new_packet["capture_id"]="GROSS.AFTER.LAYOUT206:"+tag
  final_capture=scale_call(new_packet)
  assert final_capture["composition_signature_version"]==3
  before=quality.status(identifier)
"""
s=s[:pos]+new+s[pos:]
# Outer QC rollback restores WAIT_CONTROL, current version is read by producer metadata.
needle='  print("PASS206 own small type/'
pos=s.index(needle)
new="""  signature=quality.status(identifier)["composition_signature"]
  before_layout_version=case_version()
  packing("HU_ATTACH","SMALL206.CONTROLLED.PACK:"+tag)
  controlled=quality.status(identifier);assert controlled["ready"]and controlled["composition_signature"]==signature
  assert case_version()>before_layout_version
  current_tree=hu_tree();body={"expected_version":current_tree["nodes"][0]["version"],"scan_container":parent,"scan_from_cell":current_tree["cell"],"scan_to_cell":storage,"target_cell":storage}
  post("HU_MOVE",{"uid":parent},body,"SMALL206.WHOLE.MOVE:"+tag)
  controlled=quality.status(identifier);assert controlled["ready"]and controlled["composition_signature"]==signature
  packing("HU_DETACH","SMALL206.CONTROLLED.UNPACK:"+tag)
  controlled=quality.status(identifier);assert controlled["ready"]and controlled["composition_signature"]==signature
  q.execute("select SIGNATURE_VERSION from RRL_WH_FINAL_SCALE_USE where STOCK_OPERATION_ID=:p_op",p_op=check["operation_id"]);assert q.fetchone()[0]==3
  q.execute("select h.LOT_UID,r.CELL,r.BASE_UOM,r.STOCK_VERSION from RRL_CASE_CARRIER_LOT h join RRL_REMAINS r on r.UID_POLETA=h.LOT_UID and r.REMAIN>0 where h.CASE_PICK_TASK_ID=:p_case",p_case=case)
  child_uid,child_cell,child_uom,child_stock_version=q.fetchone()
  for amount in ("7","6"):
   q.execute("select STOCK_VERSION from RRL_REMAINS where UID_POLETA=:p_uid and CELL=:p_cell",p_uid=child_uid,p_cell=child_cell);version_count=int(q.fetchone()[0])
   post("INVENTORY_COUNT",{"revision_id":revision},{"reason":"Own206 epoch7 then6","counts":[{"uid":child_uid,"cell":child_cell,"article":article,"unit":child_uom,"quantity":amount,"expected_stock_version":version_count,"unit_keys":[]}]})
  revoked=quality.status(identifier);assert not revoked["ready"]and revoked["composition_signature"]!=signature
  q.execute("select STATUS from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:p_id",p_id=case);assert q.fetchone()[0]=="WAIT_CONTROL"
  print("PASS206 unweighed child stays blocked under exempt parent/measured v3 cargo control retained through pack/whole move/unpack/operational version increased/real7then6 correction revokes old proof",article,parent,flush=True)
"""
s=s[:pos]+new+s[pos:]
needle='  if wave is not None:\n   q.execute("select CASE_PICK_TASK_ID'
pos=s.index(needle,s.index(" finally:"))
new="""  if parent is not None:
   q.execute("select CHILD_CASE_TASK_ID from RRL_WMS_HU_LINK where PARENT_UID=:p_uid and ACTIVE_FLAG=1",p_uid=parent)
   for (nested_case,)in q.fetchall():
    packing("HU_DETACH","SMALL206.CLEANUP.UNPACK:"+tag)
"""
s=s[:pos]+new+s[pos:]
out["scripts/ni042_small_hu_control_case.py"]=s
print(json.dumps(out,ensure_ascii=True))
