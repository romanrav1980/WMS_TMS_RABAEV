"""Session capacity and end-of-shift handover without changing stock."""
from typing import Any, Callable
import oracledb
from fastapi import HTTPException
from ....transaction_gateway import TransactionGateway

def open_session(gateway: Any, request: Any, create: Callable[[Any, Any], int]) -> int:
    with gateway.transaction("Open existing resource session with shift capacity") as cursor:
        cursor.execute("""select WARE_ID,REACH_SHIFT_ROLE,EXPECTED_DRIVERS,STATUS
            from RRL_RESOURCE_SHIFT where SHIFT_ID=:id for update""", {"id": request.shift_id})
        shift = cursor.fetchone()
        if shift is None:
            raise HTTPException(404, detail="Resource shift not found")
        ware, role, expected, status = shift
        existing = _open_twin(cursor, request)  # the exact repeat first: its own session already counts against the shift capacity
        if existing is not None:
            return existing
        if role in {"MAIN", "DUTY"}:
            if status != "OPEN":
                raise HTTPException(409, detail="Reachtruck shift is not open")
            cursor.execute("select WARE_ID,ACTIVE from RRL_RESOURCE where RESOURCE_ID=:id", {"id": request.resource_id})
            resource = cursor.fetchone()
            if resource is None or resource[0] != ware or resource[1] != 1:
                raise HTTPException(409, detail="Resource must be active in this warehouse")
            cursor.execute("""select count(*) from RRL_RESOURCE_SESSION where SHIFT_ID=:id
                and STATUS in('ACTIVE','PAUSED')""", {"id": request.shift_id})
            if expected is None or cursor.fetchone()[0] >= expected:
                raise HTTPException(409, detail="REACH_SHIFT_DRIVER_CAPACITY_REACHED")
        # C-0177 (T10, double assignment): one open session per operator, resource and equipment is enforced by the unique indexes
        # RRL_RESOURCE_SESSION_U1..U3. The same request repeated (for example after a lost reply) returns the session it opened;
        # a different request that collides is a confirmed refusal naming the occupied resource, never an unknown 500.
        try:
            return create(TransactionGateway(cursor), request)
        except oracledb.DatabaseError as error:
            if getattr(error.args[0], "code", 0) != 1:
                raise
            existing = _open_twin(cursor, request)  # a concurrent identical request won the unique index
            if existing is not None:
                return existing
            raise HTTPException(409, detail={"code": _occupied(str(error.args[0])), "outcome_confirmed": True}) from error


def _effective(cursor: Any, request: Any) -> tuple[Any, Any] | None:
    cursor.execute("select EQUIPMENT_ID,USER_ID from RRL_RESOURCE where RESOURCE_ID=:id", {"id": request.resource_id})
    row = cursor.fetchone()
    if row is None:
        return None
    equipment = request.equipment_id if request.equipment_id is not None else row[0]
    return equipment, (request.operator_user_id or row[1])


def _open_twin(cursor: Any, request: Any) -> int | None:
    """The open session this exact request (same shift, resource, equipment and operator) already created, if any."""
    effective = _effective(cursor, request)
    if effective is None or effective[1] is None:
        return None
    equipment, operator = effective
    cursor.execute("""select SESSION_ID from RRL_RESOURCE_SESSION where STATUS in('ACTIVE','PAUSED') and upper(OPERATOR_USER_ID)=upper(:op_user)
        and SHIFT_ID=:shift and RESOURCE_ID=:res_id and (EQUIPMENT_ID=:equip or (EQUIPMENT_ID is null and :equip is null))""",
        {"op_user": operator, "shift": request.shift_id, "res_id": request.resource_id, "equip": equipment})
    row = cursor.fetchone()
    return int(row[0]) if row else None


def _occupied(message: str) -> str:
    text = message.upper()
    if "RRL_RESOURCE_SESSION_U3" in text:
        return "OPERATOR_ALREADY_IN_SESSION"
    if "RRL_RESOURCE_SESSION_U2" in text:
        return "EQUIPMENT_ALREADY_IN_SESSION"
    if "RRL_RESOURCE_SESSION_U1" in text:
        return "RESOURCE_ALREADY_IN_SESSION"
    return "RESOURCE_SESSION_CONFLICT"

def close_session(gateway: Any, session_id: int, actor: str) -> None:
    with gateway.transaction("End resource shift after physical step or handover") as cursor:
        cursor.execute("""select STATUS,OPERATOR_USER_ID from RRL_RESOURCE_SESSION
            where SESSION_ID=:id for update""", {"id": session_id})
        session = cursor.fetchone()
        if session is None or session[0] not in {"ACTIVE", "PAUSED", "ERROR"}:
            raise HTTPException(404, detail="Open resource session not found")
        cursor.execute("""select TASK_ID from RRL_WAREHOUSE_TASK
            where (RESOURCE_SESSION_ID=:session_id or ASSIGNED_TO=:owner)
             and STATUS in('ASSIGNED','IN_PROGRESS') order by TASK_ID fetch first 20 rows only""",
            {"session_id": session_id, "owner": session[1]})
        warehouse = [int(row[0]) for row in cursor.fetchall()]
        cursor.execute("""select INVENTORY_TASK_ID from RRL_INVENTORY_TASK
            where (RESOURCE_SESSION_ID=:session_id or ASSIGNED_TO=:owner)
             and STATUS in('ASSIGNED','IN_PROGRESS') order by INVENTORY_TASK_ID fetch first 20 rows only""",
            {"session_id": session_id, "owner": session[1]})
        inventory = [int(row[0]) for row in cursor.fetchall()]
        cursor.execute("""select CASE_PICK_TASK_ID from RRL_CASE_PICK_TASK where ASSIGNED_TO=:owner
             and STATUS in('ASSIGNED','IN_PROGRESS','PARTIAL','WAIT_REPLENISHMENT')
             order by CASE_PICK_TASK_ID fetch first 20 rows only""", {"owner": session[1]})
        cases = [int(row[0]) for row in cursor.fetchall()]
        if warehouse or inventory or cases:
            raise HTTPException(409, detail={"code": "SHIFT_HANDOVER_REQUIRED", "warehouse_tasks": warehouse,
                "inventory_tasks": inventory, "case_tasks": cases,
                "message": "Finish the current physical step; transfer unstarted tasks or the CASE carrier before leaving"})
        cursor.execute("""update RRL_RESOURCE_SESSION set STATUS='CLOSED',LOGOUT_AT=systimestamp,
            CLOSED_BY=:actor,CURRENT_TASK_ID=null,CURRENT_INVENTORY_TASK_ID=null where SESSION_ID=:id""",
            {"id": session_id, "actor": actor})
