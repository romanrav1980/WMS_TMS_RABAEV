"""Preserve solver schedule in the existing plan and API; no dispatch approval."""
from typing import Any
from .vrp_models import VrpRoute

ASSUMPTIONS = [
    "MINUTES_FROM_LEGACY_06_SHIFT_NOT_ZONED_INSTANTS",
    "VIRTUAL_DEPOT_AT_ORDER_CENTROID",
    "TRAVEL_AT_CONSTANT_50_KMH",
    "DRIVER_BREAKS_AND_WAREHOUSE_RELEASE_NOT_VALIDATED",
]


def schedule_evidence(route: VrpRoute) -> dict[str, Any]:
    return {
        "schedule_status": route.schedule_status,
        "schedule_start_min": route.schedule_start_min,
        "schedule_end_min": route.schedule_end_min,
        "schedule_assumptions":[v for v in ASSUMPTIONS if not(route.road_profile_legs and v=="TRAVEL_AT_CONSTANT_50_KMH")and not(route.depot_basis=="CONFIGURED_WAREHOUSE_REFERENCE"and v=="VIRTUAL_DEPOT_AT_ORDER_CENTROID")]+(["MIXED_ROAD_PROFILE_AND_SPEED_ESTIMATES"]if route.road_profile_legs else []),
        "road_profile_legs":route.road_profile_legs,"depot_basis":route.depot_basis,
        "operational_admission": False,
    }


def route_payload(route: VrpRoute) -> dict[str, Any]:
    return {
        "vehicle_id": route.vehicle.id, "vehicle_num": route.vehicle.num,
        "stops": [stop.st_number for stop in route.stops],
        "total_km": route.total_km, "total_pallets": route.total_pallets,
        "total_kg": route.total_kg, "total_duration_min": route.total_duration_min,
        "stop_schedule": route.schedule, **schedule_evidence(route),
    }


def route_response(route: VrpRoute) -> dict[str, Any]:
    timings = {entry["st_number"]: entry for entry in route.schedule}
    stops = []
    for order in route.stops:
        timing = timings.get(order.st_number, {})
        stops.append({
            "st_number": order.st_number, "addr": order.addr, "lat": order.lat,
            "lon": order.lon, "pallets": order.pallets, "weight_kg": order.weight_kg,
            "ware_id": order.ware_id, "unload_norm_min": order.unload_norm_min,
            "tw_from": order.tw_from, "tw_to": order.tw_to, "tw_strict": order.tw_strict,
            "arrival_min": timing.get("arrival_min"),
            "departure_min": timing.get("departure_min"),
            "tw_violation_min": timing.get("tw_violation_min", 0),
            "distance_from_prev_km": timing.get("distance_from_prev_km"),
            "duration_from_prev_min": timing.get("duration_from_prev_min"),
            "duration_from_prev_basis":timing.get("duration_from_prev_basis","UNRECORDED"),
            "constraint_notes": [] if timing else ["SCHEDULE_UNAVAILABLE_NOT_WINDOW_VALIDATION"],
        })
    return {
        "vehicle_id": route.vehicle.id, "vehicle_num": route.vehicle.num,
        "vehicle_type": route.vehicle.tr_type, "max_pallets": route.vehicle.max_pallets,
        "total_pallets": route.total_pallets, "total_kg": route.total_kg,
        "total_km": route.total_km, "total_duration_min": route.total_duration_min,
        "utilization_pct": route.utilization_pct, "stops": stops,
        "capacity_status": "over" if route.utilization_pct > 100 else "low" if route.utilization_pct < 60 else "ok",
        "tw_violation_count": sum(int(entry["tw_violation_min"] > 0) for entry in route.schedule),
        "strict_tw_count": sum(int(order.tw_strict) for order in route.stops),
        "vehicle_constraints_ok": route.utilization_pct <= 100,
        "hydro_board_required_count": 0,
        "explain_notes": ["RELATIVE_SCHEDULE_NOT_OPERATIONAL_ADMISSION"] if route.schedule else ["SCHEDULE_UNAVAILABLE"],
        **schedule_evidence(route),
    }

def planner_constraint_evidence(routes: list[VrpRoute], fallback_windows: int) -> dict[str, Any]:
    return {
        "capacity_pallets": True, "capacity_weight": True,
        "time_windows": bool(routes) and all(route.schedule_status == "RELATIVE_SOLVER_SCHEDULE" for route in routes),
        "operational_admission": False, "vehicle_type": True, "hydro_board": True,
        "fallback_time_windows": fallback_windows,
    }
