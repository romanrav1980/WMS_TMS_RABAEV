"""Native warehouse-task reads, without changing physical execution admission."""
from typing import Any
from ....transaction_gateway import TransactionGateway
from ..contracts_task_read import TaskReadError


from .task_view_predicate import task_view_predicate


def require_task_viewer(cur: Any, actor: str, warehouse: int | None) -> None:
    cur.execute("""select count(*) from RUSERS u where u.ID=:actor and nvl(u.DELETED,0)=0
        and exists(select 1 from RRL_WARES w where (:ware is null or w.ID=:ware)
        and RRL_ACCESS_API.allowed(:actor,'warehouse_task_view','WAREHOUSE',to_char(w.ID),:actor)=1)""",
                actor=actor, ware=warehouse)
    if cur.fetchone()[0] != 1:
        raise TaskReadError("TASK_SCOPED_VIEW_REQUIRED")


def scoped_task_queue(gateway: Any, actor: str, warehouse: int | None, filters: dict[str, Any]) -> list[dict[str, Any]]:
    from .task_queue_read import TaskQueueRead
    with gateway.transaction("Warehouse task queue native READ ONLY") as cur:
        cur.execute("set transaction read only")
        require_task_viewer(cur, actor, warehouse)
        return TaskQueueRead(TransactionGateway(cur)).list(**filters, view_actor=actor,
            scope_global=warehouse is None, scope_warehouse_id=warehouse)


def scoped_task_detail(gateway: Any, actor: str, task: int) -> dict[str, Any]:
    from .task_queue_read import TaskQueueRead
    with gateway.transaction("Warehouse task detail native READ ONLY") as cur:
        cur.execute("set transaction read only")
        require_task_viewer(cur, actor, None)
        cur.execute("select count(*) from RRL_WAREHOUSE_TASK where TASK_ID=:task and "
                    + task_view_predicate(), task=task, view_actor=actor)
        if cur.fetchone()[0] != 1:
            raise TaskReadError("TASK_NOT_FOUND_OR_DENIED", 404)
        result = TaskQueueRead(TransactionGateway(cur)).get(task)
        if result is None:
            raise TaskReadError("TASK_NOT_FOUND_OR_DENIED", 404)
        cur.execute("select RRL_WAREHOUSE_TASK_ACCESS.task_signature(:task) from dual", task=task)
        result["task_signature"] = cur.fetchone()[0]
        return result
