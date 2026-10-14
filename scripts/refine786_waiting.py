from pathlib import Path
import json
out={}
p=Path("db/migrations/2026-10-13_ni072_waiting_tasks/007_task_plan.sql");t=p.read_text(encoding="utf-8")
assert "fence(v_p,'CONFIG','WAREHOUSE',6)" in t
out[str(p)]=t.replace("fence(v_p,'CONFIG','WAREHOUSE',6)","fence(v_p,'CONFIG','WAREHOUSE')")
p=Path("db/migrations/2026-10-13_ni072_waiting_tasks/003_core.sql");t=p.read_text(encoding="utf-8")
for field,default in (("SOURCE_DOC_ID","-1"),("SOURCE_TASK_ID","-1"),("FROM_WARE_ID","-1"),("TO_WARE_ID","-1"),("QTY","-1")):
 t=t.replace("p_task."+field+"!=","nvl(p_task."+field+","+default+")!=")
for field in ("TASK_SOURCE","SOURCE_DOC_TYPE","TASK_TYPE","UID_PALLET","FROM_CELL","TO_CELL","UNIT_CODE","QTY_MODE"):
 t=t.replace("p_task."+field+"!=","nvl(p_task."+field+",'~')!=")
out[str(p)]=t
p=Path("wiki-raw/wms_admin_ui_reference/st-deferral.js");t=p.read_text(encoding="utf-8")
old="el('sdSave').disabled=busy||!context||!!p;"
new="const target=Number(el('sdTarget').value),valid=Number.isSafeInteger(target)&&target>0&&el('sdReason').value.trim().length>=8&&el('sdReference').value.trim().length>=8;el('sdSave').disabled=busy||!context||!!p||!valid;for(const id of ['sdTarget','sdReason','sdReference'])el(id).disabled=busy||!!p;"
assert old in t;t=t.replace(old,new)
anchor=" window.addEventListener('wms-admin-auth-ready'"
assert anchor in t
t=t.replace(anchor," for(const id of ['sdTarget','sdReason','sdReference'])el(id).addEventListener('input',controls);\n"+anchor)
out[str(p)]=t
print(json.dumps(out,ensure_ascii=True))
