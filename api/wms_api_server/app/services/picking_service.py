from typing import Any

from ..oracle_gateway import OracleGateway
from ..schemas import PickingPlanCreateRequest


class PickingService:
    def __init__(self, gateway: OracleGateway | None = None) -> None:
        self.gateway = gateway or OracleGateway()

    def create_plan(self, request: PickingPlanCreateRequest) -> int:
        return self.gateway.call_number_plsql(
            """
            begin
              :result := RRL_PICKING_API.create_plan(
                p_customer_order_id => :customer_order_id,
                p_plan_strategy => :plan_strategy,
                p_created_by => :created_by
              );
            end;
            """,
            request.model_dump(),
        )

    def cancel_plan(self, pick_plan_id: int, updated_by: str | None = None) -> None:
        self.gateway.execute_plsql(
            """
            begin
              RRL_PICKING_API.cancel_plan(
                p_pick_plan_id => :pick_plan_id,
                p_updated_by => :updated_by
              );
            end;
            """,
            {"pick_plan_id": pick_plan_id, "updated_by": updated_by},
        )

    def list_plans(
        self,
        status: str | None = None,
        customer_order_id: int | None = None,
        customer_id: int | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        conditions: list[str] = []
        params: dict[str, Any] = {"limit": min(max(limit, 1), 500)}
        if status:
            conditions.append("upper(p.STATUS) = :status")
            params["status"] = status.upper()
        if customer_order_id is not None:
            conditions.append("p.CUSTOMER_ORDER_ID = :customer_order_id")
            params["customer_order_id"] = customer_order_id
        if customer_id is not None:
            conditions.append("p.CUSTOMER_ID = :customer_id")
            params["customer_id"] = customer_id
        where_sql = " where " + " and ".join(conditions) if conditions else ""
        return self.gateway.fetch_all(
            f"""
            select *
              from (
                select p.PICK_PLAN_ID,
                       p.CUSTOMER_ORDER_ID,
                       co.ORDER_NO,
                       p.CUSTOMER_ID,
                       c.CUSTOMER_NAME,
                       p.WARE_ID,
                       p.ROUTE_ID,
                       p.DOCK_ID,
                       p.STATUS,
                       p.PLAN_STRATEGY,
                       p.TOTAL_ORDER_QTY,
                       p.TOTAL_PLANNED_QTY,
                       p.TOTAL_SHORTAGE_QTY,
                       count(distinct l.PICK_PLAN_LINE_ID) LINE_COUNT,
                       count(distinct t.PICK_TASK_ID) TASK_COUNT,
                       count(distinct r.PICK_RESERVATION_ID) ACTIVE_RESERVATION_COUNT,
                       p.CREATED_AT,
                       p.CREATED_BY,
                       p.UPDATED_AT
                  from RRL_PICK_PLAN p
                  join RRL_CUSTOMER_ORDER co
                    on co.CUSTOMER_ORDER_ID = p.CUSTOMER_ORDER_ID
                  left join RRL_CUSTOMER c
                    on c.CUSTOMER_ID = p.CUSTOMER_ID
                  left join RRL_PICK_PLAN_LINE l
                    on l.PICK_PLAN_ID = p.PICK_PLAN_ID
                  left join RRL_PICK_TASK t
                    on t.PICK_PLAN_ID = p.PICK_PLAN_ID
                  left join RRL_PICK_RESERVATION r
                    on r.PICK_PLAN_ID = p.PICK_PLAN_ID
                   and r.RESERVATION_STATUS = 'ACTIVE'
                  {where_sql}
                 group by p.PICK_PLAN_ID,
                          p.CUSTOMER_ORDER_ID,
                          co.ORDER_NO,
                          p.CUSTOMER_ID,
                          c.CUSTOMER_NAME,
                          p.WARE_ID,
                          p.ROUTE_ID,
                          p.DOCK_ID,
                          p.STATUS,
                          p.PLAN_STRATEGY,
                          p.TOTAL_ORDER_QTY,
                          p.TOTAL_PLANNED_QTY,
                          p.TOTAL_SHORTAGE_QTY,
                          p.CREATED_AT,
                          p.CREATED_BY,
                          p.UPDATED_AT
                 order by p.PICK_PLAN_ID desc
              )
             where rownum <= :limit
            """,
            params,
        )

    def get_plan(self, pick_plan_id: int) -> dict[str, Any] | None:
        rows = self.gateway.fetch_all(
            """
            select p.PICK_PLAN_ID,
                   p.CUSTOMER_ORDER_ID,
                   co.ORDER_NO,
                   p.CUSTOMER_ID,
                   c.CUSTOMER_NAME,
                   p.WARE_ID,
                   p.ROUTE_ID,
                   p.DOCK_ID,
                   p.STATUS,
                   p.PLAN_STRATEGY,
                   p.TOTAL_ORDER_QTY,
                   p.TOTAL_PLANNED_QTY,
                   p.TOTAL_SHORTAGE_QTY,
                   p.COMMENT_TEXT,
                   p.CREATED_AT,
                   p.CREATED_BY,
                   p.UPDATED_AT,
                   p.UPDATED_BY
              from RRL_PICK_PLAN p
              join RRL_CUSTOMER_ORDER co
                on co.CUSTOMER_ORDER_ID = p.CUSTOMER_ORDER_ID
              left join RRL_CUSTOMER c
                on c.CUSTOMER_ID = p.CUSTOMER_ID
             where p.PICK_PLAN_ID = :pick_plan_id
            """,
            {"pick_plan_id": pick_plan_id},
        )
        if not rows:
            return None

        plan = rows[0]
        plan["lines"] = self.gateway.fetch_all(
            """
            select PICK_PLAN_LINE_ID,
                   CUSTOMER_ORDER_ROW_ID,
                   ARTICUL,
                   PRODUCT_NAME,
                   REQUESTED_QTY,
                   PLANNED_QTY,
                   FULL_PALLET_QTY,
                   CASE_PICK_QTY,
                   SHORTAGE_QTY,
                   STATUS,
                   CREATED_AT,
                   UPDATED_AT
              from RRL_PICK_PLAN_LINE
             where PICK_PLAN_ID = :pick_plan_id
             order by PICK_PLAN_LINE_ID
            """,
            {"pick_plan_id": pick_plan_id},
        )
        plan["tasks"] = self.gateway.fetch_all(
            """
            select PICK_TASK_ID,
                   PICK_PLAN_LINE_ID,
                   TASK_TYPE,
                   STATUS,
                   ARTICUL,
                   PALLET_UID,
                   SSCC,
                   PROD_BATCH_ID,
                   SOURCE_CELL_CODE,
                   TARGET_CELL_CODE,
                   QTY,
                   PICK_SEQUENCE,
                   ASSIGNED_TO,
                   CREATED_AT,
                   STARTED_AT,
                   DONE_AT,
                   UPDATED_AT,
                   ERROR_TEXT
              from RRL_PICK_TASK
             where PICK_PLAN_ID = :pick_plan_id
             order by PICK_SEQUENCE nulls last, PICK_TASK_ID
            """,
            {"pick_plan_id": pick_plan_id},
        )
        plan["reservations"] = self.list_reservations(pick_plan_id=pick_plan_id, limit=500)
        plan["shortages"] = self.list_shortages(pick_plan_id=pick_plan_id, limit=500)
        plan["decisions"] = self.gateway.fetch_all(
            """
            select PICK_DECISION_ID,
                   PICK_PLAN_LINE_ID,
                   DECISION_TYPE,
                   MESSAGE_TEXT,
                   PAYLOAD_JSON,
                   CREATED_AT,
                   CREATED_BY
              from RRL_PICK_DECISION_LOG
             where PICK_PLAN_ID = :pick_plan_id
             order by PICK_DECISION_ID
            """,
            {"pick_plan_id": pick_plan_id},
        )
        return plan

    def list_reservations(
        self,
        pick_plan_id: int | None = None,
        status: str | None = None,
        customer_order_id: int | None = None,
        pallet_uid: str | None = None,
        articul: str | None = None,
        limit: int = 200,
    ) -> list[dict[str, Any]]:
        conditions: list[str] = []
        params: dict[str, Any] = {"limit": min(max(limit, 1), 1000)}
        if pick_plan_id is not None:
            conditions.append("r.PICK_PLAN_ID = :pick_plan_id")
            params["pick_plan_id"] = pick_plan_id
        if status:
            conditions.append("upper(r.RESERVATION_STATUS) = :status")
            params["status"] = status.upper()
        if customer_order_id is not None:
            conditions.append("r.CUSTOMER_ORDER_ID = :customer_order_id")
            params["customer_order_id"] = customer_order_id
        if pallet_uid:
            conditions.append("upper(r.PALLET_UID) = :pallet_uid")
            params["pallet_uid"] = pallet_uid.upper()
        if articul:
            conditions.append("upper(r.ARTICUL) = :articul")
            params["articul"] = articul.upper()
        where_sql = " where " + " and ".join(conditions) if conditions else ""
        return self.gateway.fetch_all(
            f"""
            select *
              from (
                select r.PICK_RESERVATION_ID,
                       r.PICK_PLAN_ID,
                       r.PICK_PLAN_LINE_ID,
                       r.PICK_TASK_ID,
                       r.CUSTOMER_ORDER_ID,
                       co.ORDER_NO,
                       r.CUSTOMER_ID,
                       c.CUSTOMER_NAME,
                       r.RESERVATION_LEVEL,
                       r.RESERVATION_STATUS,
                       r.RESERVATION_SCOPE,
                       r.PALLET_UID,
                       r.SSCC,
                       r.ARTICUL,
                       r.PROD_BATCH_ID,
                       r.SOURCE_CELL_CODE,
                       r.RESERVED_QTY,
                       r.CREATED_AT,
                       r.CREATED_BY,
                       r.RELEASED_AT,
                       r.CONSUMED_AT,
                       r.UPDATED_AT
                  from RRL_PICK_RESERVATION r
                  join RRL_CUSTOMER_ORDER co
                    on co.CUSTOMER_ORDER_ID = r.CUSTOMER_ORDER_ID
                  left join RRL_CUSTOMER c
                    on c.CUSTOMER_ID = r.CUSTOMER_ID
                  {where_sql}
                 order by r.PICK_RESERVATION_ID desc
              )
             where rownum <= :limit
            """,
            params,
        )

    def list_shortages(self, pick_plan_id: int | None = None, limit: int = 200) -> list[dict[str, Any]]:
        conditions: list[str] = []
        params: dict[str, Any] = {"limit": min(max(limit, 1), 1000)}
        if pick_plan_id is not None:
            conditions.append("s.PICK_PLAN_ID = :pick_plan_id")
            params["pick_plan_id"] = pick_plan_id
        where_sql = " where " + " and ".join(conditions) if conditions else ""
        return self.gateway.fetch_all(
            f"""
            select *
              from (
                select s.PICK_SHORTAGE_ID,
                       s.PICK_PLAN_ID,
                       s.PICK_PLAN_LINE_ID,
                       s.CUSTOMER_ORDER_ID,
                       co.ORDER_NO,
                       s.CUSTOMER_ORDER_ROW_ID,
                       s.CUSTOMER_ID,
                       c.CUSTOMER_NAME,
                       s.ARTICUL,
                       s.REQUESTED_QTY,
                       s.AVAILABLE_QTY,
                       s.RESERVED_BY_OTHER_QTY,
                       s.PLANNED_QTY,
                       s.SHORTAGE_QTY,
                       s.REASON_CODE,
                       s.REASON_TEXT,
                       s.CREATED_AT,
                       s.CREATED_BY
                  from RRL_PICK_SHORTAGE s
                  join RRL_CUSTOMER_ORDER co
                    on co.CUSTOMER_ORDER_ID = s.CUSTOMER_ORDER_ID
                  left join RRL_CUSTOMER c
                    on c.CUSTOMER_ID = s.CUSTOMER_ID
                  {where_sql}
                 order by s.PICK_SHORTAGE_ID desc
              )
             where rownum <= :limit
            """,
            params,
        )
