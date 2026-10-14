"""Bounded driver-day read in caller's existing Oracle snapshot."""
from datetime import date, datetime, timedelta
from typing import Any
from ..contracts_plan import TransportPlanError
from ..domain.driver_day import planned_day_drive, planned_day_continuity
from .time_snapshot import trip_scope, original_operations
from .trip_time_approval import read_time_context
from .approved_schedule import planned_operations


def day_window(cur: Any, local_day: date, zone: str) -> tuple[str, str]:
    cur.execute("""select
        to_char(from_tz(cast(to_date(:day,'YYYY-MM-DD') as timestamp),:zone) at time zone 'UTC','YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM'),
        to_char(from_tz(cast(to_date(:day,'YYYY-MM-DD')+1 as timestamp),:zone) at time zone 'UTC','YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM')
        from dual""", day=local_day.isoformat(), zone=zone)
    return cur.fetchone()


def read_driver_days(cur: Any, trip: int, actor: str, zone: str, driver: int | None,
                     current_ops: list[dict[str, Any]]) -> dict[str, Any]:
    base = {"coverage": "RECORDED_SOURCE_APPROVED_PLANNED_TRIPS", "time_zone": zone,
            "driver_id": driver, "driver_day_complete": False, "legal_compliance_verified": False,
            "operational_admission": False, "days": [],
            "unverified": ["OUTSIDE_WMS_DUTIES", "PRIOR_DUTY", "APPLICABLE_LEGAL_RULES"]}
    if not driver or driver <= 0:
        return {**base, "status": "DRIVER_REQUIRED"}
    spans = [op for op in current_ops if op["plan_start_at"] and op["plan_end_at"]]
    if not spans:
        return {**base, "status": "PLANNED_WINDOW_REQUIRED"}
    begin = min(datetime.fromisoformat(op["plan_start_at"]) for op in spans).date()
    last = max(datetime.fromisoformat(op["plan_end_at"]) for op in spans).date()
    if (last - begin).days > 7:
        raise TransportPlanError("DRIVER_DAY_WINDOW_BOUND_7", "Сузьте окно проверки водителя")
    operation_count = 0
    for offset in range((last - begin).days + 1):
        local_day = begin + timedelta(days=offset)
        start_at, end_at = day_window(cur, local_day, zone)
        cur.execute("""select distinct t.ID from RRL_TRANSPORT_TASK t
            left join RRL_TT_OPERATIONS o on o.TT_ID=t.ID
            where t.VODITEL_ID=:driver_id and nvl(t.DELETED,0)=0
            and ((o.PLAN_START<cast(to_timestamp_tz(:end_at,'YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM') at time zone 'UTC' as date)+4/24
            and o.PLAN_END>cast(to_timestamp_tz(:start_at,'YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM') at time zone 'UTC' as date))
              or (t.SHIPMENT_DATE>=trunc(cast(to_timestamp_tz(:start_at,'YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM') at time zone 'UTC' as date))
                and t.SHIPMENT_DATE<trunc(cast(to_timestamp_tz(:end_at,'YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM') at time zone 'UTC' as date))+1))
            order by t.ID fetch first 201 rows only""", driver_id=driver,
            start_at=start_at, end_at=end_at)
        ids = [row[0] for row in cur.fetchall()]
        if len(ids) > 200:
            raise TransportPlanError("DRIVER_DAY_TRIP_BOUND_200", "Сузьте окно рейсов водителя")
        if trip not in ids:
            if len(ids) >= 200:
                raise TransportPlanError("DRIVER_DAY_TRIP_BOUND_200", "Сузьте окно рейсов водителя")
            ids.append(trip)
        all_ops: list[dict[str, Any]] = []
        sources: list[dict[str, Any]] = []
        unresolved: list[int] = []
        for other in ids:
            trip_scope(cur, other, actor)
            context = read_time_context(cur, other, actor)
            if context["approval_status"] != "APPROVED":
                unresolved.append(other)
                continue
            ops = planned_operations(context, original_operations(cur, other, context["last_approval"]["time_zone"]))
            operation_count += len(ops)
            if operation_count > 2000:
                raise TransportPlanError("DRIVER_DAY_OPERATION_BOUND_2000", "Сузьте окно операций водителя")
            measured = planned_day_drive(ops, start_at, end_at)
            all_ops.extend(ops)
            sources.append({"trip_id": other, "time_zone": context["last_approval"]["time_zone"],
                            "source_hash": context["source_hash"], **measured})
        total = planned_day_drive(all_ops, start_at, end_at)
        continuity = planned_day_continuity(all_ops, start_at, end_at)
        base["days"].append({"local_day": local_day.isoformat(), "start_at": start_at,
            "end_at": end_at, "sources": sources, "unresolved_trip_ids": unresolved, "continuity": continuity, **total,
            "recorded_plan_coverage_complete": not unresolved and not total["unknown_drive_operation_ids"] and not continuity["unknown_intervals"]})
    base["status"] = "PLANNING_LIMIT_EXCEEDED" if any(d["limit_exceeded"] or d["continuity"]["violations"] for d in base["days"]) else "RECORDED_PLANNED_DRIVING_ONLY"
    return base
