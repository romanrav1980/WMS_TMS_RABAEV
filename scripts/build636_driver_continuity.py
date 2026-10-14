from pathlib import Path
import json
p=Path("api/wms_api_server/app/modules/transport/domain/driver_day.py");v=p.read_text(encoding="utf-8")
v=v.replace("from .driver_rest import DRIVE_CODES, TRIP_DRIVE_MIN","from .driver_rest import DRIVE_CODES, TRIP_DRIVE_MIN, evaluate_driver_rest")
v+='''
def planned_day_continuity(operations: list[dict[str, Any]], start_at: str, end_at: str) -> dict[str, Any]:
    """Continue across trip boundaries; midnight and other work are not rest."""
    begin, finish = datetime.fromisoformat(start_at), datetime.fromisoformat(end_at)
    seen: set[int] = set()
    chain: list[dict[str, Any]] = []
    intersecting: set[int] = set()
    for operation in operations:
        key = operation["operation_id"]
        if key in seen:
            continue
        seen.add(key)
        a, b = operation["plan_start_at"], operation["plan_end_at"]
        if a is None or b is None:
            chain.append(operation)
            intersecting.add(key)
            continue
        start, end = datetime.fromisoformat(a), datetime.fromisoformat(b)
        if start >= finish:
            continue
        if end > begin or end <= start:
            intersecting.add(key)
        chain.append({**operation, "plan_end_at": min(end, finish).isoformat()})
    chain.sort(key=lambda op: (op["plan_start_at"] is None,
        datetime.fromisoformat(op["plan_start_at"]).timestamp() if op["plan_start_at"] else 0,
        op["operation_id"]))
    measured = evaluate_driver_rest(chain)
    violations = [item for item in measured["violations"]
        if item["code"] != "DRIVER_TRIP_DRIVE_LIMIT" and item.get("operation_id") in intersecting]
    return {"coverage": "RECORDED_APPROVED_CROSS_TRIP_CHAIN",
        "initial_continuity_verified": False, "legal_compliance_verified": False,
        "continuous_limit_min": measured["continuous_limit_min"],
        "minimum_break_min": measured["minimum_break_min"],
        "violations": violations, "unknown_intervals": measured["unknown_intervals"],
        "status": "VIOLATIONS" if violations else
            "INSUFFICIENT_EVIDENCE" if measured["unknown_intervals"] or not chain else "NO_OBSERVED_CHAIN_VIOLATION"}
'''
out={str(p):v}
p=Path("api/wms_api_server/app/modules/transport/infrastructure/driver_day.py");v=p.read_text(encoding="utf-8")
v=v.replace("from ..domain.driver_day import planned_day_drive","from ..domain.driver_day import planned_day_drive, planned_day_continuity")
a='total = planned_day_drive(all_ops, start_at, end_at)'
v=v.replace(a,a+'\n        continuity = planned_day_continuity(all_ops, start_at, end_at)')
v=v.replace('"end_at": end_at, "sources": sources, "unresolved_trip_ids": unresolved, **total,','"end_at": end_at, "sources": sources, "unresolved_trip_ids": unresolved, "continuity": continuity, **total,')
v=v.replace('not unresolved and not total["unknown_drive_operation_ids"]','not unresolved and not total["unknown_drive_operation_ids"] and not continuity["unknown_intervals"]')
v=v.replace('any(d["limit_exceeded"] for d in base["days"])','any(d["limit_exceeded"] or d["continuity"]["violations"] for d in base["days"])')
out[str(p)]=v
p=Path("admin/wms_admin_frontend/src/components/TransportDriverDay.tsx");v=p.read_text(encoding="utf-8")
v=v.replace('unresolved_trip_ids: number[]; unknown_drive_operation_ids: number[];','unresolved_trip_ids: number[]; unknown_drive_operation_ids: number[];\n    continuity?: {continuous_limit_min:string;minimum_break_min:string;violations:{code:string;operation_id?:number;continuous_min?:string}[];unknown_intervals:{code:string;operation_id?:number}[]};')
a='      {day.unknown_drive_operation_ids.length > 0'
b='''      {day.continuity && <p>Непрерывное вождение между рейсами: лимит {day.continuity.continuous_limit_min} мин; перерыв не менее {day.continuity.minimum_break_min} мин.
        {day.continuity.violations.length > 0 && <strong> Есть нарушение непрерывного вождения или перерыва.</strong>}
        {day.continuity.unknown_intervals.length > 0 && <span> Цепочка работы содержит пропуски или пересечения; уточните план.</span>}</p>}
      {day.unknown_drive_operation_ids.length > 0'''
assert a in v;out[str(p)]=v.replace(a,b)
print(json.dumps(out,ensure_ascii=True))
