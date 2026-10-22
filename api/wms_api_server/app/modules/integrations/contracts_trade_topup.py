"""Ordered demand selection for capacity calculation and the durable top-up decision commands."""
from typing import Literal
from pydantic import Field, model_validator
from .contracts_trade_base import Key, TradeModel


class TopupPreview(TradeModel):
    need_ids: list[Key] = Field(min_length=1, max_length=20)
    max_age_minutes: int = Field(strict=True, ge=1, le=1440)

    @model_validator(mode="after")
    def unique_needs(self) -> "TopupPreview":
        if len(set(self.need_ids)) != len(self.need_ids):
            raise ValueError("Duplicate demand snapshot")
        return self


class TopupSave(TopupPreview):
    """Save the calculation as proposals; the same inputs return the existing proposals."""
    operation_id: Key


class TopupDecision(TradeModel):
    operation_id: Key
    expected_version: int = Field(strict=True, gt=0)
    action: Literal["ADJUST", "REJECT"]
    boxes: int | None = Field(default=None, strict=True, ge=1, le=100000)

    @model_validator(mode="after")
    def boxes_for_adjust(self) -> "TopupDecision":
        if (self.action == "ADJUST") != (self.boxes is not None):
            raise ValueError("Adjustment requires boxes; rejection has none")
        return self


class TopupConfirm(TradeModel):
    operation_id: Key
    expected_version: int = Field(strict=True, gt=0)


class TopupRelease(TradeModel):
    operation_id: Key
    expected_version: int = Field(strict=True, gt=0)


class TopupSapReply(TradeModel):
    """SAP answer to a confirmed top-up request: the created order, or the rejection reason."""
    operation_id: Key
    source_id: Key
    event_id: Key
    expected_version: int = Field(strict=True, gt=0)
    outcome: Literal["ACCEPTED", "REJECTED"]
    sap_order_id: Key | None = None
    reason: str | None = Field(default=None, min_length=1, max_length=2000)

    @model_validator(mode="after")
    def evidence(self) -> "TopupSapReply":
        if self.outcome == "ACCEPTED" and not self.sap_order_id:
            raise ValueError("Accepted reply requires the SAP order")
        if self.outcome == "REJECTED" and not self.reason:
            raise ValueError("Rejected reply requires the SAP reason")
        return self
