from datetime import date
import json
from typing import Any
import oracledb
from ...platform.public import read_oracle_json
from .plan_application import TransportPlanError

def trip_error(exc: oracledb.DatabaseError) -> TransportPlanError:
    code=getattr(exc.args[0],"code",0)
    if code==1403:return TransportPlanError("TRANSPORT_CURRENT_SOURCE_NOT_FOUND","Действующий рейс, машина или водитель отсутствует",404)
    if 20800<=code<=20999:return TransportPlanError("TRANSPORT_EDIT_REJECTED",str(exc.args[0]).split("\n",1)[0],403 if code==20882 else 409)
    if code in {6502,12899,1841,1843,1858,1861}:return TransportPlanError("TRANSPORT_EDIT_INPUT_INVALID","Проверьте длину полей, дату и время",422)
    return TransportPlanError("TRANSPORT_EDIT_UNCONFIRMED","Повторите исходное изменение реквизитов",503)

def create_existing_trip(gateway: Any,transport_type: str,day: date,actor: str) -> int:
    try:
        with gateway.transaction("Create existing owned transport draft")as cur:
            result=cur.var(oracledb.DB_TYPE_NUMBER)
            cur.callproc("RRL_TRANSPORT_EDIT_API.create_trip",[transport_type,day,actor,result])
            return int(result.getvalue())
    except oracledb.DatabaseError as exc:raise trip_error(exc) from exc

def update_existing_trip(gateway: Any,trip: int,fields: dict[str,Any],actor: str) -> dict[str,Any]:
    try:
        with gateway.transaction("Shared validated transport plan edit")as cur:
            result=cur.var(oracledb.DB_TYPE_CLOB)
            cur.callproc("RRL_TRANSPORT_EDIT_API.update_trip",[trip,actor,json.dumps(fields,sort_keys=True,separators=(",",":"),ensure_ascii=False),result])
            return read_oracle_json(result.getvalue())
    except oracledb.DatabaseError as exc:raise trip_error(exc) from exc
