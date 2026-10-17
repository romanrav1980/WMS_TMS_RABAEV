"""Approved closure belongs to the physical finisher; returns never erase performed work."""
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Any
from .picker_kpi import PickFact


@dataclass(frozen=True)
class ShortCompletion:
    operation_id: str
    approved_at: datetime
    task_id: int
    line_id: int
    picked: Decimal
    planned: Decimal
    shortage: Decimal


@dataclass(frozen=True)
class ReturnedLine:
    operation_id: str
    at: datetime
    task_id: int
    line_id: int
    article: str
    base_uom: str
    quantity: Decimal


def quantities(values: dict[tuple[str, str], Decimal]) -> list[dict[str, str]]:
    return [{"article": article, "base_uom": unit, "quantity": str(amount)}
        for (article, unit), amount in sorted(values.items())]


def append_quality(totals: dict[str, dict[str, Any]], facts: list[PickFact],
                   closures: list[ShortCompletion], returns: list[ReturnedLine]) -> None:
    final: dict[tuple[int, int], PickFact] = {}
    for fact in facts:
        key = fact.task_id, fact.line_id
        if key not in final or (fact.at, fact.operation_id) > (final[key].at, final[key].operation_id):
            final[key] = fact
    for actor, row in totals.items():
        own = [fact for fact in facts if fact.actor == actor]
        own_lines = {(fact.task_id, fact.line_id) for fact in own}
        short_qty: dict[tuple[str, str], Decimal] = defaultdict(Decimal)
        returned_qty: dict[tuple[str, str], Decimal] = defaultdict(Decimal)
        completions = []; seen_lines = set(); seen_returns = set(); return_ids = set(); short_count = 0
        for fact in sorted(own, key=lambda item: (item.at, item.operation_id)):
            key = fact.task_id, fact.line_id
            if fact.completes_line and key not in seen_lines:
                seen_lines.add(key)
                completions.append({"operation_id": fact.operation_id, "task_id": fact.task_id,
                    "line_id": fact.line_id, "actor": actor, "at": fact.at.isoformat(), "approved_at": None,
                    "kind": "FULL", "quantity": str(fact.cumulative), "shortage_quantity": "0"})
        for item in closures:
            if item.approved_at.utcoffset() is None or not all(n.is_finite() for n in (item.picked, item.planned, item.shortage)) or not (0 < item.picked < item.planned) or item.shortage != item.planned - item.picked:
                raise ValueError("Invalid approved shortage proof")
            key = item.task_id, item.line_id
            finisher = final.get(key)
            if not finisher or finisher.actor != actor or finisher.cumulative != item.picked or item.approved_at < finisher.at:
                continue
            if key in seen_lines:
                continue
            seen_lines.add(key); row["completed_lines"] += 1; short_count += 1
            short_qty[(finisher.article, finisher.base_uom)] += item.shortage
            completions.append({"operation_id": item.operation_id, "task_id": item.task_id, "line_id": item.line_id,
                "actor": actor, "at": finisher.at.isoformat(), "approved_at": item.approved_at.isoformat(),
                "kind": "ACCEPTED_SHORT", "quantity": str(item.picked), "shortage_quantity": str(item.shortage)})
        for item in returns:
            if item.at.utcoffset() is None or not item.quantity.is_finite() or item.quantity <= 0:
                raise ValueError("Invalid physical return proof")
            key = item.task_id, item.line_id
            identity = item.operation_id, key, item.article, item.base_uom
            if key not in own_lines or identity in seen_returns:
                continue
            seen_returns.add(identity); return_ids.add(item.operation_id)
            returned_qty[(item.article, item.base_uom)] += item.quantity
        row.update(shortage_completed_lines=short_count, shortage_quantities=quantities(short_qty),
            line_completions=completions, return_events=len(return_ids), returned_quantities=quantities(returned_qty))
