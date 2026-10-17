"""Short caller-owned native transactions; never send a browser weight to Oracle."""
import json
from typing import Any
import oracledb
from ...platform.public import read_oracle_json
from ..contracts import StoreReceiptError


def request_failure(exc: oracledb.DatabaseError) -> StoreReceiptError:
    error = exc.args[0]
    code = abs(getattr(error, "code", 0))
    status = 403 if code == 20882 else 404 if code == 20884 else 409 if 20800 <= code <= 20999 else 503
    return StoreReceiptError("SCALE_REQUEST_REJECTED" if status < 500 else "SCALE_REQUEST_OUTCOME_UNCERTAIN",
                             str(error).split("\n", 1)[0], status)


class StoreScaleRequests:
    def __init__(self, gateway: Any) -> None:
        self.gateway = gateway

    def _invoke(self, procedure: str, arguments: list[Any], readonly: bool) -> dict[str, Any]:
        try:
            with self.gateway.transaction("Store weighing request handshake") as cursor:
                if readonly:
                    cursor.execute("set transaction read only")
                result = cursor.var(oracledb.DB_TYPE_CLOB)
                cursor.callproc("RRL_STORE_WEIGH_API." + procedure, [*arguments, result])
                return read_oracle_json(result.getvalue())
        except oracledb.DatabaseError as exc:
            raise request_failure(exc) from exc

    def request(self, body: dict[str, Any], actor: str) -> dict[str, Any]:
        packet = json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
        return self._invoke("request_capture", [packet, actor], False)

    def status(self, request_id: str, actor: str) -> dict[str, Any]:
        return self._invoke("request_status", [request_id, actor], True)

    def devices(self, load_operation_id: str, store_address: str, actor: str) -> dict[str, Any]:
        return self._invoke("devices", [load_operation_id, store_address, actor], True)

    def pending(self, device_id: str, actor: str) -> dict[str, Any]:
        return self._invoke("pending_requests", [device_id, actor], True)
