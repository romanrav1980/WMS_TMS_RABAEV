from pathlib import Path
import json
out={}
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/tare_load_recovery.py");s=p.read_text(encoding="utf-8")
s=s.replace("typ.PALLET_TYPE_NAME,b.PLACE_ID,","typ.PALLET_TYPE_NAME,b.PLACE_KIND,b.PLACE_ID,",1)
s=s.replace("ct.SSCC PLACE_IDENTIFIER,","coalesce(ct.SSCC,json_value(lf.COMPOSITION_JSON,'$.nodes[0].sscc'),b.PLACE_ID) PLACE_IDENTIFIER,",1)
s=s.replace("join RRL_CASE_PICK_TASK ct on b.PLACE_KIND='CASE'","left join RRL_CASE_PICK_TASK ct on b.PLACE_KIND='CASE'",1)
out[str(p)]=s
p=Path("wiki-raw/wms_admin_ui_reference/tare-load-recovery.js");s=p.read_text(encoding="utf-8").replace('place_kind:"CASE",place_id:row.place_id','place_kind:row.place_kind || "CASE",place_id:row.place_id',1)
s=s.replace('try {pending = {body};localStorage.setItem(key(),JSON.stringify(pending));await send(key());}','try {const saved = {body};localStorage.setItem(key(),JSON.stringify(saved));pending = saved;await send(key());}',1)
out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
