"""Read-only admission, separate from the legacy CASE execution guard."""
from typing import Any
from ..contracts_case_read import CaseReadError


def view_predicate(alias: str) -> str:
    if alias not in {"t", "ct", "tot"}:
        raise ValueError("Fixed CASE aliases only")
    return f"(RRL_ACCESS_API.allowed(:view_actor,'case_pick_view','WAREHOUSE',to_char({alias}.WARE_ID),{alias}.ASSIGNED_TO)=1 and RRL_TRADE_CASE_ACCESS.allowed({alias}.CASE_PICK_TASK_ID,:view_actor)=1)"


def require_viewer(cur: Any, actor: str, warehouse: int | None = None) -> None:
    if warehouse is not None and warehouse <= 0:
        raise CaseReadError("CASE_WAREHOUSE_INVALID", "Склад должен быть положительным", 422)
    cur.execute("""select count(*) from RUSERS u where u.ID=:actor and nvl(u.DELETED,0)=0
        and exists(select 1 from RRL_WARES w where (:ware is null or w.ID=:ware)
        and RRL_ACCESS_API.allowed(:actor,'case_pick_view','WAREHOUSE',to_char(w.ID),:actor)=1)""",
                actor=actor, ware=warehouse)
    if cur.fetchone()[0] != 1:
        raise CaseReadError("CASE_SCOPED_VIEW_REQUIRED", "Нет права просмотра в области склада")


def require_task_view(cur: Any, task: int, actor: str) -> None:
    cur.execute("select count(*) from RRL_CASE_PICK_TASK t where t.CASE_PICK_TASK_ID=:task and "
                + view_predicate("t"), task=task, view_actor=actor)
    if cur.fetchone()[0] != 1:
        raise CaseReadError("CASE_TASK_NOT_FOUND", "CASE-задание отсутствует или недоступно", 404)
