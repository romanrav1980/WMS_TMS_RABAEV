"""Explicit self-confirmed actual-time commands; never a browser attendance assertion."""
from collections.abc import Callable
from datetime import datetime
from typing import Any, Literal, Protocol, Self
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

PickerTimeAction = Literal["ACTUAL_SHIFT_START", "ACTUAL_SHIFT_FINISH", "WORK_START", "PAUSE", "RESUME", "WORK_FINISH"]
PickerTimeSource = Literal["CASE_PICK_TASK", "WAREHOUSE_TASK"]


class PickerTimeError(Exception):
    def __init__(self, code: str, status: int = 503, operation_id: str | None = None) -> None:
        super().__init__(code)
        self.code, self.status, self.operation_id = code, status, operation_id


def aware_instant(value: str) -> datetime:
    result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if result.utcoffset() is None:
        raise ValueError("Confirmed aware instant required")
    return result


class PickerTimeCommand(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    operation_id: str = Field(min_length=1, max_length=100, pattern=r"^[A-Za-z0-9_.:-]+$")
    action: PickerTimeAction
    expected_version: int = Field(ge=0, le=9007199254740991)
    resource_session_id: int = Field(gt=0, le=9007199254740991)
    source_kind: PickerTimeSource | None = None
    source_id: int | None = Field(default=None, gt=0, le=9007199254740991)
    reason: str = Field(min_length=8, max_length=500)

    @model_validator(mode="after")
    def explicit_source(self) -> Self:
        if len(self.reason.strip()) < 8:
            raise ValueError("Explicit meaningful reason required")
        shift = self.action in ("ACTUAL_SHIFT_START", "ACTUAL_SHIFT_FINISH")
        if shift and (self.source_kind is not None or self.source_id is not None):
            raise ValueError("Actual shift is bound to the native resource session")
        if not shift and (self.source_kind is None or self.source_id is None):
            raise ValueError("Explicit assigned work identity required")
        return self


class PickerTimeState(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    operator_id: str = Field(min_length=1, max_length=100)
    stream_version: int = Field(ge=0)
    shift_state: Literal["OFF", "OPEN"]
    work_state: Literal["IDLE", "WORK", "PAUSED"]
    warehouse_id: int | None = Field(ge=1)
    resource_session_id: int | None = Field(ge=1)
    resource_id: int | None = Field(ge=1)
    source_kind: PickerTimeSource | None
    source_id: int | None = Field(ge=1)
    shift_started_at: str | None
    work_started_at: str | None
    pause_started_at: str | None
    last_event_at: str | None
    work_coverage_certified: Literal[False]
    source_mode: Literal["MANUAL_CONFIRMED"]

    @field_validator("work_coverage_certified", mode="before")
    @classmethod
    def uncertified_work(cls, value: Any) -> Any:
        if value is not False:
            raise ValueError("Manual work is never certified complete")
        return value

    @model_validator(mode="after")
    def consistent_state(self) -> Self:
        for value in (self.shift_started_at, self.work_started_at, self.pause_started_at, self.last_event_at):
            if value is not None:
                aware_instant(value)
        if self.shift_state == "OFF" and (self.work_state != "IDLE" or any(value is not None for value in (
                self.shift_started_at, self.warehouse_id, self.resource_session_id, self.resource_id))):
            raise ValueError("Closed presence cannot retain open work")
        if self.shift_state == "OPEN" and (self.shift_started_at is None or self.resource_session_id is None or self.warehouse_id is None or self.resource_id is None):
            raise ValueError("Open presence requires native session and aware start")
        if self.work_state == "IDLE":
            if any(value is not None for value in (self.work_started_at, self.pause_started_at, self.source_kind, self.source_id)):
                raise ValueError("Idle work cannot retain an open source")
        elif self.work_started_at is None or self.source_kind is None or self.source_id is None:
            raise ValueError("Open work requires a source and aware start")
        if (self.work_state == "PAUSED") != (self.pause_started_at is not None):
            raise ValueError("Pause state requires exactly one open pause")
        if (self.stream_version == 0) != (self.last_event_at is None):
            raise ValueError("Only untracked streams have no last event")
        instants = [aware_instant(value) for value in (self.shift_started_at, self.work_started_at,
                    self.pause_started_at, self.last_event_at) if value is not None]
        if any(right < left for left, right in zip(instants, instants[1:])):
            raise ValueError("Actual state clocks must be monotonic")
        return self


class PickerTimeAck(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    operation_id: str
    actor: str
    action: PickerTimeAction
    resource_session_id: int = Field(gt=0)
    warehouse_id: int = Field(gt=0)
    request_sha256: str = Field(pattern=r"^[A-F0-9]{64}$")
    outcome: Literal["APPLIED", "REJECTED"]
    outcome_confirmed: Literal[True]
    changed: bool
    may_create_corrected_operation: bool
    error_code: str | None
    stock_posted: Literal[False]
    event_at: str | None
    before_version: int = Field(ge=0)
    after_version: int = Field(ge=0)
    state: PickerTimeState

    @field_validator("outcome_confirmed", "stock_posted", mode="before")
    @classmethod
    def strict_native_boolean(cls, value: Any) -> Any:
        if type(value) is not bool:
            raise ValueError("Explicit native boolean required")
        return value

    @model_validator(mode="after")
    def final_receipt(self) -> Self:
        rejected = self.outcome == "REJECTED"
        if self.state.operator_id != self.actor or self.state.stream_version != self.after_version:
            raise ValueError("Original operator stream required")
        if rejected:
            if self.changed or not self.error_code or not self.error_code.strip() or self.event_at is not None or self.after_version != self.before_version:
                raise ValueError("Rejected time command cannot create a fact")
        else:
            if not self.changed or self.error_code is not None or self.event_at is None or self.after_version != self.before_version + 1:
                raise ValueError("Applied time command requires one native transition")
            aware_instant(self.event_at)
            if self.state.last_event_at != self.event_at:
                raise ValueError("Acknowledged event must be current at the transition")
        if self.may_create_corrected_operation != rejected:
            raise ValueError("Corrected operation requires a durable rejection")
        return self


class PickerTimeSpan(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    span_id: str
    kind: Literal["ACTUAL_SHIFT", "WORK", "PAUSE"]
    operator_id: str
    warehouse_id: int = Field(gt=0)
    resource_session_id: int = Field(gt=0)
    source_kind: Literal["RESOURCE_SESSION", "CASE_PICK_TASK", "WAREHOUSE_TASK"]
    source_id: int = Field(gt=0)
    start_at: str
    finish_at: str
    start_operation_id: str
    finish_operation_id: str
    source_mode: Literal["MANUAL_CONFIRMED"]

    @model_validator(mode="after")
    def closed_aware_span(self) -> Self:
        if aware_instant(self.finish_at) <= aware_instant(self.start_at):
            raise ValueError("Positive closed actual span required")
        if (self.kind == "ACTUAL_SHIFT") != (self.source_kind == "RESOURCE_SESSION"):
            raise ValueError("Presence and work sources are distinct")
        return self


class PickerTimeWindow(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    operator_id: str
    report_start: str
    report_finish: str
    as_of: str
    state: PickerTimeState
    spans: list[PickerTimeSpan] = Field(max_length=5000)
    work_coverage_certified: Literal[False]
    actual_shift_coverage: Literal["CLOSED_CONFIRMED_WINDOWS_ONLY"]
    snapshot: Literal["ORACLE_READ_ONLY"]

    @field_validator("work_coverage_certified", mode="before")
    @classmethod
    def uncertified_work(cls, value: Any) -> Any:
        if value is not False:
            raise ValueError("Manual work is never certified complete")
        return value

    @model_validator(mode="after")
    def native_window(self) -> Self:
        start, finish, observed = map(aware_instant, (self.report_start, self.report_finish, self.as_of))
        if finish <= start or self.state.operator_id != self.operator_id:
            raise ValueError("Original positive operator window required")
        if any(item.operator_id != self.operator_id or aware_instant(item.finish_at) > observed for item in self.spans):
            raise ValueError("Only this operator's already-closed facts are admitted")
        if len({item.span_id for item in self.spans}) != len(self.spans):
            raise ValueError("Duplicate native span identity")
        return self


class PickerTimeNativePort(Protocol):
    def current(self, actor: str) -> dict[str, Any]: ...
    def command(self, body: PickerTimeCommand, actor: str) -> dict[str, Any]: ...
    def receipt(self, operation: str, actor: str) -> dict[str, Any]: ...
    def window(self, start: datetime, finish: datetime, actor: str) -> dict[str, Any]: ...


class PickerTimePort(PickerTimeNativePort, Protocol):
    pass


def picker_time_service() -> PickerTimePort:
    raise RuntimeError("Picker actual-time source is not wired")


PickerTimeValidator = Callable[[dict[str, Any]], None]
