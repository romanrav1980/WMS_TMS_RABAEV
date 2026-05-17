import json
from typing import Any

from fastapi import HTTPException

from ..oracle_gateway import OracleGateway
from ..schemas import (
    MesApplyWmsRequest,
    MesCompleteOrderRequest,
    MesProductionOrderCreateRequest,
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
        return self.gateway.call_number_plsql(
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


def clamp_limit(value: int) -> int:
    return min(max(value, 1), 500)


def _model_dict(model) -> dict[str, Any]:
    if hasattr(model, "model_dump"):
        return model.model_dump()
    return model.dict()
