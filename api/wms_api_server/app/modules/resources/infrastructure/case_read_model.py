"""Original CASE read model extracted; scoped API uses one current Oracle snapshot."""
from typing import Any

CASE_TASK_LIST_SQL = """
            with selected_tasks as (
              select CASE_PICK_TASK_ID,PICK_WAVE_ID from (
                select t.CASE_PICK_TASK_ID,t.PICK_WAVE_ID
                  from RRL_CASE_PICK_TASK t
                  join RRL_PICK_WAVE w on w.PICK_WAVE_ID=t.PICK_WAVE_ID
                  join RRL_CUSTOMER_ORDER co on co.CUSTOMER_ORDER_ID=t.CUSTOMER_ORDER_ID
                 where {where_sql}
                 order by t.STATUS,t.CREATED_AT,t.CASE_PICK_TASK_ID
              )where rownum<=:limit
            ),task_route as (
              select l.CASE_PICK_TASK_ID,
                     min(pr.ROUTE_CODE) keep (dense_rank first order by nvl(l.PICK_SEQUENCE, 999999), l.CASE_PICK_LINE_ID) ROUTE_CODE,
                     min(pr.ROUTE_NAME) keep (dense_rank first order by nvl(l.PICK_SEQUENCE, 999999), l.CASE_PICK_LINE_ID) ROUTE_NAME,
                     min(rc.ZONE_CODE) keep (dense_rank first order by nvl(l.PICK_SEQUENCE, 999999), l.CASE_PICK_LINE_ID) ZONE_CODE
                from RRL_CASE_PICK_LINE l
                left join RRL_PICK_ROUTE_CELL rc on rc.PICK_ROUTE_CELL_ID = l.PICK_ROUTE_CELL_ID
                left join RRL_PICK_ROUTE pr on pr.PICK_ROUTE_ID = rc.PICK_ROUTE_ID
               where l.CASE_PICK_TASK_ID in(select CASE_PICK_TASK_ID from selected_tasks)
               group by l.CASE_PICK_TASK_ID
            ),
            task_short as (
              select CASE_PICK_TASK_ID,
                     min(CASE_PICK_SHORT_ID) keep (dense_rank first order by CREATED_AT desc, CASE_PICK_SHORT_ID desc) BLOCKING_SHORT_ID,
                     min(REASON_TEXT) keep (dense_rank first order by CREATED_AT desc, CASE_PICK_SHORT_ID desc) BLOCKING_REASON,
                     min(CELL_CODE) keep (dense_rank first order by CREATED_AT desc, CASE_PICK_SHORT_ID desc) BLOCKING_CELL_CODE,
                     min(CREATED_BY) keep (dense_rank first order by CREATED_AT desc, CASE_PICK_SHORT_ID desc) BLOCKING_CREATED_BY
                from RRL_CASE_PICK_SHORT
               where STATUS in ('CREATED', 'PENDING_APPROVAL')
                 and CASE_PICK_TASK_ID in(select CASE_PICK_TASK_ID from selected_tasks)
               group by CASE_PICK_TASK_ID
            ),
            task_event as (
              select CASE_PICK_TASK_ID,
                     min(EVENT_TYPE) keep (dense_rank last order by CREATED_AT, CASE_PICK_EVENT_ID) LAST_EVENT_TYPE,
                     min(MESSAGE_TEXT) keep (dense_rank last order by CREATED_AT, CASE_PICK_EVENT_ID) LAST_EVENT_TEXT,
                     max(CREATED_AT) LAST_EVENT_AT
                from RRL_CASE_PICK_EVENT
               where CASE_PICK_TASK_ID in(select CASE_PICK_TASK_ID from selected_tasks)
               group by CASE_PICK_TASK_ID
            ),
            wave_totals as (
              select PICK_WAVE_ID,
                     count(*) ROUTE_PALLET_COUNT,
                     sum(case when STATUS in ('WAIT_CONTROL', 'CONTROL_IN_PROGRESS', 'CONTROLLED', 'READY_TO_SHIP') then 1 else 0 end) ROUTE_DONE_PALLET_COUNT,
                     sum(case when STATUS in ('ASSIGNED', 'IN_PROGRESS', 'PARTIAL', 'WAIT_REPLENISHMENT', 'PICKED') then 1 else 0 end) ROUTE_ACTIVE_PALLET_COUNT,
                     nvl(sum(PLANNED_QTY), 0) ROUTE_PLANNED_QTY,
                     nvl(sum(PICKED_QTY), 0) ROUTE_PICKED_QTY
                from RRL_CASE_PICK_TASK tot
               where STATUS not in ('CANCELLED', 'FAILED')
                 and {totals_scope_sql}
                 and PICK_WAVE_ID in(select PICK_WAVE_ID from selected_tasks)
               group by PICK_WAVE_ID
            )
            select *
              from (
                select t.CASE_PICK_TASK_ID,
                       t.PICK_WAVE_ID,
                       w.WAVE_CODE,
                       nvl(tr.ROUTE_NAME, tr.ROUTE_CODE) ROUTE,
                       tr.ROUTE_CODE,
                       tr.ROUTE_NAME,
                       t.CUSTOMER_ORDER_ID,
                       co.ORDER_NO,
                       t.CUSTOMER_ID,
                       c.CUSTOMER_NAME,
                       t.SSCC,
                       pt.PALLET_TYPE_CODE,
                       pt.PALLET_TYPE_NAME,
                       pt.DEFAULT_MAX_CLIENT_PALLETS TROLLEY_PALLET_CAPACITY,
                       t.STATUS,
                       t.ASSIGNED_RESOURCE_ID,
                       t.RESOURCE_SESSION_ID,
                       t.EQUIPMENT_ID,
                       nvl(t.ASSIGNED_TO, nvl(r.RESOURCE_NAME, rs.OPERATOR_USER_ID)) ASSIGNED_TO,
                       r.RESOURCE_CODE,
                       r.RESOURCE_NAME,
                       nvl(e_task.EQUIPMENT_CODE, e_res.EQUIPMENT_CODE) EQUIPMENT_CODE,
                       nvl(e_task.CAPACITY_CLASS, e_res.CAPACITY_CLASS) EQUIPMENT_CAPACITY_CLASS,
                       t.WARE_ID,
                       tr.ZONE_CODE,
                       t.TOTAL_LINES,
                       t.PICKED_LINES,
                       to_char(t.PLANNED_QTY,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') PLANNED_QTY,
                       to_char(t.PICKED_QTY,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') PICKED_QTY,
                       round((t.PICKED_QTY / nullif(t.PLANNED_QTY, 0)) * 100) TASK_PROGRESS_PCT,
                       wt.ROUTE_PALLET_COUNT,
                       wt.ROUTE_DONE_PALLET_COUNT,
                       wt.ROUTE_ACTIVE_PALLET_COUNT,
                       wt.ROUTE_PLANNED_QTY,
                       wt.ROUTE_PICKED_QTY,
                       round((wt.ROUTE_PICKED_QTY / nullif(wt.ROUTE_PLANNED_QTY, 0)) * 100) ROUTE_PROGRESS_PCT,
                       ts.BLOCKING_SHORT_ID,
                       ts.BLOCKING_REASON,
                       ts.BLOCKING_CELL_CODE,
                       case
                         when ts.BLOCKING_SHORT_ID is not null then ts.BLOCKING_REASON || case when ts.BLOCKING_CELL_CODE is not null then chr(10) || 'CELL ' || ts.BLOCKING_CELL_CODE end
                         when t.STATUS = 'WAIT_REPLENISHMENT' then 'WAIT_REPLENISHMENT'
                         when t.STATUS = 'SYNC_CONFLICT' then 'SYNC_CONFLICT'
                         else null
                       end PROBLEM,
                       case
                         when te.LAST_EVENT_TYPE is not null then te.LAST_EVENT_TYPE || case when te.LAST_EVENT_TEXT is not null then chr(10) || te.LAST_EVENT_TEXT end
                         when t.CLOSED_AT is not null then 'PALLET_CLOSED'
                         when t.STARTED_AT is not null then 'PICKING_IN_PROGRESS'
                         when t.ASSIGNED_TO is not null then 'TASK_ASSIGNED'
                         else 'TASK_RECEIVED'
                       end LAST_ACTION,
                       te.LAST_EVENT_AT,
                       t.CREATED_AT,
                       t.STARTED_AT,
                   to_char(t.STARTED_AT_INSTANT,'YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM') STARTED_AT_INSTANT,
                   t.STARTED_SHIFT_TIME_ZONE,
                       t.CLOSED_AT
                  from RRL_CASE_PICK_TASK t
                  join selected_tasks st on st.CASE_PICK_TASK_ID=t.CASE_PICK_TASK_ID
                  join RRL_PICK_WAVE w on w.PICK_WAVE_ID = t.PICK_WAVE_ID
                  join RRL_CUSTOMER_ORDER co on co.CUSTOMER_ORDER_ID = t.CUSTOMER_ORDER_ID
                  left join RRL_CUSTOMER c on c.CUSTOMER_ID = t.CUSTOMER_ID
                  left join RRL_PALLET_TYPE pt on pt.PALLET_TYPE_ID = t.PALLET_TYPE_ID
                  left join RRL_RESOURCE r on r.RESOURCE_ID = t.ASSIGNED_RESOURCE_ID
                  left join RRL_RESOURCE_SESSION rs on rs.SESSION_ID = t.RESOURCE_SESSION_ID
                  left join RRL_RESOURCE_EQUIPMENT e_task on e_task.EQUIPMENT_ID = t.EQUIPMENT_ID
                  left join RRL_RESOURCE_EQUIPMENT e_res on e_res.EQUIPMENT_ID = r.EQUIPMENT_ID
                  left join task_route tr on tr.CASE_PICK_TASK_ID = t.CASE_PICK_TASK_ID
                  left join task_short ts on ts.CASE_PICK_TASK_ID = t.CASE_PICK_TASK_ID
                  left join task_event te on te.CASE_PICK_TASK_ID = t.CASE_PICK_TASK_ID
                  left join wave_totals wt on wt.PICK_WAVE_ID = t.PICK_WAVE_ID
                 where {where_sql}
                 order by t.STATUS, t.CREATED_AT, t.CASE_PICK_TASK_ID
              )
             where rownum <= :limit
            """

