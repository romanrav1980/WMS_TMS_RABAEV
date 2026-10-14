"""Explicit closure after proven full followup; never a stock write."""
import json
from typing import Any
import oracledb
from ...platform.public import read_oracle_json
from ..contracts_store_returns import StoreReturnReceiveError

def close_incident(gateway: Any,operation: str,body: dict,actor: str) -> dict:
    try:
        with gateway.transaction("Explicit interwarehouse incident closure")as cur:
            payload=cur.var(oracledb.DB_TYPE_CLOB);payload.setvalue(0,json.dumps(body,sort_keys=True,separators=(",",":"),ensure_ascii=False))
            out=cur.var(oracledb.DB_TYPE_CLOB)
            cur.callproc("RRL_INTERWARE_INCIDENT_API.close_case",[operation,actor,payload,out])
            return read_oracle_json(out.getvalue())
    except oracledb.DatabaseError as exc:
        code=getattr(exc.args[0],"code",0)
        raise StoreReturnReceiveError("INTERWARE_INCIDENT_CLOSE_REJECTED",str(exc.args[0]).split("\n",1)[0],403 if code==20882 else 409 if 20800<=code<=20999 else 503)from exc
