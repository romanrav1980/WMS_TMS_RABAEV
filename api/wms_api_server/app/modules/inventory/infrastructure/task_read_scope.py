"""Current task view permission and legacy loader share one read-only snapshot."""
from collections.abc import Callable
from typing import Any,TypeVar
import oracledb
from ....oracle_gateway import OracleGateway
from ....transaction_gateway import TransactionGateway
from ..contracts_task_read import TaskReadError,TaskViewScope

Result=TypeVar("Result")

def read_task_snapshot(
    gateway: OracleGateway,actor: str,loader: Callable[[TransactionGateway,TaskViewScope],Result],
    task_id: int | None=None,
) -> Result:
    with gateway.transaction("Current warehouse task read scope") as cursor:
        cursor.execute("set transaction read only")
        bound=TransactionGateway(cursor)
        rows=bound.fetch_all("""select WARE_ID,case when upper(trim(USER_GROUP))='GLOBAL_ADMIN' then 1 else 0 end GLOBAL_ADMIN
            from RUSERS where ID=:actor and nvl(DELETED,0)=0 and RRL_HAS_WRIGHT(ID,'warehouse_task_view')=1""",{"actor":actor})
        if not rows:
            raise TaskReadError("TASK_VIEW_CURRENT_ACTOR_REQUIRED")
        warehouse=rows[0]["ware_id"]
        scope=TaskViewScope(int(warehouse) if warehouse is not None else None,bool(rows[0]["global_admin"]))
        if not scope.global_admin and (scope.warehouse_id is None or scope.warehouse_id<=0):
            raise TaskReadError("TASK_VIEW_CURRENT_WAREHOUSE_REQUIRED")
        if task_id is not None:
            try:
                cursor.callproc("RRL_WAREHOUSE_TASK_ACCESS.assert_scope",[task_id,actor,None])
            except oracledb.DatabaseError as exc:
                if getattr(exc.args[0],"code",None)==20882:
                    raise TaskReadError("TASK_USER_WAREHOUSE_FORBIDDEN") from exc
                raise
        return loader(bound,scope)


def read_task_progress_snapshot(gateway: OracleGateway,task_id: int,actor: str) -> dict[str,Any]:
    from .task_progress import task_progress
    def load(bound: TransactionGateway,scope: TaskViewScope) -> dict[str,Any]:
        result=task_progress(bound,task_id)
        if not scope.global_admin:
            for row in result["tasks"]:
                try:
                    bound.cursor.callproc("RRL_WAREHOUSE_TASK_ACCESS.assert_scope",[row["task_id"],actor,None])
                except oracledb.DatabaseError as exc:
                    if getattr(exc.args[0],"code",None)==20882:
                        raise TaskReadError("TASK_FAMILY_WAREHOUSE_FORBIDDEN") from exc
                    raise
        return result
    return read_task_snapshot(gateway,actor,load,task_id)