class LegacyCaseReads:
    def __init__(self, gateway: Any) -> None:
        self.gateway = gateway

    def list_tasks(
        self,
        resource_id: int | None = None,
        scope: str = "mine",
        status: str | None = None,
        limit: int = 100,
        warehouse_id: int | None = None,
        view_actor: str | None = None,
    ) -> list[dict[str, Any]]:
        conditions = ["1 = 1"]
        params: dict[str, Any] = {"limit": min(max(limit, 1), 500)}
        totals_scope_sql = "1=1"
        if view_actor is not None:
            from .case_view_scope import view_predicate
            conditions.append(view_predicate("t"))
            totals_scope_sql = view_predicate("tot")
            params["view_actor"] = view_actor
        if warehouse_id is not None:
            conditions.append("t.WARE_ID = :ware")
            params["ware"] = warehouse_id
        if status:
            conditions.append("t.STATUS = :status")
            params["status"] = status.upper()
        else:
            conditions.append("t.STATUS not in ('READY_TO_SHIP', 'CANCELLED')")
        if scope == "self":
            if view_actor is None:
                raise ValueError("Authenticated CASE viewer required for self queue")
            conditions.append("upper(trim(t.ASSIGNED_TO))=upper(trim(:view_actor))")
        elif scope == "mine":
            if resource_id is not None:
                conditions.append("(t.ASSIGNED_RESOURCE_ID = :resource_id or t.ASSIGNED_RESOURCE_ID is null)")
                params["resource_id"] = resource_id
            else:
                conditions.append("t.ASSIGNED_RESOURCE_ID is null")
        elif scope == "free":
            conditions.append("t.ASSIGNED_RESOURCE_ID is null")
        where_sql = " and ".join(conditions)
        return self.gateway.fetch_all(
            CASE_TASK_LIST_SQL.format(where_sql=where_sql, totals_scope_sql=totals_scope_sql),
            params,
        )


    def get_task(self, case_pick_task_id: int) -> dict[str, Any] | None:
        rows = self.gateway.fetch_all(
            """
            select t.CASE_PICK_TASK_ID,
                   t.PICK_WAVE_ID,
                   w.WAVE_CODE,
                   w.PICK_RELEASED_AT WAVE_PICK_RELEASED_AT,
                   w.PICK_RELEASED_BY WAVE_PICK_RELEASED_BY,
                   t.PICK_PLAN_ID,
                   t.CUSTOMER_ORDER_ID,
                   co.ORDER_NO,
                   t.CUSTOMER_ID,
                   c.CUSTOMER_NAME,
                   t.SSCC,
                   pt.PALLET_TYPE_CODE,
                   pt.PALLET_TYPE_NAME,
                   t.STATUS,
                   t.ASSIGNED_RESOURCE_ID,
                   t.RESOURCE_SESSION_ID,
                   t.EQUIPMENT_ID,
                   t.ASSIGNED_TO,
                   t.WARE_ID,
                   t.TOTAL_LINES,
                   t.PICKED_LINES,
                   to_char(t.PLANNED_QTY,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') PLANNED_QTY,
                   to_char(t.PICKED_QTY,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') PICKED_QTY,
                   t.CURRENT_CELL,t.CONTENT_VERSION,t.ASSIGNMENT_VERSION,t.LEGACY_SBORKA_PALLET_ID,t.SHIPPED_OPERATION,
                   t.CREATED_AT,
                   t.STARTED_AT,
                   to_char(t.STARTED_AT_INSTANT,'YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM') STARTED_AT_INSTANT,
                   t.STARTED_SHIFT_TIME_ZONE,
                   t.CLOSED_AT
              from RRL_CASE_PICK_TASK t
              join RRL_PICK_WAVE w on w.PICK_WAVE_ID = t.PICK_WAVE_ID
              join RRL_CUSTOMER_ORDER co on co.CUSTOMER_ORDER_ID = t.CUSTOMER_ORDER_ID
              left join RRL_CUSTOMER c on c.CUSTOMER_ID = t.CUSTOMER_ID
              left join RRL_PALLET_TYPE pt on pt.PALLET_TYPE_ID = t.PALLET_TYPE_ID
             where t.CASE_PICK_TASK_ID = :case_pick_task_id
            """,
            {"case_pick_task_id": case_pick_task_id},
        )
        if not rows:
            return None
        task = rows[0]
        task["lines"] = self.gateway.fetch_all(
            """
            select CASE_PICK_LINE_ID,
                   PICK_WAVE_TASK_ID,
                   PICK_TASK_ID,
                   ARTICUL,
                   PRODUCT_NAME,
                   CELL_CODE,
                   PICK_SEQUENCE, STACK_STAGE, STACK_POLICY_VERSION,
                   to_char(PLANNED_QTY,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') PLANNED_QTY,
                   to_char(PICKED_QTY,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') PICKED_QTY,
                   STATUS,
                   LAST_OFFLINE_EVENT_ID,
                   STARTED_AT,
                   DONE_AT
              from RRL_CASE_PICK_LINE
             where CASE_PICK_TASK_ID = :case_pick_task_id
             order by PICK_SEQUENCE nulls last, CASE_PICK_LINE_ID
            """,
            {"case_pick_task_id": case_pick_task_id},
        )
        task["physical_lots"] = self.gateway.fetch_all(
            "select h.LOT_UID LOT_UID,h.CASE_PICK_LINE_ID,p.ARTICUL,s.CELL,s.BASE_UOM,"
            "to_char(s.REMAIN,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') PHYSICAL_QTY,"
            "to_char(s.HARD_RESERVED_BASE,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') HARD_QTY "
            "from RRL_CASE_CARRIER_LOT h join RRL_REMAINS s on s.UID_POLETA=h.LOT_UID "
            "join RRL_PALLETS p on p.UID_PALLET=h.LOT_UID "
            "where h.CASE_PICK_TASK_ID=:id and s.REMAIN>0 order by h.LOT_UID,s.CELL fetch first 201 rows only",
            {"id": case_pick_task_id})
        for lot in task["physical_lots"]: lot["uid"]=lot.pop("lot_uid")
        from ...inventory.public import existing_case_tare_snapshot
        task['tare']=existing_case_tare_snapshot(self.gateway,case_pick_task_id)
        return task


    def list_shorts(self, status: str | None = None, limit: int = 200, warehouse_id: int | None = None,
                    view_actor: str | None = None) -> list[dict[str, Any]]:
        conditions = []
        if warehouse_id is not None:
            conditions.append("exists(select 1 from RRL_CASE_PICK_TASK ct where ct.CASE_PICK_TASK_ID=s.CASE_PICK_TASK_ID and ct.WARE_ID=:ware)")
        params: dict[str, Any] = {"limit": min(max(limit, 1), 500)}
        if view_actor is not None:
            from .case_view_scope import view_predicate
            conditions.append("exists(select 1 from RRL_CASE_PICK_TASK ct where ct.CASE_PICK_TASK_ID=s.CASE_PICK_TASK_ID and " + view_predicate("ct") + ")")
            params["view_actor"] = view_actor
        if warehouse_id is not None:
            params["ware"] = warehouse_id
        if status:
            conditions.append("s.STATUS = :status")
            params["status"] = status.upper()
        where_sql = " where " + " and ".join(conditions) if conditions else ""
        return self.gateway.fetch_all(
            f"""
            select *
              from (
                select s.CASE_PICK_SHORT_ID,
                       s.PICK_WAVE_ID,
                       s.CASE_PICK_TASK_ID,
                       s.CASE_PICK_LINE_ID,
                       s.CUSTOMER_ORDER_ID,
                       co.ORDER_NO,
                       s.CUSTOMER_ID,
                       c.CUSTOMER_NAME,
                       s.ARTICUL,
                       s.CELL_CODE,
                       s.PLANNED_QTY,
                       s.PICKED_QTY,
                       s.SHORT_QTY,
                       s.REASON_CODE,
                       s.REASON_TEXT,
                       s.STATUS,
                       s.INVENTORY_TASK_ID,
                       s.CREATED_AT,
                       s.CREATED_BY,
                       s.APPROVED_AT,
                       s.APPROVED_BY
                  from RRL_CASE_PICK_SHORT s
                  left join RRL_CUSTOMER_ORDER co on co.CUSTOMER_ORDER_ID = s.CUSTOMER_ORDER_ID
                  left join RRL_CUSTOMER c on c.CUSTOMER_ID = s.CUSTOMER_ID
                  {where_sql}
                 order by s.CREATED_AT desc, s.CASE_PICK_SHORT_ID desc
              )
             where rownum <= :limit
            """,
            params,
        )
