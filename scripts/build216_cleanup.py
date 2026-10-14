from pathlib import Path
import json
s=Path("scripts/cleanup212_case.py").read_text(encoding="utf-8").replace("212","216").replace("ware=31987650","ware=38255845").replace("wave=467","wave=472").replace("case=1113","case=1118").replace("QPB2161E544268","QPB2167DF96570").replace("CASE1113/wave467","CASE1118/wave472")
idx=s.index(' q.execute("select SSCC,CONTENT_VERSION,WARE_ID')
extra=""" from app.modules.platform.public import read_oracle_json
 outer="SMALL216.OUTER:7df96570";inner="SMALL216.HU:7df96570";slots=[(217,"UL216:7df96570:0"),(218,"UL216:7df96570:1"),(219,"UL216:7df96570:2")];cell="CPT_"+str(ware)
 def tree(uid):
  q.execute("select RRL_STOCK_HU_READ.snapshot_json(:p_uid)from dual",p_uid=uid);return read_oracle_json(q.fetchone()[0])
 def measures(version,mass):
  return {"origin":"MANUAL_CONFIRMED","content_version":version,"gross_weight_kg":mass,"width_m":"0.5","depth_m":"0.5","height_m":"0.5"}
 command("HU_UNPACK",{"uid":outer},{"child_uid":inner,"expected_version":tree(outer)["nodes"][0]["version"],"expected_child_version":tree(inner)["nodes"][0]["version"],"scan_container":outer,"scan_child":inner,"scan_cell":cell,"scan_parent_slot":slots[0][1],"scan_child_slot":slots[1][1],"child_slot_id":slots[1][0],"reason":"Own216 explicit native physical unpack","parent_measurements":measures(tree(outer)["nodes"][0]["version"],"1"),"child_measurements":measures(tree(inner)["nodes"][0]["version"],"1.45")})
 q.execute("select SSCC,CONTENT_VERSION from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:p_case",p_case=case);carrier,case_version=q.fetchone()
 command("HU_UNPACK",{"uid":inner},{"child_case_task_id":case,"expected_version":tree(inner)["nodes"][0]["version"],"expected_child_version":int(case_version),"scan_container":inner,"scan_child":carrier,"scan_cell":cell,"scan_parent_slot":slots[1][1],"scan_child_slot":slots[2][1],"child_slot_id":slots[2][0],"reason":"Own216 explicit native CASE unpack","parent_measurements":measures(tree(inner)["nodes"][0]["version"],"1"),"child_measurements":measures(int(case_version),"0.45")})
"""
s=s[:idx]+extra+s[idx:]
s=s.replace(' print("Own216',' q.execute("update RUSERS set DELETED=1 where ID=:p_actor",p_actor="UL2167df96570");c.commit()\n print("Own216',1)
print(json.dumps({"scripts/cleanup216_case.py":s},ensure_ascii=True))
