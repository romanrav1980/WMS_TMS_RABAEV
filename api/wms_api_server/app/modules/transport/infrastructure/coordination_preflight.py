"""Same snapshot of original approved times, warehouse promises and physical load."""
from datetime import datetime
from typing import Any
from ...inventory.public import read_optional_interwarehouse_incoming_snapshot, StoreReturnReceiveError
from ..contracts_plan import TransportPlanError
from ..contracts import TransportLoadingError
from .preflight_scope import dispatcher
from .trip_time_approval import read_time_context
from .loading_status import read_loading_status
from .time_preflight import read_trip_time
from .delivery_window_preview import read_delivery_windows

def coordination(gateway: Any, trip: int, actor: str) -> dict[str, Any]:
    try:
        with gateway.transaction("Original warehouse-transport coordination READ ONLY") as cur:
            cur.execute("set transaction read only")
            return read_coordination(cur,trip,actor)
    except (TransportLoadingError,StoreReturnReceiveError)as exc:
        raise TransportPlanError(exc.code,str(exc),exc.status)from exc


def read_coordination(cur: Any,trip: int,actor: str) -> dict[str,Any]:
    dispatcher(cur,actor)
    time=read_time_context(cur,trip,actor)
    load=read_loading_status(cur,trip,actor)
    incoming=read_optional_interwarehouse_incoming_snapshot(cur,trip,actor)
    blockers=[]
    cutoff=None
    if time["approval_status"]!="APPROVED":
        blockers.append({"code":"COORDINATION_TIME_NOT_CURRENT_APPROVED"})
    else:
        stages=[op for op in time["last_approval"]["operations"]if op["code"]=="LOADING"]
        if len(stages)!=1:
            blockers.append({"code":"COORDINATION_LOADING_STAGE_REQUIRED"})
        else:
            cutoff=stages[0]["start_at"]
    if not load["members"]:
        blockers.append({"code":"COORDINATION_ORIGINAL_ST_MEMBERS_REQUIRED"})
    if load["pending_st_ids"]:
        blockers.append({"code":"COORDINATION_PHYSICAL_LOADING_PENDING","st_ids":load["pending_st_ids"]})
    if time["approval_status"]=="APPROVED":
        zone=time["last_approval"]["time_zone"]
        temporal=read_trip_time(cur,trip,zone,actor)
        windows=read_delivery_windows(cur,trip,"",24,zone,actor)
        blockers.extend({"code":"COORDINATION_RESOURCE_CONFLICT","trip_id":x["trip_id"]}for x in temporal["conflicts"])
        blockers.extend({"code":x["code"]}for x in temporal["issues"])
        blockers.extend({"code":x["code"]}for x in temporal["driver_rest"]["violations"])
        blockers.extend({"code":x["code"]}for x in temporal["driver_rest"]["unknown_intervals"])
        blockers.extend({"code":x["code"],"address":x.get("address")}for x in windows["issues"])
        if any(d["limit_exceeded"]for d in temporal["driver_days"]["days"]):
            blockers.append({"code":"COORDINATION_DRIVER_DAY_LIMIT_EXCEEDED"})
        for day in temporal["driver_days" ]["days"]:
            blockers.extend({"code":x["code"],"local_day":day["local_day"],"operation_id":x.get("operation_id")}for x in day["continuity"]["violations"] )
        if not temporal["driver_days"]["days"] or any(not d["recorded_plan_coverage_complete"]for d in temporal["driver_days"]["days"]):
            blockers.append({"code":"COORDINATION_DRIVER_DAY_INCOMPLETE"})
    else:
        temporal={"status":"CURRENT_APPROVED_REGION_REQUIRED"}
        windows={"status":"CURRENT_APPROVED_REGION_REQUIRED","operational_admission":False}
    placed=0
    for plan in incoming["plans"]:
        ready=(plan["receipt_operation_state"]=="APPLIED"
               and plan["placement_operation_state"]=="APPLIED"
               and plan["placed_task_id"] is not None)
        plan["accepted_part_placement_completed"]=ready
        if plan.get("receipt_complete",1)!=1 and plan.get("shortage_resolved",0)!=1:
            ready=False
            blockers.append({"code":"COORDINATION_INCOMING_RECEIPT_INCOMPLETE","plan_operation_id":plan["operation_id"],
                "received_quantity":plan.get("received_quantity"),"short_quantity":plan.get("short_quantity")})
        placed+=int(ready)
        plan["warehouse_placement_completed"]=ready and plan.get("receipt_complete",1)==1
        plan["incoming_accounted_placement_completed"]=ready
        if not ready:
            blockers.append({"code":"COORDINATION_WAREHOUSE_PLACEMENT_PENDING","plan_operation_id":plan["operation_id"]})
        if plan["temperature_decision"]=="HOLD":
            blockers.append({"code":"COORDINATION_TEMPERATURE_HOLD","plan_operation_id":plan["operation_id"]})
        if cutoff:
            due=datetime.fromisoformat(plan["ready_due"])
            start=datetime.fromisoformat(cutoff)
            plan["ready_promise_after_loading_start"]=due>start
            if not ready and due>start:
                blockers.append({"code":"COORDINATION_READY_PROMISE_AFTER_LOADING","plan_operation_id":plan["operation_id"]})
            if ready and plan["placed_at"]:
                plan["actual_placement_after_loading_start"]=datetime.fromisoformat(plan["placed_at"])>start
                if plan["actual_placement_after_loading_start"]:
                    blockers.append({"code":"COORDINATION_ACTUAL_PLACEMENT_AFTER_LOADING","plan_operation_id":plan["operation_id"]})
    if incoming["expected_deliveries"] and not incoming["incoming_ready"]:
        blockers.append({"code":"COORDINATION_EXPECTED_CARGO_NOT_LOADED"})
    if load["trip"]["condition"]!="Спланирован":
        blockers.append({"code":"COORDINATION_PLANNED_TRIP_REQUIRED"})
    return {"trip_id":trip,"consistent_snapshot":True,"read_only":True,
        "time":time,"temporal":temporal,"delivery_windows":windows,"loading":load,"incoming":incoming,"loading_start_at":cutoff,
        "warehouse_placed_deliveries":sum(int(p["warehouse_placement_completed"])for p in incoming["plans"]),
        "incoming_accounted_placed_deliveries":placed,"blockers":blockers,
        "status":"BLOCKED"if blockers else"CURRENT_RECORDED_PHASES_COMPLETE",
        "operational_admission":False,"departure_authorized":False,
        "unverified_constraints":["APPLICABLE_DRIVER_LAW_AND_OUTSIDE_WMS_DUTIES","DESTINATION_TIME_ZONE_AND_PHYSICAL_ORIGIN",
            "CURRENT_NATIVE_QC_AND_CAPACITY_RECHECK"]}
