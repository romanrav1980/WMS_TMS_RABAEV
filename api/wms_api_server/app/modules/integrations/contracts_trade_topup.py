"""Ordered demand selection for a read-only capacity calculation."""
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
