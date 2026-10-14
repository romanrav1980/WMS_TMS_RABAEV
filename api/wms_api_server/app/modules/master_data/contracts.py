from typing import Literal, Annotated
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, model_validator, AfterValidator


def _profile_storage_value(value: str) -> str:
    """Native profile identity columns and resolvers use VARCHAR2(80 BYTE)."""
    if len(value.encode("utf-8")) > 80:
        raise ValueError("Profile code exceeds native UTF-8 storage limit of 80 bytes.")
    return value


MarkingProfileCode = Annotated[str, Field(strict=True, min_length=1, max_length=80),
    AfterValidator(_profile_storage_value)]


class MarkingProfile(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    system_code: str = Field(min_length=1, max_length=40, pattern=r"^[A-Z][A-Z0-9_]*$")
    profile_code: MarkingProfileCode
    profile_version: str = Field(min_length=1, max_length=40)
    scan_mode: Literal["UNIT", "BOX", "PALLET", "UNIT_OR_AGGREGATION"] = "UNIT"


class ReceiptPolicyUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    expected_version: int = Field(ge=0)
    marking_required: bool
    serialized_weight_boxes: bool | None = None
    stack_stage: Literal["BASE", "MAIN", "TOP"] | None = None
    order_weight_tolerance_pct: Decimal | None = Field(default=None, ge=0, le=100, decimal_places=2)
    profiles: list[MarkingProfile] = Field(default_factory=list, max_length=16)

    @model_validator(mode="after")
    def consistent_profiles(self) -> "ReceiptPolicyUpdate":
        if self.marking_required != bool(self.profiles):
            raise ValueError("Marked SKU requires profiles; unmarked SKU must have none.")
        keys = [(p.system_code, p.profile_code) for p in self.profiles]
        if len(keys) != len(set(keys)):
            raise ValueError("Duplicate system/profile in SKU policy.")
        return self
