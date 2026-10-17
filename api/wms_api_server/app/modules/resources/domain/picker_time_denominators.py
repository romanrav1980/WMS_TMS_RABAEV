"""Approved picker time denominators; confirmed backend facts only, no runtime source adapter.

WORK minus explicit PAUSE is independent of ACTUAL_SHIFT (which retains pauses).
Intervals are half-open UTC instants; absent completeness never means zero activity.
"""
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from decimal import Decimal, localcontext
from typing import Literal, TypeVar
from .workload_intervals import union_hours

IntervalKind = Literal["ACTUAL_SHIFT", "WORK", "PAUSE"]
Span = tuple[datetime, datetime]
MAX_INTERVALS = 5000
MAX_COVERAGE = 5000
FORMULA_VERSION = "PICKER_TIME_V1"
_KINDS: tuple[IntervalKind, ...] = ("ACTUAL_SHIFT", "WORK", "PAUSE")


def _identifier(value: str, label: str) -> None:
    if not isinstance(value, str) or not value or value != value.strip() or len(value) > 100:
        raise ValueError(label + "_IDENTITY_REQUIRED")


def _utc(value: datetime) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("CONFIRMED_AWARE_INSTANT_REQUIRED")
    result = value.astimezone(timezone.utc)
    restored = result.astimezone(value.tzinfo)
    if restored.replace(tzinfo=None) != value.replace(tzinfo=None) or restored.utcoffset() != value.utcoffset():
        raise ValueError("NONEXISTENT_LOCAL_INSTANT")
    return result


def _normalize_span(start: datetime, finish: datetime) -> Span:
    left, right = _utc(start), _utc(finish)
    if right <= left:
        raise ValueError("POSITIVE_CONFIRMED_INTERVAL_REQUIRED")
    return left, right


@dataclass(frozen=True)
class ConfirmedTimeInterval:
    fact_id: str
    operator_id: str
    kind: IntervalKind
    start: datetime
    finish: datetime
    confirmed: Literal[True]

    def __post_init__(self) -> None:
        _identifier(self.fact_id, "FACT")
        _identifier(self.operator_id, "OPERATOR")
        if not isinstance(self.kind, str) or self.kind not in _KINDS or self.confirmed is not True:
            raise ValueError("CONFIRMED_ACTUAL_TIME_KIND_REQUIRED")
        start, finish = _normalize_span(self.start, self.finish)
        object.__setattr__(self, "start", start)
        object.__setattr__(self, "finish", finish)


@dataclass(frozen=True)
class ConfirmedTimeCoverage:
    """Backend attestation that this kind's fact stream is complete at one as_of snapshot."""
    coverage_id: str
    operator_id: str
    kind: IntervalKind
    start: datetime
    finish: datetime
    as_of: datetime
    complete: bool
    confirmed: Literal[True]

    def __post_init__(self) -> None:
        _identifier(self.coverage_id, "COVERAGE")
        _identifier(self.operator_id, "OPERATOR")
        if not isinstance(self.kind, str) or self.kind not in _KINDS or self.confirmed is not True or type(self.complete) is not bool:
            raise ValueError("CONFIRMED_EXPLICIT_COVERAGE_REQUIRED")
        start, finish = _normalize_span(self.start, self.finish)
        object.__setattr__(self, "start", start)
        object.__setattr__(self, "finish", finish)
        object.__setattr__(self, "as_of", _utc(self.as_of))


@dataclass(frozen=True)
class TimeDenominator:
    status: Literal["AVAILABLE", "NO_DATA"]
    hours: Decimal | None
    duration_microseconds: int | None
    reasons: tuple[str, ...]


@dataclass(frozen=True)
class PickerTimeDenominators:
    operator_id: str
    report_start: datetime
    report_finish: datetime
    as_of: datetime
    effective_window: Span | None
    assembly: TimeDenominator
    actual_shift: TimeDenominator
    formula_version: str = FORMULA_VERSION


def _clip(span: Span, window: Span) -> Span | None:
    left, right = max(span[0], window[0]), min(span[1], window[1])
    return (left, right) if right > left else None


def _union(spans: Sequence[Span]) -> list[Span]:
    result: list[Span] = []
    for start, finish in sorted(set(spans)):
        if result and start <= result[-1][1]:
            result[-1] = (result[-1][0], max(result[-1][1], finish))
        else:
            result.append((start, finish))
    return result


def _subtract(work: Sequence[Span], pauses: Sequence[Span]) -> list[Span]:
    """Both inputs already merged: linear sweep avoids per-pause/per-work cross product."""
    result: list[Span] = []
    pause_index = 0
    for start, finish in work:
        cursor = start
        while pause_index < len(pauses) and pauses[pause_index][1] <= cursor:
            pause_index += 1
        index = pause_index
        while index < len(pauses) and pauses[index][0] < finish:
            left, right = pauses[index]
            if left > cursor:
                result.append((cursor, min(left, finish)))
            cursor = max(cursor, right)
            if cursor >= finish:
                break
            index += 1
        if cursor < finish:
            result.append((cursor, finish))
        pause_index = index
    return result


_Record = TypeVar("_Record", ConfirmedTimeInterval, ConfirmedTimeCoverage)


