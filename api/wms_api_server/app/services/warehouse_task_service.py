from typing import Any

from fastapi import HTTPException

from ..oracle_gateway import OracleGateway
from ..transaction_gateway import TransactionGateway
from ..schemas import WarehouseTaskStatusRequest
from .mes_service import clamp_limit


class WarehouseTaskService:
    def __init__(self, gateway: OracleGateway | TransactionGateway | None = None) -> None:
        self.gateway = gateway or OracleGateway()

    def list_tasks(
        self,
        status: str | None = None,
        task_type: str | None = None,
        task_source: str | None = None,
        assigned_to: str | None = None,
        production_order_id: int | None = None,
        source_doc_type: str | None = None,
        source_doc_id: int | None = None,
        limit: int = 100,
        scope_warehouse_id: int | None = None,
        scope_global: bool = True,
        queue_group: str | None = None,
    ) -> list[dict[str, Any]]:
        from ..modules.inventory.public import build_task_queue_read
        return build_task_queue_read(self.gateway).list(
            status=status,task_type=task_type,task_source=task_source,assigned_to=assigned_to,
            production_order_id=production_order_id,source_doc_type=source_doc_type,source_doc_id=source_doc_id,
            limit=limit,scope_warehouse_id=scope_warehouse_id,scope_global=scope_global,queue_group=queue_group,
        )

    def get_task_or_404(self,task_id: int) -> dict[str, Any]:
        from ..modules.inventory.public import build_task_queue_read
        task=build_task_queue_read(self.gateway).get(task_id)
        if task is None:
            raise HTTPException(404,detail="Warehouse task not found.")
        return task

    def assign_task(self, task_id: int, request: WarehouseTaskStatusRequest) -> None:
        if not getattr(self.gateway, "transaction_bound", False):
            from ..modules.inventory.public import run_existing_warehouse_task_action
            return run_existing_warehouse_task_action(self.gateway, task_id, "assign_task", request, type(self))
        task = self.get_task_or_404(task_id)
        if task.get("status") not in {"PLANNED", "ASSIGNED"}:
            raise HTTPException(status_code=409, detail="Only planned/assigned task can be assigned.")
        assignee = request.assigned_to or request.updated_by
        if not assignee:
            raise HTTPException(status_code=400, detail="assigned_to is required.")
        resource_ctx = self._resource_context(request, task, "ASSIGN", assignee)
        if task.get("status") == "ASSIGNED" and task.get("assigned_to") == assignee and all(
            task.get(key) == value for key, value in resource_ctx.items()
        ):
            return
        self.gateway.execute_many(
            [
                (
                    """
                    update RRL_WAREHOUSE_TASK
                       set STATUS = 'ASSIGNED',
                           ASSIGNED_TO = :assigned_to,
                           RESOURCE_ID = :resource_id,
                           RESOURCE_SESSION_ID = :resource_session_id,
                           EQUIPMENT_ID = :equipment_id,
                           LAST_ERROR = null
                     where TASK_ID = :task_id
                    """,
                    {"task_id": task_id, "assigned_to": assignee, **resource_ctx},
                ),
                self._resource_event_statement(
                    task_id=task_id,
                    event_type="ASSIGNED",
                    event_by=request.updated_by,
                    resource_ctx=resource_ctx,
                ),
            ]
        )
        self._sync_wave_replenishment_status(task, "ASSIGNED", assignee)
        self._sync_wave_picking_move_status(task, "ASSIGNED", assignee)

    def start_task(self, task_id: int, request: WarehouseTaskStatusRequest) -> None:
        if not getattr(self.gateway, "transaction_bound", False):
            from ..modules.inventory.public import run_existing_warehouse_task_action
            return run_existing_warehouse_task_action(self.gateway, task_id, "start_task", request, type(self))
        task = self.get_task_or_404(task_id)
        if task.get("status") not in {"PLANNED", "ASSIGNED", "IN_PROGRESS"}:
            raise HTTPException(status_code=409, detail="Only planned/assigned task can be started.")
        assignee = request.updated_by
        resource_ctx = self._resource_context(request, task, "START", assignee)
        if task.get("status") == "IN_PROGRESS":
            return
        self.gateway.execute_many(
            [
                (
                    """
                    update RRL_WAREHOUSE_TASK
                       set STATUS = 'IN_PROGRESS',
                           ASSIGNED_TO = nvl(:assigned_to, ASSIGNED_TO),
                           RESOURCE_ID = :resource_id,
                           RESOURCE_SESSION_ID = :resource_session_id,
                           EQUIPMENT_ID = :equipment_id,
                           STARTED_AT = nvl(STARTED_AT, systimestamp),
                           STARTED_AT_INSTANT = nvl(STARTED_AT_INSTANT, systimestamp),
                           STARTED_SHIFT_TIME_ZONE = nvl(STARTED_SHIFT_TIME_ZONE, sessiontimezone),
                           LAST_ERROR = null
                     where TASK_ID = :task_id
                    """,
                    {"task_id": task_id, "assigned_to": assignee, **resource_ctx},
                ),
                self._resource_event_statement(
                    task_id=task_id,
                    event_type="STARTED",
                    event_by=request.updated_by,
                    resource_ctx=resource_ctx,
                ),
            ]
        )
        if resource_ctx["resource_session_id"] is not None:
            self.gateway.execute(
                "update RRL_RESOURCE_SESSION set CURRENT_TASK_ID=:task where SESSION_ID=:session_id",
                {"task": task_id, "session_id": resource_ctx["resource_session_id"]},
            )
        self._sync_wave_replenishment_status(task, "IN_PROGRESS", assignee)
        self._sync_wave_picking_move_status(task, "IN_PROGRESS", assignee)

    def complete_task(self, task_id: int, request: WarehouseTaskStatusRequest, actor: str | None = None) -> dict:
        from ..modules.inventory.public import complete_existing_warehouse_task
        return complete_existing_warehouse_task(self.gateway, task_id, request, actor or request.updated_by or "API")

    def cancel_task(self, task_id: int, request: WarehouseTaskStatusRequest) -> None:
        task = self.get_task_or_404(task_id)
        if task.get('task_source') == 'SAP_RECEIPT':
            from ..modules.inventory.public import build_receiving_service
            try:
                build_receiving_service().cancel(task_id, request.reason or '', request.updated_by or 'API')
            except PermissionError as exc:
                raise HTTPException(403, detail=str(exc)) from exc
            except (ValueError, LookupError) as exc:
                raise HTTPException(status_code=409, detail=str(exc)) from exc
            return
        if not getattr(self.gateway, "transaction_bound", False):
            from ..modules.inventory.public import run_existing_warehouse_task_action
            return run_existing_warehouse_task_action(self.gateway, task_id, "cancel_task", request, type(self))
        if task.get("status") == "DONE":
            raise HTTPException(status_code=409, detail="Completed task cannot be cancelled.")
        if task.get("status") == "CANCELLED":
            return
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
        from ..modules.resources.public import release_cancelled_warehouse_task_resource
        release_cancelled_warehouse_task_resource(self.gateway,task,request.updated_by or request.assigned_to or "API",request.reason)
        self._sync_wave_replenishment_status(
            task,
            "CANCELLED",
            request.updated_by or request.assigned_to or "API",
            error_text=request.reason,
        )
        self._sync_wave_picking_move_status(
            task,
            "CANCELLED",
            request.updated_by or request.assigned_to or "API",
        )

    def _resource_context(self, request: WarehouseTaskStatusRequest,
                          task: dict[str, Any], action: str,
                          assignee: str | None = None) -> dict[str, Any]:
        from ..modules.resources.public import existing_task_resource_context
        return existing_task_resource_context(self.gateway, task, action, request, assignee or request.updated_by)

    def _resource_event_statement(
        self,
        task_id: int,
        event_type: str,
        event_by: str | None,
        resource_ctx: dict[str, Any],
        payload_json: str | None = None,
    ) -> tuple[str, dict[str, Any]]:
        return (
            """
            insert into RRL_RESOURCE_FACT_EVENT (
              EVENT_ID, TASK_ID, SESSION_ID, RESOURCE_ID,
              EVENT_TYPE, EVENT_AT, EVENT_BY, PAYLOAD_JSON
            )
            select RRL_RESOURCE_FACT_EVENT_SQ.nextval, :task_id,
                   :resource_session_id, :resource_id, :event_type,
                   systimestamp, :event_by, :payload_json
              from dual
             where :resource_id is not null
                or :resource_session_id is not null
                or :equipment_id is not null
            """,
            {
                "task_id": task_id,
                "event_type": event_type,
                "event_by": event_by,
                "payload_json": payload_json,
                **resource_ctx,
            },
        )

    def _sync_wave_replenishment_status(
        self,
        task: dict[str, Any],
        status: str,
        updated_by: str | None,
        fact_qty: float | None = None,
        error_text: str | None = None,
    ) -> None:
        if task.get("task_source") != "WAVE" or task.get("task_type") != "REPLENISHMENT":
            return
        source_task_id = task.get("source_task_id")
        if source_task_id is None:
            return
        wave_status = "FAILED" if status == "ERROR" else status
        self.gateway.execute(
            """
            update RRL_PICK_WAVE_REPLENISH_TASK
               set STATUS = :status,
                   UPDATED_AT = sysdate,
                   UPDATED_BY = substr(:updated_by, 1, 50)
             where PICK_WAVE_REPLENISH_TASK_ID = :source_task_id
            """,
            {
                "source_task_id": source_task_id,
                "status": wave_status,
                "updated_by": updated_by or "API",
            },
        )

    def _sync_wave_picking_move_status(
        self,
        task: dict[str, Any],
        status: str,
        updated_by: str | None,
    ) -> None:
        if task.get("task_source") != "WAVE" or task.get("task_type") != "PICKING_MOVE":
            return
        source_task_id = task.get("source_task_id")
        if source_task_id is None:
            return
        self.gateway.execute(
            """
            update RRL_PICK_WAVE_TASK
               set STATUS = :status,
                   UPDATED_AT = sysdate,
                   UPDATED_BY = substr(:updated_by, 1, 50)
             where PICK_WAVE_TASK_ID = :source_task_id
            """,
            {
                "source_task_id": source_task_id,
                "status": status,
                "updated_by": updated_by or "API",
            },
        )
