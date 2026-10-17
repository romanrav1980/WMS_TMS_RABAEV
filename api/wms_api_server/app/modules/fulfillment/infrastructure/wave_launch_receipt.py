"""Minimal original launch and continuation receipts under current actual warehouse access."""
from typing import Any


def read_launch_receipt(gateway: Any, wave: int, operation: str, actor: str) -> dict[str, Any]:
    with gateway.transaction("Current scoped original wave launch receipt READ ONLY") as cursor:
        cursor.execute("set transaction read only")
        cursor.execute("""select o.STATE,c.STATE,w.STATUS,w.PICK_RELEASED_AT
            from RRL_STOCK_OPERATION o join RRL_PICK_WAVE w on w.PICK_WAVE_ID=:wave
            left join RRL_WAVE_CONTINUE c on c.LAUNCH_OPERATION_ID=o.OPERATION_ID
            where o.OPERATION_ID=:operation and o.COMMAND_TYPE='WAVE_LAUNCH'
              and json_value(o.CANONICAL_REQUEST,'$.source.wave_id' returning number null on error)=w.PICK_WAVE_ID
              and(o.ACTOR=:actor or RRL_ACCESS_API.is_admin(:actor)=1)
              and RRL_ACCESS_API.allowed(:actor,'pick_wave_launch','WAREHOUSE',to_char(w.WARE_ID))=1""",
                       operation=operation, wave=wave, actor=actor)
        row = cursor.fetchone()
        steps = []
        if row and row[1]:
            cursor.execute("""select STEP_NAME,STATE,ERROR_CODE,COMPLETED_AT from RRL_WAVE_CONTINUE_STEP
                where LAUNCH_OPERATION_ID=:operation order by STEP_NO""", operation=operation)
            steps = [{"step": name, "state": state, "error_code": code,
                      "completed_at": completed.isoformat() if completed else None}
                     for name, state, code, completed in cursor.fetchall()]
    state = row[0] if row else "NOT_VISIBLE"
    continuation = row[1] if row else "NOT_VISIBLE"
    if row and continuation is None:
        continuation = "PENDING" if row[2] == "LAUNCHED" and row[3] is None else "RECONCILIATION_REQUIRED"
    return {"operation_id": operation, "wave_id": wave, "state": state,
            "wave_status": row[2] if row else None,
            "launch_outcome_confirmed": state == "APPLIED", "continuation_state": continuation,
            "continuation_steps": steps, "commands_executed": False}
