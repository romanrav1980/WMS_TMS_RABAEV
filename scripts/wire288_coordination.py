from pathlib import Path
import json
out={}
p=Path("api/wms_api_server/app/modules/transport/infrastructure/coordination_preflight.py");s=p.read_text(encoding="utf-8")
s=s.replace('if temporal["driver_days"]["status"]!="NO_RECORDED_DAY_VIOLATION":','if temporal["driver_days"]["status"]=="PLANNING_LIMIT_EXCEEDED":')
s=s.replace('blockers.append({"code":"COORDINATION_DRIVER_DAY_NOT_VERIFIED"})','blockers.append({"code":"COORDINATION_DRIVER_DAY_LIMIT_EXCEEDED"})\n                if not temporal["driver_days"]["days"] or any(not d["recorded_plan_coverage_complete"]for d in temporal["driver_days"]["days"]):\n                    blockers.append({"code":"COORDINATION_DRIVER_DAY_INCOMPLETE"})')
s=s.replace('"DRIVER_REST_AND_DAILY_LIMITS","ACTUAL_ROUTE_DURATION",','"APPLICABLE_DRIVER_LAW_AND_OUTSIDE_WMS_DUTIES","DRIVER_BREAKS_IN_ROAD_SCHEDULE","DESTINATION_TIME_ZONE_AND_PHYSICAL_ORIGIN",')
out[p.as_posix()]=s
p=Path("admin/wms_admin_frontend/src/components/TransportCoordination.tsx");s=p.read_text(encoding="utf-8")
s=s.replace('type Snapshot={','type Snapshot={temporal?:{status:string};delivery_windows?:{status:string;return_at?:string|null};')
s=s.replace(' COORDINATION_PLANNED_TRIP_REQUIRED:',' COORDINATION_RESOURCE_CONFLICT:"Машина или водитель заняты другим рейсом",\n COORDINATION_DRIVER_DAY_LIMIT_EXCEEDED:"Превышен плановый дневной лимит движения",\n COORDINATION_DRIVER_DAY_INCOMPLETE:"Есть рейсы водителя с неактуальным или неполным планом",\n DELIVERY_HARD_WINDOW_MISSED:"Строгое окно доставки пропущено",\n DELIVERY_SOFT_WINDOW_MISSED:"Плановое окно доставки пропущено",\n DELIVERY_WINDOW_MISSING:"Окно доставки не задано",\n DESTINATION_UNLOAD_NORM_UNKNOWN:"Норматив разгрузки неизвестен",\n WAREHOUSE_DEPOT_NOT_CONFIGURED:"База отправления не настроена",\n COORDINATION_PLANNED_TRIP_REQUIRED:')
s=s.replace('{tripId,apiBase,headers}:','{tripId,apiBase,headers,actor}:').replace('tripId:number;apiBase:string;headers:HeadersInit;','tripId:number;apiBase:string;headers:HeadersInit;actor:string;')
s=s.replace('[tripId,apiBase]);','[tripId,apiBase,actor]);')
s=s.replace('   {result.loading_start_at&&','   {result.delivery_windows&&<p>Окна доставки: {result.delivery_windows.status==="CURRENT_APPROVED_REGION_REQUIRED"?"нужно актуальное утверждение времени":result.delivery_windows.status==="NO_EARLIEST_WINDOW_VIOLATION"?"ранняя оценка укладывается в окна":result.delivery_windows.status==="WINDOW_VIOLATION"?"есть опоздания":"недостаточно данных"}. Возврат: {result.delivery_windows.return_at||"не рассчитан"}.</p>}\n   {result.loading_start_at&&')
out[p.as_posix()]=s
p=Path("admin/wms_admin_frontend/src/components/TransportTimePreflight.tsx");s=p.read_text(encoding="utf-8")
s=s.replace('<TransportCoordination tripId={tripId} apiBase={apiBase} headers={headers}/>','<TransportCoordination tripId={tripId} apiBase={apiBase} headers={headers} actor={actor}/>')
assert 'actor={actor}'in s
out[p.as_posix()]=s
print(json.dumps(out,ensure_ascii=True))
