"""Native metadata owner, one transaction and exact receipt; no stock posting client."""
import hashlib
import json
from collections.abc import Callable
from typing import Any
import oracledb
from pydantic import ValidationError
from ..contracts_task_resource import TaskResourceAck, TaskResourceCommand, TaskResourceError, TaskResourceState


def canonical(body: TaskResourceCommand) -> str:
    return json.dumps(body.model_dump(mode="json"), sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def oracle_json(value: Any) -> dict[str, Any]:
    if hasattr(value, "read"):
        value = value.read()
    return value if isinstance(value, dict) else json.loads(value)


class TaskResourceCommands:
    def __init__(self, gateway: Any) -> None:
        self.gateway = gateway

    def _call(self, method: str, args: list[Any], readonly: bool,
              validate: Callable[[dict[str, Any]], None], operation: str | None = None) -> dict[str, Any]:
        try:
            with self.gateway.transaction("Warehouse resource " + method) as cursor:
                if readonly:
                    cursor.execute("set transaction read only")
                output = cursor.var(oracledb.DB_TYPE_CLOB)
                cursor.callproc("RRL_WTASK_ASSIGN_API." + method, [*args, output])
                data = oracle_json(output.getvalue())
                validate(data)
                return data
        except oracledb.DatabaseError as error:
            code = error.args[0].code
            status = 403 if code == 20882 else 404 if code == 1403 else 409 if 20800 <= code <= 20999 else 503
            raise TaskResourceError(str(error.args[0]).split("\n", 1)[0], status, operation) from error
        except (ValueError, ValidationError, TypeError, KeyError) as error:
            raise TaskResourceError("WTASK_RESOURCE_ACK_INVALID", 503, operation) from error

    def context(self, task: int, actor: str, target: str) -> dict[str, Any]:
        def validate(data: dict[str, Any]) -> None:
            TaskResourceState.model_validate({k: v for k, v in data.items() if k not in {"current_actor", "target"}})
            if (data.get("task_id"), data.get("current_actor"), data.get("target")) != (task, actor, target):
                raise ValueError("Current resource context identity mismatch")
        return self._call("task_context", [task, actor, target], True, validate)

    def command(self, task: int, body: TaskResourceCommand, actor: str) -> dict[str, Any]:
        wire = canonical(body)
        digest = hashlib.sha256(wire.encode("utf-8")).hexdigest().upper()
        def validate(data: dict[str, Any]) -> None:
            ack = TaskResourceAck.model_validate(data)
            if (ack.operation_id, ack.task_id, ack.action, ack.actor, ack.target, ack.request_sha256) != (
                    body.operation_id, task, body.action, actor, body.target, digest):
                raise ValueError("Original command acknowledgement mismatch")
        return self._call("execute_command", [task, wire, actor], False, validate, body.operation_id)

    def receipt(self, operation: str, actor: str) -> dict[str, Any]:
        def validate(data: dict[str, Any]) -> None:
            ack = TaskResourceAck.model_validate(data)
            if (ack.operation_id, ack.actor) != (operation, actor):
                raise ValueError("Receipt identity mismatch")
        return self._call("receipt", [operation, actor], True, validate, operation)
