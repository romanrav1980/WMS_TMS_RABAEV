from pathlib import Path
import json
out={}
p=Path("api/wms_api_server/app/modules/transport/public.py");s=p.read_text(encoding="utf-8")+"\nfrom .domain.vrp_distance_costs import distance_costs\n";out[str(p)]=s
p=Path("api/wms_api_server/app/modules/transport/domain/vrp_travel_time.py");s=p.read_text(encoding="utf-8")
s=s.replace("cache: dict[tuple[str,str],float] | None)","cache: dict[tuple[str,str],float] | None,depot_address: str | None=None)")
s=s.replace("elif i==depot or j==depot:", "elif (i==depot or j==depot)and not depot_address:")
s=s.replace('value=(cache or {}).get((addresses[i],addresses[j]))','a=depot_address if i==depot else addresses[i];b=depot_address if j==depot else addresses[j]\n                value=(cache or {}).get((a,b))')
out[str(p)]=s
p=Path("api/wms_api_server/app/services/vrp_solver.py");s=p.read_text(encoding="utf-8")
s=s.replace("    duration_cache: dict[tuple[str,str],float] | None = None,","    duration_cache: dict[tuple[str,str],float] | None = None,\n    origin: dict | None = None,")
s=s.replace("_t.time(),duration_cache)","_t.time(),duration_cache,origin)").replace("t0,duration_cache)","t0,duration_cache,origin)")
a=s.index("    # Build integer distance matrix in metres",s.index("def _solve_with_ortools"));b=s.index("    manager, routing, solution =",a)
s=s[:a]+"""    from ..modules.transport.public import distance_costs,travel_times
    dist_matrix,depot_address=distance_costs(orders,dist_cache,origin,_hav_km)
    time_matrix,time_basis=travel_times([order.addr for order in orders],dist_matrix,depot_idx,duration_cache,depot_address)
"""+s[b:]
s=s.replace("    total_km_all = sum(r.total_km for r in routes)","    for route in routes:route.depot_basis='CONFIGURED_WAREHOUSE_REFERENCE'if depot_address else 'VIRTUAL_CENTROID'\n    total_km_all = sum(r.total_km for r in routes)")
out[str(p)]=s
p=Path("api/wms_api_server/app/modules/transport/domain/vrp_models.py");s=p.read_text(encoding="utf-8").replace("    road_profile_legs: int = 0","    depot_basis: str = \"VIRTUAL_CENTROID\"\n    road_profile_legs: int = 0");out[str(p)]=s
p=Path("api/wms_api_server/app/modules/transport/domain/vrp_presentation.py");s=p.read_text(encoding="utf-8")
s=s.replace('if not(route.road_profile_legs and v=="TRAVEL_AT_CONSTANT_50_KMH")','if not(route.road_profile_legs and v=="TRAVEL_AT_CONSTANT_50_KMH")and not(route.depot_basis=="CONFIGURED_WAREHOUSE_REFERENCE"and v=="VIRTUAL_DEPOT_AT_ORDER_CENTROID")')
s=s.replace('"road_profile_legs":route.road_profile_legs,','"road_profile_legs":route.road_profile_legs,"depot_basis":route.depot_basis,')
out[str(p)]=s
p=Path("api/wms_api_server/app/modules/transport/contracts_vrp.py");s=p.read_text(encoding="utf-8").replace("    road_profile_legs: int = 0","    depot_basis: str = \"UNRECORDED\"\n    road_profile_legs: int = 0");out[str(p)]=s
p=Path("admin/wms_admin_frontend/src/components/PlannerSchedule.tsx");s=p.read_text(encoding="utf-8").replace("  road_profile_legs?: number;","  depot_basis?: string;\n  road_profile_legs?: number;")
s=s.replace('    {available\n      ? "Расчётное обслуживание: минуты от начала смены 06:00. Виртуальное депо; допуск рейса требует проверки."','    {available\n      ? "Расчётное обслуживание: минуты от начала смены 06:00. "+(route.depot_basis==="CONFIGURED_WAREHOUSE_REFERENCE"?"Настроенный адрес отправления склада.":"Виртуальное депо.")+" Допуск рейса требует проверки."')
out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
