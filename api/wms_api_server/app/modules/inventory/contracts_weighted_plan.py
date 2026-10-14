"""Preview actual sealed boxes for the original warehouse order row."""
from typing import Any, Protocol, Literal
from pydantic import BaseModel, Field, ConfigDict


class WeightedBoxChoiceRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    choice_id: str = Field(min_length=1, max_length=100, pattern=r"^[A-Za-z0-9_.:-]+$")
    customer_order_row_id: int = Field(ge=1, strict=True)
    physical_unit_key: str = Field(pattern=r"^[A-Fa-f0-9]{64}$")
    weighted_box_barcode: str = Field(min_length=1, max_length=512)
    source_signature: str = Field(pattern=r"^[A-F0-9]{64}$")
    choice_mode: Literal["WITHIN_TOLERANCE", "LAST_WHOLE_BOX"]
    reason: str = Field(min_length=3, max_length=1000)


class WeightedChoiceCancelRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    reason: str = Field(min_length=3, max_length=1000)


class WeightedPlanPort(Protocol):
    def approval_options(self, row: int, actor: str) -> dict[str, Any]: ...
    def approve(self, body: WeightedBoxChoiceRequest, actor: str) -> dict[str, Any]: ...
    def cancel(self, choice: str, reason: str, actor: str) -> dict[str, Any]: ...
    def options(self, row: int, actor: str) -> dict[str, Any]: ...


def weighted_plan_service() -> WeightedPlanPort:
    raise RuntimeError("Weighted plan service not wired")
