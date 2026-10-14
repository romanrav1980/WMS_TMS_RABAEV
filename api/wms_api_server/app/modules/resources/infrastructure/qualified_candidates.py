"""Bounded qualified candidates using observed cells, existing shifts and rights."""
from typing import Any
from fastapi import HTTPException

class QualifiedCandidates:
    def __init__(self, gateway: Any) -> None:
        self.gateway = gateway

    def candidates(self, cell: str, task_type: str, limit: int = 10) -> list[dict[str, Any]]:
        extra = "and RRL_HAS_WRIGHT(s.OPERATOR_USER_ID,'stock_inventory_count')=1" if task_type == "INVENTORY_CHECK" else ""
        right = "inventory_task_execute" if task_type == "INVENTORY_CHECK" else "warehouse_task_execute"
        return self.gateway.fetch_all("""
            select * from (
             select s.SESSION_ID RESOURCE_SESSION_ID,r.RESOURCE_ID,s.EQUIPMENT_ID,
                    s.OPERATOR_USER_ID ASSIGNED_TO,s.LAST_CELL,s.LAST_POSITION_AT,
                    abs(origin.X-target.X)+abs(origin.Y-target.Y)+abs(origin.Z-target.Z) DISTANCE,
                    'CELL_MANHATTAN' DISTANCE_BASIS
              from RRL_RESOURCE_SESSION s join RRL_RESOURCE r on r.RESOURCE_ID=s.RESOURCE_ID
              join RRL_RESOURCE_TYPE typ on typ.RESOURCE_TYPE=r.RESOURCE_TYPE
              join RRL_RESOURCE_TASK_QUAL q on q.RESOURCE_ID=r.RESOURCE_ID and q.TASK_TYPE=:task_type
              join RRL_RESOURCE_SHIFT sh on sh.SHIFT_ID=s.SHIFT_ID
              join RRL_CELLS origin on origin.CELL=s.LAST_CELL
              join RRL_CELLS target on target.CELL=:target_cell
              join RUSERS u on u.ID=s.OPERATOR_USER_ID
              left join RRL_RESOURCE_EQUIPMENT e on e.EQUIPMENT_ID=s.EQUIPMENT_ID
             where s.STATUS='ACTIVE' and r.ACTIVE=1 and typ.ACTIVE=1 and nvl(u.DELETED,0)=0
              and (r.USER_ID is null or r.USER_ID=s.OPERATOR_USER_ID)
              and r.STATUS in('AVAILABLE','IDLE','IN_WORK') and q.ACTIVE=1
              and q.VALID_FROM<=systimestamp and (q.VALID_UNTIL is null or q.VALID_UNTIL>systimestamp)
              and instr(','||replace(typ.DEFAULT_TASK_TYPES,' ','')||',',','||:task_type||',')>0
              and sh.STATUS='OPEN' and systimestamp between sh.START_AT and sh.FINISH_AT
              and origin.WARE_ID=target.WARE_ID and r.WARE_ID=target.WARE_ID
              and origin.X is not null and origin.Y is not null and origin.Z is not null
              and target.X is not null and target.Y is not null and target.Z is not null
              and s.LAST_POSITION_AT>=cast(systimestamp as timestamp)-numtodsinterval(300,'SECOND')
              and s.LAST_HEARTBEAT_AT>=cast(systimestamp as timestamp)-numtodsinterval(300,'SECOND')
              and s.CURRENT_TASK_ID is null and s.CURRENT_INVENTORY_TASK_ID is null
              and (r.EQUIPMENT_ID is null or r.EQUIPMENT_ID=s.EQUIPMENT_ID)
              and (s.EQUIPMENT_ID is null or (e.ACTIVE=1 and e.SERVICE_STATUS='ACTIVE' and e.WARE_ID=target.WARE_ID))
              and RRL_HAS_WRIGHT(s.OPERATOR_USER_ID,:execute_right)=1
              """ + extra + """
              and not exists(select 1 from RRL_CASE_PICK_TASK ct where ct.ASSIGNED_TO=s.OPERATOR_USER_ID and ct.PICKED_QTY>0 and ct.STATUS in('IN_PROGRESS','PARTIAL','WAIT_REPLENISHMENT'))
              and not exists(select 1 from RRL_WAREHOUSE_TASK t where t.ASSIGNED_TO=s.OPERATOR_USER_ID and t.STATUS='IN_PROGRESS')
              and not exists(select 1 from RRL_WAREHOUSE_TASK t where t.RESOURCE_SESSION_ID=s.SESSION_ID
                and t.STATUS in('ASSIGNED','IN_PROGRESS'))
              and not exists(select 1 from RRL_INVENTORY_TASK it where it.RESOURCE_SESSION_ID=s.SESSION_ID
                and it.STATUS in('ASSIGNED','IN_PROGRESS'))
             order by DISTANCE,s.LAST_POSITION_AT desc,s.SESSION_ID
            ) where rownum<=:row_limit""", {"target_cell": cell, "task_type": task_type,
                                             "execute_right": right, "row_limit": limit})

    def warehouse(self, task_id: int, limit: int = 10) -> list[dict[str, Any]]:
        rows = self.gateway.fetch_all("select FROM_CELL,TO_CELL,TASK_TYPE from RRL_WAREHOUSE_TASK where TASK_ID=:id", {"id": task_id})
        if not rows:
            raise HTTPException(404, detail="Warehouse task not found")
        task = rows[0]
        return self.candidates(task["from_cell"] or task["to_cell"], task["task_type"], limit)

    def dispatch_inventory(self, short_id: int, actor: str) -> dict[str, Any]:
        from ....transaction_gateway import TransactionGateway
        with self.gateway.transaction("Assign nearest qualified inventory resource") as cursor:
            try:
                cursor.execute("begin RRL_STOCK_METADATA_TX.begin_change(:actor,'case_pick_short_approve');end;", {"actor": actor})
                cursor.execute("select RRL_HAS_WRIGHT(:actor,'resource_dispatch_manage') from dual", {"actor": actor})
                if cursor.fetchone()[0] != 1:
                    raise HTTPException(403, detail="resource_dispatch_manage permission required")
                bound = TransactionGateway(cursor)
                rows = bound.fetch_all("""select it.INVENTORY_TASK_ID,it.CELL_CODE,it.STATUS,it.ASSIGNED_TO
                    from RRL_INVENTORY_TASK it join RRL_CASE_PICK_SHORT sh on sh.INVENTORY_TASK_ID=it.INVENTORY_TASK_ID
                    where sh.CASE_PICK_SHORT_ID=:id and sh.RECOVERY_STATE='WAIT_INVENTORY' for update""", {"id": short_id})
                if not rows or rows[0]["assigned_to"]:
                    return {"short_id": short_id, "assigned": False}
                task = rows[0]
                if task["status"] != "NEW":
                    return {"short_id": short_id, "assigned": False}
                candidates = QualifiedCandidates(bound).candidates(task["cell_code"], "INVENTORY_CHECK", 1)
                if not candidates:
                    return {"short_id": short_id, "assigned": False, "reason": "NO_FREE_QUALIFIED_RESOURCE_WITH_FRESH_POSITION"}
                candidate = candidates[0]
                cursor.execute("select SESSION_ID from RRL_RESOURCE_SESSION where SESSION_ID=:id for update",
                               {"id": candidate["resource_session_id"]})
                cursor.execute("""update RRL_INVENTORY_TASK set STATUS='ASSIGNED',ASSIGNED_TO=:owner,
                    ASSIGNED_RESOURCE_ID=:p_resource,RESOURCE_SESSION_ID=:session_id,ASSIGNED_AT=systimestamp,
                    UPDATED_AT=systimestamp,UPDATED_BY=:actor where INVENTORY_TASK_ID=:id""",
                    {"owner": candidate["assigned_to"], "p_resource": candidate["resource_id"],
                     "session_id": candidate["resource_session_id"], "actor": actor, "id": task["inventory_task_id"]})
                cursor.execute("update RRL_RESOURCE_SESSION set CURRENT_INVENTORY_TASK_ID=:task where SESSION_ID=:session_id",
                    {"task": task["inventory_task_id"], "session_id": candidate["resource_session_id"]})
                return {"short_id": short_id, "assigned": True, **candidate}
            finally:
                cursor.execute("begin RRL_STOCK_METADATA_TX.end_change;end;")
