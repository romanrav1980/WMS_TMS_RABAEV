from pathlib import Path
import json
out={}
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse_queue.sql");s=p.read_text(encoding="utf-8").replace("where p.SOURCE_WARE_ID=:ware or p.TARGET_WARE_ID=:ware\norder by p.ARRIVAL_DUE,p.OPERATION_ID", """where (p.SOURCE_WARE_ID=:ware or p.TARGET_WARE_ID=:ware)
 and (:history=1 or not exists(
  select 1 from RRL_TT_HU_LOAD_ST member_record join RRL_TT_HU_LOAD_FACT load_record on load_record.LOAD_OPERATION_ID=member_record.LOAD_OPERATION_ID
  where member_record.SBORKA_PALLET_ID=b.ST_ID and member_record.ACTIVE_FLAG=1 and load_record.STATUS='DEPARTED'
 ))
order by case when :history=1 then p.ARRIVAL_DUE end desc,p.ARRIVAL_DUE,p.OPERATION_ID""");out[str(p)]=s
for path in["api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse_queue.py","api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse.py","api/wms_api_server/app/modules/inventory/contracts_interwarehouse.py"]:
 p=Path(path);s=p.read_text(encoding="utf-8")
 if path.endswith("interwarehouse_queue.py"):s=s.replace("actor: str) -> list[dict[str, Any]]:","actor: str, include_completed: bool=False) -> list[dict[str, Any]]:").replace("q.execute(QUEUE_SQL, ware=ware_id)","q.execute(QUEUE_SQL, ware=ware_id,history=int(include_completed))")
 else:s=s.replace("def queue(self, ware_id: int, actor: str)","def queue(self, ware_id: int, actor: str, include_completed: bool=False)").replace("read(ware_id,actor)","read(ware_id,actor,include_completed)")
 out[str(p)]=s
p=Path("api/wms_api_server/app/modules/inventory/api/interwarehouse_routes.py");s=p.read_text(encoding="utf-8").replace("Depends,HTTPException","Depends,HTTPException,Query",1).replace("def queue(ware_id: int,user: AdminUser=","def queue(ware_id: int,include_completed: bool=Query(default=False),user: AdminUser=",1).replace("return service.queue(ware_id,user.username)","return service.queue(ware_id,user.username,include_completed)",1);out[str(p)]=s
p=Path("wiki-raw/wms_admin_ui_reference/interwarehouse.html");s=p.read_text(encoding="utf-8");out["db/migrations/2026-10-11_ni061_phase_timing/000_before_interwarehouse.html"]=s
idx=s.index('id="iwLoad"');a=s.rfind("<button",0,idx);s=s[:a]+'<label><input id="iwHistory" type="checkbox">Показать последние завершённые подвозы</label>'+s[a:];out[str(p)]=s
p=Path("wiki-raw/wms_admin_ui_reference/interwarehouse.js");s=p.read_text(encoding="utf-8").replace('request("/warehouses/"+id)','request("/warehouses/"+id+"?include_completed="+el("iwHistory").checked)',1);out[str(p)]=s
p=Path("scripts/ni061_phase_timing_case.py");s=p.read_text(encoding="utf-8").replace('warehouses/51365792")','warehouses/51365792?include_completed=true")',1);out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
