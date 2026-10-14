import json
from pathlib import Path
out={}
p=Path("api/wms_api_server/app/modules/inventory/domain/slotting_recommendation.py");s=p.read_text(encoding="utf-8").replace('        raise ValueError("SLOTTING_RECOMMENDATION_PALLET_BOUND_100")','        return {"status": "RECOMMENDATION_PALLET_SCOPE_REQUIRED", "required_additional_whole_pallets": needed,\n                "selected_faces": [], "physical_admission": False, "applied": False, "old_faces_preserved": True}')
s=s.replace('    status = "NO_ADDITIONAL_PALLET_REQUIRED"', '''    uncertain = any(row["refusal_reasons"] and not any("INSUFFICIENT" in reason for reason in row["refusal_reasons"])
                    for row in candidates)
    status = "NO_ADDITIONAL_PALLET_REQUIRED"''')
s=s.replace('"NOMINAL_RECOMMENDATION" if len(selected) == needed else "INSUFFICIENT_NOMINAL_FACES")','"NOMINAL_RECOMMENDATION" if len(selected) == needed else "CAPACITY_EVIDENCE_REQUIRED" if uncertain else "INSUFFICIENT_NOMINAL_FACES")')
out[str(p)]=s
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/slotting_candidates.py");s=p.read_text(encoding="utf-8")
s=s.replace('        raise SlottingError("SLOTTING_CANDIDATE_BOUND_100", "Сузьте складской диапазон кандидатов")','        return {"status": "CANDIDATE_SCOPE_REQUIRED", "selected_faces": [], "physical_admission": False,\n                "applied": False, "old_faces_preserved": True, "candidate_limit": 100}')
out[str(p)]=s
print(json.dumps(out))
