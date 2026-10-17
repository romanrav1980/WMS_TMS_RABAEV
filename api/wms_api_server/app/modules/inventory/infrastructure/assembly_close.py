"""Thin session binding; existing CASE close owner retains quantity and journal rules."""
from collections.abc import Callable
from typing import Any
import oracledb
from fastapi import HTTPException
from ...platform.public import read_oracle_json
from ..contracts_assembly_close import AssemblyCloseInput
from ..contracts_case_current_close import CaseCurrentCloseInput
from .case_current_close import CaseCurrentClose

class AssemblyClose:
    def __init__(self, gateway: Any, assert_scope: Callable[[Any, int, str, str], None]) -> None:
        self.gateway, self.assert_scope = gateway, assert_scope

    def _session(self, cursor: Any, session: str, actor: str) -> dict[str, Any]:
        output = cursor.var(oracledb.DB_TYPE_CLOB)
        cursor.callproc("RRL_ASSEMBLY_SCALE_API.read_session", [session, actor, output])
        return read_oracle_json(output.getvalue())

    def close(self, session: str, body: AssemblyCloseInput, actor: str) -> dict[str, Any]:
        try:
            with self.gateway.transaction("Assembly close current session") as cursor:
                cursor.execute("set transaction read only")
                current = self._session(cursor, session, actor)
            task = int(current["task_id"])
            def bound_scope(cursor: Any, actual_task: int, actual_actor: str, permission: str) -> None:
                actual = self._session(cursor, session, actual_actor)
                if actual["task_id"] != actual_task or actual["operator_id"] != actual_actor:
                    raise HTTPException(403, "ASSEMBLY_CLOSE_SESSION_SCOPE_CHANGED")
                self.assert_scope(cursor, actual_task, actual_actor, permission)
            request = CaseCurrentCloseInput(**body.model_dump())
            result = CaseCurrentClose(self.gateway).close(task, request, actor, assert_binding=bound_scope)
            return dict(session_id=session, **result)
        except oracledb.DatabaseError as exc:
            code = exc.args[0].code
            status = 403 if code == 20882 else 404 if code == 1403 else 409 if 20800 <= code <= 20999 else 503
            raise HTTPException(status, dict(code="ASSEMBLY_CLOSE_NATIVE_REJECTED" if status < 500 else "ASSEMBLY_CLOSE_OUTCOME_UNCERTAIN", message=str(exc.args[0]).split("\n",1)[0], read_before_retry=True)) from exc
