from pathlib import Path
r=Path(__file__).resolve().parents[1]
p=r/"api/wms_api_server/app/modules/transport/contracts_plan.py"
s=p.read_text(encoding="utf-8")
(r/"api/wms_api_server/app/modules/transport/domain/plan_error.py").write_text(s,encoding="utf-8")
p.write_text('from .domain.plan_error import TransportPlanError\n',encoding="utf-8")
p=r/"api/wms_api_server/app/modules/transport/domain/preflight_routes.py"
p.write_text(p.read_text(encoding="utf-8").replace('from ..contracts_plan import','from .plan_error import'),encoding="utf-8")
p=r/"api/wms_api_server/app/modules/transport/domain/vrp_presentation.py"
p.write_text(p.read_text(encoding="utf-8")+'''
def planner_constraint_evidence(routes: list[VrpRoute], fallback_windows: int) -> dict[str, Any]:
    return {
        "capacity_pallets": True, "capacity_weight": True,
        "time_windows": bool(routes) and all(route.schedule_status == "RELATIVE_SOLVER_SCHEDULE" for route in routes),
        "operational_admission": False, "vehicle_type": True, "hydro_board": True,
        "fallback_time_windows": fallback_windows,
    }
''',encoding="utf-8")
p=r/"api/wms_api_server/app/modules/transport/contracts.py"
p.write_text(p.read_text(encoding="utf-8")+'from .domain.vrp_presentation import planner_constraint_evidence\n',encoding="utf-8")
p=r/"api/wms_api_server/app/services/transport_service.py"
s=p.read_text(encoding="utf-8")
a=s.index('            "constraints": {',s.index('        # Save plan to Oracle'))
b=s.index('            "fleet":',a)
s=s[:a]+'            "constraints": planner_constraint_evidence(plan.routes, fallback_tw_count),\n'+s[b:]
# Import must precede explain construction (not only JSON serialization).
s=s.replace('        from ..modules.transport.contracts import route_payload, route_response\n','')
s=s.replace('        # Save plan to Oracle','        from ..modules.transport.contracts import route_payload, route_response, planner_constraint_evidence\n        # Save plan to Oracle')
p.write_text(s,encoding="utf-8")
