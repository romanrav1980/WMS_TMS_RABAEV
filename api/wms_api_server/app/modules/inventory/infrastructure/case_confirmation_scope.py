"""Pure CASE preflight shares the current native guard, no permission copy in Python."""
from typing import Any
import json
import oracledb
from ....oracle_gateway import OracleGateway
from ..contracts_case_confirmation import CaseConfirmationAccessError


def authorize_existing_case_confirmation(task: int, line: int, actor: str, gateway: Any | None = None) -> None:
    gateway = gateway if gateway is not None else OracleGateway()
    payload = json.dumps({"command_type": "CASE_PICK_CONFIRM", "source": {"case_task_id": task, "case_line_id": line}},
                         sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    try:
        with gateway.transaction("CASE confirmation current native admission READ ONLY") as cursor:
            cursor.execute("set transaction read only")
            cursor.callproc("RRL_CASE_TASK_ACCESS.assert_command", [payload, actor])
    except oracledb.DatabaseError as exc:
        code = exc.args[0].code
        status = 403 if code == 20882 else 409 if code == 1403 or 20800 <= code <= 20999 else 503
        raise CaseConfirmationAccessError("CASE_CURRENT_EXECUTE_REQUIRED" if status == 403 else "CASE_SOURCE_REJECTED" if status == 409 else "CASE_ACCESS_UNAVAILABLE",
            str(exc.args[0]).split("\n", 1)[0], status) from exc
