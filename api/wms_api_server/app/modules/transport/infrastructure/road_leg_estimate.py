"""One authorised trip and legacy matrix snapshot; no provider call or route mutation."""
import json
from hashlib import sha256
from typing import Any
import oracledb
from ...platform.public import read_oracle_json
from ..domain.road_legs import ordered_stops,summarise_legs
from .trip_edit import trip_error

def road_leg_estimate(gateway: Any,trip: int,depot: str,max_age: int,actor: str) -> dict:
    try:
        with gateway.transaction("Current trip road-cache provenance READ ONLY")as cur:
            cur.execute("set transaction read only")
            return read_snapshot(cur,trip,depot,max_age,actor)
    except oracledb.DatabaseError as exc:raise trip_error(exc)from exc

def read_snapshot(cur: Any,trip: int,depot: str,max_age: int,actor: str,context: dict | None=None) -> dict:
    if context is None:
        out=cur.var(oracledb.DB_TYPE_CLOB);cur.callproc("RRL_TT_ROUTE_API.context",[trip,actor,out]);context=read_oracle_json(out.getvalue())
    stops,issues=ordered_stops(context["source"]["members"])
    origins=context["source"].get("warehouse_origins",[])
    configured=len(origins)==1 and origins[0].get("configured") is True
    if not depot:
        if configured:depot=origins[0]["depot_address"]
        else:issues.append("WAREHOUSE_DEPOT_NOT_CONFIGURED")
    depot_basis="CONFIGURED_WAREHOUSE_REFERENCE"if configured and depot==origins[0]["depot_address"]else "DISPATCHER_EXPLICIT_ADDRESS"if depot else "WAREHOUSE_DEPOT_UNKNOWN"

    pairs=list(zip([depot,*stops],[*stops,depot]))
    payload=cur.var(oracledb.DB_TYPE_CLOB)
    payload.setvalue(0,json.dumps([{"from_address":a,"to_address":b}for a,b in pairs]))
    cur.execute("""select /*+ leading(p m) use_nl(m) */ /* ROAD_LEGS_PK281 */ p.FROM_ADDR,p.TO_ADDR,
        RRL_STOCK_PLAN_HELPER.decimal_text(m.DISTANCE_KM),RRL_STOCK_PLAN_HELPER.decimal_text(m.DURATION_MIN),
        m.DURATION_BASIS,m.SOURCE,to_char(m.UPDATED_AT,'YYYY-MM-DD HH24:MI:SS'),
        case when m.UPDATED_AT>=sysdate-(:max_age/24)then 1 else 0 end,m.FROM_ADDR
        from json_table(:pairs,'$[*]'columns(FROM_ADDR varchar2(200)path '$.from_address',TO_ADDR varchar2(200)path '$.to_address'))p
        left join RRL_ADDR_DISTANCE_MATRIX m on m.FROM_ADDR=p.FROM_ADDR and m.TO_ADDR=p.TO_ADDR""",pairs=payload,max_age=max_age)
    costs={}
    for a,b,km,minutes,basis,provider,updated,fresh,found in cur.fetchall():
        if found is not None:costs[(a,b)]={"distance_km":km,"duration_min":minutes,"duration_basis":basis,
            "provider":provider,"updated_at":updated,"fresh":fresh==1}
    result=summarise_legs(depot,stops,costs,issues)
    result.update({"depot_basis":depot_basis,"warehouse_origin":origins[0]if len(origins)==1 else None,"trip_id":trip,"depot_address":depot,"source_hash":context["source_hash"],
                   "route_input_version":context["version"],"maximum_cache_age_hours":max_age,
                   "consistent_snapshot":True,"stock_changed":False})
    result["road_snapshot_signature"]=sha256(json.dumps(result,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    return result
