"""Assign an existing urgent replenishment step; never conduct stock."""
from typing import Any, Callable
from fastapi import HTTPException
from .nearest_dispatch import dispatch_warehouse

def dispatch_urgent(gateway: Any, short_id: int, actor: str,assign: Callable[[Any,int,Any],None]) -> dict[str,Any]:
    rows=gateway.fetch_all("""select wt.TASK_ID,wt.STATUS,wt.ASSIGNED_TO
        from RRL_CASE_PICK_SHORT sh join RRL_WAREHOUSE_TASK wt
         on wt.TASK_SOURCE='WAVE' and wt.TASK_TYPE='REPLENISHMENT'
          and wt.SOURCE_TASK_ID=sh.REPLENISH_TASK_ID
        where sh.CASE_PICK_SHORT_ID=:short_id and sh.RECOVERY_STATE='WAIT_REPLENISHMENT'
         and wt.PRIORITY=0 and wt.STATUS in('PLANNED','ASSIGNED','IN_PROGRESS')
        order by wt.TASK_ID fetch first 1 row only""",{"short_id":short_id})
    if not rows:return {"assigned":False,"reason":"URGENT_PHYSICAL_STEP_NOT_READY"}
    task=rows[0]
    if task["status"]!="PLANNED":
        return {"assigned":True,"task_id":task["task_id"],"assigned_to":task["assigned_to"],"status":task["status"]}
    try:
        return {"assigned":True,**dispatch_warehouse(gateway,int(task["task_id"]),actor,assign)}
    except HTTPException as exc:
        if exc.status_code==409 and exc.detail=="NO_FREE_QUALIFIED_RESOURCE_WITH_FRESH_POSITION":
            return {"assigned":False,"task_id":task["task_id"],"reason":exc.detail}
        raise
