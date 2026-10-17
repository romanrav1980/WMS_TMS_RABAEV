"""Confirmed operation deltas, final-line credit and explicit missing packaging proof."""
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, ROUND_FLOOR
from typing import Any


@dataclass(frozen=True)
class PickFact:
    operation_id: str
    actor: str
    at: datetime
    task_id: int
    line_id: int
    article: str
    base_uom: str
    previous: Decimal
    cumulative: Decimal
    planned: Decimal
    boxes: Decimal | None
    packaging_reason: str | None
    box_size_base: Decimal | None = None
    input_kind: str | None = None

    @property
    def delta(self) -> Decimal:
        return self.cumulative - self.previous

    @property
    def completes_line(self) -> bool:
        return self.previous < self.planned == self.cumulative

    @property
    def whole_boxes(self) -> Decimal | None:
        if self.boxes is not None:
            return self.boxes.to_integral_value(rounding=ROUND_FLOOR)
        if self.packaging_reason == "PARTIAL_BOX_RULE_REQUIRED" and self.box_size_base is not None:
            return (self.delta / self.box_size_base).to_integral_value(rounding=ROUND_FLOOR)
        return None

    @property
    def pieces(self) -> Decimal | None:
        if self.base_uom != "EA":
            return None
        if self.whole_boxes == 0:
            return self.delta
        if self.whole_boxes is not None and self.box_size_base is not None:
            return self.delta - self.whole_boxes * self.box_size_base
        return None


def summarize_picks(facts: list[PickFact]) -> dict[str, dict[str, Any]]:
    unique: dict[str, PickFact] = {}
    for fact in facts:
        numbers = [fact.previous, fact.cumulative, fact.planned]
        if not all(n.is_finite() for n in numbers) or fact.at.utcoffset() is None or fact.delta <= 0 or fact.cumulative > fact.planned:
            raise ValueError("Invalid confirmed pick fact")
        if fact.boxes is not None and (not fact.boxes.is_finite() or fact.boxes < 0):
            raise ValueError("Invalid confirmed box count")
        if fact.box_size_base is not None and (not fact.box_size_base.is_finite() or fact.box_size_base <= 0):
            raise ValueError("Invalid frozen box conversion")
        if fact.pieces is not None and (fact.pieces < 0 or (fact.box_size_base is not None and fact.pieces >= fact.box_size_base)):
            raise ValueError("Frozen box/piece quantity mismatch")
        if fact.operation_id in unique and unique[fact.operation_id] != fact:
            raise ValueError("One operation has conflicting facts")
        unique[fact.operation_id] = fact
    actors: dict[str, dict[str, Any]] = {}
    completed: set[tuple[int, int]] = set()
    for fact in sorted(unique.values(), key=lambda item: (item.at, item.operation_id)):
        row = actors.setdefault(fact.actor, {"completed_lines": 0, "boxes": Decimal(0),
            "box_reasons": set(), "quantities": defaultdict(Decimal), "operation_ids": [],
            "pieces": Decimal(0), "pieces_unknown": False})
        key = fact.task_id, fact.line_id
        if fact.completes_line and key not in completed:
            row["completed_lines"] += 1
            completed.add(key)
        row["operation_ids"].append(fact.operation_id)
        row["quantities"][(fact.article, fact.base_uom)] += fact.delta
        if fact.whole_boxes is None:
            row["box_reasons"].add(fact.packaging_reason or "PACKAGING_PROOF_UNAVAILABLE")
        else:
            row["boxes"] += fact.whole_boxes
        if fact.base_uom == "EA":
            if fact.pieces is None:
                row["pieces_unknown"] = True
            else:
                row["pieces"] += fact.pieces
    return {actor: {"completed_lines": row["completed_lines"],
        "boxes": None if row["box_reasons"] else str(row["boxes"]),
        "pieces": None if row["pieces_unknown"] else str(row["pieces"]),
        "box_reasons": sorted(row["box_reasons"]), "operation_ids": row["operation_ids"],
        "quantities": [{"article": article, "base_uom": unit, "quantity": str(qty)}
            for (article, unit), qty in sorted(row["quantities"].items())]}
        for actor, row in actors.items()}


def hourly(value: int | str | None, hours: str | None) -> str | None:
    if value is None or hours is None:
        return None
    divisor = Decimal(hours)
    return str((Decimal(value) / divisor).quantize(Decimal("0.001"))) if divisor > 0 else None
