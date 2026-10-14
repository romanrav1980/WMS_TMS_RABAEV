from pathlib import Path
import json
out={}
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/case_labels.py");s=p.read_text(encoding="utf-8")
s=s.replace('with self.gateway.transaction("Current warehouse CASE logistic label read")as q:\n                q.callproc','with self.gateway.transaction("Current warehouse CASE logistic label read")as q:\n                q.execute("set transaction read only")\n                q.callproc')
s=s.replace('select l.RESULT_JSON,l.CONFIRMED_AT,l.CONFIRMED_BY,c.SSCC,c.CONTENT_VERSION from RRL_CASE_SSCC_LABEL l join RRL_CASE_PICK_TASK c on c.CASE_PICK_TASK_ID=l.CASE_PICK_TASK_ID where l.CASE_PICK_TASK_ID=:task',"""select l.RESULT_JSON,l.CONFIRMED_AT,l.CONFIRMED_BY,c.SSCC,c.CONTENT_VERSION,case when p.FINAL_WEIGHT_REQUIRED=1 and upper(p.LOAD_UNIT_CLASS)='CONTAINER'then 1 else 0 end from RRL_CASE_PICK_TASK c join RRL_PALLET_TYPE p on p.PALLET_TYPE_ID=c.PALLET_TYPE_ID left join RRL_CASE_SSCC_LABEL l on l.CASE_PICK_TASK_ID=c.CASE_PICK_TASK_ID where c.CASE_PICK_TASK_ID=:task""")
s=s.replace('if not row:return {"case_pick_task_id":task,"issued":False}','if not row:raise StockPostingError("CASE_SSCC_SOURCE_REQUIRED","",20886)\n                if row[0]is None:return {"case_pick_task_id":task,"issued":False,"final_scale_required":row[5]==1}')
s=s.replace('"current_content_version":int(row[4])}','"current_content_version":int(row[4]),"final_scale_required":row[5]==1}')
out[str(p)]=s
p=Path("wiki-raw/wms_admin_ui_reference/case-sscc-label.js");s=p.read_text(encoding="utf-8")
s=s.replace("current=null,tareNote;", "current=null,tareNote,tareRefresh;",1).replace('const tareRefresh=node("button","Обновить показание пустой тары")','tareRefresh=node("button","Обновить показание пустой тары")')
s=s.replace('   const readings=await cpTsdFetch(', '   tareNote.hidden=!data.final_scale_required;tareRefresh.hidden=!data.final_scale_required;\n   const readings=data.final_scale_required?await cpTsdFetch(')
s=s.replace('"/api/inventory/warehouse-scales/final-captures?task="+id);','"/api/inventory/warehouse-scales/final-captures?task="+id):{items:[]};')
out[str(p)]=s
p=Path("api/wms_api_server/app/middleware/audit_body.py");s=p.read_text(encoding="utf-8")
s=s.replace('"/api/inventory/warehouse-scales/captures"}','"/api/inventory/warehouse-scales/captures", "/api/inventory/warehouse-scales/final-captures"}')
out[str(p)]=s
p=Path("scripts/ni042_final_qc_case.py");s=p.read_text(encoding="utf-8")
needle='  replay=qc_gateway.post(base+final_path,json=check);'
pos=s.index(needle);s=s[:pos]+"""  status_http=qc_gateway.get(base+"/api/outgoing-quality/"+identifier);assert status_http.status_code==200 and status_http.json()["final_scale_required"]and status_http.json()["case_task_id"]==case
  captures_http=qc_gateway.get(base+"/api/outgoing-quality/"+identifier+"/final-captures");assert captures_http.status_code==200 and captures_http.json()["use_by_capture"][check["capture_key"]]["operation_id"]==check["operation_id"]
  assert verified["final_scale_device_mode"]=="TEST"and verified["net_weight_kg"]=="0.3"
"""+s[pos:];out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
