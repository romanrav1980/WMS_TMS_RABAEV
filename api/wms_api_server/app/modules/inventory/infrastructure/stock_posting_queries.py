"""Read committed operation envelope without pretending NOT_FOUND proves rollback."""
from typing import Any
from ....oracle_gateway import OracleGateway


class StockPostingQueries:
    def __init__(self, gateway: OracleGateway | None = None) -> None:
        self.gateway = gateway or OracleGateway()

    def status(self) -> dict[str, Any]:
        rows = self.gateway.fetch_all(
            "select STATE,BASELINE_ID,CHANGED_AT from RRL_STOCK_RELEASE where RELEASE_ID=1"
        )
        return rows[0] if rows else {"state": "NOT_INSTALLED"}

    def operation(self, operation_id: str, actor: str) -> dict[str, Any]:
        rows = self.gateway.fetch_all(
            """select OPERATION_ID,COMMAND_TYPE,STATE,RESULT_JSON,CREATED_AT,APPLIED_AT
                 from RRL_STOCK_OPERATION where OPERATION_ID=:id
                   and (ACTOR=:actor or exists(select 1 from RUSERS u where u.ID=:actor and u.USER_GROUP='GLOBAL_ADMIN'))""",
            {"id": operation_id, "actor": actor},
        )
        if not rows:
            return {"operation_id": operation_id, "state": "NOT_VISIBLE", "outcome_confirmed": False}
        return rows[0]
