"""Explain planned capacity gaps and one-person duration scenarios; no staff availability invented."""
from datetime import datetime,timedelta
from decimal import Decimal,localcontext,ROUND_CEILING
from typing import Any
from .workload_intervals import hours

def workload_recommendations(intervals: list[dict[str,Any]], work: list[dict[str,Any]]) -> dict[str,Any]:
    capacity=[];unresolved=[]
    with localcontext()as ctx:
        ctx.prec=80
        for row in intervals:
            deficit=row["deficit_person_hours"]
            if deficit is None:
                unresolved.append({"from_utc":row["from_utc"],"to_utc":row["to_utc"],
                    "missing_norm_line_ids":row["missing_norm_line_ids"],"unscheduled_line_ids":row["unscheduled_line_ids"]})
                continue
            gap=Decimal(deficit)
            if gap<=0:continue
            span=hours(datetime.fromisoformat(row["from_utc"]),datetime.fromisoformat(row["to_utc"]))
            capacity.append({"from_utc":row["from_utc"],"to_utc":row["to_utc"],
                "additional_planned_person_hours":format(gap,"f"),
                "additional_full_interval_people":int((gap/span).to_integral_value(rounding=ROUND_CEILING)),
                "existing_planned_person_hours":row["planned_person_hours"],
                "future_person_availability_confirmed":False,"action":"PLAN_ADDITIONAL_CASE_CAPACITY"})
        by_wave: dict[int,list[dict[str,Any]]]={}
        for row in work:by_wave.setdefault(int(row["pick_wave_id"]),[]).append(row)
        scenarios=[]
        for wave,rows in sorted(by_wave.items()):
            missing=[r["case_pick_line_id"]for r in rows if r["base_per_hour"]is None]
            windows={r.get("window")for r in rows}
            if missing or None in windows or len(windows)!=1:
                scenarios.append({"wave_id":wave,"status":"CURRENT_NORM_AND_SINGLE_WINDOW_REQUIRED","missing_norm_line_ids":missing})
                continue
            start,finish=next(iter(windows))
            required=sum((Decimal(r["remaining_quantity"])/Decimal(r["base_per_hour"])for r in rows),Decimal(0))
            duration=int((required*Decimal(3600000000)).to_integral_value(rounding=ROUND_CEILING))
            bounded=0<duration<=86400000000
            scenarios.append({"wave_id":wave,"status":"ONE_PERSON_DURATION_SCENARIO"if bounded else"ONE_PERSON_WINDOW_BOUND_24H",
                "known_remaining_person_hours":format(required,"f"),"current_from_utc":start.isoformat(),
                "current_to_utc":finish.isoformat(),"one_person_to_utc":(start+timedelta(microseconds=duration)).isoformat()if bounded else None,
                "one_person_required_seconds":None if not bounded else format(Decimal(duration)/1000000,"f"),
                "current_window_change_required":bounded and duration>hours(start,finish)*3600000000,
                "named_person_assigned":False,"wave_time_applied":False})
    return {"capacity_actions":capacity,"unresolved_intervals":unresolved,"wave_duration_scenarios":scenarios,
        "status":"SOURCE_COMPLETION_REQUIRED"if unresolved else"CAPACITY_ACTIONS"if capacity else"NO_ESTIMATED_INTERVAL_DEFICIT",
        "basis":"EXISTING_REMAINING_CASE_WORK_AND_DECLARED_NORM_UNIFORM_WITHIN_WAVE",
        "operational_admission":False,"actual_presence_changed":False,"planned_attendance_applied":False,
        "task_assignments_changed":False,"missing_admission":["NAMED_PERSON_AVAILABILITY","BREAKS_AND_EQUIPMENT",
            "REPLENISHMENT_AND_PICK_RELEASE","JOINT_WAVE_TRANSPORT_CUTOFF"]}
