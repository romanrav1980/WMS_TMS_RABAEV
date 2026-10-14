"""Preserve the original shortage report result and reject reuse with another body."""
from typing import Any
from fastapi import HTTPException


def short_report_replay(gateway: Any, task_id: int, line_id: int,
                         request: Any) -> dict[str, Any] | None:
    if not request.offline_event_id:
        return None
    rows = gateway.fetch_all("""select CASE_PICK_TASK_ID,CASE_PICK_LINE_ID,EVENT_TYPE,
        PAYLOAD_JSON,CREATED_BY from RRL_CASE_PICK_EVENT where OFFLINE_EVENT_ID=:event_id""",
        {"event_id": request.offline_event_id})
    if not rows:
        return None
    wire = str(request.model_dump())
    row = rows[0]
    if (len(rows) != 1 or len(wire) > 3900 or row["case_pick_task_id"] != task_id
            or row["case_pick_line_id"] != line_id or row["event_type"] != "SHORT_CREATED"
            or row["created_by"] != request.actor or row["payload_json"] != wire):
        raise HTTPException(409, detail={"code": "SHORT_REPORT_CONTENT_CONFLICT"})
    shorts = gateway.fetch_all("""select CASE_PICK_SHORT_ID,STATUS,RECOVERY_STATE,
        to_char(SHORT_QTY,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') SHORT_QTY
        from RRL_CASE_PICK_SHORT where OFFLINE_EVENT_ID=:event_id
          and CASE_PICK_TASK_ID=:task_id and CASE_PICK_LINE_ID=:line_id""",
        {"event_id": request.offline_event_id, "task_id": task_id, "line_id": line_id})
    if len(shorts) != 1:
        raise HTTPException(409, detail={"code": "SHORT_REPORT_RESULT_INCONSISTENT"})
    return {"case_pick_short_id": shorts[0]["case_pick_short_id"],
            "status": shorts[0]["status"], "short_qty": shorts[0]["short_qty"],
            "recovery_state": shorts[0]["recovery_state"], "idempotent": True}
