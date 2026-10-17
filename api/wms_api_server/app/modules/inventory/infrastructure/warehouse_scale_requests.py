"""Native intent/claim queue. Captures remain owned by RRL_WH_SCALE_API."""
import json
from typing import Any
import oracledb
from ...platform.public import read_oracle_json
from ..contracts_warehouse_scale import WarehouseScaleError


class WarehouseWeighRequests:
    def __init__(self, gateway: Any) -> None:
        self.gateway = gateway

    def _invoke(self, procedure: str, arguments: list[Any], readonly: bool) -> dict[str, Any]:
        try:
            with self.gateway.transaction("Warehouse weighing request") as cursor:
                if readonly:
                    cursor.execute("set transaction read only")
                result = cursor.var(oracledb.DB_TYPE_CLOB)
                cursor.callproc("RRL_WH_WEIGH_REQUEST_API." + procedure, [*arguments, result])
                return read_oracle_json(result.getvalue())
        except oracledb.DatabaseError as exc:
            error = exc.args[0]
            code = abs(getattr(error, "code", 0))
            status = 403 if code == 20882 else 404 if code == 20884 else 409 if 20800 <= code <= 20999 else 503
            raise WarehouseScaleError("WEIGH_REQUEST_REJECTED" if status < 500 else "WEIGH_REQUEST_UNCERTAIN",
                                      str(error).split("\n", 1)[0], status) from exc

    @staticmethod
    def _wire(body: dict[str, Any]) -> str:
        return json.dumps(body, ensure_ascii=True, sort_keys=True, separators=(",", ":"))

    def request(self, body: dict[str, Any], actor: str) -> dict[str, Any]:
        return self._invoke("request_capture", [self._wire(body), actor], False)

    def status(self, request_id: str, actor: str) -> dict[str, Any]:
        return self._invoke("request_status", [request_id, actor], True)

    def pending(self, device_id: str, actor: str) -> dict[str, Any]:
        return self._invoke("pending_requests", [device_id, actor], True)

    def devices(self, task: int, purpose: str, actor: str) -> dict[str, Any]:
        return self._invoke("devices", [task, purpose, actor], True)

    def claim(self, request_id: str, body: dict[str, Any], actor: str) -> dict[str, Any]:
        return self._invoke("claim_request", [request_id, self._wire(body), actor], False)

    def zero(self, request_id: str, body: dict[str, Any], actor: str) -> dict[str, Any]:
        return self._invoke("confirm_zero", [request_id, self._wire(body), actor], False)