def _deduplicate(records: Sequence[_Record], operator: str, coverage: bool) -> list[_Record]:
    expected_type = ConfirmedTimeCoverage if coverage else ConfirmedTimeInterval
    result: dict[str, _Record] = {}
    for record in records:
        if not isinstance(record, expected_type) or record.operator_id != operator:
            raise ValueError("ONE_OPERATOR_CONFIRMED_TIME_RECORDS_REQUIRED")
        identity = record.coverage_id if isinstance(record, ConfirmedTimeCoverage) else record.fact_id
        if identity in result and result[identity] != record:
            raise ValueError("COVERAGE_ID_CONFLICT" if coverage else "FACT_ID_CONFLICT")
        result[identity] = record
    return list(result.values())


def _coverage_reason(kind: IntervalKind, records: Sequence[ConfirmedTimeCoverage], window: Span,
                     as_of: datetime) -> str | None:
    relevant = [record for record in records if record.kind == kind and _clip((record.start, record.finish), window)]
    if any(record.as_of != as_of for record in relevant):
        return kind + "_COVERAGE_AS_OF_MISMATCH"
    if any(not record.complete for record in relevant):
        return kind + "_COVERAGE_INCOMPLETE"
    merged = _union([(record.start, record.finish) for record in relevant])
    if not any(start <= window[0] and finish >= window[1] for start, finish in merged):
        return kind + "_COVERAGE_INCOMPLETE"
    return None


def _amount(spans: Sequence[Span], reasons: tuple[str, ...] = ()) -> TimeDenominator:
    if reasons:
        return TimeDenominator("NO_DATA", None, None, reasons)
    microseconds = 0
    for start, finish in spans:
        delta = finish - start
        microseconds += (delta.days * 86400 + delta.seconds) * 1000000 + delta.microseconds
    if microseconds == 0:
        return TimeDenominator("NO_DATA", None, 0, ("ZERO_DURATION",))
    with localcontext() as context:
        context.prec = 60
        value = union_hours(list(spans))
    return TimeDenominator("AVAILABLE", value, microseconds, ())


def picker_time_denominators(operator_id: str, report_start: datetime, report_finish: datetime,
                             as_of: datetime, intervals: Sequence[ConfirmedTimeInterval],
                             coverage: Sequence[ConfirmedTimeCoverage]) -> PickerTimeDenominators:
    """Calculate two denominators only; never derives attendance, picking rows, boxes or rates.

    as_of is an explicit reporting cutoff. Confirmed spans can cross it, but no future
    part is counted. Coverage must attest the effective window at exactly this snapshot.
    Completeness is independent per kind, including an explicitly empty PAUSE stream.
    """
    _identifier(operator_id, "OPERATOR")
    start, finish = _normalize_span(report_start, report_finish)
    observed = _utc(as_of)
    if finish - start > timedelta(days=366):
        raise ValueError("REPORT_WINDOW_BOUND_366_DAYS")
    if len(intervals) > MAX_INTERVALS or len(coverage) > MAX_COVERAGE:
        raise ValueError("CONFIRMED_TIME_INPUT_BOUND_EXCEEDED")
    facts = _deduplicate(intervals, operator_id, False)
    attestations = _deduplicate(coverage, operator_id, True)
    end = min(finish, observed)
    if end <= start:
        unavailable = _amount([], ("WINDOW_NOT_OBSERVED",))
        return PickerTimeDenominators(operator_id, start, finish, observed, None, unavailable, unavailable)
    window = (start, end)
    spans: dict[str, list[Span]] = {kind: [] for kind in _KINDS}
    for fact in facts:
        clipped = _clip((fact.start, fact.finish), window)
        if clipped is not None:
            spans[fact.kind].append(clipped)
    merged = {kind: _union(values) for kind, values in spans.items()}
    reasons = {kind: _coverage_reason(kind, attestations, window, observed) for kind in _KINDS}
    work_reasons = tuple(reasons[kind] for kind in ("WORK", "PAUSE") if reasons[kind] is not None)
    shift_reasons = (reasons["ACTUAL_SHIFT"],) if reasons["ACTUAL_SHIFT"] is not None else ()
    assembly = _amount(_subtract(merged["WORK"], merged["PAUSE"]), work_reasons)
    actual_shift = _amount(merged["ACTUAL_SHIFT"], shift_reasons)
    return PickerTimeDenominators(operator_id, start, finish, observed, window, assembly, actual_shift)


def registered_time_denominators(operator_id: str, report_start: datetime, report_finish: datetime,
                                 as_of: datetime, intervals: Sequence[ConfirmedTimeInterval]) -> PickerTimeDenominators:
    """Totals of explicitly registered facts; never attests completeness of all work."""
    _identifier(operator_id, "OPERATOR")
    start, finish = _normalize_span(report_start, report_finish)
    observed = _utc(as_of)
    if finish - start > timedelta(days=31) or len(intervals) > MAX_INTERVALS:
        raise ValueError("REGISTERED_TIME_WINDOW_BOUND")
    facts = _deduplicate(intervals, operator_id, False)
    end = min(finish, observed)
    if end <= start:
        missing = _amount([], ("WINDOW_NOT_OBSERVED",))
        return PickerTimeDenominators(operator_id, start, finish, observed, None, missing, missing)
    window = start, end
    groups = {kind: _union([clipped for fact in facts if fact.kind == kind
        if (clipped := _clip((fact.start, fact.finish), window)) is not None]) for kind in _KINDS}
    return PickerTimeDenominators(operator_id, start, finish, observed, window,
        _amount(_subtract(groups["WORK"], groups["PAUSE"])), _amount(groups["ACTUAL_SHIFT"]),
        "REGISTERED_PICKER_TIME_V1")
