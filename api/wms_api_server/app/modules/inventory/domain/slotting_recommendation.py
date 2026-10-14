"""Conservative one-whole-pallet-per-face recommendation with explicit cost assumptions."""
from decimal import Decimal, localcontext
from typing import Any

def recommend_range(scenario: dict[str, Any], current: list[dict[str, Any]],
                    candidates: list[dict[str, Any]], costs: list[dict[str, Any]]) -> dict[str, Any]:
    cost_by_face = {int(row["pick_face_id"]): row for row in costs}
    if len(cost_by_face) != len(costs):
        raise ValueError("SLOTTING_DUPLICATE_FACE_COST")
    allowed = {int(row["pick_face_id"]) for row in candidates}
    if set(cost_by_face) - allowed:
        raise ValueError("SLOTTING_COST_OUTSIDE_CURRENT_CANDIDATES")
    required = scenario["nominal_additional_pallets"]
    existing_ids = {int(row["pick_face_id"]) for row in current}
    if required is None:
        return {"status": "PALLET_MULTIPLE_REQUIRED", "selected_faces": [], "applied": False}
    needed = int(Decimal(required))
    if needed > 100:
        return {"status": "RECOMMENDATION_PALLET_SCOPE_REQUIRED", "required_additional_whole_pallets": needed,
                "selected_faces": [], "physical_admission": False, "applied": False, "old_faces_preserved": True}
    ranked = []
    missing_cost = []
    with localcontext() as ctx:
        ctx.prec = 80
        for row in candidates:
            identity = int(row["pick_face_id"])
            if row["whole_pallet_nominal_fit"] is not True:
                continue
            cost = cost_by_face.get(identity)
            if cost is None:
                missing_cost.append(identity)
                continue
            quantity = Decimal(row["nominal_pallet_base_quantity"])
            picking = quantity * Decimal(cost["pick_seconds_per_base"])
            replenishing = Decimal(cost["replenish_seconds_per_pallet"])
            if min(picking, replenishing) < 0:
                raise ValueError("SLOTTING_NEGATIVE_COST")
            ranked.append({**row, "estimated_pick_seconds": format(picking, "f"),
                           "estimated_replenish_seconds": format(replenishing, "f"),
                           "estimated_total_seconds": format(picking + replenishing, "f")})
        ranked.sort(key=lambda row: (Decimal(row["estimated_total_seconds"]), int(row["pick_face_id"])))
        # Unknown feasible alternatives can change optimum, so never call partial costs optimal.
        complete = not missing_cost
        selected = ranked[:needed] if complete and len(ranked) >= needed else []
        total = sum((Decimal(row["estimated_total_seconds"]) for row in selected), Decimal(0))
    uncertain = any(row["refusal_reasons"] and not any("INSUFFICIENT" in reason for reason in row["refusal_reasons"])
                    for row in candidates)
    status = "NO_ADDITIONAL_PALLET_REQUIRED" if needed == 0 else "COST_ASSUMPTIONS_REQUIRED" if missing_cost else (
        "NOMINAL_RECOMMENDATION" if len(selected) == needed else "CAPACITY_EVIDENCE_REQUIRED" if uncertain else "INSUFFICIENT_NOMINAL_FACES")
    return {"status": status, "required_additional_whole_pallets": needed,
            "existing_face_count": len(existing_ids), "selected_faces": selected, "alternatives": ranked,
            "faces_without_declared_cost": missing_cost, "cost_comparison_complete": complete,
            "recommended_total_face_count": len(existing_ids) + sum(row["pick_face_id"] not in existing_ids for row in selected)
                if selected or needed == 0 else None,
            "estimated_total_additional_seconds": format(total, "f") if selected or needed == 0 else None,
            "capacity_assumption": "AT_MOST_ONE_ADDITIONAL_WHOLE_PALLET_PER_FACE",
            "cost_basis": "DECLARED_PICK_SECONDS_PER_BASE_AND_REPLENISH_SECONDS_PER_PALLET",
            "physical_admission": False, "applied": False, "old_faces_preserved": True,
            "missing_admission": ["ACTUAL_PALLET_GEOMETRY_AND_COMPATIBILITY", "RANGE_APPROVAL_AND_DRAIN_POLICY"]}
