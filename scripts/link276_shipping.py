from pathlib import Path
import json
out={}
p=Path("api/wms_api_server/app/modules/finance/infrastructure/shipping_register.py");s=p.read_text(encoding="utf-8")
s=s.replace("        p.STDATE,t.CONDITION,t.SHIPMENT_DATE,","        p.STDATE,t.CONDITION,t.SHIPMENT_DATE,")
s=s.replace("coalesce(l.ROOT_UID,'CASE:'||to_char(l.ROOT_CASE_TASK_ID))","coalesce(l.ROOT_UID,'CASE:'||to_char(l.ROOT_CASE_TASK_ID)),\n        (select max(d.VERSION_NO)from RRL_ST_DEFER_DECISION d where d.ST_NUMBER=p.ST_NUMBER and d.WARE_ID=p.WARE_ID)")
s=s.replace("root_state,root_uid=r","root_state,root_uid,deferral_version=r")
s=s.replace('"physical_departure_confirmed":state=="PHYSICALLY_DEPARTED"', '"deferral_version":deferral_version,"physical_departure_confirmed":state=="PHYSICALLY_DEPARTED"')
out[str(p)]=s
p=Path("wiki-raw/wms_admin_ui_reference/shipping-register.js");s=p.read_text(encoding="utf-8")
s=s.replace("row.root_uid])","row.root_uid,row.deferral_version?'Перенос, версия '+row.deferral_version:''])")
s=s.replace("tr.appendChild(cell(value));return tr;", "tr.appendChild(cell(value));tr.addEventListener('click',()=>{document.getElementById('sdSt').value=row.st_number;document.getElementById('sdSt').dispatchEvent(new Event('input'));});return tr;",1)
out[str(p)]=s
p=Path("wiki-raw/wms_admin_ui_reference/day-reconciliation.html");s=p.read_text(encoding="utf-8").replace("<th>Корневое место</th>","<th>Корневое место</th><th>Перенос</th>")
out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
