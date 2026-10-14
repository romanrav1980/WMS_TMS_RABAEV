"""Configured reference to an existing warehouse origin; no solver/stock replacement."""
import json
from typing import Any
import oracledb
from ...platform.public import read_oracle_json
from .trip_edit import trip_error

class WarehouseDepot:
    def __init__(self,gateway: Any) -> None:self.gateway=gateway
    def context(self,ware: int,actor: str) -> dict:
        try:
            with self.gateway.transaction("Warehouse origin configuration READ ONLY")as cur:
                cur.execute("set transaction read only");out=cur.var(oracledb.DB_TYPE_CLOB)
                cur.callproc("RRL_WARE_DEPOT_API.context",[ware,actor,out]);return read_oracle_json(out.getvalue())
        except oracledb.DatabaseError as exc:raise trip_error(exc)from exc
    def apply(self,operation: str,body: dict,actor: str) -> dict:
        try:
            with self.gateway.transaction("Versioned configured warehouse origin")as cur:
                payload=cur.var(oracledb.DB_TYPE_CLOB);payload.setvalue(0,json.dumps(body,sort_keys=True,separators=(",",":"),ensure_ascii=True))
                out=cur.var(oracledb.DB_TYPE_CLOB);cur.callproc("RRL_WARE_DEPOT_API.apply_setting",[operation,actor,payload,out])
                return read_oracle_json(out.getvalue())
        except oracledb.DatabaseError as exc:raise trip_error(exc)from exc

    def resolve(self,operation: str,body: dict,actor: str) -> dict:
        request=json.dumps(body,sort_keys=True,separators=(",",":"),ensure_ascii=True)
        try:
            with self.gateway.transaction("Await warehouse origin configuration outcome")as cur:
                entered=False
                try:
                    check=cur.var(oracledb.DB_TYPE_CLOB);cur.callproc("RRL_WARE_DEPOT_API.context",[body["warehouse_id"],actor,check])
                    cur.callproc("RRL_STOCK_METADATA_TX.begin_change",[actor,"warehouse_settings_edit"]);entered=True
                    cur.callproc("RRL_WARE_DEPOT_API.context",[body["warehouse_id"],actor,check])
                    cur.execute("select WARE_ID,ACTOR,REQUEST_JSON,RESULT_JSON from RRL_WARE_DEPOT_HISTORY where OPERATION_ID=:operation_id",operation_id=operation)
                    row=cur.fetchone()
                    if row is None:return {"state":"NOT_RECORDED","operation_id":operation,"warehouse_id":body["warehouse_id"],"stock_changed":False}
                    saved=json.dumps(read_oracle_json(row[2]),sort_keys=True,separators=(",",":"),ensure_ascii=True)
                    if row[0]!=body["warehouse_id"]or row[1]!=actor or saved!=request:
                        from ..contracts_plan import TransportPlanError
                        raise TransportPlanError("WARE_DEPOT_OPERATION_PAYLOAD_CONFLICT","Сохранённая команда отличается от исходной",409)
                    return {"state":"RECORDED","operation_id":operation,"result":read_oracle_json(row[3]),"stock_changed":False}
                finally:
                    if entered:cur.callproc("RRL_STOCK_METADATA_TX.end_change")
        except oracledb.DatabaseError as exc:raise trip_error(exc)from exc
