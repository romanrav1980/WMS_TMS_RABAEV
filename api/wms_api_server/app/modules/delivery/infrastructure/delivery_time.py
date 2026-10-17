"""Native immutable window/arrival commands and scoped read-only KPI cohorts."""
import json
from typing import Any, Literal
import oracledb
from ...platform.public import read_oracle_json
from ..contracts import StoreReceiptError
from .delivery_kpi_read import read_report


class DeliveryTime:
    def __init__(self, gateway: Any) -> None:
        self.gateway = gateway

    def command(self, kind: Literal["plan_window", "record_arrival"], body: dict[str, Any], actor: str) -> dict[str, Any]:
        if kind not in ("plan_window", "record_arrival"):
            raise ValueError("Unknown delivery-time command")
        try:
            with self.gateway.transaction("Native delivery time " + kind) as q:
                result = q.var(oracledb.DB_TYPE_CLOB)
                q.callproc("RRL_DELIVERY_TIME_API." + kind,
                    [json.dumps(body, sort_keys=True, ensure_ascii=False, separators=(",", ":")), actor, result])
                return read_oracle_json(result.getvalue())
        except oracledb.DatabaseError as error:
            code = error.args[0].code
            raise StoreReceiptError("DELIVERY_TIME_REJECTED" if 20800 <= code <= 20999 else "DELIVERY_TIME_UNCERTAIN",
                str(error.args[0]).splitlines()[0], 403 if code == 20882 else 409 if 20800 <= code <= 20999 else 503,
                body["operation_id"]) from error

    def read(self, load: str, address: str, actor: str) -> dict[str, Any]:
        try:
            with self.gateway.transaction("Delivery timing current source read") as q:
                q.execute("set transaction read only")
                result = q.var(oracledb.DB_TYPE_CLOB)
                q.callproc("RRL_DELIVERY_TIME_API.read_times", [load, address, actor, result])
                return read_oracle_json(result.getvalue())
        except oracledb.DatabaseError as error:
            raise StoreReceiptError("DELIVERY_TIME_READ_UNAVAILABLE", str(error.args[0]).splitlines()[0],
                403 if error.args[0].code == 20882 else 503) from error

    def report(self, warehouse: int, start: str, finish: str, actor: str) -> dict[str, Any]:
        return read_report(self.gateway, warehouse, start, finish, actor)
