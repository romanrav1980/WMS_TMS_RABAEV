"""Dispatcher metadata decision; original stock execution remains in native owners."""
from datetime import datetime, timezone
from typing import Any
import json
import oracledb
from ...platform.public import read_oracle_json
from ..contracts_store_returns import StoreReturnReceiveError
from .metadata_transactions import receipt_task_metadata

class InterwarehouseDispatch:
    def __init__(self, gateway: Any) -> None:
        self.gateway = gateway

    def record(self, operation_id: str, metadata: dict[str, Any], actor: str) -> dict[str, Any]:
        return self._record("RRL_INTERWARE_ROUTING.record_decision",operation_id,metadata,actor)

    def thermal(self, operation_id: str, metadata: dict[str, Any], actor: str) -> dict[str, Any]:
        return self._record("RRL_INTERWARE_THERMAL.record_decision",operation_id,metadata,actor)

    def _record(self, procedure: str, operation_id: str, metadata: dict[str, Any], actor: str) -> dict[str, Any]:
        request = dict(metadata,operation_id=operation_id,actor=actor)
        for name in ("expected_arrival","ready_due"):
            value = request.get(name)
            if isinstance(value,datetime):
                request[name] = value.astimezone(timezone.utc).isoformat(timespec="microseconds")
        payload = json.dumps(request,ensure_ascii=False,sort_keys=True,separators=(",",":"))
        try:
            with receipt_task_metadata(self.gateway,"Interwarehouse dispatcher decision",actor,"transport_dispatch_edit") as cur:
                result = cur.var(oracledb.DB_TYPE_CLOB)
                cur.setinputsizes(oracledb.DB_TYPE_CLOB,None,oracledb.DB_TYPE_CLOB)
                cur.callproc(procedure,[payload,actor,result])
                return read_oracle_json(result.getvalue())
        except oracledb.DatabaseError as exc:
            code = getattr(exc.args[0],"code",0)
            if code == 1 or 20800 <= code <= 20999:
                raise StoreReturnReceiveError("INTERWARE_DECISION_REJECTED",str(exc.args[0]).split("\n",1)[0],403 if code==20882 else 409) from exc
            raise
