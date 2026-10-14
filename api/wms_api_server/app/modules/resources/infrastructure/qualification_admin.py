"""Metadata-only qualification and observed position commands."""
from typing import Any
from fastapi import HTTPException

class QualificationAdmin:
    def __init__(self, gateway: Any) -> None:
        self.gateway = gateway

    def qualifications(self, resource_id: int) -> list[dict[str, Any]]:
        return self.gateway.fetch_all("""select RESOURCE_ID,TASK_TYPE,ACTIVE,VALID_FROM,VALID_UNTIL,UPDATED_BY,UPDATED_AT
            from RRL_RESOURCE_TASK_QUAL where RESOURCE_ID=:id order by TASK_TYPE fetch first 100 rows only""", {"id": resource_id})

    def set_qualification(self, resource_id: int, task_type: str, active: bool, actor: str) -> dict[str, Any]:
        with self.gateway.transaction("Maintain resource qualification") as cursor:
            try:
                cursor.execute("begin RRL_STOCK_CONFIG_API.begin_change(:actor,'warehouse_settings_edit');end;", {"actor": actor})
                cursor.execute("select r.RESOURCE_ID from RRL_RESOURCE r join RRL_RESOURCE_TYPE t on t.RESOURCE_TYPE=r.RESOURCE_TYPE where r.RESOURCE_ID=:id and instr(','||replace(t.DEFAULT_TASK_TYPES,' ','')||',',','||:task_type||',')>0",
                               {"id": resource_id, "task_type": task_type})
                if cursor.fetchone() is None:
                    raise HTTPException(409, detail="Task type is not supported by this resource type")
                cursor.execute("""merge into RRL_RESOURCE_TASK_QUAL d
                    using(select :rid RESOURCE_ID,:task_type TASK_TYPE from dual)s
                    on(d.RESOURCE_ID=s.RESOURCE_ID and d.TASK_TYPE=s.TASK_TYPE)
                    when matched then update set ACTIVE=:active,UPDATED_BY=:actor,UPDATED_AT=systimestamp
                    when not matched then insert(RESOURCE_ID,TASK_TYPE,ACTIVE,UPDATED_BY)
                    values(s.RESOURCE_ID,s.TASK_TYPE,:active,:actor)""",
                    {"rid": resource_id, "task_type": task_type, "active": int(active), "actor": actor})
            finally:
                cursor.execute("begin RRL_STOCK_CONFIG_API.end_change;end;")
        return {"resource_id": resource_id, "task_type": task_type, "active": active}

    def position(self, session_id: int, cell: str, actor: str) -> dict[str, Any]:
        with self.gateway.transaction("Confirm observed resource position") as cursor:
            try:
                cursor.execute("select RRL_HAS_WRIGHT(:actor,'inventory_task_execute'),RRL_HAS_WRIGHT(:actor,'warehouse_task_execute') from dual", {"actor": actor})
                rights = cursor.fetchone()
                if rights != (1,1) and 1 not in rights:
                    raise HTTPException(403, detail="Task executor permission required")
                permission = "inventory_task_execute" if rights[0] == 1 else "warehouse_task_execute"
                cursor.execute("begin RRL_STOCK_METADATA_TX.begin_change(:actor,:permission);end;", {"actor": actor,"permission":permission})
                cursor.execute("""select s.OPERATOR_USER_ID,r.WARE_ID from RRL_RESOURCE_SESSION s
                    join RRL_RESOURCE r on r.RESOURCE_ID=s.RESOURCE_ID
                    where s.SESSION_ID=:id and s.STATUS='ACTIVE' for update""", {"id": session_id})
                row = cursor.fetchone()
                if row is None:
                    raise HTTPException(404, detail="Active session not found")
                if row[0] != actor:
                    raise HTTPException(403, detail="Only the session operator may confirm its position")
                cursor.execute("select WARE_ID from RRL_CELLS where CELL=:cell", {"cell": cell})
                target = cursor.fetchone()
                if target is None or target[0] != row[1]:
                    raise HTTPException(409, detail="Cell must belong to the resource warehouse")
                cursor.execute("""update RRL_RESOURCE_SESSION set LAST_CELL=:cell,LAST_POSITION_AT=systimestamp,
                    LAST_HEARTBEAT_AT=systimestamp where SESSION_ID=:id""", {"cell": cell, "id": session_id})
            finally:
                cursor.execute("begin RRL_STOCK_METADATA_TX.end_change;end;")
        return {"resource_session_id": session_id, "cell": cell}
