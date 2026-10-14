"""162 real installed OR-Tools: strict arrival vs own service, return leg, archive."""
import sys, time, json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.services.vrp_solver import VrpOrder,VrpVehicle,solve,_solve_ortools
from app.modules.transport.contracts import extract_solver_routes,route_payload,route_response,VrpRouteItem
orders=[
 VrpOrder("QA162.A","A",41.7,44.8,1,10,6667491,None,tw_from=10,tw_to=10,tw_strict=True,unload_norm_min=40),
 VrpOrder("QA162.B","B",41.71,44.81,1,10,6667491,None,tw_from=60,tw_to=60,tw_strict=True,unload_norm_min=20),
]
vehicles=[VrpVehicle(162,"QA162","5",4,1)]
# Deliberately asymmetric return arc: all legs must remain in route distance.
matrix=[[0,8333,0],[8333,0,16667],[0,0,0]]
manager,routing,solution=_solve_ortools(orders,vehicles,matrix,2,1)
assert solution is not None
routes,unassigned,violations=extract_solver_routes(orders,vehicles,matrix,2,manager,routing,solution)
assert not unassigned and violations==0 and len(routes)==1,(unassigned,violations)
r=routes[0];assert [x.st_number for x in r.stops]==["QA162.A","QA162.B"]
a,b=r.schedule
assert (a["arrival_min"],a["departure_min"])==(10,50),a
assert (b["arrival_min"],b["departure_min"])==(60,80),b
assert r.total_km==25 and r.schedule_end_min>=101,(r.total_km,r.schedule_end_min)
assert r.total_duration_min==r.schedule_end_min-r.schedule_start_min
assert all(x["wait_after_service_min"]>=0 for x in r.schedule)
saved=json.loads(json.dumps(route_payload(r)));assert saved["stop_schedule"]==r.schedule and not saved["operational_admission"]
response=VrpRouteItem(**route_response(r));assert response.stops[0].arrival_min==10 and response.stops[1].departure_min==80
fallback=solve(orders,vehicles,solver="savings")
assert fallback.routes
unavailable=VrpRouteItem(**route_response(fallback.routes[0]))
assert unavailable.schedule_status=="UNAVAILABLE" and all(s.arrival_min is None for s in unavailable.stops)
assert not unavailable.operational_admission and unavailable.explain_notes==["SCHEDULE_UNAVAILABLE"]
print("PASS162 installed OR-Tools strict arrival10/60 ownservice40/20; return25km/end101; exact schedule archive/API; fallback unknown/no operational admission/no Oracle writes")
