"""Pure actual-time rules only; none of these fixtures are runtime/hardware attendance facts."""
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from decimal import Decimal, localcontext
from zoneinfo import ZoneInfo
import pytest
from api.wms_api_server.app.modules.resources.domain.picker_time_denominators import (
    ConfirmedTimeCoverage, ConfirmedTimeInterval, MAX_COVERAGE, MAX_INTERVALS, picker_time_denominators,
)

OPERATOR = "picker-1"
START = datetime(2026, 10, 15, 0, tzinfo=timezone.utc)
FINISH = START + timedelta(hours=8)


def fact(identity, kind, start, finish, operator=OPERATOR):
    return ConfirmedTimeInterval(identity, operator, kind, start, finish, True)


def coverage(kind, identity=None, start=START, finish=FINISH, as_of=FINISH, complete=True):
    return ConfirmedTimeCoverage(identity or kind, OPERATOR, kind, start, finish, as_of, complete, True)


def calculate(facts=(), proofs=None, start=START, finish=FINISH, as_of=FINISH):
    if proofs is None:
        proofs = [coverage(kind, start=start, finish=finish, as_of=as_of) for kind in ("WORK", "PAUSE", "ACTUAL_SHIFT")]
    return picker_time_denominators(OPERATOR, start, finish, as_of, facts, proofs)


def test_registered_pauses_reduce_only_actual_assembly_and_overlaps_are_not_double_hours():
    work = fact("w1", "WORK", START, START + timedelta(hours=5))
    result = calculate([work, work, fact("w2", "WORK", START + timedelta(hours=3), FINISH),
                        fact("s", "ACTUAL_SHIFT", START, FINISH),
                        fact("p1", "PAUSE", START + timedelta(hours=1), START + timedelta(hours=2)),
                        fact("p2", "PAUSE", START + timedelta(minutes=90), START + timedelta(hours=3))])
    assert result.assembly.hours == Decimal(6)
    assert result.actual_shift.hours == Decimal(8)
    assert result.assembly.duration_microseconds == 6 * 3600 * 1000000


def test_work_is_not_silently_intersected_with_shift_or_lost_when_shift_is_unknown():
    result = calculate([fact("w", "WORK", START, FINISH)], [coverage("WORK"), coverage("PAUSE")])
    assert result.assembly.hours == 8
    assert result.actual_shift.status == "NO_DATA" and result.actual_shift.hours is None
    with_short_shift = calculate([fact("w", "WORK", START, FINISH),
                                  fact("s", "ACTUAL_SHIFT", START, START + timedelta(hours=4))])
    assert with_short_shift.assembly.hours == 8 and with_short_shift.actual_shift.hours == 4


def test_missing_pause_coverage_never_means_no_pauses_and_shift_remains_available():
    result = calculate([fact("w", "WORK", START, FINISH), fact("s", "ACTUAL_SHIFT", START, FINISH)],
                       [coverage("WORK"), coverage("ACTUAL_SHIFT")])
    assert result.assembly.reasons == ("PAUSE_COVERAGE_INCOMPLETE",)
    assert result.assembly.hours is None and result.assembly.duration_microseconds is None
    assert result.actual_shift.hours == 8


def test_zero_known_activity_is_no_data_instead_of_a_zero_or_infinite_rate():
    result = calculate()
    assert result.assembly.status == "NO_DATA" and result.assembly.hours is None
    assert result.assembly.duration_microseconds == 0 and result.assembly.reasons == ("ZERO_DURATION",)
    assert result.actual_shift.hours is None


def test_reporting_window_and_as_of_cutoff_are_explicit_and_future_time_is_not_counted():
    observed = START + timedelta(hours=3)
    result = calculate([fact("w", "WORK", START - timedelta(hours=1), FINISH + timedelta(hours=2)),
                        fact("s", "ACTUAL_SHIFT", START, FINISH)], as_of=observed)
    assert result.effective_window == (START, observed)
    assert result.assembly.hours == 3 and result.actual_shift.hours == 3
    assert result.report_finish == FINISH and result.as_of == observed
    future = calculate(as_of=START - timedelta(seconds=1))
    assert future.effective_window is None and future.assembly.reasons == ("WINDOW_NOT_OBSERVED",)


