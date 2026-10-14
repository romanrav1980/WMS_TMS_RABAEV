from pathlib import Path
import json
s=Path("scripts/cleanup212_case.py").read_text(encoding="utf-8").replace("212","214").replace("ware=31987650","ware=42987529").replace("wave=467","wave=470").replace("case=1113","case=1116").replace("QPB2141E544268","QPB214C62C896A").replace("CASE1113/wave467","CASE1116/wave470")
anchor=' q.execute("select SSCC,CONTENT_VERSION,WARE_ID'
idx=s.index(anchor)
extra=""" from app.json_wire import read_oracle_json
 outer="SMALL214.OUTER:c62c896a";inner="SMALL214.HU:c62c896a"
 def tree(uid):
  q.execute("select RRL_STOCK_HU_READ.snapshot_json(:p_uid)from dual",p_uid=uid);return read_oracle_json(q.fetchone()[0])
 command("HU_DETACH",{"uid":outer},{"child_uid":inner,"expected_version":tree(outer)["nodes"][0]["version"],"expected_child_version":tree(inner)["nodes"][0]["version"],"scan_container":outer,"scan_child":inner,"reason":"Own214 native outer unpack"})
 q.execute("select SSCC,CONTENT_VERSION from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:p_case",p_case=case);carrier,case_version=q.fetchone()
 command("HU_DETACH",{"uid":inner},{"child_case_task_id":case,"expected_version":tree(inner)["nodes"][0]["version"],"expected_child_version":int(case_version),"scan_container":inner,"scan_child":carrier,"reason":"Own214 native CASE unpack"})
"""
# Use the established json decoder import, avoid guessing module.
extra=extra.replace("from app.json_wire import read_oracle_json","from app.modules.inventory.infrastructure.oracle_json import read_oracle_json")
s=s[:idx]+extra+s[idx:]
s=s.replace(' print("Own214',' q.execute("update RUSERS set DELETED=1 where ID=:p_actor",p_actor="UL214c62c896a");c.commit()\n print("Own214',1)
print(json.dumps({"scripts/cleanup214_case.py":s},ensure_ascii=True))
