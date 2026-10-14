"""Current RUSERS warehouse, rights and original CASE evidence in one snapshot."""
from typing import Any
import oracledb
from ....transaction_gateway import TransactionGateway
from ..contracts_case_read import CaseReadError
from .case_read_model import LegacyCaseReads


def actor_scope(cur: Any, actor: str) -> tuple[int | None, bool]:
    cur.execute("""select WARE_ID,case when upper(trim(USER_GROUP))='GLOBAL_ADMIN'then 1 else 0 end
        from RUSERS where ID=:actor and nvl(DELETED,0)=0 and RRL_HAS_WRIGHT(ID,'case_pick_view')=1""", actor=actor)
    row = cur.fetchone()
    if row is None or (row[0] is None and row[1] != 1):
        raise CaseReadError("CASE_CURRENT_WARE_VIEWER_REQUIRED", "Требуется действующий пользователь своего склада")
    return row[0], row[1] == 1


def native_task_scope(cur: Any, task: int, actor: str, permission: str) -> None:
    try:
        cur.callproc("RRL_CASE_TASK_ACCESS.assert_scope", [task, actor, permission, None])
    except oracledb.DatabaseError as exc:
        code = getattr(exc.args[0], "code", 0)
        if code == 20882:
            raise CaseReadError("CASE_CURRENT_WARE_VIEWER_REQUIRED", "Недоступный склад CASE-задания") from exc
        if code == 20886:
            missing = "CASE_TASK_IDENTITY_MISSING" in str(exc.args[0])
            raise CaseReadError("CASE_TASK_NOT_FOUND" if missing else "CASE_TASK_WARE_REQUIRED",
                                "CASE-задание отсутствует" if missing else "Не задан склад CASE-задания",
                                404 if missing else 409) from exc
        raise


def task_scope(cur: Any, task: int, actor: str) -> None:
    actor_scope(cur, actor)
    native_task_scope(cur, task, actor, "case_pick_view")


class ScopedCaseReads:
    def __init__(self, gateway: Any) -> None:
        self.gateway = gateway

    def tasks(self, actor: str, resource: int | None, scope: str, status: str | None, limit: int) -> list[dict[str, Any]]:
        if scope not in {"mine", "free", "all"} or not 1 <= limit <= 500:
            raise CaseReadError("CASE_LIST_SCOPE_INVALID", "Допустимы mine/free/all и предел1–500", 422)
        with self.gateway.transaction("Current CASE queue READ ONLY snapshot") as cur:
            if not getattr(self.gateway, "transaction_bound", False):
                cur.execute("set transaction read only")
            ware, global_admin = actor_scope(cur, actor)
            if resource is not None:
                cur.execute("select WARE_ID from RRL_RESOURCE where RESOURCE_ID=:id and ACTIVE=1", id=resource)
                row = cur.fetchone()
                if row is None:
                    raise CaseReadError("CASE_RESOURCE_NOT_FOUND", "Действующий ресурс отсутствует", 404)
                if not global_admin and row[0] != ware:
                    raise CaseReadError("CASE_CURRENT_WARE_RESOURCE_REQUIRED", "Недоступный склад ресурса")
            return LegacyCaseReads(TransactionGateway(cur)).list_tasks(
                resource, scope, status, limit, None if global_admin else ware,
            )

    def task(self, task: int, actor: str) -> dict[str, Any]:
        with self.gateway.transaction("Current CASE detail READ ONLY snapshot") as cur:
            if not getattr(self.gateway, "transaction_bound", False):
                cur.execute("set transaction read only")
            task_scope(cur, task, actor)
            result = LegacyCaseReads(TransactionGateway(cur)).get_task(task)
            if result is None:
                raise CaseReadError("CASE_TASK_NOT_FOUND", "CASE-задание отсутствует", 404)
            return result


    def shorts(self, actor: str, status: str | None, limit: int) -> list[dict[str, Any]]:
        if not 1 <= limit <= 500:
            raise CaseReadError("CASE_LIST_SCOPE_INVALID", "Предел должен быть1–500", 422)
        with self.gateway.transaction("Current CASE shortages READ ONLY snapshot") as cur:
            if not getattr(self.gateway, "transaction_bound", False):
                cur.execute("set transaction read only")
            ware, global_admin = actor_scope(cur, actor)
            return LegacyCaseReads(TransactionGateway(cur)).list_shorts(status, limit, None if global_admin else ware)
