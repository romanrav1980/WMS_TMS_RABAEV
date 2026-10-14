from pathlib import Path
import json
out={}
p=Path("api/wms_api_server/app/modules/transport/public.py");out[str(p)]=p.read_text(encoding="utf-8")+"\nfrom .domain.vrp_travel_time import travel_times\nfrom .infrastructure.profile_duration_cache import profile_duration_cache\n"
p=Path("api/wms_api_server/app/services/vrp_solver.py");s=p.read_text(encoding="utf-8")
s=s.replace("    time_limit_s: int,\n) -> \"Any\":","    time_limit_s: int,\n    time_matrix: list[list[int]] | None = None,\n) -> \"Any\":",1)
s=s.replace("travel = math.ceil(dist_km / SPEED_KM_MIN)","travel = time_matrix[fi][ti]if time_matrix is not None else math.ceil(dist_km / SPEED_KM_MIN)",1)
s=s.replace('    solver: str = "auto",\n)', '    solver: str = "auto",\n    duration_cache: dict[tuple[str,str],float] | None = None,\n)',1)
s=s.replace("_solve_with_ortools(valid, vehicles, dist_cache, time_limit_s, _t.time())","_solve_with_ortools(valid, vehicles, dist_cache, time_limit_s, _t.time(),duration_cache)")
s=s.replace("_solve_with_ortools(valid, vehicles, dist_cache, time_limit_s, t0)","_solve_with_ortools(valid, vehicles, dist_cache, time_limit_s, t0,duration_cache)")
s=s.replace("    t0: float,\n) -> VrpPlan:", "    t0: float,\n    duration_cache: dict[tuple[str,str],float] | None = None,\n) -> VrpPlan:",1)
s=s.replace("    manager, routing, solution = _solve_ortools(orders, vehicles, dist_matrix, depot_idx, time_limit_s)","    from ..modules.transport.public import travel_times\n    time_matrix,time_basis=travel_times([order.addr for order in orders],dist_matrix,depot_idx,duration_cache)\n    manager, routing, solution = _solve_ortools(orders, vehicles, dist_matrix, depot_idx, time_limit_s,time_matrix)")
s=s.replace("orders, vehicles, dist_matrix, depot_idx, manager, routing, solution,","orders, vehicles, dist_matrix, depot_idx, manager, routing, solution,time_matrix,time_basis,",1)
out[str(p)]=s
p=Path("api/wms_api_server/app/modules/transport/infrastructure/vrp_schedule.py");s=p.read_text(encoding="utf-8")
s=s.replace("    manager: Any, routing: Any, solution: Any,","    manager: Any, routing: Any, solution: Any,\n    time_matrix: list[list[int]] | None = None,time_basis: list[list[str]] | None = None,")
s=s.replace("        previous_distance = 0","        previous_distance = 0;previous_node=depot;road_legs=0")
s=s.replace("travel = math.ceil(leg / 1000 / (50 / 60))","travel = time_matrix[node][next_node]if time_matrix is not None else math.ceil(leg / 1000 / (50 / 60))")
s=s.replace('"duration_from_prev_min": math.ceil(previous_distance / 1000 / (50 / 60)),','"duration_from_prev_min":time_matrix[previous_node][node]if time_matrix is not None else math.ceil(previous_distance/1000/(50/60)),\n                    "duration_from_prev_basis":time_basis[previous_node][node]if time_basis is not None else "SPEED_50_ESTIMATE",')
s=s.replace("            distance += leg","            if time_basis is not None and time_basis[node][next_node]=='ROAD_PROFILE_ESTIMATE':road_legs+=1\n            previous_node=node\n            distance += leg")
s=s.replace('schedule_start_min=start, schedule_end_min=end,','schedule_start_min=start, schedule_end_min=end,road_profile_legs=road_legs,')
out[str(p)]=s
p=Path("api/wms_api_server/app/modules/transport/domain/vrp_models.py");s=p.read_text(encoding="utf-8").replace('    schedule_status: str = "UNAVAILABLE"','    road_profile_legs: int = 0\n    schedule_status: str = "UNAVAILABLE"');out[str(p)]=s
p=Path("api/wms_api_server/app/modules/transport/domain/vrp_presentation.py");s=p.read_text(encoding="utf-8")
s=s.replace('"schedule_assumptions": list(ASSUMPTIONS),','"schedule_assumptions":[v for v in ASSUMPTIONS if not(route.road_profile_legs and v=="TRAVEL_AT_CONSTANT_50_KMH")]+(["MIXED_ROAD_PROFILE_AND_SPEED_ESTIMATES"]if route.road_profile_legs else []),\n        "road_profile_legs":route.road_profile_legs,')
out[str(p)]=s
p=Path("api/wms_api_server/app/modules/transport/contracts_vrp.py");s=p.read_text(encoding="utf-8").replace('    constraint_notes: list[str]', '    duration_from_prev_basis: str = "UNRECORDED"\n    constraint_notes: list[str]',1).replace('    schedule_status: str = "UNAVAILABLE"','    road_profile_legs: int = 0\n    schedule_status: str = "UNAVAILABLE"',1);out[str(p)]=s
p=Path("api/wms_api_server/app/services/transport_service.py");s=p.read_text(encoding="utf-8")
s=s.replace("        dist_cache = DistanceMatrixService(self.gateway).get_matrix_as_dict(addr_list)","        dist_cache = DistanceMatrixService(self.gateway).get_matrix_as_dict(addr_list)\n        from ..modules.transport.public import profile_duration_cache\n        duration_cache=profile_duration_cache(self.gateway,addr_list)")
s=s.replace("                dist_cache=dist_cache or None,","                dist_cache=dist_cache or None,duration_cache=duration_cache or None,",1)
out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
