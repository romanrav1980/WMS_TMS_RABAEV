"""Create operational tasks from existing reserved replenishment rows."""
from typing import Any
from fastapi import HTTPException
from ....transaction_gateway import TransactionGateway
from ...inventory.public import reconcile_existing_shared_arrival, begin_wave_metadata
from .wave_task_projection import INSERT_TASKS


def sync_wave_tasks(gateway: Any, wave_id: int, actor: str) -> None:
    with gateway.transaction("Sync reserved wave warehouse tasks") as cursor:
        entered = False
        try:
            entered = begin_wave_metadata(gateway, cursor, wave_id, actor)
            cursor.execute("""select count(*)from RRL_PICK_WAVE w join RUSERS u on u.ID=:actor
                where w.PICK_WAVE_ID=:wave and nvl(u.DELETED,0)=0
                  and(u.WARE_ID=w.WARE_ID or upper(trim(u.USER_GROUP))='GLOBAL_ADMIN' or :scoped=1)""",
                           {"wave": wave_id, "actor": actor, "scoped": 0 if entered else 1})
            if cursor.fetchone()[0]!=1:
                raise HTTPException(403,detail="WAVE_TASK_CURRENT_WAREHOUSE_REQUIRED")
            reconcile_existing_shared_arrival(TransactionGateway(cursor),wave_id,actor)
            cursor.execute(INSERT_TASKS, {"wave": wave_id, "actor": actor})
        finally:
            if entered:
                cursor.execute("begin RRL_STOCK_METADATA_TX.end_change;end;")
