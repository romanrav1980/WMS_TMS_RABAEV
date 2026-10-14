from pathlib import Path
import json
out={}
p=Path("api/wms_api_server/app/modules/transport/domain/vrp_presentation.py");s=p.read_text(encoding="utf-8").replace('"duration_from_prev_min": timing.get("duration_from_prev_min"),','"duration_from_prev_min": timing.get("duration_from_prev_min"),\n            "duration_from_prev_basis":timing.get("duration_from_prev_basis","UNRECORDED"),');out[str(p)]=s
p=Path("admin/wms_admin_frontend/src/components/PlannerSchedule.tsx");s=p.read_text(encoding="utf-8")
s=s.replace("  duration_from_prev_min?: number | null;","  duration_from_prev_min?: number | null;\n  duration_from_prev_basis?: string;")
s=s.replace("  schedule_status?: string;","  road_profile_legs?: number;\n  schedule_status?: string;",1)
s=s.replace('    constraint_notes: ["SCHEDULE_STALE_RECALCULATE"],','    duration_from_prev_basis:"UNRECORDED",\n    constraint_notes: ["SCHEDULE_STALE_RECALCULATE"],')
s=s.replace('    {available\n', '    {(route.road_profile_legs??0)>0&&<span>Дорожных участков из матрицы: {route.road_profile_legs}. </span>}\n    {available\n',1)
s=s.replace('    Обслуживание +{stop.arrival_min}', '    {stop.duration_from_prev_min!=null&&<>До остановки {stop.duration_from_prev_min} мин ({stop.duration_from_prev_basis==="ROAD_PROFILE_ESTIMATE"?"дорожный профиль":stop.duration_from_prev_basis==="UNRECORDED"?"источник не сохранён":"расчётная скорость"}). </>}\n    Обслуживание +{stop.arrival_min}')
out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
