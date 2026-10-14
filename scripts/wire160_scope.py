import json
from pathlib import Path
out={}
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/slotting_layout.py");s=p.read_text(encoding="utf-8")
s=s.replace("pf.PICK_ROUTE_ID,pf.PICK_ROUTE_CELL_ID\n        from RRL_PICK_FACE pf where", """pf.PICK_ROUTE_ID,pf.PICK_ROUTE_CELL_ID,nvl(rs.MODE_CODE,'LEGACY_ACTIVE')MODE_CODE,rs.APPROVAL_OPERATION_ID
        from RRL_PICK_FACE pf
        left join RRL_PICK_FACE_ARTICUL mapping on mapping.PICK_FACE_ID=pf.PICK_FACE_ID and mapping.ARTICUL=:article and mapping.ACTIVE=1
        left join RRL_PICK_RANGE_STATUS rs on rs.PICK_FACE_ARTICUL_ID=mapping.PICK_FACE_ARTICUL_ID
        where""")
s=s.replace("for face,cell,volume,weight,route,route_cell in faces:", "for face,cell,volume,weight,route,route_cell,mode,approval in faces:")
s=s.replace('"pick_face_id":face,"cell":cell,', '"pick_face_id":face,"cell":cell,"range_mode":mode,"current_approval_operation_id":approval,\n                "new_replenishment_allowed":mode not in{"DRAINING","CLOSED"},')
out[str(p)]=s
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/slotting_candidates.py");s=p.read_text(encoding="utf-8")
s=s.replace("costs: list[dict[str, Any]]) ->", "costs: list[dict[str, Any]], candidate_route: int | None = None) ->")
s=s.replace("    # Empty dynamic faces;", """    if candidate_route is not None:
        cur.execute("select count(*)from RRL_PICK_ROUTE where PICK_ROUTE_ID=:route and WARE_ID=:ware and ACTIVE=1 and STATUS='PUBLISHED'",
                    route=candidate_route,ware=ware)
        if cur.fetchone()[0]!=1:
            raise SlottingError("SLOTTING_CURRENT_CANDIDATE_ROUTE_REQUIRED", "Нужен действующий опубликованный маршрут этого склада",404)
    # Empty dynamic faces;""")
s=s.replace("where pf.WARE_ID=:ware and pf.ACTIVE=1 and (pf.PICK_FACE_TYPE", "where pf.WARE_ID=:ware and pf.ACTIVE=1 and (:route is null or pf.PICK_ROUTE_ID=:route)and (pf.PICK_FACE_TYPE")
s=s.replace('order by pf.PICK_FACE_ID fetch first 101 rows only""", ware=ware)', 'order by pf.PICK_FACE_ID fetch first 101 rows only""", ware=ware,route=candidate_route)')
s=s.replace('"template_configuration": configuration,', '"candidate_pick_route_id":candidate_route,"candidate_scope":"WAREHOUSE_EMPTY_DYNAMIC_FACES"if candidate_route is None else"PUBLISHED_ROUTE_EMPTY_DYNAMIC_FACES",\n        "demand_and_old_range_scope":"WHOLE_ARTICLE_WAREHOUSE", "template_configuration": configuration,')
out[str(p)]=s
for relative in ["api/wms_api_server/app/modules/inventory/infrastructure/slotting_demand_reader.py",
                 "api/wms_api_server/app/modules/inventory/contracts_slotting.py"]:
 p=Path(relative);s=p.read_text(encoding="utf-8")
 s=s.replace("costs: list[dict[str,Any]]|None=None) ->", "costs: list[dict[str,Any]]|None=None,candidate_route: int|None=None) ->")
 s=s.replace("actor,pallet_weight,costs)", "actor,pallet_weight,costs,candidate_route)")
 s=s.replace("layout,pallet_weight,costs or [])", "layout,pallet_weight,costs or [],candidate_route)")
 out[str(p)]=s
p=Path("api/wms_api_server/app/modules/inventory/api/slotting_routes.py");s=p.read_text(encoding="utf-8")
s=s.replace("    recommendation_costs: list[FaceTravelCost]", "    candidate_pick_route_id: int|None=Field(default=None,gt=0)\n    recommendation_costs: list[FaceTravelCost]")
s=s.replace('[row.model_dump(mode="json")for row in request.recommendation_costs])', '[row.model_dump(mode="json")for row in request.recommendation_costs],request.candidate_pick_route_id)')
out[str(p)]=s
p=Path("api/wms_api_server/app/modules/inventory/contracts_range_proposal.py");s=p.read_text(encoding="utf-8").replace("    reason: str\n\nclass", "    reason: str\n    candidate_pick_route_id: int | None = None\n\nclass")
out[str(p)]=s
p=Path("api/wms_api_server/app/modules/inventory/api/range_proposal_routes.py");s=p.read_text(encoding="utf-8").replace("request.expected_source_signature,request.reason)", "request.expected_source_signature,request.reason,request.candidate_pick_route_id)")
out[str(p)]=s
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/range_proposal.py");s=p.read_text(encoding="utf-8")
s=s.replace('        probe = self._command', '        if command.candidate_pick_route_id is not None:\n            body["candidate_pick_route_id"]=command.candidate_pick_route_id\n        probe = self._command',1)
s=s.replace("command.declared_pallet_gross_weight_kg, command.recommendation_costs)", "command.declared_pallet_gross_weight_kg, command.recommendation_costs, command.candidate_pick_route_id)")
out[str(p)]=s
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/range_apply.py");s=p.read_text(encoding="utf-8").replace('                    request["recommendation_costs"])', '                    request["recommendation_costs"],request.get("candidate_pick_route_id"))')
out[str(p)]=s
print(json.dumps(out))
