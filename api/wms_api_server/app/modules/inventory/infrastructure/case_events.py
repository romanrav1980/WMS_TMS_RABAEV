"""Existing CASE journal writer; caller owns transaction and physical effects."""
from typing import Any

def write_case_event(
    gateway: Any,
    case_pick_task_id: int | None,
    line_id: int | None,
    event_type: str,
    request: Any,
    actor: str,
) -> None:
    data = request.model_dump() if hasattr(request, "model_dump") else {}
    gateway.execute_plsql(
        """
        begin
          insert into RRL_CASE_PICK_EVENT (
            CASE_PICK_EVENT_ID, CASE_PICK_TASK_ID, CASE_PICK_LINE_ID, EVENT_TYPE,
            OFFLINE_EVENT_ID, RESOURCE_ID, RESOURCE_SESSION_ID, EQUIPMENT_ID,
            MESSAGE_TEXT, PAYLOAD_JSON, CREATED_AT, CREATED_BY
          ) values (
            RRL_CASE_PICK_EVENT_SQ.nextval, :case_pick_task_id, :case_pick_line_id, :event_type,
            substr(:offline_event_id, 1, 100), :resource_id, :resource_session_id, :equipment_id,
            substr(:message_text, 1, 1000), :payload_json, systimestamp, substr(:actor, 1, 100)
          );
        exception
          when dup_val_on_index then
            null;
        end;
        """,
        {
            "case_pick_task_id": case_pick_task_id,
            "case_pick_line_id": line_id,
            "event_type": event_type,
            "offline_event_id": data.get("offline_event_id"),
            "resource_id": data.get("resource_id") or data.get("to_resource_id"),
            "resource_session_id": data.get("resource_session_id") or data.get("to_resource_session_id"),
            "equipment_id": data.get("equipment_id") or data.get("to_equipment_id"),
            "message_text": data.get("reason") or data.get("reason_text"),
            "payload_json": str(data)[:3900],
            "actor": actor,
        },
    )
