"""Explicit, versioned carrier handoff metadata; existing event journal owns replay."""
from decimal import Decimal
from typing import Any
from fastapi import HTTPException

def replay(gateway: Any, task_id: int, request: Any) -> bool:
    if not request.offline_event_id:return False
    rows=gateway.fetch_all("""select CASE_PICK_TASK_ID,EVENT_TYPE,PAYLOAD_JSON,CREATED_BY
        from RRL_CASE_PICK_EVENT where OFFLINE_EVENT_ID=:event_id fetch first 2 rows only""",
        {"event_id":request.offline_event_id})
    if not rows:return False
    wire=str(request.model_dump());row=rows[0]
    if (len(rows)!=1 or len(wire)>3900 or row["case_pick_task_id"]!=task_id
        or row["event_type"]!="TRANSFERRED" or row["created_by"]!=request.actor or row["payload_json"]!=wire):
        raise HTTPException(409,detail={"code":"CASE_HANDOFF_CONTENT_CONFLICT"})
    return True

def validate(gateway: Any, task_id: int, request: Any) -> None:
    rows=gateway.fetch_all("""select SSCC,PICKED_QTY,CONTENT_VERSION,ASSIGNED_TO,RESOURCE_SESSION_ID
        from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:task_id""",{"task_id":task_id})
    if not rows:raise HTTPException(404,detail="CASE task not found")
    task=rows[0]
    if Decimal(str(task["picked_qty"] or 0))<=0:return
    if (not request.offline_event_id or not request.scan_container or request.expected_content_version is None
        or not request.expected_assigned_to):
        raise HTTPException(409,detail={"code":"CASE_PHYSICAL_HANDOFF_CONFIRMATION_REQUIRED"})
    if request.scan_container!=task["sscc"]:
        raise HTTPException(409,detail={"code":"CASE_HANDOFF_WRONG_CARRIER"})
    if (request.expected_content_version!=task["content_version"]
        or request.expected_assigned_to!=task["assigned_to"]
        or request.expected_from_session_id!=task["resource_session_id"]):
        raise HTTPException(409,detail={"code":"CASE_HANDOFF_STALE_OWNER_OR_CONTENT"})
    if len(str(request.model_dump()))>3900:
        raise HTTPException(422,detail="CASE handoff payload exceeds the existing immutable event contract")
