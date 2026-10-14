from datetime import date,datetime
"""Reasoned move of existing unpicked ST using original native assignment."""
from typing import Any
import json
import oracledb
from ...platform.public import read_oracle_json
from .trip_edit import trip_error

class StDeferral:
    def __init__(self,gateway: Any) -> None:self.gateway=gateway
    def candidates(self,st: str,actor: str,start: date|None,end: date|None,district: str|None,store: str|None,after_date: datetime|None,after_id: int,limit: int,purpose: str="DEFER") -> dict:
        from .trip_selector import candidates
        try:
            return candidates(self.gateway,st,actor,start,end,district,store,after_date,after_id,limit,purpose)
        except oracledb.DatabaseError as exc:
            raise trip_error(exc) from exc

    def context(self,st: str,actor: str) -> dict:
        try:
            with self.gateway.transaction("Existing ST deferral context READ ONLY")as cur:
                cur.execute("set transaction read only");out=cur.var(oracledb.DB_TYPE_CLOB)
                cur.callproc("RRL_ST_DEFER_API.context",[st,actor,out]);return read_oracle_json(out.getvalue())
        except oracledb.DatabaseError as exc:raise trip_error(exc)from exc
    def defer(self,operation: str,body: dict,actor: str) -> dict:
        try:
            with self.gateway.transaction("Original ST unassign and validated reassign plus immutable reason")as cur:
                payload=cur.var(oracledb.DB_TYPE_CLOB);payload.setvalue(0,json.dumps(body,sort_keys=True,separators=(",",":"),ensure_ascii=True))
                out=cur.var(oracledb.DB_TYPE_CLOB);cur.callproc("RRL_ST_DEFER_API.apply_decision",[operation,actor,payload,out])
                return read_oracle_json(out.getvalue())
        except oracledb.DatabaseError as exc:raise trip_error(exc)from exc
    def history(self,st: str,after: int,actor: str) -> dict:
        try:
            with self.gateway.transaction("ST deferral journal READ ONLY")as cur:
                cur.execute("set transaction read only");out=cur.var(oracledb.DB_TYPE_CLOB)
                cur.callproc("RRL_ST_DEFER_API.history",[st,actor,after,out]);return read_oracle_json(out.getvalue())
        except oracledb.DatabaseError as exc:raise trip_error(exc)from exc
