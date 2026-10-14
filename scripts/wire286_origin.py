from pathlib import Path
import json
out={}
p=Path("api/wms_api_server/app/modules/transport/infrastructure/road_leg_estimate.py");s=p.read_text(encoding="utf-8")
needle='context=read_oracle_json(out.getvalue());stops,issues=ordered_stops(context["source"]["members"])'
replacement=needle+'''
    origins=context["source"].get("warehouse_origins",[])
    configured=len(origins)==1 and origins[0].get("configured") is True
    if not depot:
        if configured:depot=origins[0]["depot_address"]
        else:issues.append("WAREHOUSE_DEPOT_NOT_CONFIGURED")
    depot_basis="CONFIGURED_WAREHOUSE_REFERENCE"if configured and depot==origins[0]["depot_address"]else "DISPATCHER_EXPLICIT_ADDRESS"if depot else "WAREHOUSE_DEPOT_UNKNOWN"
'''
assert needle in s;s=s.replace(needle,replacement)
s=s.replace('result.update({"trip_id":trip,','result.update({"depot_basis":depot_basis,"warehouse_origin":origins[0]if len(origins)==1 else None,"trip_id":trip,')
out[p.as_posix()]=s
p=Path("api/wms_api_server/app/modules/transport/api/preflight_routes.py");s=p.read_text(encoding="utf-8")
s=s.replace('depot_address: str=Query(min_length=1,max_length=200)','depot_address: str=Query(default="",max_length=200)')
s=s.replace('if trip_id<1 or not depot_address.strip():raise HTTPException(422,"Positive trip and explicit depot address required")','if trip_id<1:raise HTTPException(422,"Positive trip required")')
s=s.replace('service.road_legs(trip_id,depot_address,max_age_hours','service.road_legs(trip_id,depot_address.strip(),max_age_hours')
out[p.as_posix()]=s
p=Path("admin/wms_admin_frontend/src/components/TransportRoadLegs.tsx");s=p.read_text(encoding="utf-8")
s=s.replace('TRIP_HAS_NO_DESTINATION_MEMBERS:"В рейсе нет адресов доставки"','TRIP_HAS_NO_DESTINATION_MEMBERS:"В рейсе нет адресов доставки",WAREHOUSE_DEPOT_NOT_CONFIGURED:"База отправления склада не настроена"')
s=s.replace('disabled={busy||!depot.trim()}','disabled={busy}')
s=s.replace('Адрес отправления, код справочника','Адрес отправления (пусто — база склада), код справочника')
s=s.replace('Адрес отправления выбран диспетчером.','Использованный адрес отправления: {report.depot_address||"не определён"}.')
# Actual result shape already includes source hash; add optional depot_address field.
s=s.replace('type Report=RoadAdvice&{','type Report=RoadAdvice&{depot_address?:string;')
out[p.as_posix()]=s
print(json.dumps(out,ensure_ascii=True))
