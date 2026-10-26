"""Bounded physical TOP proofs; caller has already authorized all trip warehouses."""
from typing import Any
import json
import oracledb
from ...platform.public import read_oracle_json

def loading_floor_read(cur: Any,load_ids: list[str],trip: int)->dict[str,Any]:
    if len(load_ids)>4000:
        raise ValueError("LOADING_FLOOR_HISTORY_BOUND_4000")
    facts={}
    if load_ids:
        cur.setinputsizes(load_ids=oracledb.DB_TYPE_CLOB)
        cur.execute("""select f.LOAD_OPERATION_ID,f.PALLET_TYPE_ID,t.PALLET_TYPE_CODE,t.PALLET_TYPE_NAME,
            f.PROFILE_VERSION,f.TYPE_ORIGIN,f.SOURCE_REFERENCE,f.RECORDED_AT
            from RRL_TT_LOAD_FLOOR_FACT f join RRL_PALLET_TYPE t on t.PALLET_TYPE_ID=f.PALLET_TYPE_ID
            where f.LOAD_OPERATION_ID in(select id from json_table(:load_ids,'$[*]'
              columns(id varchar2(100) path '$')))""",load_ids=json.dumps(load_ids))
        for op,type_id,code,name,version,origin,reference,recorded in cur:
            facts[op]={"pallet_type_id":type_id,"type_code":code,"current_type_name":name,
                       "profile_version":version,"origin":origin,"source_reference":reference,
                       "recorded_at":recorded,"top_place_count":1}
    cur.execute("""select o.RESULT_JSON from RRL_TT_VEHICLE_SOURCE s join RRL_STOCK_OPERATION o
        on o.OPERATION_ID=s.DEPARTURE_OPERATION_ID where s.TT_ID=:trip and o.STATE='APPLIED'
        and o.COMMAND_TYPE='TRIP_DEPART'""",trip=trip)
    row=cur.fetchone()
    departure=read_oracle_json(row[0]) if row else {}
    return {"load_confirmations":facts,"departure_confirmation":departure.get("floor_at_departure"),
            "basis":"IMMUTABLE_PHYSICAL_TOP_PROOF","operational_admission":False}
