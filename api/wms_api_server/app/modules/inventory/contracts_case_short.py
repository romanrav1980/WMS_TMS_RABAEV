"""Existing CASE decision contract with explicit weight tolerance proof."""
from typing import Literal
from pydantic import BaseModel, Field


class CasePickShortDecisionRequest(BaseModel):
    decision: Literal["ACCEPT_SHORT", "RESTORE", "WEIGHT_TOLERANCE"] = "ACCEPT_SHORT"
    expected_weight_policy_version: int | None = Field(default=None, ge=0, strict=True)
    expected_content_version: int | None = Field(default=None, ge=0, strict=True)
    expected_order_weight_signature: str | None = Field(default=None, pattern=r"^[A-F0-9]{64}$")
    operation_id: str | None = Field(default=None, min_length=1, max_length=100)
    reason_text: str | None = None
    actor: str | None = None
