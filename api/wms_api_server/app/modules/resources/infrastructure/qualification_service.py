"""Composition of existing resource metadata and assignment commands."""
from typing import Any, Callable
from .qualification_admin import QualificationAdmin
from .qualified_candidates import QualifiedCandidates
from .nearest_dispatch import dispatch_warehouse

class QualificationService(QualificationAdmin):
    def __init__(self,gateway: Any,assign: Callable[[Any,int,Any],None]) -> None:
        super().__init__(gateway)
        self.assign=assign

    def warehouse(self, task_id: int, limit: int) -> list[dict[str, Any]]:
        return QualifiedCandidates(self.gateway).warehouse(task_id, limit)

    def dispatch(self, task_id: int, actor: str) -> dict[str, Any]:
        return dispatch_warehouse(self.gateway, task_id, actor,self.assign)
