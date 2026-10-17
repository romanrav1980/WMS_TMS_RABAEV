"""Original bounded task queue; immutable deferral binding identifies HU waiting tasks."""
from __future__ import annotations
from typing import Any
from fastapi import HTTPException

_LIST_SQL = """
            select *
              from (
                select TASK_ID, TASK_TYPE, TASK_SOURCE, SOURCE_TASK_ID,
                       SOURCE_MOVEMENT_ID, SOURCE_DOC_TYPE, SOURCE_DOC_ID,
                       PRODUCTION_ORDER_ID, PROD_BATCH_ID, RAW_ARTICUL,
                       TARGET_ARTICUL, UID_PALLET, SSCC, FROM_WARE_ID,
                       FROM_CELL, TO_WARE_ID, TO_CELL, QTY, UNIT_CODE,
                       QTY_MODE, FACT_QTY, PARENT_TASK_ID,
                       to_char(QTY,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') QTY_EXACT,
                       to_char(FACT_QTY,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') FACT_QTY_EXACT,
                       TO_CELL_SLOT_ID, HU_CONTENT_VERSION,
                       (select sl.SLOT_CODE from RRL_TOPOLOGY_CELL_SLOT sl where sl.CELL_SLOT_ID=RRL_WAREHOUSE_TASK.TO_CELL_SLOT_ID) TO_SLOT_CODE,
                       PRIORITY, STATUS, ASSIGNED_TO, RESOURCE_ID,
                       RESOURCE_SESSION_ID, EQUIPMENT_ID,
                       PLANNED_START_AT, PLANNED_FINISH_AT, DISPATCH_PRIORITY,
                       WAIT_PLAN_OPERATION_ID,WAIT_DECISION_OPERATION_ID,WAIT_ST_NUMBER,WAIT_TARGET_TT_ID,
                       CREATED_AT,
                       CREATED_BY, STARTED_AT, FINISHED_AT, CANCELLED_AT,
                       CANCELLED_BY, LAST_ERROR
                  from (select wt.*,wp.PLAN_OPERATION_ID WAIT_PLAN_OPERATION_ID,wr.DECISION_OPERATION_ID WAIT_DECISION_OPERATION_ID,
                         wd.ST_NUMBER WAIT_ST_NUMBER,wd.TARGET_TT_ID WAIT_TARGET_TT_ID
                    from RRL_WAREHOUSE_TASK wt left join RRL_ST_DEFER_WAIT_PLAN wp on wp.TASK_ID=wt.TASK_ID
                    left join RRL_ST_DEFER_WAIT_RUN wr on wr.OPERATION_ID=wp.PLAN_OPERATION_ID
                    left join RRL_ST_DEFER_DECISION wd on wd.OPERATION_ID=wr.DECISION_OPERATION_ID) RRL_WAREHOUSE_TASK
                  {where_sql}
                 order by case STATUS
                            when 'PLANNED' then 1
                            when 'ASSIGNED' then 2
                            when 'IN_PROGRESS' then 3
                            when 'ERROR' then 4
                            else 9
                          end,
                          PRIORITY,
                          WAIT_PLAN_OPERATION_ID,WAIT_DECISION_OPERATION_ID,WAIT_ST_NUMBER,WAIT_TARGET_TT_ID,
                       CREATED_AT,
                          TASK_ID
              )
             where rownum <= :limit
            """

class TaskQueueRead:
    def __init__(self,gateway: Any) -> None:
        self.gateway=gateway

    def list(
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
        view_actor: str | None = None,
    ) -> list[dict[str, Any]]:
        conditions: list[str] = []
        params: dict[str, Any] = {"limit": min(max(limit,1),500)}
        if view_actor is not None:
            from .task_view_predicate import task_view_predicate
            conditions.append("(" + task_view_predicate() + ")")
            params["view_actor"] = view_actor
        if not scope_global:
            conditions.append("(FROM_WARE_ID=:scope_ware or TO_WARE_ID=:scope_ware)")
            params["scope_ware"]=scope_warehouse_id
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
        if queue_group:
            if queue_group == "SHIPPING":
                conditions.append("(TASK_TYPE='PICKING_MOVE' or (TASK_TYPE='REPLENISHMENT' and SOURCE_DOC_TYPE='SHIPMENT'))")
            elif queue_group == "DEFER_WAITING":
                conditions.append("(TASK_TYPE='PUTAWAY' and TASK_SOURCE='MANUAL' and (SOURCE_DOC_TYPE in('ST_DEFER','ST_DEFER_CASE') or WAIT_PLAN_OPERATION_ID is not null))")
            else:
                raise HTTPException(422, detail="Unknown warehouse task queue group")
        where_sql = " where " + " and ".join(conditions) if conditions else ""
        return self.gateway.fetch_all(_LIST_SQL.format(where_sql=where_sql),params)

    def get(self, task_id: int) -> dict[str, Any] | None:
        rows = self.gateway.fetch_all(
            """
            select t.*,wp.PLAN_OPERATION_ID WAIT_PLAN_OPERATION_ID,wr.DECISION_OPERATION_ID WAIT_DECISION_OPERATION_ID,
                   wd.ST_NUMBER WAIT_ST_NUMBER,wd.TARGET_TT_ID WAIT_TARGET_TT_ID,
                   to_char(t.QTY,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') QTY_EXACT,
                   to_char(t.FACT_QTY,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') FACT_QTY_EXACT
              from RRL_WAREHOUSE_TASK t left join RRL_ST_DEFER_WAIT_PLAN wp on wp.TASK_ID=t.TASK_ID
              left join RRL_ST_DEFER_WAIT_RUN wr on wr.OPERATION_ID=wp.PLAN_OPERATION_ID
              left join RRL_ST_DEFER_DECISION wd on wd.OPERATION_ID=wr.DECISION_OPERATION_ID
             where t.TASK_ID = :task_id
            """,
            {"task_id": task_id},
        )
        return rows[0] if rows else None
