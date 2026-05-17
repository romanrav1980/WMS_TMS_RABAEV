import json
from typing import Any

from fastapi import HTTPException

from ..oracle_gateway import OracleGateway
from ..schemas import (
    MesApplyWmsRequest,
    MesCompleteOrderRequest,
    MesProductionOrderCreateRequest,
    MesRawSupplyCalculateRequest,
    MesRawTransferTaskCancelRequest,
    MesRawTransferTaskConfirmRequest,
    MesReleaseToProductionRequest,
    MesRawIssueRequest,
    MesRetryMovementRequest,
)


class MesService:
    def __init__(self, gateway: OracleGateway | None = None) -> None:
        self.gateway = gateway or OracleGateway()

    def create_order(self, request: MesProductionOrderCreateRequest) -> int:
        return self.gateway.call_number_plsql(
            """
            begin
              :result := RRL_MES_PRODUCTION_API.create_order(
                p_order_no => :order_no,
                p_bom_id => :bom_id,
                p_target_articul => :target_articul,
                p_planned_qty => :planned_qty,
                p_unit_code => :unit_code,
                p_ware_id => :ware_id,
                p_production_line => :production_line,
                p_shift_id => :shift_id,
                p_planned_start_at => :planned_start_at,
                p_planned_finish_at => :planned_finish_at,
                p_source_system => :source_system,
                p_source_message_id => :source_message_id,
                p_idempotency_key => :idempotency_key,
                p_comment_text => :comment_text,
                p_created_by => :created_by
              );
            end;
            """,
            _model_dict(request),
        )

    def issue_raw(self, production_order_id: int, request: MesRawIssueRequest) -> int:
        return self.gateway.call_number_plsql(
            """
            begin
              :result := RRL_MES_PRODUCTION_API.issue_raw_to_production(
                p_production_order_id => :production_order_id,
                p_uid_pallet => :uid_pallet,
                p_raw_batch_id => :raw_batch_id,
                p_raw_articul => :raw_articul,
                p_quantity => :quantity,
                p_unit_code => :unit_code,
                p_source_location => :source_location,
                p_production_location => :production_location,
                p_created_by => :created_by
              );
            end;
            """,
            {"production_order_id": production_order_id, **_model_dict(request)},
        )

    def complete_order(self, production_order_id: int, request: MesCompleteOrderRequest) -> int:
        payload = [_model_dict(pallet) for pallet in request.pallets]
        completion_id = self.gateway.call_number_plsql(
            """
            begin
              :result := RRL_MES_PRODUCTION_API.complete_order(
                p_production_order_id => :production_order_id,
                p_prod_batch_no => :prod_batch_no,
                p_fact_qty => :fact_qty,
                p_unit_code => :unit_code,
                p_pallets_json => :pallets_json,
                p_idempotency_key => :idempotency_key,
                p_created_by => :created_by
              );
            end;
            """,
            {
                "production_order_id": production_order_id,
                "prod_batch_no": request.prod_batch_no,
                "fact_qty": request.fact_qty,
                "unit_code": request.unit_code,
                "pallets_json": json.dumps(payload, ensure_ascii=False),
                "idempotency_key": request.idempotency_key,
                "created_by": request.created_by,
            },
        )
        self._create_fg_storage_warehouse_tasks(production_order_id, request)
        self._ensure_completion_trace_links(production_order_id, request)
        return completion_id

    def apply_wms(self, production_order_id: int, request: MesApplyWmsRequest) -> None:
        self.gateway.execute_plsql(
            """
            begin
              RRL_MES_PRODUCTION_API.apply_mes_movements_to_wms(
                p_production_order_id => :production_order_id,
                p_applied_by => :applied_by
              );
            end;
            """,
            {"production_order_id": production_order_id, **_model_dict(request)},
        )

    def retry_movement(self, movement_id: int, request: MesRetryMovementRequest) -> None:
        self.gateway.execute_plsql(
            """
            begin
              RRL_MES_PRODUCTION_API.retry_mes_movement(
                p_movement_id => :movement_id,
                p_updated_by => :updated_by
              );
            end;
            """,
            {"movement_id": movement_id, **_model_dict(request)},
        )

    def get_order(self, production_order_id: int) -> dict[str, Any]:
        rows = self.gateway.fetch_all(
            """
            select PRODUCTION_ORDER_ID, ORDER_NO, BOM_ID, TARGET_ARTICUL, TARGET_MOD_ID,
                   TARGET_GTIN, PLANNED_QTY, FACT_QTY, UNIT_CODE, WARE_ID,
                   PRODUCTION_LINE, SHIFT_ID, STATUS, PLANNED_START_AT,
                   PLANNED_FINISH_AT, STARTED_AT, COMPLETED_AT, PROD_BATCH_ID,
                   IDEMPOTENCY_KEY, SOURCE_SYSTEM, SOURCE_MESSAGE_ID, COMMENT_TEXT,
                   CREATED_AT, CREATED_BY, UPDATED_AT, UPDATED_BY
              from RRL_PRODUCTION_ORDER
             where PRODUCTION_ORDER_ID = :production_order_id
            """,
            {"production_order_id": production_order_id},
        )
        if not rows:
            return {}
        order = rows[0]
        order["bom_lines"] = self.list_order_lines(production_order_id)
        order["movements"] = self.list_movements(production_order_id=production_order_id, limit=500)
        return order

    def list_orders(
        self,
        status: str | None = None,
        target_articul: str | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        conditions = []
        params: dict[str, Any] = {"limit": clamp_limit(limit)}
        if status:
            conditions.append("STATUS = :status")
            params["status"] = status.upper()
        if target_articul:
            conditions.append("TARGET_ARTICUL = :target_articul")
            params["target_articul"] = target_articul.upper()
        where_sql = " where " + " and ".join(conditions) if conditions else ""
        return self.gateway.fetch_all(
            f"""
            select *
              from (
                select PRODUCTION_ORDER_ID, ORDER_NO, BOM_ID, TARGET_ARTICUL,
                       PLANNED_QTY, FACT_QTY, UNIT_CODE, PRODUCTION_LINE,
                       SHIFT_ID, STATUS, STARTED_AT, COMPLETED_AT, PROD_BATCH_ID,
                       CREATED_AT, CREATED_BY
                  from RRL_PRODUCTION_ORDER
                  {where_sql}
                 order by CREATED_AT desc, PRODUCTION_ORDER_ID desc
              )
             where rownum <= :limit
            """,
            params,
        )

    def list_order_lines(self, production_order_id: int) -> list[dict[str, Any]]:
        return self.gateway.fetch_all(
            """
            select ORDER_LINE_ID, PRODUCTION_ORDER_ID, BOM_ID, BOM_LINE_ID, LINE_NO,
                   COMPONENT_TYPE, COMPONENT_ARTICUL, COMPONENT_MOD_ID,
                   COMPONENT_NAME, PLANNED_QTY, UNIT_CODE, LOSS_PERCENT,
                   IS_REQUIRED, CREATED_AT, CREATED_BY
              from RRL_PROD_ORDER_BOM_LINE
             where PRODUCTION_ORDER_ID = :production_order_id
             order by LINE_NO, ORDER_LINE_ID
            """,
            {"production_order_id": production_order_id},
        )

    def list_movements(
        self,
        production_order_id: int | None = None,
        status: str | None = None,
        movement_type: str | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        conditions = []
        params: dict[str, Any] = {"limit": clamp_limit(limit)}
        if production_order_id is not None:
            conditions.append("PRODUCTION_ORDER_ID = :production_order_id")
            params["production_order_id"] = production_order_id
        if status:
            conditions.append("STATUS = :status")
            params["status"] = status.upper()
        if movement_type:
            conditions.append("MOVEMENT_TYPE = :movement_type")
            params["movement_type"] = movement_type.upper()
        where_sql = " where " + " and ".join(conditions) if conditions else ""
        return self.gateway.fetch_all(
            f"""
            select *
              from (
                select MOVEMENT_ID, MOVEMENT_TYPE, PRODUCTION_ORDER_ID, PROD_BATCH_ID,
                       BOM_ID, BOM_LINE_ID, RAW_BATCH_ID, RAW_ARTICUL, UID_PALLET,
                       SSCC, QUANTITY, PACK_COUNT, UNIT_CODE, SOURCE_LOCATION,
                       TARGET_LOCATION, STATUS, WMS_APPLIED_AT, WMS_APPLIED_BY,
                       RETRY_COUNT, LAST_ERROR, CREATED_AT, CREATED_BY, UPDATED_AT,
                       UPDATED_BY
                  from RRL_MES_MOVEMENT
                  {where_sql}
                 order by CREATED_AT desc, MOVEMENT_ID desc
              )
             where rownum <= :limit
            """,
            params,
        )

    def calculate_raw_supply(
        self,
        production_order_id: int,
        request: MesRawSupplyCalculateRequest,
    ) -> dict[str, Any]:
        order = self.get_order(production_order_id)
        if not order:
            raise HTTPException(status_code=404, detail="MES production order not found.")
        if order.get("status") in {"COMPLETED", "CANCELLED"}:
            raise HTTPException(status_code=409, detail="Raw supply cannot be recalculated for completed/cancelled order.")

        calculated_by = request.calculated_by or "API"
        self._clear_raw_supply_calculation(production_order_id, calculated_by)

        demand_count = 0
        candidate_count = 0
        shortage_count = 0
        for line in self.list_order_lines(production_order_id):
            raw_articul = str(line.get("component_articul") or "").upper()
            if not raw_articul:
                continue
            required_qty = float(line.get("planned_qty") or 0)
            issued_qty = self._issued_raw_qty(production_order_id, line)
            open_qty = max(required_qty - issued_qty, 0)
            if open_qty <= 0:
                status = "COVERED"
                soft_reservation_id = None
            else:
                status = "OPEN"
                soft_reservation_id = self._create_soft_raw_reservation(
                    production_order_id=production_order_id,
                    line=line,
                    raw_articul=raw_articul,
                    qty=open_qty,
                    unit_code=line.get("unit_code") or order.get("unit_code"),
                    created_by=calculated_by,
                )
            demand_id = self._next_sequence_value("RRL_MES_RAW_DEMAND_SQ", "DEMAND_ID")
            self.gateway.execute(
                """
                insert into RRL_MES_RAW_DEMAND (
                  DEMAND_ID, PRODUCTION_ORDER_ID, ORDER_LINE_ID, BOM_ID, BOM_LINE_ID,
                  RAW_ARTICUL, REQUIRED_QTY, ISSUED_QTY, OPEN_QTY, UNIT_CODE,
                  SOFT_RESERVATION_ID, STATUS, CALCULATED_BY
                ) values (
                  :demand_id, :production_order_id, :order_line_id, :bom_id, :bom_line_id,
                  :raw_articul, :required_qty, :issued_qty, :open_qty, :unit_code,
                  :soft_reservation_id, :status, :calculated_by
                )
                """,
                {
                    "demand_id": demand_id,
                    "production_order_id": production_order_id,
                    "order_line_id": line.get("order_line_id"),
                    "bom_id": line.get("bom_id"),
                    "bom_line_id": line.get("bom_line_id"),
                    "raw_articul": raw_articul,
                    "required_qty": required_qty,
                    "issued_qty": issued_qty,
                    "open_qty": open_qty,
                    "unit_code": line.get("unit_code") or order.get("unit_code"),
                    "soft_reservation_id": soft_reservation_id,
                    "status": status,
                    "calculated_by": calculated_by,
                },
            )
            demand_count += 1
            if open_qty <= 0:
                continue

            remaining_to_suggest = open_qty
            available_total = 0.0
            sort_order = 0
            for candidate in self._find_raw_candidates(raw_articul, limit=200):
                available_qty = float(candidate.get("available_qty") or 0)
                if available_qty <= 0:
                    continue
                sort_order += 1
                suggested_qty = min(remaining_to_suggest, available_qty) if remaining_to_suggest > 0 else 0
                available_total += available_qty
                if suggested_qty > 0:
                    remaining_to_suggest = max(remaining_to_suggest - suggested_qty, 0)
                self._insert_raw_candidate(demand_id, production_order_id, raw_articul, candidate, suggested_qty, sort_order)
                candidate_count += 1

            if available_total < open_qty:
                self._insert_raw_shortage(
                    production_order_id=production_order_id,
                    demand_id=demand_id,
                    raw_articul=raw_articul,
                    required_qty=required_qty,
                    issued_qty=issued_qty,
                    available_qty=available_total,
                    shortage_qty=max(open_qty - available_total, 0),
                    unit_code=line.get("unit_code") or order.get("unit_code"),
                )
                shortage_count += 1

        return {
            "status": "ok",
            "production_order_id": production_order_id,
            "demand_count": demand_count,
            "candidate_count": candidate_count,
            "shortage_count": shortage_count,
        }

    def get_raw_supply(self, production_order_id: int) -> dict[str, Any]:
        order = self.get_order(production_order_id)
        if not order:
            raise HTTPException(status_code=404, detail="MES production order not found.")
        return {
            "order": order,
            "demands": self.gateway.fetch_all(
                """
                select *
                  from RRL_MES_RAW_DEMAND
                 where PRODUCTION_ORDER_ID = :production_order_id
                 order by DEMAND_ID
                """,
                {"production_order_id": production_order_id},
            ),
            "candidates": self.gateway.fetch_all(
                """
                select *
                  from RRL_MES_RAW_SUPPLY_CANDIDATE
                 where PRODUCTION_ORDER_ID = :production_order_id
                 order by DEMAND_ID, SORT_ORDER, CANDIDATE_ID
                """,
                {"production_order_id": production_order_id},
            ),
            "shortages": self.gateway.fetch_all(
                """
                select *
                  from RRL_MES_RAW_SHORTAGE
                 where PRODUCTION_ORDER_ID = :production_order_id
                 order by SHORTAGE_ID
                """,
                {"production_order_id": production_order_id},
            ),
            "reservations": self.gateway.fetch_all(
                """
                select *
                  from RRL_STOCK_RESERVATION
                 where RESERVATION_DOMAIN = 'MES_RAW'
                   and PRODUCTION_ORDER_ID = :production_order_id
                 order by RESERVATION_ID
                """,
                {"production_order_id": production_order_id},
            ),
            "tasks": self.list_raw_transfer_tasks(production_order_id=production_order_id, limit=500),
        }

    def release_to_production(
        self,
        production_order_id: int,
        request: MesReleaseToProductionRequest,
    ) -> dict[str, Any]:
        order = self.get_order(production_order_id)
        if not order:
            raise HTTPException(status_code=404, detail="MES production order not found.")
        if order.get("status") in {"COMPLETED", "CANCELLED"}:
            raise HTTPException(status_code=409, detail="Completed/cancelled production order cannot be released.")

        task_count = self.gateway.call_number_plsql(
            """
            begin
              :result := RRL_MES_RAW_SUPPLY_API.release_to_production(
                p_production_order_id => :production_order_id,
                p_to_ware_id => :to_ware_id,
                p_to_cell => :to_cell,
                p_allow_partial => :allow_partial,
                p_created_by => :created_by
              );
            end;
            """,
            {
                "production_order_id": production_order_id,
                "to_ware_id": request.to_ware_id,
                "to_cell": request.to_cell,
                "allow_partial": int(request.allow_partial or 0),
                "created_by": request.created_by or "API",
            },
        )
        shortages = self.gateway.fetch_all(
            """
            select *
              from RRL_MES_RAW_SHORTAGE
             where PRODUCTION_ORDER_ID = :production_order_id
               and STATUS = 'OPEN'
               and SHORTAGE_QTY > 0
            """,
            {"production_order_id": production_order_id},
        )
        if shortages and int(request.allow_partial or 0) != 1:
            raise HTTPException(
                status_code=409,
                detail={
                    "message": "Raw material shortage. Use allow_partial=1 to create partial transfer tasks.",
                    "shortages": shortages,
                },
            )
        tasks = self.gateway.fetch_all(
            """
            select TASK_ID
              from RRL_MES_RAW_TRANSFER_TASK
             where PRODUCTION_ORDER_ID = :production_order_id
               and TASK_STATUS in ('PLANNED', 'IN_PROGRESS')
             order by TASK_ID
            """,
            {"production_order_id": production_order_id},
        )
        task_ids = [int(row["task_id"]) for row in tasks]
        self._create_raw_warehouse_tasks(production_order_id)
        return {
            "status": "ok",
            "production_order_id": production_order_id,
            "created_task_count": task_count,
            "task_ids": task_ids,
            "shortage_count": len(shortages),
        }

    def list_raw_transfer_tasks(
        self,
        production_order_id: int | None = None,
        status: str | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        conditions = []
        params: dict[str, Any] = {"limit": clamp_limit(limit)}
        if production_order_id is not None:
            conditions.append("PRODUCTION_ORDER_ID = :production_order_id")
            params["production_order_id"] = production_order_id
        if status:
            conditions.append("TASK_STATUS = :status")
            params["status"] = status.upper()
        where_sql = " where " + " and ".join(conditions) if conditions else ""
        return self.gateway.fetch_all(
            f"""
            select *
              from (
                select *
                  from RRL_MES_RAW_TRANSFER_TASK
                  {where_sql}
                 order by CREATED_AT desc, TASK_ID desc
              )
             where rownum <= :limit
            """,
            params,
        )

    def list_raw_shortages(
        self,
        production_order_id: int | None = None,
        status: str | None = None,
        raw_articul: str | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        conditions = []
        params: dict[str, Any] = {"limit": clamp_limit(limit)}
        if production_order_id is not None:
            conditions.append("s.PRODUCTION_ORDER_ID = :production_order_id")
            params["production_order_id"] = production_order_id
        if status:
            conditions.append("s.STATUS = :status")
            params["status"] = status.upper()
        if raw_articul:
            conditions.append("upper(s.RAW_ARTICUL) = :raw_articul")
            params["raw_articul"] = raw_articul.upper()
        where_sql = " where " + " and ".join(conditions) if conditions else ""
        return self.gateway.fetch_all(
            f"""
            select *
              from (
                select s.SHORTAGE_ID, s.PRODUCTION_ORDER_ID, o.ORDER_NO,
                       o.TARGET_ARTICUL, o.STATUS ORDER_STATUS,
                       s.DEMAND_ID, s.RAW_ARTICUL, s.REQUIRED_QTY,
                       s.ISSUED_QTY, s.AVAILABLE_QTY, s.SHORTAGE_QTY,
                       s.UNIT_CODE, s.STATUS, s.CREATED_AT
                  from RRL_MES_RAW_SHORTAGE s
                  left join RRL_PRODUCTION_ORDER o
                    on o.PRODUCTION_ORDER_ID = s.PRODUCTION_ORDER_ID
                  {where_sql}
                 order by s.CREATED_AT desc, s.SHORTAGE_ID desc
              )
             where rownum <= :limit
            """,
            params,
        )

    def get_raw_transfer_task_or_404(self, task_id: int) -> dict[str, Any]:
        rows = self.gateway.fetch_all(
            """
            select *
              from RRL_MES_RAW_TRANSFER_TASK
             where TASK_ID = :task_id
            """,
            {"task_id": task_id},
        )
        if not rows:
            raise HTTPException(status_code=404, detail="MES raw transfer task not found.")
        return rows[0]

    def confirm_raw_transfer_task(
        self,
        task_id: int,
        request: MesRawTransferTaskConfirmRequest,
    ) -> int:
        task = self.get_raw_transfer_task_or_404(task_id)
        if task.get("task_status") not in {"PLANNED", "IN_PROGRESS"}:
            raise HTTPException(status_code=409, detail="Only planned/in-progress transfer task can be confirmed.")
        fact_qty = request.fact_qty if request.fact_qty is not None else task.get("task_qty")
        if fact_qty is None or float(fact_qty) <= 0:
            raise HTTPException(status_code=400, detail="fact_qty must be positive.")
        movement_id = self.issue_raw(
            int(task["production_order_id"]),
            MesRawIssueRequest(
                uid_pallet=task.get("uid_pallet"),
                raw_batch_id=task.get("raw_batch_id"),
                raw_articul=task.get("raw_articul"),
                quantity=float(fact_qty),
                unit_code=task.get("unit_code") or "KG",
                source_location=task.get("from_cell"),
                production_location=task.get("to_cell"),
                created_by=request.confirmed_by or "API",
            ),
        )
        self.gateway.execute(
            """
            update RRL_MES_RAW_TRANSFER_TASK
               set TASK_STATUS = 'DONE',
                   FACT_QTY = :fact_qty,
                   FINISHED_AT = systimestamp,
                   LAST_ERROR = null
             where TASK_ID = :task_id
            """,
            {"task_id": task_id, "fact_qty": fact_qty},
        )
        if task.get("reservation_id") is not None:
            self.gateway.execute(
                """
                update RRL_STOCK_RESERVATION
                   set STATUS = 'CONSUMED',
                       CONSUMED_AT = systimestamp,
                       CONSUMED_BY = :consumed_by
                 where RESERVATION_ID = :reservation_id
                """,
                {
                    "reservation_id": task.get("reservation_id"),
                    "consumed_by": request.confirmed_by or "API",
                },
            )
        self._sync_warehouse_task_from_raw_task(task_id, "DONE", request.confirmed_by or "API", fact_qty)
        return movement_id

    def cancel_raw_transfer_task(
        self,
        task_id: int,
        request: MesRawTransferTaskCancelRequest,
    ) -> None:
        task = self.get_raw_transfer_task_or_404(task_id)
        if task.get("task_status") == "DONE":
            raise HTTPException(status_code=409, detail="Completed transfer task cannot be cancelled.")
        cancelled_by = request.cancelled_by or "API"
        self.gateway.execute(
            """
            update RRL_MES_RAW_TRANSFER_TASK
               set TASK_STATUS = 'CANCELLED',
                   CANCELLED_AT = systimestamp,
                   CANCELLED_BY = :cancelled_by,
                   LAST_ERROR = :reason
             where TASK_ID = :task_id
            """,
            {"task_id": task_id, "cancelled_by": cancelled_by, "reason": request.reason},
        )
        if task.get("reservation_id") is not None:
            self.gateway.execute(
                """
                update RRL_STOCK_RESERVATION
                   set STATUS = 'CANCELLED',
                       RELEASED_AT = systimestamp,
                       RELEASED_BY = :released_by,
                       RELEASE_REASON = :reason
                 where RESERVATION_ID = :reservation_id
                """,
                {
                    "reservation_id": task.get("reservation_id"),
                    "released_by": cancelled_by,
                    "reason": request.reason,
                },
            )
        self._sync_warehouse_task_from_raw_task(task_id, "CANCELLED", cancelled_by, None, request.reason)

    def _clear_raw_supply_calculation(self, production_order_id: int, updated_by: str) -> None:
        self.gateway.execute(
            """
            update RRL_STOCK_RESERVATION
               set STATUS = 'CANCELLED',
                   RELEASED_AT = systimestamp,
                   RELEASED_BY = :updated_by,
                   RELEASE_REASON = 'MES raw supply recalculation'
             where RESERVATION_DOMAIN = 'MES_RAW'
               and PRODUCTION_ORDER_ID = :production_order_id
               and RESERVATION_KIND = 'SOFT'
               and STATUS = 'ACTIVE'
            """,
            {"production_order_id": production_order_id, "updated_by": updated_by},
        )
        for table_name in (
            "RRL_MES_RAW_SUPPLY_CANDIDATE",
            "RRL_MES_RAW_SHORTAGE",
            "RRL_MES_RAW_DEMAND",
        ):
            self.gateway.execute(
                f"delete from {table_name} where PRODUCTION_ORDER_ID = :production_order_id",
                {"production_order_id": production_order_id},
            )

    def _issued_raw_qty(self, production_order_id: int, line: dict[str, Any]) -> float:
        rows = self.gateway.fetch_all(
            """
            select nvl(sum(nvl(QUANTITY, 0)), 0) ISSUED_QTY
              from RRL_MES_MOVEMENT
             where PRODUCTION_ORDER_ID = :production_order_id
               and MOVEMENT_TYPE = 'RAW_ISSUE_TO_PRODUCTION'
               and STATUS <> 'CANCELLED'
               and (
                    (BOM_LINE_ID is not null and BOM_LINE_ID = :bom_line_id)
                    or (BOM_LINE_ID is null and upper(RAW_ARTICUL) = :raw_articul)
               )
            """,
            {
                "production_order_id": production_order_id,
                "bom_line_id": line.get("bom_line_id"),
                "raw_articul": str(line.get("component_articul") or "").upper(),
            },
        )
        return float(rows[0]["issued_qty"] or 0) if rows else 0.0

    def _create_soft_raw_reservation(
        self,
        production_order_id: int,
        line: dict[str, Any],
        raw_articul: str,
        qty: float,
        unit_code: str | None,
        created_by: str,
    ) -> int:
        reservation_id = self._next_sequence_value("RRL_STOCK_RESERVATION_SQ", "RESERVATION_ID")
        self.gateway.execute(
            """
            insert into RRL_STOCK_RESERVATION (
              RESERVATION_ID, RESERVATION_KIND, RESERVATION_SCOPE, RESERVATION_DOMAIN,
              SOURCE_DOC_TYPE, SOURCE_DOC_ID, SOURCE_LINE_ID, PRODUCTION_ORDER_ID,
              ARTICUL, QTY, UNIT_CODE, STATUS, PRIORITY, CREATED_BY
            ) values (
              :reservation_id, 'SOFT', 'QTY', 'MES_RAW',
              'PRODUCTION_ORDER', :production_order_id, :source_line_id, :production_order_id,
              :articul, :qty, :unit_code, 'ACTIVE', 100, :created_by
            )
            """,
            {
                "reservation_id": reservation_id,
                "production_order_id": production_order_id,
                "source_line_id": line.get("order_line_id"),
                "articul": raw_articul,
                "qty": qty,
                "unit_code": unit_code,
                "created_by": created_by,
            },
        )
        return reservation_id

    def _find_raw_candidates(self, raw_articul: str, limit: int = 200) -> list[dict[str, Any]]:
        return self.gateway.fetch_all(
            """
            select *
              from (
                select w.ID WARE_ID,
                       r.CELL,
                       r.UID_POLETA UID_PALLET,
                       p.SSCC,
                       p.ARTICUL,
                       p.PRIHOD_NAKLAD_ID RAW_BATCH_ID,
                       to_char(p.PRIHOD_NAKLAD_ID) BATCH_ID,
                       p.EXPIRY_DATE,
                       nvl(p.QUALITY_STATUS, 'UNKNOWN') QUALITY_STATUS,
                       nvl(r.REMAIN, 0) PHYSICAL_QTY,
                       nvl(hr.HARD_RESERVED_QTY, 0) HARD_RESERVED_QTY,
                       greatest(nvl(r.REMAIN, 0) - nvl(hr.HARD_RESERVED_QTY, 0), 0) AVAILABLE_QTY
                  from RRL_REMAINS r
                  join RRL_CELLS c on c.CELL = r.CELL
                  join RRL_WARES w on w.ID = c.WARE_ID
                  join RRL_PALLETS p on p.UID_PALLET = r.UID_POLETA
                  left join (
                    select UID_PALLET, sum(nvl(QTY, 0)) HARD_RESERVED_QTY
                      from RRL_STOCK_RESERVATION
                     where RESERVATION_KIND = 'HARD'
                       and STATUS in ('ACTIVE', 'ALLOCATED', 'PICKING')
                       and UID_PALLET is not null
                     group by UID_PALLET
                  ) hr on hr.UID_PALLET = r.UID_POLETA
                 where nvl(w.FLAG_RAW_MATERIAL, 0) = 1
                   and upper(p.ARTICUL) = :raw_articul
                   and nvl(r.REMAIN, 0) > 0
                 order by p.EXPIRY_DATE nulls last, p.PRODUCED_DATE nulls last, r.CELL, r.UID_POLETA
              )
             where rownum <= :limit
            """,
            {"raw_articul": raw_articul.upper(), "limit": min(max(limit, 1), 1000)},
        )

    def _insert_raw_candidate(
        self,
        demand_id: int,
        production_order_id: int,
        raw_articul: str,
        candidate: dict[str, Any],
        suggested_qty: float,
        sort_order: int,
    ) -> None:
        candidate_id = self._next_sequence_value("RRL_MES_RAW_SUPPLY_CANDIDATE_SQ", "CANDIDATE_ID")
        self.gateway.execute(
            """
            insert into RRL_MES_RAW_SUPPLY_CANDIDATE (
              CANDIDATE_ID, DEMAND_ID, PRODUCTION_ORDER_ID, RAW_ARTICUL,
              UID_PALLET, BATCH_ID, RAW_BATCH_ID, SSCC, FROM_WARE_ID, FROM_CELL,
              PHYSICAL_QTY, HARD_RESERVED_QTY, AVAILABLE_QTY, SUGGESTED_QTY,
              EXPIRY_DATE, QUALITY_STATUS, SORT_ORDER
            ) values (
              :candidate_id, :demand_id, :production_order_id, :raw_articul,
              :uid_pallet, :batch_id, :raw_batch_id, :sscc, :from_ware_id, :from_cell,
              :physical_qty, :hard_reserved_qty, :available_qty, :suggested_qty,
              :expiry_date, :quality_status, :sort_order
            )
            """,
            {
                "candidate_id": candidate_id,
                "demand_id": demand_id,
                "production_order_id": production_order_id,
                "raw_articul": raw_articul,
                "uid_pallet": candidate.get("uid_pallet"),
                "batch_id": candidate.get("batch_id"),
                "raw_batch_id": candidate.get("raw_batch_id"),
                "sscc": candidate.get("sscc"),
                "from_ware_id": candidate.get("ware_id"),
                "from_cell": candidate.get("cell"),
                "physical_qty": candidate.get("physical_qty"),
                "hard_reserved_qty": candidate.get("hard_reserved_qty"),
                "available_qty": candidate.get("available_qty"),
                "suggested_qty": suggested_qty,
                "expiry_date": candidate.get("expiry_date"),
                "quality_status": candidate.get("quality_status"),
                "sort_order": sort_order,
            },
        )

    def _insert_raw_shortage(
        self,
        production_order_id: int,
        demand_id: int,
        raw_articul: str,
        required_qty: float,
        issued_qty: float,
        available_qty: float,
        shortage_qty: float,
        unit_code: str | None,
    ) -> None:
        shortage_id = self._next_sequence_value("RRL_MES_RAW_SHORTAGE_SQ", "SHORTAGE_ID")
        self.gateway.execute(
            """
            insert into RRL_MES_RAW_SHORTAGE (
              SHORTAGE_ID, PRODUCTION_ORDER_ID, DEMAND_ID, RAW_ARTICUL,
              REQUIRED_QTY, ISSUED_QTY, AVAILABLE_QTY, SHORTAGE_QTY, UNIT_CODE, STATUS
            ) values (
              :shortage_id, :production_order_id, :demand_id, :raw_articul,
              :required_qty, :issued_qty, :available_qty, :shortage_qty, :unit_code, 'OPEN'
            )
            """,
            {
                "shortage_id": shortage_id,
                "production_order_id": production_order_id,
                "demand_id": demand_id,
                "raw_articul": raw_articul,
                "required_qty": required_qty,
                "issued_qty": issued_qty,
                "available_qty": available_qty,
                "shortage_qty": shortage_qty,
                "unit_code": unit_code,
            },
        )

    def _active_mes_task_exists(self, production_order_id: int, candidate: dict[str, Any]) -> bool:
        rows = self.gateway.fetch_all(
            """
            select count(*) CNT
              from RRL_MES_RAW_TRANSFER_TASK
             where PRODUCTION_ORDER_ID = :production_order_id
               and ORDER_LINE_ID = :order_line_id
               and UID_PALLET = :uid_pallet
               and TASK_STATUS in ('PLANNED', 'IN_PROGRESS')
            """,
            {
                "production_order_id": production_order_id,
                "order_line_id": candidate.get("order_line_id"),
                "uid_pallet": candidate.get("uid_pallet"),
            },
        )
        return bool(rows and int(rows[0]["cnt"] or 0) > 0)

    def _create_hard_raw_reservation(
        self,
        production_order_id: int,
        candidate: dict[str, Any],
        created_by: str,
    ) -> int:
        reservation_id = self._next_sequence_value("RRL_STOCK_RESERVATION_SQ", "RESERVATION_ID")
        suggested_qty = float(candidate.get("suggested_qty") or 0)
        physical_qty = float(candidate.get("physical_qty") or 0)
        reservation_scope = "PALLET" if physical_qty > 0 and suggested_qty >= physical_qty else "QTY"
        self.gateway.execute(
            """
            insert into RRL_STOCK_RESERVATION (
              RESERVATION_ID, RESERVATION_KIND, RESERVATION_SCOPE, RESERVATION_DOMAIN,
              SOURCE_DOC_TYPE, SOURCE_DOC_ID, SOURCE_LINE_ID, PRODUCTION_ORDER_ID,
              ARTICUL, QTY, UNIT_CODE, WARE_ID, CELL, BATCH_ID, UID_PALLET, SSCC,
              STATUS, PRIORITY, CREATED_BY
            ) values (
              :reservation_id, 'HARD', :reservation_scope, 'MES_RAW',
              'PRODUCTION_ORDER', :production_order_id, :source_line_id, :production_order_id,
              :articul, :qty, :unit_code, :ware_id, :cell, :batch_id, :uid_pallet, :sscc,
              'ACTIVE', 100, :created_by
            )
            """,
            {
                "reservation_id": reservation_id,
                "reservation_scope": reservation_scope,
                "production_order_id": production_order_id,
                "source_line_id": candidate.get("order_line_id"),
                "articul": candidate.get("raw_articul"),
                "qty": suggested_qty,
                "unit_code": candidate.get("unit_code"),
                "ware_id": candidate.get("from_ware_id"),
                "cell": candidate.get("from_cell"),
                "batch_id": candidate.get("batch_id"),
                "uid_pallet": candidate.get("uid_pallet"),
                "sscc": candidate.get("sscc"),
                "created_by": created_by,
            },
        )
        return reservation_id

    def _create_raw_transfer_task(
        self,
        production_order_id: int,
        candidate: dict[str, Any],
        reservation_id: int,
        to_ware_id: int | None,
        to_cell: str,
        created_by: str,
    ) -> int:
        task_id = self._next_sequence_value("RRL_MES_RAW_TRANSFER_TASK_SQ", "TASK_ID")
        self.gateway.execute(
            """
            insert into RRL_MES_RAW_TRANSFER_TASK (
              TASK_ID, PRODUCTION_ORDER_ID, ORDER_LINE_ID, BOM_ID, BOM_LINE_ID,
              RAW_ARTICUL, RAW_BATCH_ID, BATCH_ID, UID_PALLET, SSCC,
              FROM_WARE_ID, FROM_CELL, TO_WARE_ID, TO_CELL,
              REQUIRED_QTY, TASK_QTY, UNIT_CODE, RESERVATION_ID,
              TASK_STATUS, PRIORITY, CREATED_BY
            ) values (
              :task_id, :production_order_id, :order_line_id, :bom_id, :bom_line_id,
              :raw_articul, :raw_batch_id, :batch_id, :uid_pallet, :sscc,
              :from_ware_id, :from_cell, :to_ware_id, :to_cell,
              :required_qty, :task_qty, :unit_code, :reservation_id,
              'PLANNED', 100, :created_by
            )
            """,
            {
                "task_id": task_id,
                "production_order_id": production_order_id,
                "order_line_id": candidate.get("order_line_id"),
                "bom_id": candidate.get("bom_id"),
                "bom_line_id": candidate.get("bom_line_id"),
                "raw_articul": candidate.get("raw_articul"),
                "raw_batch_id": candidate.get("raw_batch_id"),
                "batch_id": candidate.get("batch_id"),
                "uid_pallet": candidate.get("uid_pallet"),
                "sscc": candidate.get("sscc"),
                "from_ware_id": candidate.get("from_ware_id"),
                "from_cell": candidate.get("from_cell"),
                "to_ware_id": to_ware_id,
                "to_cell": to_cell,
                "required_qty": candidate.get("required_qty"),
                "task_qty": candidate.get("suggested_qty"),
                "unit_code": candidate.get("unit_code"),
                "reservation_id": reservation_id,
                "created_by": created_by,
            },
        )
        return task_id

    def _create_raw_warehouse_tasks(self, production_order_id: int) -> None:
        self.gateway.execute(
            """
            insert into RRL_WAREHOUSE_TASK (
              TASK_ID, TASK_TYPE, TASK_SOURCE, SOURCE_TASK_ID, SOURCE_DOC_TYPE,
              SOURCE_DOC_ID, PRODUCTION_ORDER_ID, RAW_ARTICUL, UID_PALLET, SSCC,
              FROM_WARE_ID, FROM_CELL, TO_WARE_ID, TO_CELL, QTY, UNIT_CODE,
              PRIORITY, STATUS, CREATED_AT, CREATED_BY
            )
            select RRL_WAREHOUSE_TASK_SQ.nextval, 'RAW_TO_PRODUCTION',
                   'MES_RAW_SUPPLY', t.TASK_ID, 'PRODUCTION_ORDER',
                   t.PRODUCTION_ORDER_ID, t.PRODUCTION_ORDER_ID, t.RAW_ARTICUL,
                   t.UID_PALLET, t.SSCC, t.FROM_WARE_ID, t.FROM_CELL,
                   t.TO_WARE_ID, t.TO_CELL, t.TASK_QTY, t.UNIT_CODE,
                   t.PRIORITY, t.TASK_STATUS, t.CREATED_AT, t.CREATED_BY
              from RRL_MES_RAW_TRANSFER_TASK t
             where t.PRODUCTION_ORDER_ID = :production_order_id
               and t.TASK_STATUS in ('PLANNED', 'IN_PROGRESS')
               and not exists (
                 select 1
                   from RRL_WAREHOUSE_TASK wt
                  where wt.TASK_SOURCE = 'MES_RAW_SUPPLY'
                    and wt.SOURCE_TASK_ID = t.TASK_ID
                    and wt.TASK_TYPE = 'RAW_TO_PRODUCTION'
               )
            """,
            {"production_order_id": production_order_id},
        )

    def _sync_warehouse_task_from_raw_task(
        self,
        source_task_id: int,
        status: str,
        updated_by: str,
        fact_qty: float | None = None,
        error_text: str | None = None,
    ) -> None:
        if status == "DONE":
            self.gateway.execute(
                """
                update RRL_WAREHOUSE_TASK
                   set STATUS = 'DONE',
                       QTY = nvl(:fact_qty, QTY),
                       FINISHED_AT = systimestamp,
                       ASSIGNED_TO = nvl(ASSIGNED_TO, :updated_by),
                       LAST_ERROR = null
                 where TASK_SOURCE = 'MES_RAW_SUPPLY'
                   and SOURCE_TASK_ID = :source_task_id
                   and TASK_TYPE = 'RAW_TO_PRODUCTION'
                """,
                {"source_task_id": source_task_id, "updated_by": updated_by, "fact_qty": fact_qty},
            )
            return
        self.gateway.execute(
            """
            update RRL_WAREHOUSE_TASK
               set STATUS = :status,
                   CANCELLED_AT = case when :status = 'CANCELLED' then systimestamp else CANCELLED_AT end,
                   CANCELLED_BY = case when :status = 'CANCELLED' then :updated_by else CANCELLED_BY end,
                   LAST_ERROR = :error_text
             where TASK_SOURCE = 'MES_RAW_SUPPLY'
               and SOURCE_TASK_ID = :source_task_id
               and TASK_TYPE = 'RAW_TO_PRODUCTION'
            """,
            {
                "source_task_id": source_task_id,
                "status": status,
                "updated_by": updated_by,
                "error_text": error_text,
            },
        )

    def _create_fg_storage_warehouse_tasks(
        self,
        production_order_id: int,
        request: MesCompleteOrderRequest,
    ) -> None:
        for pallet in request.pallets:
            target_cell = pallet.target_cell or "FG_RECEIVE"
            self.gateway.execute(
                """
                update RRL_MES_MOVEMENT
                   set TARGET_LOCATION = :target_cell,
                       UPDATED_AT = sysdate,
                       UPDATED_BY = :updated_by
                 where PRODUCTION_ORDER_ID = :production_order_id
                   and MOVEMENT_TYPE = 'FG_PALLET_RELEASE'
                   and UID_PALLET = :uid_pallet
                   and STATUS in ('MES_POSTED', 'ERROR')
                """,
                {
                    "production_order_id": production_order_id,
                    "uid_pallet": pallet.uid_pallet,
                    "target_cell": target_cell,
                    "updated_by": request.created_by or "API",
                },
            )
        self.gateway.execute(
            """
            insert into RRL_WAREHOUSE_TASK (
              TASK_ID, TASK_TYPE, TASK_SOURCE, SOURCE_MOVEMENT_ID,
              SOURCE_DOC_TYPE, SOURCE_DOC_ID, PRODUCTION_ORDER_ID, PROD_BATCH_ID,
              TARGET_ARTICUL, UID_PALLET, SSCC, FROM_CELL, TO_WARE_ID,
              TO_CELL, QTY, UNIT_CODE, PRIORITY, STATUS, CREATED_AT, CREATED_BY
            )
            select RRL_WAREHOUSE_TASK_SQ.nextval, 'FG_TO_STORAGE',
                   'MES_COMPLETION', m.MOVEMENT_ID, 'PRODUCTION_ORDER',
                   m.PRODUCTION_ORDER_ID, m.PRODUCTION_ORDER_ID, m.PROD_BATCH_ID,
                   o.TARGET_ARTICUL, m.UID_PALLET, m.SSCC,
                   nvl(m.SOURCE_LOCATION, 'MES_PRODUCTION'),
                   :target_ware_id, nvl(m.TARGET_LOCATION, 'FG_RECEIVE'),
                   nvl(m.QUANTITY, 0), m.UNIT_CODE, 100, 'PLANNED',
                   systimestamp, :created_by
              from RRL_MES_MOVEMENT m
              join RRL_PRODUCTION_ORDER o
                on o.PRODUCTION_ORDER_ID = m.PRODUCTION_ORDER_ID
             where m.PRODUCTION_ORDER_ID = :production_order_id
               and m.MOVEMENT_TYPE = 'FG_PALLET_RELEASE'
               and not exists (
                 select 1
                   from RRL_WAREHOUSE_TASK wt
                  where wt.TASK_SOURCE = 'MES_COMPLETION'
                    and wt.SOURCE_MOVEMENT_ID = m.MOVEMENT_ID
                    and wt.TASK_TYPE = 'FG_TO_STORAGE'
               )
            """,
            {
                "production_order_id": production_order_id,
                "target_ware_id": next((p.target_ware_id for p in request.pallets if p.target_ware_id is not None), None),
                "created_by": request.created_by or "API",
            },
        )

    def _next_sequence_value(self, sequence_name: str, alias: str) -> int:
        rows = self.gateway.fetch_all(f"select {sequence_name}.nextval {alias} from dual")
        return int(rows[0][alias.lower()])

    def get_genealogy(self, production_order_id: int) -> dict[str, Any]:
        order = self.get_order(production_order_id)
        if not order:
            raise HTTPException(status_code=404, detail="MES production order not found.")
        prod_batch_id = order.get("prod_batch_id")
        pallets = []
        usages = []
        if prod_batch_id is not None:
            batch_readiness = self.gateway.fetch_all(
                """
                select PROD_BATCH_ID, QUALITY_STATUS, AGING_REQUIRED_HOURS,
                       AGING_UNTIL, SHIPMENT_ALLOWED_AT, SHIPMENT_RELEASE_STATUS,
                       SHIPMENT_BLOCK_REASON, SHIPMENT_EFFECTIVE_STATUS,
                       IS_SHIPMENT_ALLOWED
                  from RRL_PROD_BATCH_READY_V
                 where PROD_BATCH_ID = :prod_batch_id
                """,
                {"prod_batch_id": prod_batch_id},
            )
            pallets = self.gateway.fetch_all(
                """
                select PROD_BATCH_ID, UID_PALLET, PALLET_NO, QUANTITY, PACK_COUNT,
                       NET_WEIGHT, GROSS_WEIGHT, SSCC, AGGREGATION_STATUS,
                       CREATED_AT, CREATED_BY
                  from RRL_PROD_BATCH_PALLETS
                 where PROD_BATCH_ID = :prod_batch_id
                 order by PALLET_NO, UID_PALLET
                """,
                {"prod_batch_id": prod_batch_id},
            )
            usages = self.gateway.fetch_all(
                """
                select RAW_USAGE_ID, PROD_BATCH_ID, PRODUCTION_ORDER_ID, RAW_BATCH_ID,
                       RAW_ARTICUL, QUANTITY_PLANNED, QUANTITY_FACT, UNIT_CODE,
                       USED_AT, USED_BY
                  from RRL_PROD_RAW_USAGE
                 where PROD_BATCH_ID = :prod_batch_id
                 order by RAW_USAGE_ID
                """,
                {"prod_batch_id": prod_batch_id},
            )
        else:
            batch_readiness = []
        return {
            "order": order,
            "batch_readiness": batch_readiness[0] if batch_readiness else {},
            "raw_usage": usages,
            "pallets": pallets,
        }

    def _ensure_completion_trace_links(
        self,
        production_order_id: int,
        request: MesCompleteOrderRequest,
    ) -> None:
        rows = self.gateway.fetch_all(
            """
            select PRODUCTION_ORDER_ID, ORDER_NO, PROD_BATCH_ID, FACT_QTY, UNIT_CODE
              from RRL_PRODUCTION_ORDER
             where PRODUCTION_ORDER_ID = :production_order_id
            """,
            {"production_order_id": production_order_id},
        )
        if not rows or rows[0].get("prod_batch_id") is None:
            return

        order = rows[0]
        prod_batch_id = str(order["prod_batch_id"])
        created_by = request.created_by or "API"
        unit_code = request.unit_code or order.get("unit_code") or "KG"
        trace_event_id = self._find_completion_trace_event_id(production_order_id)

        self._add_trace_edge_once(
            from_entity_type="PRODUCTION_ORDER",
            from_entity_id=str(production_order_id),
            to_entity_type="FINISHED_GOODS_LOT",
            to_entity_id=prod_batch_id,
            edge_type="PRODUCES",
            quantity=request.fact_qty or order.get("fact_qty"),
            unit_code=unit_code,
            trace_event_id=trace_event_id,
            created_by=created_by,
        )

        raw_usages = self.gateway.fetch_all(
            """
            select RAW_BATCH_ID, RAW_ARTICUL, QUANTITY_FACT, UNIT_CODE
              from RRL_PROD_RAW_USAGE
             where PRODUCTION_ORDER_ID = :production_order_id
                or PROD_BATCH_ID = :prod_batch_id
             order by RAW_USAGE_ID
            """,
            {"production_order_id": production_order_id, "prod_batch_id": order["prod_batch_id"]},
        )
        raw_pallets = self.gateway.fetch_all(
            """
            select UID_PALLET, RAW_BATCH_ID, RAW_ARTICUL, QUANTITY, UNIT_CODE
              from RRL_MES_MOVEMENT
             where PRODUCTION_ORDER_ID = :production_order_id
               and MOVEMENT_TYPE = 'RAW_ISSUE_TO_PRODUCTION'
               and STATUS <> 'CANCELLED'
             order by MOVEMENT_ID
            """,
            {"production_order_id": production_order_id},
        )

        for raw in raw_usages:
            if raw.get("raw_batch_id") is not None:
                self._add_trace_edge_once(
                    from_entity_type="RAW_MATERIAL_LOT",
                    from_entity_id=str(raw["raw_batch_id"]),
                    to_entity_type="PRODUCTION_ORDER",
                    to_entity_id=str(production_order_id),
                    edge_type="CONSUMED_BY",
                    quantity=raw.get("quantity_fact"),
                    unit_code=raw.get("unit_code") or unit_code,
                    trace_event_id=trace_event_id,
                    created_by=created_by,
                )
            elif raw.get("raw_articul"):
                self._add_trace_edge_once(
                    from_entity_type="RAW_MATERIAL_ARTICUL",
                    from_entity_id=str(raw["raw_articul"]),
                    to_entity_type="PRODUCTION_ORDER",
                    to_entity_id=str(production_order_id),
                    edge_type="CONSUMED_BY",
                    quantity=raw.get("quantity_fact"),
                    unit_code=raw.get("unit_code") or unit_code,
                    trace_event_id=trace_event_id,
                    created_by=created_by,
                )

        for raw in raw_pallets:
            if raw.get("uid_pallet"):
                self._add_trace_edge_once(
                    from_entity_type="RAW_MATERIAL_PALLET",
                    from_entity_id=str(raw["uid_pallet"]),
                    to_entity_type="PRODUCTION_ORDER",
                    to_entity_id=str(production_order_id),
                    edge_type="CONSUMED_BY",
                    quantity=raw.get("quantity"),
                    unit_code=raw.get("unit_code") or unit_code,
                    trace_event_id=trace_event_id,
                    created_by=created_by,
                )

        pallets = self.gateway.fetch_all(
            """
            select UID_PALLET, SSCC, QUANTITY
              from RRL_PROD_BATCH_PALLETS
             where PROD_BATCH_ID = :prod_batch_id
             order by PALLET_NO, UID_PALLET
            """,
            {"prod_batch_id": order["prod_batch_id"]},
        )
        for pallet in pallets:
            uid_pallet = pallet.get("uid_pallet")
            if not uid_pallet:
                continue
            self._add_trace_edge_once(
                from_entity_type="FINISHED_GOODS_LOT",
                from_entity_id=prod_batch_id,
                to_entity_type="PALLET",
                to_entity_id=str(uid_pallet),
                edge_type="PACKED_AS",
                quantity=pallet.get("quantity"),
                unit_code=unit_code,
                trace_event_id=trace_event_id,
                created_by=created_by,
            )
            if pallet.get("sscc"):
                self._add_trace_edge_once(
                    from_entity_type="PALLET",
                    from_entity_id=str(uid_pallet),
                    to_entity_type="SSCC",
                    to_entity_id=str(pallet["sscc"]),
                    edge_type="HAS_SSCC",
                    quantity=pallet.get("quantity"),
                    unit_code=unit_code,
                    trace_event_id=trace_event_id,
                    created_by=created_by,
                )

    def _find_completion_trace_event_id(self, production_order_id: int) -> int | None:
        rows = self.gateway.fetch_all(
            """
            select TRACE_EVENT_ID
              from (
                select TRACE_EVENT_ID
                  from RRL_TRACE_EVENT
                 where EVENT_TYPE = 'PRODUCTION_COMPLETED'
                   and ENTITY_TYPE = 'PRODUCTION_ORDER'
                   and ENTITY_ID = :entity_id
                 order by TRACE_EVENT_ID desc
              )
             where rownum = 1
            """,
            {"entity_id": str(production_order_id)},
        )
        return int(rows[0]["trace_event_id"]) if rows else None

    def _add_trace_edge_once(
        self,
        from_entity_type: str,
        from_entity_id: str,
        to_entity_type: str,
        to_entity_id: str,
        edge_type: str,
        quantity: Any,
        unit_code: str | None,
        trace_event_id: int | None,
        created_by: str | None,
    ) -> None:
        self.gateway.execute_plsql(
            """
            declare
              v_count number;
              v_edge_id number;
            begin
              select count(*)
                into v_count
                from RRL_TRACE_EDGE
               where FROM_ENTITY_TYPE = :from_entity_type
                 and FROM_ENTITY_ID = :from_entity_id
                 and TO_ENTITY_TYPE = :to_entity_type
                 and TO_ENTITY_ID = :to_entity_id
                 and EDGE_TYPE = :edge_type;

              if v_count = 0 then
                v_edge_id := RRL_TRACEABILITY_API.add_trace_edge(
                  p_from_entity_type => :from_entity_type,
                  p_from_entity_id => :from_entity_id,
                  p_to_entity_type => :to_entity_type,
                  p_to_entity_id => :to_entity_id,
                  p_edge_type => :edge_type,
                  p_quantity => :quantity,
                  p_unit_code => :unit_code,
                  p_trace_event_id => :trace_event_id,
                  p_created_by => :created_by
                );
              end if;
            end;
            """,
            {
                "from_entity_type": from_entity_type,
                "from_entity_id": from_entity_id,
                "to_entity_type": to_entity_type,
                "to_entity_id": to_entity_id,
                "edge_type": edge_type,
                "quantity": quantity,
                "unit_code": unit_code,
                "trace_event_id": trace_event_id,
                "created_by": created_by,
            },
        )


def clamp_limit(value: int) -> int:
    return min(max(value, 1), 500)


def _model_dict(model) -> dict[str, Any]:
    if hasattr(model, "model_dump"):
        return model.model_dump()
    return model.dict()
