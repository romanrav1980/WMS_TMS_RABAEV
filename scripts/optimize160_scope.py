import json
from pathlib import Path
out={}
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/slotting_candidates.py");s=p.read_text(encoding="utf-8")
s=s.replace('    # Empty dynamic faces;', '    route_clause=" and pf.PICK_ROUTE_ID=:route "if candidate_route is not None else" "\n    candidate_binds={"ware":ware,**({"route":candidate_route}if candidate_route is not None else{})}\n    # Empty dynamic faces;')
s=s.replace("and (:route is null or pf.PICK_ROUTE_ID=:route)and (pf.PICK_FACE_TYPE", '"""+route_clause+"""and (pf.PICK_FACE_TYPE')
s=s.replace('order by pf.PICK_FACE_ID fetch first 101 rows only""", ware=ware,route=candidate_route)', 'order by pf.PICK_FACE_ID fetch first 101 rows only""", candidate_binds)')
out[str(p)]=s
p=Path("db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json");m=json.loads(p.read_text(encoding="utf-8"))
m["additional_scripts"].append("../2026-10-10_ni081_cell_commitment_indexes/apply.sql")
out[str(p)]=json.dumps(m,ensure_ascii=False,indent=2)+"\n"
print(json.dumps(out))
