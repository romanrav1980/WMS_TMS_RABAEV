"""Narrow native admission; original close validations, effect and journal stay authoritative."""
from contextlib import contextmanager
from collections.abc import Iterator, Callable
from typing import Any
import oracledb
from fastapi import HTTPException
from ..contracts_case_current_close import CaseCurrentCloseInput
from ..contracts_case_close import CaseCarrierCloseRequest
from .case_carrier_close import close_case_carrier


class CaseCurrentClose:
    def __init__(self, gateway: Any) -> None:
        self.gateway = gateway

    def close(self, task: int, body: CaseCurrentCloseInput, actor: str,
              assert_binding: Callable[[Any, int, str, str], None] | None = None) -> dict[str, Any]:
        @contextmanager
        def metadata(gateway: Any, purpose: str, actual_actor: str, permission: str) -> Iterator[Any]:
            with gateway.transaction(purpose) as cursor:
                begun = False
                try:
                    cursor.callproc("RRL_CASE_LIFECYCLE_API.begin_close", [task, actual_actor])
                    begun = True
                    yield cursor
                finally:
                    if begun:
                        cursor.callproc("RRL_CASE_LIFECYCLE_API.end_close")

        def current(cursor: Any, actual_task: int, actual_actor: str, permission: str) -> None:
            cursor.callproc("RRL_CASE_LIFECYCLE_API.task_current_scope", [actual_task, actual_actor])
            if assert_binding is not None:
                assert_binding(cursor, actual_task, actual_actor, permission)

        def new_close(cursor: Any, actual_task: int, actual_actor: str) -> None:
            cursor.callproc("RRL_CASE_LIFECYCLE_API.assert_new_close", [actual_task, actual_actor])

        def validate_result(result: Any) -> None:
            if (not isinstance(result, dict) or set(result) != {"status", "content_version", "already_closed", "physical_stock_changed"}
                    or result.get("physical_stock_changed") is not False or result.get("status") not in
                    {"WAIT_CONTROL", "CONTROL_IN_PROGRESS", "CONTROLLED", "READY_TO_SHIP", "SHIPPED"}
                    or type(result.get("content_version")) is not int or result["content_version"] < 0
                    or type(result.get("already_closed")) is not bool):
                raise HTTPException(503, dict(code="CASE_CURRENT_CLOSE_ACK_INVALID", operation_id=body.operation_id,
                    outcome_confirmed=False, retry_same_operation_id=True))

        request = CaseCarrierCloseRequest(**body.model_dump(), actor=actor)
        try:
            result = close_case_carrier(self.gateway, task, request, current,
                                        metadata_context=metadata, assert_new=new_close, validate_result=validate_result)
        except oracledb.DatabaseError as error:
            code = getattr(error.args[0], "code", 0)
            status = 403 if code == 20882 else 404 if code == 1403 else 409 if 20800 <= code <= 20999 else 503
            raise HTTPException(status, dict(code="CASE_CURRENT_CLOSE_REJECTED" if status < 500 else "CASE_CURRENT_CLOSE_OUTCOME_UNCERTAIN",
                operation_id=body.operation_id, message=str(error.args[0]).split("\n", 1)[0],
                outcome_confirmed=False, retry_same_operation_id=True)) from error
        validate_result(result)
        return dict(operation_id=body.operation_id, case_pick_task_id=task, **result)
