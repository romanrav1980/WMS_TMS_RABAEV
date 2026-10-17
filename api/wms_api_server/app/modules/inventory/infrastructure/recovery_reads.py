"""Inventory-owned queues scoped by the current native warehouse authority."""
from typing import Any
from fastapi import HTTPException
from ....db import rows_as_dicts as queue_rows

INVENTORY_PROJECTION = """select it.INVENTORY_TASK_ID,it.STATUS,it.WARE_ID WAREHOUSE_ID,it.CELL_CODE CELL,
    it.ARTICUL ARTICLE,it.ASSIGNED_TO,it.PRIORITY,it.REVISION_ID,it.COUNT_OPERATION_ID,
    sh.CASE_PICK_SHORT_ID SHORT_ID,sh.RECOVERY_STATE,sh.RECOVERY_DEADLINE_AT,
    to_char(it.FACT_QTY,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') FACT_QUANTITY
    from RRL_INVENTORY_TASK it left join RRL_CASE_PICK_SHORT sh on sh.CASE_PICK_SHORT_ID=it.SOURCE_DOC_ID
    and it.SOURCE_DOC_TYPE='CASE_PICK_SHORT'"""

RECOVERY_PROJECTION = """select sh.CASE_PICK_SHORT_ID SHORT_ID,sh.CASE_PICK_TASK_ID,sh.CASE_PICK_LINE_ID,
    sh.PICK_WAVE_ID,w.WARE_ID WAREHOUSE_ID,sh.CELL_CODE CELL,sh.ARTICUL ARTICLE,sh.CREATED_BY PICKER,
    sh.STATUS,sh.RECOVERY_STATE,sh.INVENTORY_TASK_ID,sh.REPLENISH_TASK_ID,
    sh.RECOVERY_LAST_ERROR,sh.RECOVERY_DEADLINE_AT,sh.RESTORED_AT,
    to_char(sh.SHORT_QTY,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') SHORT_QUANTITY,
    greatest(0,round((cast(systimestamp as date)-cast(sh.CREATED_AT as date))*86400)) AGE_SECONDS,
    round((cast(nvl(sh.RECOVERY_DEADLINE_AT,sh.CREATED_AT+numtodsinterval(300,'SECOND')) as date)
      -cast(systimestamp as date))*86400) REMAINING_SECONDS,
    to_char(greatest(0,l.PICKED_QTY-sh.PICKED_QTY),'TM9','NLS_NUMERIC_CHARACTERS=''.,''') RESTORED_QUANTITY,
    to_char(greatest(0,l.PLANNED_QTY-l.PICKED_QTY),'TM9','NLS_NUMERIC_CHARACTERS=''.,''') ORDER_REMAINING_QUANTITY,
    it.STATUS INVENTORY_STATUS,it.ASSIGNED_TO AUDITOR,it.COUNT_OPERATION_ID,
    rt.STATUS REPLENISH_STATUS,rt.WAIT_REASON,
    (select min(wt.TASK_ID) from RRL_WAREHOUSE_TASK wt
     where wt.TASK_SOURCE='WAVE' and wt.TASK_TYPE='REPLENISHMENT'
      and wt.SOURCE_TASK_ID=sh.REPLENISH_TASK_ID and wt.STATUS not in('DONE','CANCELLED')) WAREHOUSE_TASK_ID
    from RRL_CASE_PICK_SHORT sh join RRL_CASE_PICK_LINE l on l.CASE_PICK_LINE_ID=sh.CASE_PICK_LINE_ID
    join RRL_PICK_WAVE w on w.PICK_WAVE_ID=sh.PICK_WAVE_ID
    left join RRL_INVENTORY_TASK it on it.INVENTORY_TASK_ID=sh.INVENTORY_TASK_ID
    left join RRL_PICK_WAVE_REPLENISH_TASK rt on rt.PICK_WAVE_REPLENISH_TASK_ID=sh.REPLENISH_TASK_ID"""


def assert_queue_scope(cur: Any, actor: str, permission: str, warehouse: int | None) -> None:
    # Omitted warehouse means all currently permitted warehouses, never a flat bypass.
    cur.execute("""select ID from RRL_WARES where (:ware is null or ID=:ware)
        and RRL_ACCESS_API.allowed(:actor,:permission,'WAREHOUSE',to_char(ID))=1
        fetch first 1 rows only""", actor=actor, permission=permission, ware=warehouse)
    if cur.fetchone() is None:
        raise HTTPException(403, detail="INVENTORY_QUEUE_WARE_VIEW_REQUIRED")


class RecoveryReads:
    def __init__(self, gateway: Any) -> None:
        self.gateway = gateway

    def inventory(self, actor: str, limit: int, task_id: int | None, warehouse: int | None) -> list[dict[str, Any]]:
        with self.gateway.transaction("Inventory queue scoped READ ONLY") as cur:
            cur.execute("set transaction read only")
            assert_queue_scope(cur, actor, "inventory_task_view", warehouse)
            cur.execute("select * from ("+INVENTORY_PROJECTION+"""
                where ((:task_id is not null and it.INVENTORY_TASK_ID=:task_id)
                   or (:task_id is null and it.STATUS in('NEW','ASSIGNED','IN_PROGRESS')))
                and (:ware is null or it.WARE_ID=:ware) and it.WARE_ID is not null
                and RRL_ACCESS_API.allowed(:actor,'inventory_task_view','WAREHOUSE',to_char(it.WARE_ID))=1
                order by it.PRIORITY,it.CREATED_AT,it.INVENTORY_TASK_ID
                ) where rownum<=:row_limit""", actor=actor, ware=warehouse, task_id=task_id, row_limit=limit)
            return queue_rows(cur)

    def recovery(self, actor: str, limit: int, warehouse: int | None) -> list[dict[str, Any]]:
        with self.gateway.transaction("Recovery queue scoped READ ONLY") as cur:
            cur.execute("set transaction read only")
            assert_queue_scope(cur, actor, "case_pick_view", warehouse)
            cur.execute("select * from ("+RECOVERY_PROJECTION+"""
                where w.STATUS!='CANCELLED'
                and (sh.STATUS in('CREATED','PENDING_APPROVAL')
                  or sh.RECOVERY_STATE in('WAIT_INVENTORY','WAIT_REPLENISHMENT','READY','FAILED'))
                and (:ware is null or w.WARE_ID=:ware) and w.WARE_ID is not null
                and RRL_ACCESS_API.allowed(:actor,'case_pick_view','WAREHOUSE',to_char(w.WARE_ID))=1
                order by sh.CREATED_AT,sh.CASE_PICK_SHORT_ID
                ) where rownum<=:row_limit""", actor=actor, ware=warehouse, row_limit=limit)
            return queue_rows(cur)
