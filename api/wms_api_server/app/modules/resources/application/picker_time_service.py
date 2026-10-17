"""Project only explicit closed native spans; manual work never certifies all picking."""
from datetime import datetime, timedelta, timezone
from hashlib import sha256
from typing import Any
from ..contracts_picker_time import PickerTimeCommand, PickerTimeError, PickerTimeNativePort, PickerTimeWindow, aware_instant
from ..domain.picker_time_denominators import ConfirmedTimeCoverage, ConfirmedTimeInterval, TimeDenominator, picker_time_denominators


def denominator_json(value: TimeDenominator) -> dict[str, Any]:
    return {"status": value.status, "hours": None if value.hours is None else str(value.hours),
            "duration_microseconds": value.duration_microseconds, "reasons": list(value.reasons)}


class PickerTimeService:
    def __init__(self, native: PickerTimeNativePort) -> None:
        self.native = native

    def current(self, actor: str) -> dict[str, Any]:
        return self.native.current(actor)

    def command(self, body: PickerTimeCommand, actor: str) -> dict[str, Any]:
        return self.native.command(body, actor)

    def receipt(self, operation: str, actor: str) -> dict[str, Any]:
        return self.native.receipt(operation, actor)

    def window(self, start: datetime, finish: datetime, actor: str) -> dict[str, Any]:
        if start.utcoffset() is None or finish.utcoffset() is None:
            raise PickerTimeError("PICKER_TIME_WINDOW_BOUND_31_DAYS", 422)
        start, finish = start.astimezone(timezone.utc), finish.astimezone(timezone.utc)
        if finish <= start or finish - start > timedelta(days=31):
            raise PickerTimeError("PICKER_TIME_WINDOW_BOUND_31_DAYS", 422)
        raw = self.native.window(start, finish, actor)
        try:
            return project_window(raw, start, finish, actor)
        except (ValueError, TypeError, KeyError) as error:
            raise PickerTimeError("PICKER_TIME_WINDOW_ACK_INVALID", 503) from error


def project_window(raw: dict[str, Any], start: datetime, finish: datetime, actor: str) -> dict[str, Any]:
    data = PickerTimeWindow.model_validate(raw)
    if data.operator_id != actor or aware_instant(data.report_start) != start or aware_instant(data.report_finish) != finish:
        raise PickerTimeError("PICKER_TIME_WINDOW_IDENTITY_INVALID", 503)
    observed = aware_instant(data.as_of)
    facts = [ConfirmedTimeInterval(sha256(item.span_id.encode("utf-8")).hexdigest(), actor, item.kind, aware_instant(item.start_at),
                                   aware_instant(item.finish_at), True) for item in data.spans]
    coverage = [ConfirmedTimeCoverage("SHIFT:" + sha256(item.span_id.encode("utf-8")).hexdigest(), actor, "ACTUAL_SHIFT", aware_instant(item.start_at),
                                     aware_instant(item.finish_at), observed, True, True)
                for item in data.spans if item.kind == "ACTUAL_SHIFT"]
    result = picker_time_denominators(actor, start, finish, observed, facts, coverage)
    return {**raw, "denominators": {"assembly": denominator_json(result.assembly),
            "actual_shift": denominator_json(result.actual_shift)}, "formula_version": result.formula_version,
            "source_limitations": ["WORK_OWNER_INSTRUMENTATION_NOT_CERTIFIED", "OPEN_INTERVALS_NOT_PROJECTED",
                                   "NO_LEGACY_CLOCK_BACKFILL", "NUMERATORS_NOT_IMPLEMENTED"]}
