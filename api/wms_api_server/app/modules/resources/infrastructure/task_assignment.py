"""Use the installed read-only policy while the caller owns task/session row locks."""
import json
from typing import Any
from fastapi import HTTPException
import oracledb


def task_resource_context(gateway: Any, task: dict[str, Any], action: str,
                          request: Any, assignee: str) -> dict[str, Any]:
    session = request.resource_session_id
    if session is None and task.get("assigned_to") == assignee:
        session = task.get("resource_session_id")
    if session is not None:
        gateway.fetch_all("select SESSION_ID from RRL_RESOURCE_SESSION where SESSION_ID=:id for update",
                          {"id": session})
    try:
        rows = gateway.fetch_all(
            """select RRL_TASK_RESOURCE_POLICY.context_json(
                :p_task,:p_action,:p_actor,:p_assignee,:p_resource,:p_session_id,:p_equipment) CONTEXT_JSON from dual""",
            {"p_task": task["task_id"], "p_action": action, "p_actor": request.updated_by,
             "p_assignee": assignee, "p_resource": request.resource_id,
             "p_session_id": request.resource_session_id, "p_equipment": request.equipment_id},
        )
        context=json.loads(rows[0]["context_json"])
        # Policy diagnostics are not bind parameters or persistent assignment fields.
        keys=("resource_id","resource_session_id","equipment_id")
        if any(key not in context for key in keys):
            raise HTTPException(409,detail="TASK_RESOURCE_CONTEXT_INVALID")
        return {key:context[key] for key in keys}
    except oracledb.DatabaseError as exc:
        code = getattr(exc.args[0], "code", None)
        if code in {20881, 20882, 20886}:
            raise HTTPException(403 if code == 20882 else 409,
                                detail={"code": "TASK_RESOURCE_REJECTED", "oracle_code": code,
                                        "message": exc.args[0].message.split("\n")[0]}) from exc
        raise
