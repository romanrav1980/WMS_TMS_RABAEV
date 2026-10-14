"""Inventory task queue and recovery monitoring on the existing domain objects."""
from typing import Any
from fastapi import HTTPException


class RecoveryTasks:
    def __init__(self, gateway: Any) -> None:
        self.gateway = gateway

    def list_inventory(self, limit: int, task_id: int | None = None) -> list[dict[str, Any]]:
        return self.gateway.fetch_all("""select * from (
            select it.INVENTORY_TASK_ID,it.STATUS,it.WARE_ID WAREHOUSE_ID,it.CELL_CODE CELL,
                   it.ARTICUL ARTICLE,it.ASSIGNED_TO,it.PRIORITY,it.REVISION_ID,it.COUNT_OPERATION_ID,
                   sh.CASE_PICK_SHORT_ID SHORT_ID,sh.RECOVERY_STATE,sh.RECOVERY_DEADLINE_AT,
                   to_char(it.FACT_QTY,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') FACT_QUANTITY
              from RRL_INVENTORY_TASK it left join RRL_CASE_PICK_SHORT sh on sh.CASE_PICK_SHORT_ID=it.SOURCE_DOC_ID
               and it.SOURCE_DOC_TYPE='CASE_PICK_SHORT'
             where (:task_id is not null and it.INVENTORY_TASK_ID=:task_id)
                or (:task_id is null and it.STATUS in('NEW','ASSIGNED','IN_PROGRESS'))
             order by it.PRIORITY,it.CREATED_AT,it.INVENTORY_TASK_ID
        ) where rownum<=:row_limit""", {"task_id": task_id, "row_limit": limit})

    def list_recovery(self, limit: int) -> list[dict[str, Any]]:
        return self.gateway.fetch_all("""select * from (
            select sh.CASE_PICK_SHORT_ID SHORT_ID,sh.CASE_PICK_TASK_ID,sh.CASE_PICK_LINE_ID,
                   sh.PICK_WAVE_ID,sh.CELL_CODE CELL,sh.ARTICUL ARTICLE,sh.CREATED_BY PICKER,
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
              from RRL_CASE_PICK_SHORT sh join RRL_CASE_PICK_LINE l on l.CASE_PICK_LINE_ID=sh.CASE_PICK_LINE_ID join RRL_PICK_WAVE w on w.PICK_WAVE_ID=sh.PICK_WAVE_ID left join RRL_INVENTORY_TASK it on it.INVENTORY_TASK_ID=sh.INVENTORY_TASK_ID
              left join RRL_PICK_WAVE_REPLENISH_TASK rt on rt.PICK_WAVE_REPLENISH_TASK_ID=sh.REPLENISH_TASK_ID
             where w.STATUS!='CANCELLED' and (sh.STATUS in('CREATED','PENDING_APPROVAL') or sh.RECOVERY_STATE in('WAIT_INVENTORY','WAIT_REPLENISHMENT','READY','FAILED'))
             order by sh.CREATED_AT,sh.CASE_PICK_SHORT_ID
        ) where rownum<=:row_limit""", {"row_limit": limit})

    def claim_inventory(self, task_id: int, actor: str) -> dict[str, Any]:
        with self.gateway.transaction("Claim existing inventory task") as cursor:
            try:
                cursor.execute("begin RRL_STOCK_METADATA_TX.begin_change(:actor,:permission);end;",
                               {"actor": actor, "permission": "inventory_task_execute"})
                cursor.execute("select RRL_HAS_WRIGHT(:actor,'stock_inventory_count') from dual", {"actor": actor})
                if cursor.fetchone()[0] != 1:
                    raise HTTPException(403, detail="stock_inventory_count permission is required")
                cursor.execute("select STATUS,ASSIGNED_TO from RRL_INVENTORY_TASK where INVENTORY_TASK_ID=:task_id for update",
                               {"task_id": task_id})
                row = cursor.fetchone()
                if row is None:
                    raise HTTPException(404, detail="Inventory task not found")
                state, owner = row
                if state not in {"NEW", "ASSIGNED", "IN_PROGRESS"} or owner not in {None, actor}:
                    raise HTTPException(409, detail="Inventory task is closed or assigned to another auditor")
                cursor.execute("""update RRL_INVENTORY_TASK set STATUS='IN_PROGRESS',ASSIGNED_TO=:actor,
                    ASSIGNED_AT=nvl(ASSIGNED_AT,systimestamp),STARTED_AT=nvl(STARTED_AT,systimestamp),
                    UPDATED_AT=systimestamp,UPDATED_BY=:actor where INVENTORY_TASK_ID=:task_id""",
                    {"task_id": task_id, "actor": actor})
            finally:
                cursor.execute("begin RRL_STOCK_METADATA_TX.end_change;end;")
        return self.list_inventory(1, task_id)[0]
