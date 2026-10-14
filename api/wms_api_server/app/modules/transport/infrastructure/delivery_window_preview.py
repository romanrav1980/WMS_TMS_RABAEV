"""One current Oracle snapshot of original ST windows, route and road provenance."""
from typing import Any
import oracledb
from ...platform.public import read_oracle_json
import json
from ..contracts_plan import TransportPlanError
from .trip_edit import trip_error

def delivery_window_preview(gateway: Any,trip: int,depot: str,max_age: int,zone: str,actor: str) -> dict:
    try:
        with gateway.transaction("Current original delivery windows READ ONLY")as cur:
            cur.execute("set transaction read only")
            return read_delivery_windows(cur,trip,depot,max_age,zone,actor)
    except oracledb.DatabaseError as exc:raise trip_error(exc)from exc

def read_delivery_windows(cur: Any,trip: int,depot: str,max_age: int,zone: str,actor: str) -> dict:
    out=cur.var(oracledb.DB_TYPE_CLOB)
    cur.callproc("RRL_TT_TIME_API.context",[trip,actor,out]);context=read_oracle_json(out.getvalue())
    material=context["source"]["route_material"]
    if max_age!=material["maximum_cache_age_hours"] or (depot and depot!=material["depot_address"]):
        raise TransportPlanError("ROUTE_APPROVAL_POLICY_REQUIRED","Используйте базу склада и действующий срок дорожных данных: 24 часа",422)
    wire=cur.var(oracledb.DB_TYPE_CLOB);wire.setvalue(0,json.dumps(context["source"],ensure_ascii=False))
    cur.callproc("RRL_TT_ROUTE_SCHEDULE.calculate",[wire,zone,out]);result=read_oracle_json(out.getvalue())
    profiles = {p["address"]: p for p in context["source"].get("store_window_profiles", [])}
    for stop in result.get("stops", []):
        profile = profiles.get(stop.get("address"))
        if profile is not None:
            stop["profile_version"] = profile.get("profile_version")
            stop["store_window_mode"] = profile.get("mode", "UNCONFIGURED")
            stop["store_time_zone"] = profile.get("time_zone")
            stop["configured_weekly_windows"] = profile.get("windows", [])
    result.update({"trip_id":trip,"source_hash":context["source_hash"],"consistent_snapshot":True})
    return result
