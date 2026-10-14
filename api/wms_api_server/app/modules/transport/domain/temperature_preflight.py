"""Exact feasibility of one shared temperature environment; no physical admission."""
from decimal import Decimal, InvalidOperation

def temperature_preflight(requirements: dict, vehicle_profile: dict | None) -> dict:
    result={"basis":"SINGLE_SHARED_TEMPERATURE_ENVIRONMENT","profile_version":None,
            "vehicle_capability_verified":False,"planning_temperature_verified":False,
            "measurement_verified":False,"operational_admission":False,
            "feasible_min_c":None,"feasible_max_c":None}
    if requirements.get("ranges_conflict"):
        return {**result,"status":"SKU_RANGES_CONFLICT"}
    if not requirements.get("all_ranges_configured"):
        return {**result,"status":"SKU_REQUIREMENTS_UNCONFIRMED"}
    if not vehicle_profile or vehicle_profile.get("state")!="READY":
        return {**result,"status":"VEHICLE_PROFILE_UNCONFIRMED"}
    capability=(vehicle_profile.get("profile") or {}).get("temperature_capability")
    if not isinstance(capability,dict):
        return {**result,"status":"VEHICLE_RANGE_UNCONFIRMED"}
    try:
        lo=Decimal(capability["temp_min_c"]);hi=Decimal(capability["temp_max_c"])
        required_lo=Decimal(requirements["common_min_c"]) if requirements.get("common_min_c") is not None else None
        required_hi=Decimal(requirements["common_max_c"]) if requirements.get("common_max_c") is not None else None
        values=(lo,hi,required_lo,required_hi)
        if any(x is not None and not x.is_finite() for x in values) or lo>hi:
            raise ValueError("invalid range")
    except (KeyError,InvalidOperation,TypeError,ValueError):
        return {**result,"status":"VEHICLE_OR_REQUIREMENT_RANGE_INVALID"}
    result.update(profile_version=vehicle_profile["version"],vehicle_capability_verified=True,
                  vehicle_min_c=str(lo),vehicle_max_c=str(hi))
    feasible_lo=max(lo,required_lo) if required_lo is not None else lo
    feasible_hi=min(hi,required_hi) if required_hi is not None else hi
    if feasible_lo>feasible_hi:
        return {**result,"status":"VEHICLE_RANGE_INCOMPATIBLE"}
    return {**result,"status":"DECLARED_CAPABILITY_COMPATIBLE","planning_temperature_verified":True,
            "feasible_min_c":str(feasible_lo),"feasible_max_c":str(feasible_hi)}
