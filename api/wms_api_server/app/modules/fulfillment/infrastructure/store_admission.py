"""Atomic source decision and operational admission, never quantity posting."""
import json
from typing import Any
import oracledb
from ...platform.public import read_oracle_json
from ..domain.store_decision import read_store_decision
from ..application.ports import StoreOrderConflict


def admission_error(exc: oracledb.DatabaseError) -> Exception:
    code = getattr(exc.args[0], "code", 0)
    if code == 20882:
        return PermissionError("STORE_ORDER_CURRENT_WARE_ACTOR_REQUIRED")
    if code == 1403:
        return LookupError("Original source order not found")
    if code in {20886, 20863, 1}:
        return StoreOrderConflict(str(exc.args[0]).split("\n", 1)[0])
    if code in {6502, 12899, 1841, 1843, 1858, 1861}:
        return ValueError(str(exc.args[0]).split("\n", 1)[0])
    return exc


class StoreAdmission:
    def __init__(self, gateway: Any) -> None:
        self.gateway = gateway

    def receive(self, raw: bytes, actor: str) -> dict[str, Any]:
        body = read_store_decision(raw)
        try:
            with self.gateway.transaction("ERP source admission decision one UOW") as cur:
                payload = cur.var(oracledb.DB_TYPE_CLOB)
                payload.setvalue(0, json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False))
                result = cur.var(oracledb.DB_TYPE_CLOB)
                cur.callproc("RRL_SAP_STORE_ADMISSION_API.apply_decision", [actor, payload, result])
                return read_oracle_json(result.getvalue())
        except oracledb.DatabaseError as exc:
            raise admission_error(exc) from exc


def read_admission(cur: Any, order: int, actor: str) -> dict[str, Any]:
    result = cur.var(oracledb.DB_TYPE_CLOB)
    try:
        cur.callproc("RRL_SAP_STORE_ADMISSION_API.context", [order, actor, result])
        return read_oracle_json(result.getvalue())
    except oracledb.DatabaseError as exc:
        raise admission_error(exc) from exc