def test_confirmed_night_shift_crosses_midnight_without_calendar_day_splitting():
    start = datetime.fromisoformat("2026-10-14T22:00:00+03:00")
    finish = datetime.fromisoformat("2026-10-15T06:00:00+03:00")
    result = calculate([fact("w", "WORK", start, finish), fact("s", "ACTUAL_SHIFT", start, finish)],
                       start=start, finish=finish, as_of=finish)
    assert result.assembly.hours == 8 and result.actual_shift.hours == 8
    assert result.report_start.tzinfo is timezone.utc


def test_dst_fall_back_uses_elapsed_utc_time_and_distinguishes_repeated_local_hour():
    berlin = ZoneInfo("Europe/Berlin")
    start = datetime(2026, 10, 25, 1, tzinfo=berlin)
    finish = datetime(2026, 10, 25, 4, tzinfo=berlin)
    pause_start = datetime(2026, 10, 25, 2, 15, tzinfo=berlin, fold=0)
    pause_finish = datetime(2026, 10, 25, 2, 45, tzinfo=berlin, fold=1)
    result = calculate([fact("w", "WORK", start, finish), fact("s", "ACTUAL_SHIFT", start, finish),
                        fact("p", "PAUSE", pause_start, pause_finish)], start=start, finish=finish, as_of=finish)
    assert result.actual_shift.hours == 4
    assert result.assembly.hours == Decimal("2.5")


def test_dst_spring_forward_counts_actual_two_hours_and_rejects_nonexistent_wall_clock():
    berlin = ZoneInfo("Europe/Berlin")
    start = datetime(2026, 3, 29, 1, tzinfo=berlin)
    finish = datetime(2026, 3, 29, 4, tzinfo=berlin)
    assert calculate([fact("w", "WORK", start, finish)], start=start, finish=finish, as_of=finish).assembly.hours == 2
    with pytest.raises(ValueError, match="NONEXISTENT"):
        fact("imaginary", "WORK", datetime(2026, 3, 29, 2, 30, tzinfo=berlin), finish)


def test_exact_duplicate_identity_normalizes_offsets_but_conflicting_identity_is_rejected():
    original = fact("w", "WORK", START, FINISH)
    same = fact("w", "WORK", START.astimezone(timezone(timedelta(hours=3))), FINISH)
    assert calculate([original, same]).assembly.hours == 8
    with pytest.raises(ValueError, match="FACT_ID_CONFLICT"):
        calculate([original, replace(original, finish=FINISH - timedelta(seconds=1))])
    proof = coverage("WORK")
    with pytest.raises(ValueError, match="COVERAGE_ID_CONFLICT"):
        calculate([], [proof, replace(proof, complete=False)])


def test_different_fact_ids_for_same_physical_span_and_offset_do_not_double_hours():
    offset = timezone(timedelta(hours=3))
    result = calculate([fact("source-a", "WORK", START, FINISH),
                        fact("source-b", "WORK", START.astimezone(offset), FINISH.astimezone(offset))])
    assert result.assembly.hours == 8
    assert result.assembly.duration_microseconds == 8 * 3600 * 1000000


def test_complete_empty_pause_stream_is_required_and_does_not_need_a_fabricated_pause():
    facts = [fact("w", "WORK", START, FINISH)]
    assert calculate(facts, [coverage("WORK"), coverage("PAUSE")]).assembly.hours == 8
    assert calculate(facts, [coverage("WORK")]).assembly.reasons == ("PAUSE_COVERAGE_INCOMPLETE",)


def test_explicit_incomplete_attestation_is_not_overridden_by_another_coverage_id():
    proofs = [coverage("WORK"), coverage("WORK", "incomplete-overlap", complete=False), coverage("PAUSE")]
    assert calculate([fact("w", "WORK", START, FINISH)], proofs).assembly.reasons == ("WORK_COVERAGE_INCOMPLETE",)


def test_pause_crossing_several_disjoint_work_spans_is_subtracted_once_per_overlap():
    spans = [fact("w1", "WORK", START, START + timedelta(hours=2)),
             fact("w2", "WORK", START + timedelta(hours=4), START + timedelta(hours=6)),
             fact("p", "PAUSE", START + timedelta(hours=1), START + timedelta(hours=5))]
    result = calculate(spans)
    assert result.assembly.hours == 2


