"""Typed range proposal commands; original scenario is archived, no stock effects."""
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Any, Protocol

@dataclass(frozen=True)
class RangeDraft:
    operation_id: str
    period_from: date
    period_to_exclusive: date
    declared_period_forecast: Decimal | None
    forecast_base_uom: str | None
    declared_pallet_gross_weight_kg: Decimal | None
    recommendation_costs: list[dict[str, Any]]
    expected_source_signature: str
    reason: str
    candidate_pick_route_id: int | None = None

class RangeProposalPort(Protocol):
    def save(self, ware: int, article: str, command: RangeDraft, actor: str) -> dict[str, Any]: ...
    def cancel(self, ware: int, article: str, proposal: str, operation: str, reason: str, actor: str) -> dict[str, Any]: ...
    def approve(self, ware: int, article: str, proposal: str, operation: str, reason: str,
                geometry: bool, compatibility: bool, actor: str) -> dict[str, Any]: ...
    def close(self, ware: int, article: str, mapping: int, operation: str, reason: str, actor: str) -> dict[str, Any]: ...
    def get(self, ware: int, article: str, proposal: str, actor: str) -> dict[str, Any]: ...

def range_proposal_service() -> RangeProposalPort:
    raise RuntimeError("Range proposal service not wired")
