"""Inventory task queue and recovery monitoring on the existing domain objects."""
from typing import Any
from fastapi import HTTPException
import oracledb
from .recovery_reads import RecoveryReads, INVENTORY_PROJECTION, queue_rows


class RecoveryTasks:
    def __init__(self, gateway: Any) -> None:
        self.gateway = gateway

    def list_inventory(self, limit: int, task_id: int | None = None, *, actor: str, ware_id: int | None = None) -> list[dict[str, Any]]:
        return RecoveryReads(self.gateway).inventory(actor, limit, task_id, ware_id)

    def list_recovery(self, limit: int, *, actor: str, ware_id: int | None = None) -> list[dict[str, Any]]:
        return RecoveryReads(self.gateway).recovery(actor, limit, ware_id)

    def claim_inventory(self, task_id: int, actor: str) -> dict[str, Any]:
        try:
            with self.gateway.transaction("Claim existing inventory task") as cursor:
                cursor.callproc("RRL_INVENTORY_TASK_ACCESS.claim_task", [task_id, actor])
                cursor.execute(INVENTORY_PROJECTION+" where it.INVENTORY_TASK_ID=:task_id", task_id=task_id)
                return queue_rows(cursor)[0]
        except oracledb.DatabaseError as exc:
            code = exc.args[0].code
            status = 403 if code == 20882 else 404 if code == 20884 else 409 if 20800 <= code <= 20999 else 503
            raise HTTPException(status, dict(code="INVENTORY_CLAIM_REJECTED" if status < 500 else "INVENTORY_CLAIM_OUTCOME_UNCERTAIN",
                read_before_retry=True)) from exc
