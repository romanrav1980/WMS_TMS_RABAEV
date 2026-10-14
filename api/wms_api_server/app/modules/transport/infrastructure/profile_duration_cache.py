"""One bounded snapshot of the existing solver distance/time cache."""
import json
from typing import Any
import oracledb
from ...platform.public import read_oracle_json

def read_cost_cache(cur: Any,addresses: list[str]) -> tuple[dict,dict,str]:
    keys=sorted(set(addresses))
    if not keys:return {},{},"haversine"
    if len(keys)>201:raise ValueError("VRP_ROAD_CACHE_ADDRESS_BOUND_201")
    payload=cur.var(oracledb.DB_TYPE_CLOB);payload.setvalue(0,json.dumps(keys))
    cur.execute("""with a as(select ADDR from json_table(:addresses,'$[*]'columns(ADDR varchar2(200)path '$')))
        select /*+ leading(f m t) use_nl(m) */ /* VRP_PROFILE_PK282 */ m.FROM_ADDR,m.TO_ADDR,m.DISTANCE_KM,m.DURATION_MIN,m.DURATION_BASIS,m.SOURCE,
        case when m.UPDATED_AT>=sysdate-1 then 1 else 0 end
        from RRL_ADDR_DISTANCE_MATRIX m join a f on f.ADDR=m.FROM_ADDR join a t on t.ADDR=m.TO_ADDR""",addresses=payload)
    distances={};durations={};sources=set()
    for a,b,km,minutes,basis,source,fresh in cur.fetchall():
        if km is None or km<0:continue
        distances[(a,b)]=float(km);sources.add(str(source or "unrecorded"))
        if basis=="ROAD_PROFILE_ESTIMATE"and fresh==1 and minutes is not None and 0<=minutes<=10080:
            durations[(a,b)]=float(minutes)
    provider=next(iter(sources))if len(sources)==1 else "mixed"if sources else "haversine"
    return distances,durations,provider

def profile_duration_cache(gateway: Any,addresses: list[str]) -> dict:
    return planner_cost_cache(gateway,addresses)[1]

def planner_cost_cache(gateway: Any,addresses: list[str]) -> tuple[dict,dict,str]:
    with gateway.transaction("Existing planner costs READ ONLY")as cur:
        cur.execute("set transaction read only");return read_cost_cache(cur,addresses)

def planner_inputs(gateway: Any,orders: list[Any]) -> tuple[dict,dict,str,dict | None]:
    with gateway.transaction("Existing planner costs and warehouse origin READ ONLY")as cur:
        cur.execute("set transaction read only")
        wares={o.ware_id for o in orders};origin=None
        if len(wares)==1:
            out=cur.var(oracledb.DB_TYPE_CLOB);cur.callproc("RRL_WARE_DEPOT_API.material",[next(iter(wares)),out])
            candidate=read_oracle_json(out.getvalue())
            if candidate["configured"]:origin=candidate
        addresses=[o.addr for o in orders if o.addr]+([origin["depot_address"]]if origin else [])
        distances,durations,provider=read_cost_cache(cur,addresses)
        return distances,durations,provider,origin
