from pathlib import Path
root=Path(__file__).resolve().parents[1]
solver=root/"api/wms_api_server/app/services/vrp_solver.py"
s=solver.read_text(encoding="utf-8")
start=s.index("@dataclass\nclass VrpOrder")
end=s.index("# ---------------------------------------------------------------------------\n# Distance helper",start)
models=s[start:end].rstrip()
models=models.replace('    total_duration_min: int = 0','    total_duration_min: int = 0\n    schedule: list[dict[str, Any]] = field(default_factory=list)\n    schedule_status: str = "UNAVAILABLE"\n    schedule_start_min: int | None = None\n    schedule_end_min: int | None = None')
(root/"api/wms_api_server/app/modules/transport/domain/vrp_models.py").write_text('"""Passive models of the existing solver; relative time is not dispatch admission."""\nfrom dataclasses import dataclass, field\nfrom typing import Any\n\n'+models+'\n',encoding="utf-8")
s=s[:start]+'from ..modules.transport.contracts import VrpOrder, VrpVehicle, VrpRoute, VrpPlan, extract_solver_routes\n\n\n'+s[end:]
s=s.replace('from dataclasses import dataclass, field\n','')
s=s.replace('service = orders[ti].unload_norm_min if ti != depot_idx else 0','service = orders[fi].unload_norm_min if fi != depot_idx else 0')
s=s.replace('travel = int(dist_km / SPEED_KM_MIN)','travel = math.ceil(dist_km / SPEED_KM_MIN)')
a=s.index('    # Extract routes\n',s.index('def _solve_with_ortools'))
b=s.index('    total_km_all =',a)
s=s[:a]+'''    routes, unassigned, tw_violations = extract_solver_routes(
        orders, vehicles, dist_matrix, depot_idx, manager, routing, solution,
    )

'''+s[b:]
solver.write_text(s,encoding="utf-8")
c=root/"api/wms_api_server/app/modules/transport/contracts.py"
c.write_text(c.read_text(encoding="utf-8")+'\nfrom .domain.vrp_models import VrpOrder, VrpVehicle, VrpRoute, VrpPlan\nfrom .infrastructure.vrp_schedule import extract_solver_routes\nfrom .domain.vrp_presentation import route_payload, route_response\n',encoding="utf-8")
p=root/"api/wms_api_server/app/services/transport_service.py"
s=p.read_text(encoding="utf-8")
s=s.replace('from .vrp_solver import VrpPlan as _VrpPlanInner, VrpRouteItem as _VrpRouteInner','from .vrp_solver import VrpPlan as _VrpPlanInner, VrpRoute as _VrpRouteInner')
a=s.index('                "routes": [',s.index('        plan_json = json.dumps(',s.index('def plan_vrp') if 'def plan_vrp' in s else 0))
b=s.index('                "unassigned":',a)
s=s[:a]+'                "routes": [route_payload(r) for r in plan.routes],\n'+s[b:]
a=s.index('        route_items = [',a)
b=s.index('        explain_steps.append({',a)
s=s[:a]+'        route_items = [VrpRouteItem(**route_response(r)) for r in plan.routes]\n'+s[b:]
anchor='        plan_json = json.dumps('
pos=s.index(anchor,s.index('        # Sprint 117'))
s=s[:pos]+'        from ..modules.transport.contracts import route_payload, route_response\n'+s[pos:]
p.write_text(s,encoding="utf-8")
p=root/"api/wms_api_server/app/schemas.py"
s=p.read_text(encoding="utf-8")
s=s.replace('    capacity_status: str = "ok"','    schedule_status: str = "UNAVAILABLE"\n    schedule_start_min: int | None = None\n    schedule_end_min: int | None = None\n    schedule_assumptions: list[str] = Field(default_factory=list)\n    operational_admission: bool = False\n    capacity_status: str = "ok"',1)
p.write_text(s,encoding="utf-8")
