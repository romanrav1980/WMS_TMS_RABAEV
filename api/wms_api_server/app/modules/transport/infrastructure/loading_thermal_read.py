"""Scoped caller supplies existing load IDs after its warehouse authorization."""
from typing import Any
import oracledb
from ...platform.public import read_oracle_json

def loading_thermal_read(cur: Any, plate: str | None, load_ids: list[str], trip: int) -> dict[str, Any]:
    if len(load_ids)>200:
        raise ValueError("LOADING_THERMAL_HISTORY_BOUND_200")
    cur.execute("select ID from RRL_TR_VEHICLE where NUM=:plate and nvl(DELETED,0)=0 fetch first 2 rows only",plate=plate)
    vehicles=cur.fetchall()
    profile=None
    if len(vehicles)==1:
        profile=read_oracle_json(cur.callfunc("RRL_VEHICLE_PROFILE_API.describe_profile",oracledb.DB_TYPE_CLOB,[vehicles[0][0]]))
    facts={}
    if load_ids:
        binds={"op"+str(i):value for i,value in enumerate(load_ids)}
        names=",".join(":"+name for name in binds)
        cur.execute("select LOAD_OPERATION_ID,CONFIRMATION_JSON,RECORDED_AT from RRL_TT_LOAD_THERMAL_FACT where LOAD_OPERATION_ID in("+names+")",binds)
        for op,wire,recorded in cur:
            facts[op]={"confirmation":read_oracle_json(wire),"recorded_at":recorded,
                       "sensor_verified":False,"basis":"MANUAL_AT_LOADING"}
    cur.execute("""select o.RESULT_JSON from RRL_TT_VEHICLE_SOURCE s join RRL_STOCK_OPERATION o
        on o.OPERATION_ID=s.DEPARTURE_OPERATION_ID where s.TT_ID=:trip and o.STATE='APPLIED'
        and o.COMMAND_TYPE='TRIP_DEPART'""",trip=trip)
    row=cur.fetchone()
    departed=read_oracle_json(row[0]) if row else {}
    return {"vehicle_profile":profile,"vehicle_resolution":"FOUND" if len(vehicles)==1 else "MISSING_OR_AMBIGUOUS",
            "load_confirmations":facts,"departure_confirmation":departed.get("temperature_at_departure"),
            "departure_confirmed_at":departed.get("temperature_confirmed_at"),"sensor_verified":False,"operational_admission":False}
