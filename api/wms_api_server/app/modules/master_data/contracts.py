from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class MarkingProfile(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    system_code: str = Field(min_length=1, max_length=40, pattern=r"^[A-Z][A-Z0-9_]*$")
    profile_code: str = Field(min_length=1, max_length=80)
    profile_version: str = Field(min_length=1, max_length=40)
    scan_mode: Literal["UNIT", "BOX", "PALLET", "UNIT_OR_AGGREGATION"] = "UNIT"


class ReceiptPolicyUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    expected_version: int = Field(ge=0)
    marking_required: bool
    profiles: list[MarkingProfile] = Field(default_factory=list, max_length=16)

    @model_validator(mode="after")
    def consistent_profiles(self) -> "ReceiptPolicyUpdate":
        if self.marking_required != bool(self.profiles):
            raise ValueError("Marked SKU requires profiles; unmarked SKU must have none.")
        keys = [(p.system_code, p.profile_code) for p in self.profiles]
        if len(keys) != len(set(keys)):
            raise ValueError("Duplicate system/profile in SKU policy.")
        return self
