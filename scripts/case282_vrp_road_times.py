exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.services.vrp_solver import VrpOrder,VrpVehicle,_solve_ortools
from app.modules.transport.contracts import extract_solver_routes,route_response,route_payload,VrpRouteItem
from app.modules.transport.public import travel_times,planner_cost_cache
from app.oracle_gateway import OracleGateway
orders=[VrpOrder("QA282.A","A",41.7,44.8,1,10,9807,None,tw_from=10,tw_to=10,tw_strict=True,unload_norm_min=40),
 VrpOrder("QA282.B","B",41.71,44.81,1,10,9807,None,tw_from=75,tw_to=75,tw_strict=True,unload_norm_min=20)]
vehicles=[VrpVehicle(282,"QA282","5",4,1)]
distance=[[0,8333,16667],[8333,0,16667],[16667,16667,0]]
time_matrix=[[0,25,2],[35,0,7],[3,9,0]]
basis=[["SAME_NODE","ROAD_PROFILE_ESTIMATE","VIRTUAL_DEPOT_SPEED_ESTIMATE"],
 ["ROAD_PROFILE_ESTIMATE","SAME_NODE","VIRTUAL_DEPOT_SPEED_ESTIMATE"],
 ["VIRTUAL_DEPOT_SPEED_ESTIMATE","VIRTUAL_DEPOT_SPEED_ESTIMATE","SAME_NODE"]]
manager,routing,solution=_solve_ortools(orders,vehicles,distance,2,1,time_matrix);assert solution is not None
routes,unassigned,violation=extract_solver_routes(orders,vehicles,distance,2,manager,routing,solution,time_matrix,basis)
assert len(routes)==1 and not unassigned and violation==0
route=routes[0];a,b=route.schedule
assert (a["arrival_min"],a["departure_min"])==(10,50)
assert (b["arrival_min"],b["departure_min"],b["duration_from_prev_min"],b["duration_from_prev_basis"])==(75,95,25,"ROAD_PROFILE_ESTIMATE")
assert a["wait_after_service_min"]==0 and route.schedule_end_min==102 and route.road_profile_legs==1
assert VrpRouteItem(**route_response(route)).stops[1].duration_from_prev_basis=="ROAD_PROFILE_ESTIMATE"
assert route_payload(route)["road_profile_legs"]==1 and not route_payload(route)["operational_admission"]
times,sources=travel_times(["A","B"],distance,2,{("A","B"):25.01,("B","A"):35})
assert times[0][1]==26 and times[1][0]==35 and sources[0][2]=="VIRTUAL_DEPOT_SPEED_ESTIMATE"
d,t,provider=planner_cost_cache(OracleGateway(),["DS-BASE","DS-WARE"]);assert isinstance(d,dict)and isinstance(t,dict)
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("""select executions,round(elapsed_time/1000/nullif(executions,0),3),buffer_gets
 from V$SQL where PARSING_SCHEMA_NAME='RABAEV'and executions>0 and SQL_TEXT not like '%V$SQL%'and dbms_lob.instr(SQL_FULLTEXT,'VRP_PROFILE_PK282')>0
 order by last_active_time desc fetch first 2 rows only""");print("SQL282_MS",q.fetchall())
print("PASS282 installed OR-Tools uses25road minutes instead of10speed estimate: strict arrival75/service95/return102, sharedcallback/displaybasis/nonnegativewait; existingreadonlycostcache/no plan orquantity birth; virtualdepot stillestimate")
