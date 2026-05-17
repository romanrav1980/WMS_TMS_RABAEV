from typing import Any

from fastapi import HTTPException

from ..oracle_gateway import OracleGateway
from ..schemas import WarehouseTaskStatusRequest
from .mes_service import clamp_limit


class WarehouseTaskService:
    def __init__(self, gateway: OracleGateway | None = None) -> None:
        self.gateway = gateway or OracleGateway()

    def list_tasks(
        self,
        status: str | None = None,
        task_type: str | None = None,
        assigned_to: str | None = None,
        production_order_id: int | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        conditions = []
        params: dict[str, Any] = {"limit": clamp_limit(limit)}
        if status:
            conditions.append("STATUS = :status")
            params["status"] = status.upper()
        if task_type:
            conditions.append("TASK_TYPE = :task_type")
            params["task_type"] = task_type.upper()
        if assigned_to:
            conditions.append("upper(ASSIGNED_TO) = :assigned_to")
            params["assigned_to"] = assigned_to.upper()
        if production_order_id is not None:
            conditions.append("PRODUCTION_ORDER_ID = :production_order_id")
            params["production_order_id"] = production_order_id
        where_sql = " where " + " and ".join(conditions) if conditions else ""
        return self.gateway.fetch_all(
            f"""
            select *
              from (
                select TASK_ID, TASK_TYPE, TASK_SOURCE, SOURCE_TASK_ID,
                       SOURCE_MOVEMENT_ID, SOURCE_DOC_TYPE, SOURCE_DOC_ID,
                       PRODUCTION_ORDER_ID, PROD_BATCH_ID, RAW_ARTICUL,
                       TARGET_ARTICUL, UID_PALLET, SSCC, FROM_WARE_ID,
                       FROM_CELL, TO_WARE_ID, TO_CELL, QTY, UNIT_CODE,
                       PRIORITY, STATUS, ASSIGNED_TO, CREATED_AT,
                       CREATED_BY, STARTED_AT, FINISHED_AT, CANCELLED_AT,
                       CANCELLED_BY, LAST_ERROR
                  from RRL_WAREHOUSE_TASK
                  {where_sql}
                 order by case STATUS
                            when 'PLANNED' then 1
                            when 'ASSIGNED' then 2
                            when 'IN_PROGRESS' then 3
                            when 'ERROR' then 4
                            else 9
                          end,
                          PRIORITY,
                          CREATED_AT,
                          TASK_ID
              )
             where rownum <= :limit
            """,
            params,
        )

    def get_task_or_404(self, task_id: int) -> dict[str, Any]:
        rows = self.gateway.fetch_all(
            """
            select *
              from RRL_WAREHOUSE_TASK
             where TASK_ID = :task_id
            """,
            {"task_id": task_id},
        )
        if not rows:
            raise HTTPException(status_code=404, detail="Warehouse task not found.")
        return rows[0]

    def assign_task(self, task_id: int, request: WarehouseTaskStatusRequest) -> None:
        task = self.get_task_or_404(task_id)
        if task.get("status") not in {"PLANNED", "ASSIGNED"}:
            raise HTTPException(status_code=409, detail="Only planned/assigned task can be assigned.")
        assignee = request.assigned_to or request.updated_by
        if not assignee:
            raise HTTPException(status_code=400, detail="assigned_to is required.")
        self.gateway.execute(
            """
            update RRL_WAREHOUSE_TASK
               set STATUS = 'ASSIGNED',
                   ASSIGNED_TO = :assigned_to,
                   LAST_ERROR = null
             where TASK_ID = :task_id
            """,
            {"task_id": task_id, "assigned_to": assignee},
        )

    def start_task(self, task_id: int, request: WarehouseTaskStatusRequest) -> None:
        task = self.get_task_or_404(task_id)
        if task.get("status") not in {"PLANNED", "ASSIGNED"}:
            raise HTTPException(status_code=409, detail="Only planned/assigned task can be started.")
        self.gateway.execute(
            """
            update RRL_WAREHOUSE_TASK
               set STATUS = 'IN_PROGRESS',
                   ASSIGNED_TO = nvl(:assigned_to, ASSIGNED_TO),
                   STARTED_AT = nvl(STARTED_AT, systimestamp),
                   LAST_ERROR = null
             where TASK_ID = :task_id
            """,
            {
                "task_id": task_id,
                "assigned_to": request.assigned_to or request.updated_by,
            },
        )

    def complete_task(self, task_id: int, request: WarehouseTaskStatusRequest) -> None:
        task = self.get_task_or_404(task_id)
        if task.get("status") in {"DONE", "CANCELLED"}:
            raise HTTPException(status_code=409, detail="Task is already closed.")
        self.gateway.execute(
            """
            update RRL_WAREHOUSE_TASK
               set STATUS = 'DONE',
                   FINISHED_AT = systimestamp,
                   ASSIGNED_TO = nvl(:assigned_to, ASSIGNED_TO),
                   QTY = nvl(:fact_qty, QTY),
                   LAST_ERROR = null
             where TASK_ID = :task_id
            """,
            {
                "task_id": task_id,
                "assigned_to": request.assigned_to or request.updated_by,
                "fact_qty": request.fact_qty,
            },
        )

    def cancel_task(self, task_id: int, request: WarehouseTaskStatusRequest) -> None:
        task = self.get_task_or_404(task_id)
        if task.get("status") == "DONE":
            raise HTTPException(status_code=409, detail="Completed task cannot be cancelled.")
        self.gateway.execute(
            """
            update RRL_WAREHOUSE_TASK
               set STATUS = 'CANCELLED',
                   CANCELLED_AT = systimestamp,
                   CANCELLED_BY = :cancelled_by,
                   LAST_ERROR = :reason
             where TASK_ID = :task_id
            """,
            {
                "task_id": task_id,
                "cancelled_by": request.updated_by or request.assigned_to or "API",
                "reason": request.reason,
            },
        )
