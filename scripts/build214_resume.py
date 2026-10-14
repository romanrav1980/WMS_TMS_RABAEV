from pathlib import Path
import json
s=Path("scripts/resume212_case.py").read_text(encoding="utf-8").replace("212","214").replace("1e544268","c62c896a").replace("case=1113","case=1116").replace("wave=467","wave=470").replace("ware=31987650","ware=42987529").replace("== (6,6)","==(7,7)").replace("==(6,6)","==(7,7)").replace("==-6","==-7").replace("==6","==7")
s=s.replace("q.execute(\"select PASS from RUSERS","q.execute(\"update RUSERS set DELETED=0 where ID=:p_actor\",p_actor=actor);c.commit()\n q.execute(\"select PASS from RUSERS",1)
s=s.replace("json_value(COMPOSITION_JSON,'$.nodes[0].sscc')","coalesce(json_value(COMPOSITION_JSON,'$.nodes[0].sscc'),ROOT_UID)")
s=s.replace(" print(\"PASS214"," q.execute(\"select count(*)from RRL_WMS_HU_LINK where LINKED_OPERATION_ID=:p_op and ACTIVE_FLAG=1\",p_op=body[\"operation_id\"]);assert q.fetchone()[0]==2\n q.execute(\"select count(*)from RRL_WMS_HU_LINK where UNLINKED_OPERATION_ID=:p_load and ACTIVE_FLAG=0\",p_load=load_id);assert q.fetchone()[0]==2\n print(\"PASS214",1).replace("CASE1113","CASE1116").replace("original-6","original-7").replace("new+6/P6H6","new+7/P7H7/new links2 old links2")
print(json.dumps({"scripts/resume214_case.py":s},ensure_ascii=True))
