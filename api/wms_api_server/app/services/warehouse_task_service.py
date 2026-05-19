from typing import Any

from fastapi import HTTPException

from ..oracle_gateway import OracleGateway
from ..schemas import WarehouseTaskStatusRequest
from .mes_service import clamp_limit
from .warehouse_task_domain_sync_service import WarehouseTaskDomainSyncService


class WarehouseTaskService:
    def __init__(self, gateway: OracleGateway | None = None) -> None:
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
    ) -> list[dict[str, Any]]:
        conditions = []
        params: dict[str, Any] = {"limit": clamp_limit(limit)}
        if status:
            conditions.append("STATUS = :status")
            params["status"] = status.upper()
        if task_type:
            conditions.append("TASK_TYPE = :task_type")
            params["task_type"] = task_type.upper()
        if task_source:
            conditions.append("TASK_SOURCE = :task_source")
            params["task_source"] = task_source.upper()
        if assigned_to:
            conditions.append("upper(ASSIGNED_TO) = :assigned_to")
            params["assigned_to"] = assigned_to.upper()
        if production_order_id is not None:
            conditions.append("PRODUCTION_ORDER_ID = :production_order_id")
            params["production_order_id"] = production_order_id
        if source_doc_type:
            conditions.append("SOURCE_DOC_TYPE = :source_doc_type")
            params["source_doc_type"] = source_doc_type.upper()
        if source_doc_id is not None:
            conditions.append("SOURCE_DOC_ID = :source_doc_id")
            params["source_doc_id"] = source_doc_id
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
                       QTY_MODE, FACT_QTY, PARENT_TASK_ID,
                       PRIORITY, STATUS, ASSIGNED_TO, RESOURCE_ID,
                       RESOURCE_SESSION_ID, EQUIPMENT_ID,
                       PLANNED_START_AT, PLANNED_FINISH_AT, DISPATCH_PRIORITY,
                       CREATED_AT,
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
        resource_ctx = self._resource_context(request)
        self.gateway.execute_many(
            [
                (
                    """
                    update RRL_WAREHOUSE_TASK
                       set STATUS = 'ASSIGNED',
                           ASSIGNED_TO = :assigned_to,
                           RESOURCE_ID = nvl(:resource_id, RESOURCE_ID),
                           RESOURCE_SESSION_ID = nvl(:resource_session_id, RESOURCE_SESSION_ID),
                           EQUIPMENT_ID = nvl(:equipment_id, EQUIPMENT_ID),
                           LAST_ERROR = null
                     where TASK_ID = :task_id
                    """,
                    {"task_id": task_id, "assigned_to": assignee, **resource_ctx},
                ),
                self._resource_event_statement(
                    task_id=task_id,
                    event_type="ASSIGNED",
                    event_by=assignee,
                    resource_ctx=resource_ctx,
                ),
            ]
        )
        self._sync_wave_replenishment_status(task, "ASSIGNED", assignee)
        self._sync_wave_picking_move_status(task, "ASSIGNED", assignee)

    def start_task(self, task_id: int, request: WarehouseTaskStatusRequest) -> None:
        task = self.get_task_or_404(task_id)
        if task.get("status") not in {"PLANNED", "ASSIGNED"}:
            raise HTTPException(status_code=409, detail="Only planned/assigned task can be started.")
        assignee = request.assigned_to or request.updated_by
        resource_ctx = self._resource_context(request)
        self.gateway.execute_many(
            [
                (
                    """
                    update RRL_WAREHOUSE_TASK
                       set STATUS = 'IN_PROGRESS',
                           ASSIGNED_TO = nvl(:assigned_to, ASSIGNED_TO),
                           RESOURCE_ID = nvl(:resource_id, RESOURCE_ID),
                           RESOURCE_SESSION_ID = nvl(:resource_session_id, RESOURCE_SESSION_ID),
                           EQUIPMENT_ID = nvl(:equipment_id, EQUIPMENT_ID),
                           STARTED_AT = nvl(STARTED_AT, systimestamp),
                           LAST_ERROR = null
                     where TASK_ID = :task_id
                    """,
                    {"task_id": task_id, "assigned_to": assignee, **resource_ctx},
                ),
                self._resource_event_statement(
                    task_id=task_id,
                    event_type="STARTED",
                    event_by=assignee,
                    resource_ctx=resource_ctx,
                ),
            ]
        )
        self._sync_wave_replenishment_status(task, "IN_PROGRESS", assignee)
        self._sync_wave_picking_move_status(task, "IN_PROGRESS", assignee)

    def complete_task(self, task_id: int, request: WarehouseTaskStatusRequest) -> None:
        task = self.get_task_or_404(task_id)
        if task.get("status") in {"DONE", "CANCELLED"}:
            raise HTTPException(status_code=409, detail="Task is already closed.")
        self._validate_completion_scans(task, request)
        planned_qty = float(task.get("qty") or 0)
        qty_mode = str(task.get("qty_mode") or "BOX").upper()
        fact_qty = request.fact_qty
        if fact_qty is not None and fact_qty <= 0:
            raise HTTPException(status_code=400, detail="fact_qty must be greater than zero when provided.")
        if fact_qty is not None and fact_qty > planned_qty:
            raise HTTPException(status_code=409, detail="fact_qty cannot exceed planned task quantity.")
        if qty_mode == "PALLET" and fact_qty is not None and fact_qty < planned_qty:
            raise HTTPException(status_code=409, detail="Full-pallet task cannot be partially completed.")

        assignee = request.assigned_to or request.updated_by
        resource_ctx = self._resource_context(request)
        completed_qty = fact_qty if fact_qty is not None else planned_qty
        residual_qty = planned_qty - fact_qty if fact_qty is not None and fact_qty < planned_qty else 0
        if residual_qty > 0:
            self.gateway.execute_many(
                [
                    (
                        """
                        update RRL_WAREHOUSE_TASK
                           set STATUS = 'DONE',
                               FINISHED_AT = systimestamp,
                               ASSIGNED_TO = nvl(:assigned_to, ASSIGNED_TO),
                               RESOURCE_ID = nvl(:resource_id, RESOURCE_ID),
                               RESOURCE_SESSION_ID = nvl(:resource_session_id, RESOURCE_SESSION_ID),
                               EQUIPMENT_ID = nvl(:equipment_id, EQUIPMENT_ID),
                               QTY = :fact_qty,
                               FACT_QTY = :fact_qty,
                               LAST_ERROR = null
                         where TASK_ID = :task_id
                        """,
                        {
                            "task_id": task_id,
                            "assigned_to": assignee,
                            "fact_qty": fact_qty,
                            **resource_ctx,
                        },
                    ),
                    self._resource_event_statement(
                        task_id=task_id,
                        event_type="COMPLETED",
                        event_by=assignee,
                        resource_ctx=resource_ctx,
                        payload_json=(
                            f'{{"fact_qty":{fact_qty},"planned_qty":{planned_qty},'
                            f'"residual_qty":{residual_qty}}}'
                        ),
                    ),
                    (
                        """
                        insert into RRL_WAREHOUSE_TASK (
                          TASK_ID, TASK_TYPE, TASK_SOURCE, SOURCE_TASK_ID,
                          SOURCE_MOVEMENT_ID, SOURCE_DOC_TYPE, SOURCE_DOC_ID,
                          PRODUCTION_ORDER_ID, PROD_BATCH_ID, RAW_ARTICUL,
                          TARGET_ARTICUL, UID_PALLET, SSCC, FROM_WARE_ID,
                          FROM_CELL, TO_WARE_ID, TO_CELL, QTY, UNIT_CODE,
                          QTY_MODE, PARENT_TASK_ID, PRIORITY, STATUS,
                          CREATED_BY, LAST_ERROR
                        )
                        select RRL_WAREHOUSE_TASK_SQ.nextval, TASK_TYPE, TASK_SOURCE,
                               nvl(SOURCE_TASK_ID, :task_id), :task_id,
                               SOURCE_DOC_TYPE, SOURCE_DOC_ID, PRODUCTION_ORDER_ID,
                               PROD_BATCH_ID, RAW_ARTICUL, TARGET_ARTICUL,
                               UID_PALLET, SSCC, FROM_WARE_ID, FROM_CELL,
                               TO_WARE_ID, TO_CELL, :residual_qty, UNIT_CODE,
                               QTY_MODE, :task_id, PRIORITY, 'PLANNED',
                               substr(:created_by, 1, 100), substr(:last_error, 1, 2000)
                          from RRL_WAREHOUSE_TASK
                         where TASK_ID = :task_id
                        """,
                        {
                            "task_id": task_id,
                            "residual_qty": residual_qty,
                            "created_by": assignee or "API",
                            "last_error": (
                                f"Residual after partial completion of TASK_ID={task_id}: "
                                f"moved {fact_qty} of {planned_qty}."
                            ),
                        },
                    ),
                ]
            )
            self._sync_wave_replenishment_status(task, "IN_PROGRESS", assignee)
            WarehouseTaskDomainSyncService(self.gateway).dispatch_after_complete(task_id, assignee)
            return

        self.gateway.execute_many(
            [
                (
                    """
                    update RRL_WAREHOUSE_TASK
                       set STATUS = 'DONE',
                           FINISHED_AT = systimestamp,
                           ASSIGNED_TO = nvl(:assigned_to, ASSIGNED_TO),
                           RESOURCE_ID = nvl(:resource_id, RESOURCE_ID),
                           RESOURCE_SESSION_ID = nvl(:resource_session_id, RESOURCE_SESSION_ID),
                           EQUIPMENT_ID = nvl(:equipment_id, EQUIPMENT_ID),
                           QTY = nvl(:fact_qty, QTY),
                           FACT_QTY = :completed_qty,
                           LAST_ERROR = null
                     where TASK_ID = :task_id
                    """,
                    {
                        "task_id": task_id,
                        "assigned_to": assignee,
                        "fact_qty": fact_qty,
                        "completed_qty": completed_qty,
                        **resource_ctx,
                    },
                ),
                self._resource_event_statement(
                    task_id=task_id,
                    event_type="COMPLETED",
                    event_by=assignee,
                    resource_ctx=resource_ctx,
                    payload_json=f'{{"fact_qty":{completed_qty},"planned_qty":{planned_qty}}}',
                ),
            ]
        )
        WarehouseTaskDomainSyncService(self.gateway).dispatch_after_complete(task_id, assignee)

    def _validate_completion_scans(self, task: dict[str, Any], request: WarehouseTaskStatusRequest) -> None:
        scanned_pallet = self._normalize_scan(request.scanned_pallet)
        expected_pallets = {
            self._normalize_scan(task.get("uid_pallet")),
            self._normalize_scan(task.get("sscc")),
        }
        expected_pallets.discard("")
        if expected_pallets and not scanned_pallet:
            raise HTTPException(status_code=400, detail="scanned_pallet is required for this warehouse task.")
        if scanned_pallet and expected_pallets and scanned_pallet not in expected_pallets:
            raise HTTPException(status_code=409, detail="Scanned pallet does not match the warehouse task.")

        scanned_from_cell = self._normalize_scan(request.scanned_from_cell)
        expected_from_cell = self._normalize_scan(task.get("from_cell"))
        if expected_from_cell and scanned_from_cell and scanned_from_cell != expected_from_cell:
            raise HTTPException(status_code=409, detail="Scanned source cell does not match the warehouse task.")

        scanned_to_cell = self._normalize_scan(request.scanned_to_cell)
        expected_to_cell = self._normalize_scan(task.get("to_cell"))
        if expected_to_cell and not scanned_to_cell:
            raise HTTPException(status_code=400, detail="scanned_to_cell is required for this warehouse task.")
        if expected_to_cell and scanned_to_cell != expected_to_cell:
            raise HTTPException(status_code=409, detail="Scanned destination cell does not match the warehouse task.")

    def _normalize_scan(self, value: Any) -> str:
        return str(value or "").strip().upper()

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

    def _resource_context(self, request: WarehouseTaskStatusRequest) -> dict[str, Any]:
        resource_id = request.resource_id
        resource_session_id = request.resource_session_id
        equipment_id = request.equipment_id
        if resource_session_id is not None:
            rows = self.gateway.fetch_all(
                """
                select SESSION_ID, RESOURCE_ID, EQUIPMENT_ID, OPERATOR_USER_ID, STATUS
                  from RRL_RESOURCE_SESSION
                 where SESSION_ID = :session_id
                """,
                {"session_id": resource_session_id},
            )
            if not rows:
                raise HTTPException(status_code=404, detail="Resource session not found.")
            session = rows[0]
            if session.get("status") not in {"ACTIVE", "PAUSED"}:
                raise HTTPException(status_code=409, detail="Resource session is not active.")
            resource_id = resource_id or session.get("resource_id")
            equipment_id = equipment_id or session.get("equipment_id")
        return {
            "resource_id": resource_id,
            "resource_session_id": resource_session_id,
            "equipment_id": equipment_id,
        }

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
