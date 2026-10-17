"""Observed rates use explicit actual-time registrations, never invented global coverage."""
from dataclasses import asdict
from datetime import datetime, timedelta, timezone
from hashlib import sha256
from typing import Any
import oracledb
from ..contracts_picker_kpi import PickerKpiError, PickerKpiReadPort
from ..domain.picker_kpi import PickFact, hourly, summarize_picks
from ..domain.picker_kpi_quality import append_quality
from ..domain.picker_time_denominators import ConfirmedTimeInterval, registered_time_denominators


def aware(value: str) -> datetime:
    result = datetime.fromisoformat(value)
    if result.utcoffset() is None:
        raise ValueError("Native aware source required")
    return result.astimezone(timezone.utc)


def registered_spans(raw: dict[str, Any]) -> list[dict[str, Any]]:
    values = list(raw["spans"])
    for item in raw["active"]:
        base = {"operator_id": item["operator_id"], "source_kind": item["source_kind"],
            "source_id": item["source_id"], "source_mode": "MANUAL_CONFIRMED", "finish_at": raw["as_of"].isoformat()}
        for kind, start in (("ACTUAL_SHIFT", item["shift_start"]), ("WORK", item["work_start"]), ("PAUSE", item["pause_start"])):
            if start is not None and aware(start) < raw["as_of"]:
                values.append({**base, "span_id": "OPEN." + kind + ":" + item["operator_id"], "kind": kind, "start_at": start})
    return values


def intervals(rows: list[dict[str, Any]], actor: str) -> list[ConfirmedTimeInterval]:
    result = []
    for row in rows:
        if row["operator_id"] != actor:
            continue
        if row["source_mode"] != "MANUAL_CONFIRMED":
            raise ValueError("Unsupported time source")
        result.append(ConfirmedTimeInterval(sha256(row["span_id"].encode()).hexdigest(), actor,
            row["kind"], aware(row["start_at"]), aware(row["finish_at"]), True))
    return result


def covered(fact: PickFact, rows: list[dict[str, Any]], kind: str) -> bool:
    return any(row["operator_id"] == fact.actor and row["kind"] == kind
        and aware(row["start_at"]) <= fact.at < aware(row["finish_at"])
        and (kind != "WORK" or (row["source_kind"] == "CASE_PICK_TASK" and int(row["source_id"]) == fact.task_id))
        for row in rows)


def operator_row(actor: str, facts: list[PickFact], totals: dict[str, Any], spans: list[dict[str, Any]],
                 start: datetime, finish: datetime, observed: datetime) -> dict[str, Any]:
    own = [fact for fact in facts if fact.actor == actor]
    time = registered_time_denominators(actor, start, finish, observed, intervals(spans, actor))
    gaps_work = [fact.operation_id for fact in own if not covered(fact, spans, "WORK") or covered(fact, spans, "PAUSE")]
    gaps_shift = [fact.operation_id for fact in own if not covered(fact, spans, "ACTUAL_SHIFT")]
    work = str(time.assembly.hours) if time.assembly.hours is not None and not gaps_work else None
    shift = str(time.actual_shift.hours) if time.actual_shift.hours is not None and not gaps_shift else None
    return {"operator_id": actor, **totals, "registered_assembly_hours": work, "registered_shift_hours": shift,
        "rates": {"lines_per_assembly_hour": hourly(totals["completed_lines"], work),
            "boxes_per_assembly_hour": hourly(totals["boxes"], work),
            "lines_per_shift_hour": hourly(totals["completed_lines"], shift), "boxes_per_shift_hour": hourly(totals["boxes"], shift)},
        "time_basis": "REGISTERED_CONFIRMED_INTERVALS", "work_coverage_certified": False,
        "uncovered_work_operations": gaps_work, "uncovered_shift_operations": gaps_shift,
        "observed_pick_coverage": {"total": len(own), "covered_work": len(own) - len(gaps_work),
            "covered_shift": len(own) - len(gaps_shift), "complete_for_observed_picks": not gaps_work and not gaps_shift},
        "time_reasons": {"assembly": list(time.assembly.reasons), "shift": list(time.actual_shift.reasons)},
        "facts": [{**asdict(fact), "at": fact.at.isoformat(), "previous": str(fact.previous),
            "cumulative": str(fact.cumulative), "planned": str(fact.planned), "delta": str(fact.delta),
            "boxes": str(fact.whole_boxes) if fact.whole_boxes is not None else None,
            "pieces": str(fact.pieces) if fact.pieces is not None else None,
            "box_size_base": str(fact.box_size_base) if fact.box_size_base is not None else None} for fact in own]}


class PickerKpiService:
    def __init__(self, reader: PickerKpiReadPort) -> None:
        self.reader = reader

    def window(self, warehouse: int, start: datetime, finish: datetime, actor: str,
               operator: str | None = None) -> dict[str, Any]:
        if start.utcoffset() is None or finish.utcoffset() is None or finish <= start or finish - start > timedelta(days=31):
            raise PickerKpiError("KPI_WINDOW_BOUND_31_DAYS", 422)
        start, finish = start.astimezone(timezone.utc), finish.astimezone(timezone.utc)
        try:
            raw = self.reader.snapshot(warehouse, start, finish, actor, operator)
            facts, spans = raw["facts"], registered_spans(raw)
            totals = summarize_picks(facts)
            append_quality(totals, facts, raw.get("closures", []), raw.get("returns", []))
            actors = sorted(set(totals) | {row["operator_id"] for row in spans})
            if len(actors) > 500:
                raise PickerKpiError("KPI_OPERATOR_BOUND_500", 422)
            empty = {"completed_lines": 0, "boxes": "0", "pieces": "0", "box_reasons": [], "operation_ids": [], "quantities": [],
                "shortage_completed_lines": 0, "shortage_quantities": [], "line_completions": [],
                "return_events": 0, "returned_quantities": []}
            result = [operator_row(op, facts, totals.get(op, empty), spans, start, finish, raw["as_of"]) for op in actors]
        except (ValueError, KeyError, TypeError, ArithmeticError) as error:
            raise PickerKpiError("KPI_SOURCE_FACT_INVALID", 503) from error
        except oracledb.DatabaseError as error:
            raise PickerKpiError("KPI_SOURCE_UNAVAILABLE", 503) from error
        return {"warehouse_id": warehouse, "start_at": start.isoformat(), "finish_at": finish.isoformat(),
            "as_of": raw["as_of"].isoformat(), "formula_version": "PICKER_KPI_V2", "operators": result,
            "scope": "REGISTERED_OBSERVATIONS", "work_coverage_certified": False,
            "source_limitations": ["REGISTERED_TIME_IS_NOT_CERTIFIED_ALL_WORK", "NATIVE_APPLIED_CLOCK_NOT_PHYSICAL_PICK_TIME",
                "HISTORICAL_PACKAGING_NOT_BACKFILLED", "HISTORICAL_QUALITY_WITHOUT_AWARE_CLOCK_NOT_BACKFILLED", "OPEN_INTERVALS_PROJECTED_TO_AS_OF",
                "WHOLE_BOXES_AND_LOOSE_PIECES_SEPARATE", "APPROVED_SHORT_CREDIT_AT_LAST_PHYSICAL_PICK",
                "RETURNS_RETAIN_WORK_LINE_QUALITY_SEPARATE", "QUALITY_IS_NOT_EMPLOYEE_FAULT_ATTRIBUTION"], "stock_changed": False}
