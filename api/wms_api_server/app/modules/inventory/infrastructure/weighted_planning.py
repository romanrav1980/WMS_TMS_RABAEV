"""One current read-only source for actual whole-box planning candidates."""
import oracledb
import json
from typing import Any
from ....oracle_gateway import OracleGateway
from ...platform.public import read_oracle_json
from ..contracts_stock import StockPostingError
from ..contracts_weighted_plan import WeightedBoxChoiceRequest
from .metadata_transactions import receipt_task_metadata


class WeightedPlanning:
    def __init__(self, gateway: OracleGateway) -> None:
        self.gateway = gateway

    def options(self, row: int, actor: str) -> dict[str, Any]:
        return self._options(row, actor, "pick_plan_create")

    def approval_options(self, row: int, actor: str) -> dict[str, Any]:
        return self._options(row, actor, "case_pick_short_approve")

    def _options(self, row: int, actor: str, permission: str) -> dict[str, Any]:
        try:
            with self.gateway.transaction("Actual whole-box planning READ ONLY") as q:
                q.execute("set transaction read only")
                result = read_oracle_json(q.callfunc("RRL_WEIGHT_BOX_PLANNING_READ.snapshot_json", oracledb.DB_TYPE_CLOB, [row, actor, permission]))
                q.execute("""select CHOICE_ID,STATUS,RRL_STOCK_PLAN_HELPER.decimal_text(NET_WEIGHT_KG),PICK_PLAN_ID
                    from RRL_PICK_WEIGHT_CHOICE where case when STATUS in('ACCEPTED','USED')then CUSTOMER_ORDER_ROW_ID end=:p_row and WARE_ID=:p_ware fetch first 2 rows only""", p_row=row,p_ware=result["warehouse_id"])
                choices = q.fetchall()
                if len(choices)>1:
                    raise StockPostingError("WEIGHT_BOX_ACTIVE_CHOICE_AMBIGUOUS", None, 20887)
                result["active_choice"] = ({"choice_id": choices[0][0], "status": choices[0][1],
                    "selected_net_weight_kg": choices[0][2], "pick_plan_id": choices[0][3]} if choices else None)
                return result
        except oracledb.DatabaseError as exc:
            code = exc.args[0].code
            if code in {20881,20882,20886,20860,20868,1403,1422}:
                raise StockPostingError("WEIGHT_BOX_PLAN_SOURCE_REJECTED", None, code) from exc
            raise

    def approve(self, body: WeightedBoxChoiceRequest, actor: str) -> dict[str, Any]:
        wire = json.dumps(body.model_dump(mode="json"), ensure_ascii=True, sort_keys=True, separators=(",", ":"))
        try:
            with receipt_task_metadata(self.gateway, "Approve final whole weighted box", actor, "case_pick_short_approve") as q:
                # Canonical ASCII request is bounded to 16KB by the native contract.
                # Bind VARCHAR directly: Oracle converts to CLOB before entering the package.
                out = q.var(oracledb.DB_TYPE_CLOB)
                q.callproc("RRL_WEIGHT_BOX_CHOICE_API.approve_request", [wire, actor, out])
                return read_oracle_json(out.getvalue())
        except oracledb.DatabaseError as exc:
            raise choice_error(exc, body.choice_id) from exc

    def cancel(self, choice: str, reason: str, actor: str) -> dict[str, Any]:
        try:
            with receipt_task_metadata(self.gateway, "Cancel unused weighted box choice", actor, "case_pick_short_approve") as q:
                out = q.var(oracledb.DB_TYPE_CLOB)
                q.callproc("RRL_WEIGHT_BOX_CHOICE_API.cancel_choice", [choice, actor, reason, out])
                return read_oracle_json(out.getvalue())
        except oracledb.DatabaseError as exc:
            raise choice_error(exc, choice) from exc


def choice_error(exc: oracledb.DatabaseError, choice: str) -> StockPostingError:
    code = exc.args[0].code
    kind = ("OPERATION_CONTENT_CONFLICT" if code == 20873 else
            "RESULT_UNCERTAIN" if not (20800 <= code <= 20999 or code in {1, 1403, 1422}) else
            "WEIGHT_BOX_CHOICE_REJECTED")
    return StockPostingError(kind, choice, code, str(exc).split("\n", 1)[0])
