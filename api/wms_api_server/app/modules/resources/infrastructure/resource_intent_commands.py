"""Native metadata tombstones; reuse existing canonical command builders."""
import hashlib
import json
from typing import Any, Callable
import oracledb
from pydantic import ValidationError
from ..contracts_case_resource import CaseResourceAck, CaseResourceCommand
from ..contracts_task_resource import TaskResourceAck, TaskResourceCommand
from ..contracts_resource_intents import (ResourceIntentAbandon, ResourceIntentAbandoned,
    ResourceIntentError, ResourceIntentQuery, ResourceIntentResolution)
from .case_resource_commands import canonical as case_canonical, oracle_json
from .task_resource_commands import canonical as task_canonical


def original(body: ResourceIntentAbandon) -> CaseResourceCommand | TaskResourceCommand:
    model = CaseResourceCommand if body.domain == "CASE" else TaskResourceCommand
    command = model.model_validate_json(body.original_wire)
    builder = case_canonical if isinstance(command, CaseResourceCommand) else task_canonical
    if builder(command) != body.original_wire:
        raise ValueError("Original command must retain existing canonical bytes")
    return command


def control_wire(body: ResourceIntentAbandon) -> str:
    original(body)
    return json.dumps(body.model_dump(mode="json"), ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def digest(wire: str) -> str:
    return hashlib.sha256(wire.encode("utf-8")).hexdigest().upper()


def validate_abandoned(data: dict[str, Any], actor: str, operation: str | None = None) -> ResourceIntentAbandoned:
    ack = ResourceIntentAbandoned.model_validate(data)
    model = CaseResourceCommand if ack.domain == "CASE" else TaskResourceCommand
    command = model.model_validate_json(ack.original_wire)
    builder = case_canonical if isinstance(command, CaseResourceCommand) else task_canonical
    target = actor if isinstance(command, CaseResourceCommand) else command.target
    if (ack.actor, ack.original_operation_id, ack.action, ack.target, ack.original_request_sha256,
        ack.original_expected_assignment_version) != (actor, command.operation_id, command.action,
        target, digest(ack.original_wire), command.expected_assignment_version):
        raise ValueError("Original abandonment identity mismatch")
    if builder(command) != ack.original_wire or (operation is not None and ack.operation_id != operation):
        raise ValueError("Abandonment canonical bytes or control operation mismatch")
    return ack


class ResourceIntentCommands:
    def __init__(self, gateway: Any) -> None:
        self.gateway = gateway

    def _call(self, method: str, args: list[Any], readonly: bool,
              validate: Callable[[dict[str, Any]], None], operation: str | None = None) -> dict[str, Any]:
        try:
            with self.gateway.transaction("Resource metadata intent " + method) as cursor:
                if readonly:
                    cursor.execute("set transaction read only")
                output = cursor.var(oracledb.DB_TYPE_CLOB)
                cursor.callproc("RRL_RESOURCE_INTENT_API." + method, [*args, output])
                data = oracle_json(output.getvalue())
                validate(data)
                return data
        except oracledb.DatabaseError as error:
            code = error.args[0].code
            status = 403 if code == 20882 else 404 if code == 1403 else 409 if 20800 <= code <= 20999 else 503
            raise ResourceIntentError(str(error.args[0]).split("\n", 1)[0], status, operation) from error
        except (ValueError, ValidationError, TypeError, KeyError) as error:
            raise ResourceIntentError("RESOURCE_INTENT_ACK_INVALID", 503, operation) from error

    def abandon(self, body: ResourceIntentAbandon, actor: str) -> dict[str, Any]:
        try:
            wire = control_wire(body)
        except ValueError as error:
            raise ResourceIntentError("RESOURCE_INTENT_ORIGINAL_CANONICAL_REQUIRED", 422, body.operation_id) from error
        def validate(data: dict[str, Any]) -> None:
            ack = validate_abandoned(data, actor, body.operation_id)
            if (ack.domain, ack.task_id, ack.original_wire, ack.control_request_sha256) != (
                body.domain, body.task_id, body.original_wire, digest(wire)):
                raise ValueError("Frozen abandonment request mismatch")
        return self._call("abandon", [wire, actor], False, validate, body.operation_id)

    def receipt(self, operation: str, actor: str) -> dict[str, Any]:
        def validate(data: dict[str, Any]) -> None:
            validate_abandoned(data, actor, operation)
        return self._call("describe", [operation, actor], True, validate, operation)

    def resolution(self, query: ResourceIntentQuery, actor: str) -> dict[str, Any]:
        def validate(data: dict[str, Any]) -> None:
            result = ResourceIntentResolution.model_validate(data)
            if (result.domain, result.task_id, result.actor, result.original_operation_id,
                result.original_request_sha256) != (query.domain, query.task_id, actor,
                query.original_operation_id, query.original_request_sha256):
                raise ValueError("Resolution belongs to another original intent")
            if result.original_receipt is not None:
                ack = result.original_receipt
                expected_type = CaseResourceAck if query.domain == "CASE" else TaskResourceAck
                if not isinstance(ack, expected_type):
                    raise ValueError("Recorded receipt belongs to another domain")
                target = actor if query.domain == "CASE" else getattr(ack, "target", None)
                if (ack.actor, ack.task_id, ack.operation_id, ack.action, target, ack.request_sha256) != (
                    actor, query.task_id, query.original_operation_id, query.action, query.target,
                    query.original_request_sha256):
                    raise ValueError("Original recorded receipt mismatch")
            else:
                ack = validate_abandoned(data["abandonment"], actor)
                if (ack.domain, ack.task_id, ack.action, ack.target, ack.original_request_sha256) != (
                    query.domain, query.task_id, query.action, query.target, query.original_request_sha256):
                    raise ValueError("Tombstone belongs to another intent")
        return self._call("resolve", [query.domain, query.task_id, query.original_operation_id,
            query.action, query.target, query.original_request_sha256, actor], True, validate,
            query.original_operation_id)

