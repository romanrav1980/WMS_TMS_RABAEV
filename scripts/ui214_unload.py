from pathlib import Path
import json,hashlib
f=Path("db/migrations/2026-10-11_ni052_unload_hu");out={}
paths=["api/wms_api_server/app/modules/transport/infrastructure/loading.py","wiki-raw/wms_admin_ui_reference/transport-unloading.js","wiki-raw/wms_admin_ui_reference/transport-loading.html"]
for p in paths:out[str(f/("000_before_"+Path(p).name))]=Path(p).read_text(encoding="utf-8")
p=Path(paths[0]);s=p.read_text(encoding="utf-8").replace("json_value(COMPOSITION_JSON,'$.nodes[0].sscc') ROOT_SCAN_IDENTIFIER,","json_value(COMPOSITION_JSON,'$.nodes[0].sscc') ROOT_SCAN_IDENTIFIER,\n                   json_value(COMPOSITION_JSON,'$.nodes[0].kind') ROOT_KIND,");out[str(p)]=s
p=Path(paths[1]);s=p.read_text(encoding="utf-8").replace('row.status === "LOADED" && row.root_case_task_id != null','row.status === "LOADED" && (row.root_case_task_id != null || row.root_kind === "CONTAINER")').replace("Погруженных самостоятельных CASE для этого действия нет.","Погруженных мест для выгрузки до выезда нет.");out[str(p)]=s
p=Path(paths[2]);s=p.read_text(encoding="utf-8").replace("Выберите погруженный самостоятельный CASE.","Выберите погруженное место целиком.").replace("Для вложенного места или переданной водителю тары требуется отдельное решение.","Выгружаются все вложенные места. Переданная водителю тара требует отдельного решения.");out[str(p)]=s
p=f/"checkpoint.json";j=json.loads(p.read_text(encoding="utf-8"));j["sha256"][str(f/"000_before_departure_guard.sql")]=hashlib.sha256((f/"000_before_departure_guard.sql").read_bytes()).hexdigest()
j["sha256"].update({k:hashlib.sha256(v.encode()).hexdigest()for k,v in out.items()if Path(k).name.startswith("000_before_")});out[str(p)]=json.dumps(j,indent=2)+"\n"
print(json.dumps(out,ensure_ascii=True))
