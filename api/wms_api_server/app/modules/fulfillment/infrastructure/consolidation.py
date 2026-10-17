"""One native UOW for logical expectations; original HU owners retain physical effects."""
import json
from typing import Any
import oracledb
from ...platform.public import read_oracle_json
from ..contracts_consolidation import ConsolidationError


def failure(error: oracledb.Error, operation_id: str | None = None) -> ConsolidationError:
    detail = error.args[0]
    code = getattr(detail, "code", 0)
    uncertain = code not in {1, 1403, 20881, 20882, 20884, 20886, 20890}
    status = 403 if code == 20882 else 404 if code in {1403, 20884} else 422 if code == 20881 else 503 if uncertain else 409
    message = getattr(detail, "message", "").split("\n", 1)[0]
    return ConsolidationError(status, message or "CONSOLIDATION_UNAVAILABLE", operation_id, uncertain)


class ConsolidationPlans:
    def __init__(self, gateway: Any) -> None:
        self.gateway = gateway

    def page(self, warehouse_id: int, actor: str, after: str | None, limit: int, status: str) -> dict[str, Any]:
        try:
            with self.gateway.transaction("Read scoped consolidation plan page") as cursor:
                cursor.execute("set transaction read only")
                return read_oracle_json(cursor.callfunc("RRL_HU_CONSOL_LIST.page_json", oracledb.DB_TYPE_CLOB,
                    [actor, warehouse_id, after, limit, status]))
        except oracledb.Error as error:
            raise failure(error) from error

    def read(self, plan_id: str, actor: str) -> dict[str, Any]:
        try:
            with self.gateway.transaction("Read current expected consolidation membership") as cursor:
                cursor.execute("set transaction read only")
                return read_oracle_json(cursor.callfunc("RRL_HU_CONSOL_READ.plan_json", oracledb.DB_TYPE_CLOB, [plan_id, actor]))
        except oracledb.Error as error:
            raise failure(error) from error

    def command(self, plan_id: str, body: dict[str, Any], actor: str) -> dict[str, Any]:
        operation = body["operation_id"]
        payload = dict(body, plan_id=plan_id)
        if "fulfillment_ids" in payload:
            payload["fulfillment_ids"] = sorted(payload["fulfillment_ids"])
        wire = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        if len(wire.encode("utf-8")) > 262144:
            raise ConsolidationError(422, "CONSOLIDATION_INPUT_BOUND", operation)
        try:
            with self.gateway.transaction("Save expected consolidation and immutable receipt") as cursor:
                result = cursor.var(oracledb.DB_TYPE_CLOB)
                cursor.callproc("RRL_HU_CONSOL_API.execute_command", [actor, wire, result])
                acknowledgement = read_oracle_json(result.getvalue())
                if (not isinstance(acknowledgement, dict) or acknowledgement.get("operation_id") != operation
                        or acknowledgement.get("plan_id") != plan_id or acknowledgement.get("stock_changed") is not False
                        or type(acknowledgement.get("version")) is not int or acknowledgement["version"] < 1
                        or acknowledgement.get("status") not in {"ACTIVE", "CANCELLED"}):
                    raise ConsolidationError(503, "CONSOLIDATION_ACK_INVALID", operation, True)
            return acknowledgement
        except oracledb.Error as error:
            raise failure(error, operation) from error
