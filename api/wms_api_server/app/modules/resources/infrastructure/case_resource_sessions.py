"""Own physical sessions for one authorized CASE; native policy decides readiness."""
from typing import Any
import oracledb
from ...platform.public import read_oracle_json
from ..contracts_case_resource import CaseResourceError, CaseResourceState


def session_choices(gateway: Any, task: int, actor: str) -> dict[str, Any]:
    with gateway.transaction("Own CASE physical session choices READ ONLY") as cursor:
        cursor.execute("set transaction read only")
        output = cursor.var(oracledb.DB_TYPE_CLOB)
        cursor.callproc("RRL_CASE_ASSIGNMENT_API.task_context", [task, actor, output])
        current = read_oracle_json(output.getvalue())
        state = CaseResourceState.model_validate({k: v for k, v in current.items() if k != "current_actor"})
        if current.get("current_actor") != actor or state.task_id != task:
            raise CaseResourceError("CASE_RESOURCE_SESSION_CONTEXT_INVALID", 503)
        cursor.execute("""select s.SESSION_ID,s.RESOURCE_ID,s.EQUIPMENT_ID,r.RESOURCE_CODE
            from RRL_RESOURCE_SESSION s join RRL_RESOURCE r on r.RESOURCE_ID=s.RESOURCE_ID
            where s.OPERATOR_USER_ID=:actor and s.STATUS='ACTIVE' and r.WARE_ID=:ware
            order by s.SESSION_ID desc fetch first 21 rows only""", actor=actor, ware=state.warehouse_id)
        rows = cursor.fetchall()
        if len(rows) > 20:
            raise CaseResourceError("CASE_OWN_ACTIVE_SESSION_BOUND_20", 409)
        action = "CLAIM" if state.status == "NEW" else "START"
        items = []
        for session, resource, equipment, code in rows:
            reason = None
            try:
                value = cursor.callfunc("RRL_CASE_RESOURCE_POLICY.context_json", oracledb.DB_TYPE_CLOB,
                                        [task, action, actor, resource, session, equipment])
                resolved = read_oracle_json(value)
                if (resolved.get("assigned_to"), resolved.get("resource_session_id"), resolved.get("resource_id"),
                    resolved.get("equipment_id")) != (actor, session, resource, equipment):
                    raise CaseResourceError("CASE_OWN_SESSION_POLICY_CONTEXT_INVALID", 503)
            except oracledb.DatabaseError as error:
                if error.args[0].code != 20886:
                    raise
                reason = str(error.args[0]).split("\n", 1)[0]
            items.append(dict(resource_session_id=session, resource_id=resource, equipment_id=equipment,
                              resource_code=code, ready=reason is None, reason=reason))
        return dict(task_id=task, warehouse_id=state.warehouse_id, current_actor=actor,
                    action=action, items=items, command_revalidates=True)
