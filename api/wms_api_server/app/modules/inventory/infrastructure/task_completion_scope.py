"""Pure preflight; final current rights remain inside canonical native posting."""
from typing import Any
import json
import oracledb
from ..contracts_task_completion import TaskCompletionAccessError


def authorize_task_completion(gateway: Any, task: int, actor: str,
                              operation: str | None, expected_signature: str | None) -> None:
    with gateway.transaction("Read current ordinary task completion admission") as cursor:
        cursor.execute("set transaction read only")
        cursor.execute("""select RRL_HAS_WRIGHT(u.ID,'warehouse_task_execute'),
            RRL_WAREHOUSE_TASK_ACCESS.scoped_stock_executor(:task,u.ID),
            (select t.HU_CONTENT_VERSION from RRL_WAREHOUSE_TASK t where t.TASK_ID=:task)
            from RUSERS u where u.ID=:actor and nvl(u.DELETED,0)=0""", task=task, actor=actor)
        current = cursor.fetchone()
        if not current:
            raise TaskCompletionAccessError("TASK_CURRENT_ACTIVE_ACTOR_REQUIRED")
        if current[0] == 1:
            return
        if len(current) > 2 and current[2] is not None:
            # The HU owner freezes task/HU versions and checks the whole planned
            # place. Reuse its native current authority, preserving its wire.
            wire=json.dumps({"command_type":"HU_TASK_COMPLETE","source":{"task_id":task},"metadata":{}})
            try:
                cursor.callproc("RRL_WAREHOUSE_TASK_ACCESS.assert_completion",[wire,actor])
            except oracledb.DatabaseError as error:
                raise TaskCompletionAccessError("TASK_CURRENT_SCOPED_EXECUTE_REQUIRED",
                    403 if error.args[0].code in (20882,1403) else 503) from error
            if not operation:
                raise TaskCompletionAccessError("TASK_OPERATION_ID_REQUIRED",422)
            return
        if current[1] != 1:
            raise TaskCompletionAccessError("TASK_CURRENT_SCOPED_EXECUTE_REQUIRED")
        if not operation:
            raise TaskCompletionAccessError("TASK_OPERATION_ID_REQUIRED", 422)
        if expected_signature:
            return
        # An original committed request may predate expected_signature. Never add a
        # field to its body merely to recover it; native compares the exact body.
        cursor.execute("""select count(*) from RRL_STOCK_OPERATION where OPERATION_ID=:operation
            and ACTOR=:actor and COMMAND_TYPE='TASK_COMPLETE' and STATE='APPLIED'
            and json_value(CANONICAL_REQUEST,'$.source.task_id' returning number null on error)=:task""",
                       operation=operation, actor=actor, task=task)
        if cursor.fetchone()[0] != 1:
            raise TaskCompletionAccessError("TASK_EXPECTED_SIGNATURE_REQUIRED", 422)
