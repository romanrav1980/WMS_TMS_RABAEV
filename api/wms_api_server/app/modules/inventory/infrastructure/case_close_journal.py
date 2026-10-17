"""Exact metadata command result in the original immutable CASE event journal."""
import json
from typing import Any, Callable
import oracledb
from fastapi import HTTPException


def close_replay(cur: Any, operation: str | None, task: int, actor: str, body: dict[str, Any],
                 validate_result: Callable[[Any],None] | None = None) -> dict[str, Any] | None:
    if operation is None:
        return None
    cur.execute("""select CASE_PICK_TASK_ID,EVENT_TYPE,CREATED_BY,to_clob(PAYLOAD_JSON)
        from RRL_CASE_PICK_EVENT where OFFLINE_EVENT_ID=:id""", id=operation)
    row = cur.fetchone()
    if row is None:
        return None
    raw = row[3].read() if hasattr(row[3], "read") else row[3]
    try:
        data = json.loads(raw)
    except (TypeError, json.JSONDecodeError):
        raise HTTPException(409, detail="CASE_CLOSE_CONTENT_CONFLICT")
    if not isinstance(data, dict) or row[0] != task or row[1] not in ("CLOSED", "CLOSE_ACK") or row[2] != actor or data.get("request") != body:
        raise HTTPException(409, detail="CASE_CLOSE_CONTENT_CONFLICT")
    if validate_result is not None:
        validate_result(data.get("result"))
    return data["result"]


def record_close(cur: Any, operation: str | None, task: int, actor: str, body: dict[str, Any], result: dict[str, Any]) -> None:
    event = "CLOSE_ACK" if result.get("already_closed") else "CLOSED"
    wire = cur.var(oracledb.DB_TYPE_CLOB)
    wire.setvalue(0, json.dumps({"command_kind": "CASE_CARRIER_CLOSE", "request": body, "result": result}, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
    cur.execute("""insert into RRL_CASE_PICK_EVENT(CASE_PICK_EVENT_ID,CASE_PICK_TASK_ID,EVENT_TYPE,
        OFFLINE_EVENT_ID,RESOURCE_ID,RESOURCE_SESSION_ID,EQUIPMENT_ID,MESSAGE_TEXT,PAYLOAD_JSON,CREATED_AT,CREATED_BY)
        values(RRL_CASE_PICK_EVENT_SQ.nextval,:p_task,:p_event,:p_operation,:p_resource,:p_session_id,:p_equipment,
               :p_reason,:p_payload,systimestamp,:p_actor)""",
        p_task=task,p_event=event,p_operation=operation,p_resource=body.get("resource_id"),
        p_session_id=body.get("resource_session_id"),p_equipment=body.get("equipment_id"),
        p_reason=(body.get("reason") or "")[:1000],p_payload=wire,p_actor=actor)
