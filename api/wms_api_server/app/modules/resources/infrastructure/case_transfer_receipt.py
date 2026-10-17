"""Read the immutable original handoff event; current assignment is not a receipt."""
import ast
from typing import Any
import oracledb
from ....schemas import CasePickTransferRequest
from ..contracts_case_resource import CaseResourceError


def transfer_receipt(gateway: Any, task: int, event: str, actor: str) -> dict[str, Any]:
    try:
        with gateway.transaction("Immutable CASE transfer receipt READ ONLY") as cursor:
            cursor.execute("set transaction read only")
            cursor.callproc("RRL_CASE_TRANSFER_SCOPE.assert_manager", [task, actor])
            cursor.execute("""select CASE_PICK_TASK_ID,EVENT_TYPE,PAYLOAD_JSON,CREATED_BY
                from RRL_CASE_PICK_EVENT where OFFLINE_EVENT_ID=:event_id
                fetch first 2 rows only""", event_id=event)
            rows = cursor.fetchall()
            if not rows:
                raise CaseResourceError("CASE_TRANSFER_RECEIPT_NOT_OBSERVED", 404, event)
            if len(rows) != 1:
                raise CaseResourceError("CASE_TRANSFER_RECEIPT_AMBIGUOUS", 503, event)
            task_id, kind, payload, author = rows[0]
            if task_id != task or kind != "TRANSFERRED" or author != actor:
                raise CaseResourceError("CASE_TRANSFER_ORIGINAL_ACTOR_REQUIRED", 403, event)
            if hasattr(payload, "read"):
                payload = payload.read()
            if not isinstance(payload, str) or len(payload) > 3900:
                raise ValueError("Bounded existing CASE event required")
            request = CasePickTransferRequest.model_validate(ast.literal_eval(payload))
            if request.actor != actor or request.offline_event_id != event:
                raise ValueError("Original event identity mismatch")
            return {"case_pick_task_id": task, "status": "TRANSFERRED", "offline_event_id": event,
                    "actor": actor, "outcome_confirmed": True, "source": "IMMUTABLE_TRANSFERRED_EVENT",
                    "request": request.model_dump(mode="json", exclude={"actor"})}
    except oracledb.DatabaseError as error:
        code = error.args[0].code
        raise CaseResourceError("CASE_TRANSFER_RECEIPT_FORBIDDEN" if code == 20882 else
            "CASE_TRANSFER_RECEIPT_UNAVAILABLE", 403 if code == 20882 else 503, event) from error
    except (ValueError, TypeError, SyntaxError, RecursionError) as error:
        raise CaseResourceError("CASE_TRANSFER_RECEIPT_INVALID", 503, event) from error
