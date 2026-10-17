"""One caller-owned native transaction, validated immutable receipt before gateway commit."""
import hashlib
import json
from datetime import datetime
from typing import Any
import oracledb
from pydantic import ValidationError
from ...platform.public import read_oracle_json
from ..contracts_picker_time import PickerTimeAck, PickerTimeCommand, PickerTimeError, PickerTimeState, PickerTimeValidator, PickerTimeWindow


def picker_time_canonical(body: PickerTimeCommand) -> str:
    return json.dumps(body.model_dump(mode="json"), ensure_ascii=False, sort_keys=True, separators=(",", ":"))


class PickerTimeNative:
    def __init__(self, gateway: Any) -> None:
        self.gateway = gateway

    def _call(self, method: str, args: list[Any], actor: str, readonly: bool,
              validate: PickerTimeValidator, operation: str | None = None) -> dict[str, Any]:
        try:
            with self.gateway.transaction("Picker confirmed actual-time " + method) as cursor:
                if readonly:
                    cursor.execute("set transaction read only")
                output = cursor.var(oracledb.DB_TYPE_CLOB)
                cursor.callproc("RRL_PICKER_TIME_API." + method, [actor, *args, output])
                data = read_oracle_json(output.getvalue())
                validate(data)
                return data
        except oracledb.DatabaseError as error:
            code = error.args[0].code
            status = 403 if code == 20882 else 404 if code == 1403 else 409 if 20800 <= code <= 20999 else 503
            raise PickerTimeError(str(error.args[0]).split("\n", 1)[0], status, operation) from error
        except (ValueError, ValidationError, TypeError, KeyError) as error:
            raise PickerTimeError("PICKER_TIME_NATIVE_ACK_INVALID", 503, operation) from error

    def current(self, actor: str) -> dict[str, Any]:
        def validate(data: dict[str, Any]) -> None:
            state = PickerTimeState.model_validate(data)
            if state.operator_id != actor:
                raise ValueError("Original operator required")
        return self._call("current_state", [], actor, True, validate)

    def command(self, body: PickerTimeCommand, actor: str) -> dict[str, Any]:
        wire = picker_time_canonical(body)
        digest = hashlib.sha256(wire.encode("utf-8")).hexdigest().upper()
        def validate(data: dict[str, Any]) -> None:
            ack = PickerTimeAck.model_validate(data)
            if (ack.operation_id, ack.actor, ack.action, ack.resource_session_id, ack.request_sha256) != (
                    body.operation_id, actor, body.action, body.resource_session_id, digest):
                raise ValueError("Original command acknowledgement required")
            if ack.outcome == "APPLIED":
                if ack.before_version != body.expected_version or ack.after_version != body.expected_version + 1:
                    raise ValueError("Original expected version required")
                expected = {"ACTUAL_SHIFT_START": ("OPEN", "IDLE"), "ACTUAL_SHIFT_FINISH": ("OFF", "IDLE"),
                            "WORK_START": ("OPEN", "WORK"), "PAUSE": ("OPEN", "PAUSED"),
                            "RESUME": ("OPEN", "WORK"), "WORK_FINISH": ("OPEN", "IDLE")}[body.action]
                if (ack.state.shift_state, ack.state.work_state) != expected:
                    raise ValueError("Original transition state required")
                if body.action != "ACTUAL_SHIFT_FINISH" and ack.state.resource_session_id != body.resource_session_id:
                    raise ValueError("Original physical session required")
                if body.action in ("WORK_START", "PAUSE", "RESUME") and (
                        ack.state.source_kind, ack.state.source_id) != (body.source_kind, body.source_id):
                    raise ValueError("Original work source required")
        return self._call("execute_command", [wire], actor, False, validate, body.operation_id)

    def receipt(self, operation: str, actor: str) -> dict[str, Any]:
        def validate(data: dict[str, Any]) -> None:
            ack = PickerTimeAck.model_validate(data)
            if ack.operation_id != operation or ack.actor != actor:
                raise ValueError("Original actor receipt required")
        return self._call("receipt", [operation], actor, True, validate, operation)

    def window(self, start: datetime, finish: datetime, actor: str) -> dict[str, Any]:
        def validate(data: dict[str, Any]) -> None:
            if PickerTimeWindow.model_validate(data).operator_id != actor:
                raise ValueError("Original operator snapshot required")
        return self._call("read_window", [start.isoformat(timespec="microseconds"), finish.isoformat(timespec="microseconds")],
                          actor, True, validate)
