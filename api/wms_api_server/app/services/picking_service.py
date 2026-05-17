from typing import Any

from ..oracle_gateway import OracleGateway
from ..schemas import (
    PickFaceArticulUpsertRequest,
    PickFaceUpsertRequest,
    PickRouteCellUpsertRequest,
    PickRouteUpsertRequest,
    PickingPlanCreateRequest,
)


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
                   PICK_FACE_ID,
                   PICK_ROUTE_CELL_ID,
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

    def list_routes(self, ware_id: int | None = None, active_only: int | None = None) -> list[dict[str, Any]]:
        conditions: list[str] = []
        params: dict[str, Any] = {}
        if ware_id is not None:
            conditions.append("r.WARE_ID = :ware_id")
            params["ware_id"] = ware_id
        if active_only is not None and int(active_only) == 1:
            conditions.append("r.ACTIVE = 1")
        where_sql = " where " + " and ".join(conditions) if conditions else ""
        return self.gateway.fetch_all(
            f"""
            select r.PICK_ROUTE_ID,
                   r.WARE_ID,
                   w.NAME WARE_NAME,
                   r.ROUTE_CODE,
                   r.ROUTE_NAME,
                   r.ROUTE_KIND,
                   r.ACTIVE,
                   count(distinct rc.PICK_ROUTE_CELL_ID) CELL_COUNT,
                   count(distinct pf.PICK_FACE_ID) PICK_FACE_COUNT,
                   r.CREATED_AT,
                   r.UPDATED_AT
              from RRL_PICK_ROUTE r
              left join RRL_WARES w
                on w.ID = r.WARE_ID
              left join RRL_PICK_ROUTE_CELL rc
                on rc.PICK_ROUTE_ID = r.PICK_ROUTE_ID
              left join RRL_PICK_FACE pf
                on pf.PICK_ROUTE_ID = r.PICK_ROUTE_ID
              {where_sql}
             group by r.PICK_ROUTE_ID,
                      r.WARE_ID,
                      w.NAME,
                      r.ROUTE_CODE,
                      r.ROUTE_NAME,
                      r.ROUTE_KIND,
                      r.ACTIVE,
                      r.CREATED_AT,
                      r.UPDATED_AT
             order by r.WARE_ID, r.ROUTE_CODE
            """,
            params,
        )

    def upsert_route(self, request: PickRouteUpsertRequest) -> int:
        return self.gateway.call_number_plsql(
            """
            begin
              :result := RRL_PICK_TOPOLOGY_API.upsert_route(
                p_pick_route_id => :pick_route_id,
                p_route_code => :route_code,
                p_route_name => :route_name,
                p_ware_id => :ware_id,
                p_route_kind => :route_kind,
                p_active => :active,
                p_updated_by => :updated_by
              );
            end;
            """,
            request.model_dump(),
        )

    def list_route_cells(
        self,
        pick_route_id: int | None = None,
        ware_id: int | None = None,
        active_only: int | None = None,
    ) -> list[dict[str, Any]]:
        conditions: list[str] = []
        params: dict[str, Any] = {}
        if pick_route_id is not None:
            conditions.append("rc.PICK_ROUTE_ID = :pick_route_id")
            params["pick_route_id"] = pick_route_id
        if ware_id is not None:
            conditions.append("rc.WARE_ID = :ware_id")
            params["ware_id"] = ware_id
        if active_only is not None and int(active_only) == 1:
            conditions.append("rc.ACTIVE = 1")
        where_sql = " where " + " and ".join(conditions) if conditions else ""
        return self.gateway.fetch_all(
            f"""
            select rc.PICK_ROUTE_CELL_ID,
                   rc.PICK_ROUTE_ID,
                   r.ROUTE_CODE,
                   rc.WARE_ID,
                   w.NAME WARE_NAME,
                   rc.CELL_CODE,
                   rc.PICK_SEQUENCE,
                   rc.ZONE_CODE,
                   rc.AISLE_CODE,
                   rc.SIDE_CODE,
                   rc.LEVEL_NO,
                   rc.ACTIVE,
                   rc.CREATED_AT,
                   rc.UPDATED_AT
              from RRL_PICK_ROUTE_CELL rc
              join RRL_PICK_ROUTE r
                on r.PICK_ROUTE_ID = rc.PICK_ROUTE_ID
              left join RRL_WARES w
                on w.ID = rc.WARE_ID
              {where_sql}
             order by rc.WARE_ID, r.ROUTE_CODE, rc.PICK_SEQUENCE, rc.CELL_CODE
            """,
            params,
        )

    def upsert_route_cell(self, request: PickRouteCellUpsertRequest) -> int:
        return self.gateway.call_number_plsql(
            """
            begin
              :result := RRL_PICK_TOPOLOGY_API.upsert_route_cell(
                p_pick_route_cell_id => :pick_route_cell_id,
                p_pick_route_id => :pick_route_id,
                p_cell_code => :cell_code,
                p_pick_sequence => :pick_sequence,
                p_zone_code => :zone_code,
                p_aisle_code => :aisle_code,
                p_side_code => :side_code,
                p_level_no => :level_no,
                p_active => :active,
                p_updated_by => :updated_by
              );
            end;
            """,
            request.model_dump(),
        )

    def list_pick_faces(
        self,
        ware_id: int | None = None,
        articul: str | None = None,
        active_only: int | None = None,
    ) -> list[dict[str, Any]]:
        conditions: list[str] = []
        params: dict[str, Any] = {}
        if ware_id is not None:
            conditions.append("pf.WARE_ID = :ware_id")
            params["ware_id"] = ware_id
        if active_only is not None and int(active_only) == 1:
            conditions.append("pf.ACTIVE = 1")
        if articul:
            conditions.append(
                "exists (select 1 from RRL_PICK_FACE_ARTICUL pfa "
                "where pfa.PICK_FACE_ID = pf.PICK_FACE_ID "
                "and upper(pfa.ARTICUL) = :articul and pfa.ACTIVE = 1)"
            )
            params["articul"] = articul.upper()
        where_sql = " where " + " and ".join(conditions) if conditions else ""
        return self.gateway.fetch_all(
            f"""
            select pf.PICK_FACE_ID,
                   pf.WARE_ID,
                   w.NAME WARE_NAME,
                   pf.CELL_CODE,
                   pf.PICK_FACE_CODE,
                   pf.PICK_FACE_TYPE,
                   pf.PICK_ROUTE_ID,
                   r.ROUTE_CODE,
                   pf.PICK_ROUTE_CELL_ID,
                   pf.PICK_SEQUENCE,
                   pf.MIN_CASE_QTY,
                   pf.MAX_CASE_QTY,
                   pf.REPLENISHMENT_TRIGGER_QTY,
                   pf.MAX_WEIGHT,
                   pf.MAX_VOLUME,
                   pf.ALLOW_DYNAMIC_ASSIGNMENT,
                   pf.ACTIVE,
                   (select count(*)
                      from RRL_PICK_FACE_ARTICUL pfa
                     where pfa.PICK_FACE_ID = pf.PICK_FACE_ID
                       and pfa.ACTIVE = 1) ARTICUL_COUNT,
                   pf.CREATED_AT,
                   pf.UPDATED_AT
              from RRL_PICK_FACE pf
              left join RRL_WARES w
                on w.ID = pf.WARE_ID
              left join RRL_PICK_ROUTE r
                on r.PICK_ROUTE_ID = pf.PICK_ROUTE_ID
              {where_sql}
             order by pf.WARE_ID, pf.PICK_SEQUENCE nulls last, pf.CELL_CODE, pf.PICK_FACE_ID
            """,
            params,
        )

    def upsert_pick_face(self, request: PickFaceUpsertRequest) -> int:
        return self.gateway.call_number_plsql(
            """
            begin
              :result := RRL_PICK_TOPOLOGY_API.upsert_pick_face(
                p_pick_face_id => :pick_face_id,
                p_ware_id => :ware_id,
                p_cell_code => :cell_code,
                p_pick_face_code => :pick_face_code,
                p_pick_face_type => :pick_face_type,
                p_pick_route_id => :pick_route_id,
                p_pick_route_cell_id => :pick_route_cell_id,
                p_pick_sequence => :pick_sequence,
                p_min_case_qty => :min_case_qty,
                p_max_case_qty => :max_case_qty,
                p_replenishment_trigger_qty => :replenishment_trigger_qty,
                p_max_weight => :max_weight,
                p_max_volume => :max_volume,
                p_allow_dynamic_assignment => :allow_dynamic_assignment,
                p_active => :active,
                p_comment_text => :comment_text,
                p_updated_by => :updated_by
              );
            end;
            """,
            request.model_dump(),
        )

    def list_pick_face_articuls(self, pick_face_id: int) -> list[dict[str, Any]]:
        return self.gateway.fetch_all(
            """
            select PICK_FACE_ARTICUL_ID,
                   PICK_FACE_ID,
                   ARTICUL,
                   PRIORITY,
                   MIN_QTY,
                   MAX_QTY,
                   CASE_PICK_ENABLED,
                   ACTIVE,
                   VALID_FROM,
                   VALID_TO,
                   CREATED_AT,
                   UPDATED_AT
              from RRL_PICK_FACE_ARTICUL
             where PICK_FACE_ID = :pick_face_id
             order by PRIORITY, ARTICUL, PICK_FACE_ARTICUL_ID
            """,
            {"pick_face_id": pick_face_id},
        )

    def assign_pick_face_articul(self, request: PickFaceArticulUpsertRequest) -> int:
        return self.gateway.call_number_plsql(
            """
            begin
              :result := RRL_PICK_TOPOLOGY_API.assign_articul(
                p_pick_face_articul_id => :pick_face_articul_id,
                p_pick_face_id => :pick_face_id,
                p_articul => :articul,
                p_priority => :priority,
                p_min_qty => :min_qty,
                p_max_qty => :max_qty,
                p_case_pick_enabled => :case_pick_enabled,
                p_active => :active,
                p_valid_from => :valid_from,
                p_valid_to => :valid_to,
                p_updated_by => :updated_by
              );
            end;
            """,
            request.model_dump(),
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
