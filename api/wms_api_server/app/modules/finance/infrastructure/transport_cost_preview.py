"""Shared native Q26 calculation, also used by monetary recognition."""
from typing import Any
import oracledb
from ...platform.public import read_oracle_json
from ..contracts import LogisticsCostError


def native_failure(exc: oracledb.DatabaseError)->None:
    code=getattr(exc.args[0],"code",0)
    if 20800<=code<=20999:
        message=str(exc.args[0]).split("\n",1)[0]
        raise LogisticsCostError("TRANSPORT_COST_REJECTED",message,403 if code==20882 else 409)from exc
    if code==1:
        raise LogisticsCostError("TRANSPORT_COST_SOURCE_ALREADY_RECOGNIZED","Исходный выезд уже начислен; откройте сохранённый расчёт",409)from exc
    raise exc


def preview_transport_cost(cursor: Any,trip: int,ware: int,price_id: int,actor: str)->dict[str,Any]:
    try:
        out=cursor.var(oracledb.DB_TYPE_CLOB)
        cursor.callproc("RRL_TRANSPORT_COST_API.preview",[trip,ware,price_id,actor,out])
        return read_oracle_json(out.getvalue())
    except oracledb.DatabaseError as exc:
        native_failure(exc)
        raise


def conduct_transport_cost(gateway: Any,body: dict[str,Any],actor: str)->dict[str,Any]:
    import json
    try:
        with gateway.transaction("Recognize original transport Q26 cost and required outbox")as cursor:
            out=cursor.var(oracledb.DB_TYPE_CLOB)
            cursor.callproc("RRL_TRANSPORT_COST_API.conduct",[json.dumps(body,sort_keys=True,separators=(",",":")),actor,out])
            return read_oracle_json(out.getvalue())
    except oracledb.DatabaseError as exc:
        native_failure(exc)
        raise