def test_adjacent_complete_coverage_merges_but_one_microsecond_gap_is_unknown():
    midpoint = START + timedelta(hours=4)
    proofs = [coverage("WORK", "left", finish=midpoint), coverage("WORK", "right", start=midpoint), coverage("PAUSE")]
    assert calculate([fact("w", "WORK", START, FINISH)], proofs).assembly.hours == 8
    proofs[1] = replace(proofs[1], start=midpoint + timedelta(microseconds=1))
    assert calculate([fact("w", "WORK", START, FINISH)], proofs).assembly.reasons == ("WORK_COVERAGE_INCOMPLETE",)


def test_incomplete_or_different_as_of_coverage_is_no_data_even_with_positive_spans():
    work = fact("w", "WORK", START, FINISH)
    result = calculate([work], [coverage("WORK", complete=False), coverage("PAUSE")])
    assert result.assembly.reasons == ("WORK_COVERAGE_INCOMPLETE",)
    mismatch = calculate([work], [coverage("WORK", as_of=FINISH - timedelta(seconds=1)), coverage("PAUSE")])
    assert mismatch.assembly.reasons == ("WORK_COVERAGE_AS_OF_MISMATCH",)


def test_pauses_outside_work_do_not_subtract_or_make_duration_negative():
    result = calculate([fact("w", "WORK", START + timedelta(hours=2), START + timedelta(hours=3)),
                        fact("p", "PAUSE", START, START + timedelta(hours=1))])
    assert result.assembly.hours == 1
    fully_paused = calculate([fact("w", "WORK", START, FINISH), fact("p", "PAUSE", START, FINISH)])
    assert fully_paused.assembly.hours is None and fully_paused.assembly.duration_microseconds == 0


def test_microsecond_truth_and_decimal_hours_do_not_depend_on_callers_decimal_context():
    end = START + timedelta(microseconds=1)
    with localcontext() as context:
        context.prec = 2
        result = calculate([fact("w", "WORK", START, end)])
    assert result.assembly.duration_microseconds == 1
    assert result.assembly.hours is not None and result.assembly.hours > 0
    assert result.assembly.hours == calculate([fact("w", "WORK", START, end)]).assembly.hours


@pytest.mark.parametrize("changes", [{"confirmed": False}, {"confirmed": 1}, {"kind": "PLANNED_SHIFT"},
                                    {"start": START.replace(tzinfo=None)}, {"finish": START}])
def test_unconfirmed_planned_naive_or_nonpositive_facts_are_rejected(changes):
    with pytest.raises(ValueError):
        replace(fact("w", "WORK", START, FINISH), **changes)


def test_foreign_operator_unknown_record_and_input_bounds_cannot_mix_into_hours():
    with pytest.raises(ValueError, match="ONE_OPERATOR"):
        calculate([fact("w", "WORK", START, FINISH, operator="other-picker")])
    with pytest.raises(ValueError, match="ONE_OPERATOR"):
        calculate([{"kind": "WORK"}])
    with pytest.raises(ValueError, match="INPUT_BOUND"):
        calculate([fact("w", "WORK", START, FINISH)] * (MAX_INTERVALS + 1))
    with pytest.raises(ValueError, match="INPUT_BOUND"):
        calculate([], [coverage("WORK")] * (MAX_COVERAGE + 1))
    with pytest.raises(ValueError, match="366"):
        calculate(finish=START + timedelta(days=367), as_of=START + timedelta(days=367))


def test_maximum_bounded_disjoint_input_keeps_exact_microseconds_after_many_pauses():
    facts = []
    for index in range(MAX_INTERVALS // 2):
        start = START + timedelta(microseconds=index * 4)
        facts.append(fact("w" + str(index), "WORK", start, start + timedelta(microseconds=2)))
        facts.append(fact("p" + str(index), "PAUSE", start + timedelta(microseconds=1), start + timedelta(microseconds=2)))
    result = calculate(facts)
    assert result.assembly.status == "AVAILABLE"
    assert result.assembly.duration_microseconds == MAX_INTERVALS // 2
