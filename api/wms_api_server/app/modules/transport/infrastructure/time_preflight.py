"""Bounded original ARM occupancy in an explicitly selected wall-time region."""
from datetime import datetime
from typing import Any
from ..contracts_plan import TransportPlanError
from ..domain.driver_rest import evaluate_driver_rest
from .trip_time_approval import read_time_context
from .time_snapshot import trip_scope, original_operations
from .driver_day import read_driver_days
from .approved_schedule import planned_operations

ZONES = {"UTC", "Europe/Moscow", "Asia/Tbilisi"}

def trip_time_preview(gateway: Any, trip: int, zone: str, actor: str) -> dict[str, Any]:
    if zone not in ZONES:
        raise TransportPlanError("TIME_EXPLICIT_REGION_REQUIRED", "Выберите часовой пояс", 422)
    with gateway.transaction("Original ARM temporal occupancy READ ONLY snapshot") as cur:
        cur.execute("set transaction read only")
        return read_trip_time(cur,trip,zone,actor)


def read_trip_time(cur: Any,trip: int,zone: str,actor: str) -> dict[str,Any]:
    header = trip_scope(cur, trip, actor)
    current_time = read_time_context(cur, trip, actor)
    requested_zone = zone
    if current_time["approval_status"] == "APPROVED":
        zone = current_time["last_approval"]["time_zone"]
    operations = original_operations(cur, trip, zone)
    issues = []
    if current_time["approval_status"] in {"SOURCE_CHANGED", "LEGACY_SOURCE_CONTRACT"}:
        issues.append({"code":"TIME_SOURCE_APPROVAL_CHANGED"})
    if not operations:
        issues.append({"code": "TIME_ORIGINAL_OPERATIONS_REQUIRED"})
    valid = []
    for operation in operations:
        start, finish = operation["plan_start_at"], operation["plan_end_at"]
        if start is None or finish is None or datetime.fromisoformat(finish) < datetime.fromisoformat(start):
            issues.append({"code": "TIME_OPERATION_INTERVAL_INVALID", "operation_id": operation["operation_id"]})
        else:
            valid.append(operation)
    conflicts = []
    start_at = min((r["plan_start_at"] for r in valid), default=None)
    finish_at = max((r["plan_end_at"] for r in valid), default=None)
    if start_at and finish_at:
        if datetime.fromisoformat(finish_at) == datetime.fromisoformat(start_at):
            issues.append({"code":"TIME_POSITIVE_WINDOW_REQUIRED"})
        if (datetime.fromisoformat(finish_at)-datetime.fromisoformat(start_at)).total_seconds() > 7*86400:
            raise TransportPlanError("TIME_WINDOW_BOUND_7_DAYS", "Проверка ограничена семью днями")
        # Half-open intervals: an operation ending at start does not overlap.
        cur.execute("""select distinct t.ID,t.TRANSPORT,t.VODITEL_ID
            from RRL_TRANSPORT_TASK t join RRL_TT_OPERATIONS o on o.TT_ID=t.ID
            where t.ID!=:trip_id and nvl(t.DELETED,0)=0
            and ((:plate is not null and t.TRANSPORT=:plate)
              or (:driver_id is not null and t.VODITEL_ID=:driver_id))
            and coalesce(o.FACT_START,o.PLAN_START)<cast(to_timestamp_tz(:finish_at,'YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM') at time zone 'UTC' as date)+4/24
            and ((o.FACT_START is not null and o.FACT_END is null)
              or coalesce(o.FACT_END,o.PLAN_END)>cast(to_timestamp_tz(:start_at,'YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM') at time zone 'UTC' as date))
            order by t.ID fetch first 201 rows only""",
            trip_id=trip, plate=header[1], driver_id=header[2], start_at=start_at, finish_at=finish_at)
        candidates = cur.fetchall()
        if len(candidates) > 200:
            raise TransportPlanError("TIME_CONFLICT_TRIP_BOUND_200", "Превышена граница рейсов; сузьте окно")
        count = 0
        begin, end = datetime.fromisoformat(start_at), datetime.fromisoformat(finish_at)
        for other_id, plate, driver in candidates:
            trip_scope(cur, other_id, actor)
            other_time = read_time_context(cur, other_id, actor)
            other_zone = zone
            if other_time["approval_status"] == "APPROVED":
                other_zone = other_time["last_approval"]["time_zone"]
            elif other_time["approval_status"] in {"SOURCE_CHANGED", "LEGACY_SOURCE_CONTRACT"}:
                issues.append({"code":"TIME_OTHER_APPROVAL_CHANGED", "trip_id":other_id})
            for other in original_operations(cur, other_id, other_zone):
                count += 1
                if count > 2000:
                    raise TransportPlanError("TIME_CONFLICT_OPERATION_BOUND_2000", "Превышена граница операций конфликтов")
                a = other["fact_start_at"] or other["plan_start_at"]
                open_fact = other["fact_start_at"] is not None and other["fact_end_at"] is None
                b = other["fact_end_at"] if other["fact_start_at"] else other["plan_end_at"]
                if a and datetime.fromisoformat(a) < end and (open_fact or (b and datetime.fromisoformat(b) > begin)):
                    conflicts.append({"trip_id":other_id,"operation":other,
                        "time_zone":other_zone,"time_approval_status":other_time["approval_status"],
                        "vehicle_conflict":bool(header[1] and plate==header[1]),
                        "driver_conflict":bool(header[2] and driver==header[2]),
                        "occupancy_basis":"RECORDED_OPEN_FACT" if open_fact else "RECORDED_FACT_WITH_PLAN_FALLBACK"})
    if not header[1]:
        issues.append({"code":"TIME_VEHICLE_REQUIRED"})
    if header[2] is None or header[2] <= 0:
        issues.append({"code":"TIME_DRIVER_REQUIRED"})
    if header[5]:
        issues.append({"code":"TIME_DELETED_TRIP"})
    return {"trip_id":trip,"time_zone":zone,"requested_time_zone":requested_zone,
        "time_approval_status":current_time["approval_status"],
        "time_basis":"APPROVED_ORIGINAL_PLANNED_TIME_REGION" if current_time["approval_status"]=="APPROVED" else "EXPLICIT_LEGACY_WALL_TIME_INTERPRETATION",
        "operations":operations,"driver_rest":evaluate_driver_rest(planned_operations(current_time, operations)),
        "driver_days":read_driver_days(cur,trip,actor,zone,header[2],planned_operations(current_time, operations)),"start_at":start_at,"finish_at":finish_at,"conflicts":conflicts,"issues":issues,
        "status":"BLOCKED" if conflicts or issues else "NO_RECORDED_OCCUPANCY_CONFLICT",
        "read_only":True,"operational_admission":False,
        "unverified_constraints":["APPROVED_AWARE_SCHEDULE","DRIVER_REST_AND_DAILY_LIMITS",
            "WAREHOUSE_READY_AND_LOADING","ACTUAL_EXTERNAL_ROUTE_DURATION"]}
