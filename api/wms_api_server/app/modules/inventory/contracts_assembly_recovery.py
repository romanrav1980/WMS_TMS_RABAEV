"""Explicit dual-principal recovery of an unposted assembly step."""
from typing import Literal
from pydantic import Field, field_validator
from .contracts_assembly_scale import AssemblyInput, AssemblyCapture


class AssemblyReconciliationRequest(AssemblyInput):
    operation_id: str = Field(min_length=1, max_length=100, pattern=r"^[A-Za-z0-9_.:-]+$")
    step_id: str = Field(min_length=1, max_length=100)
    expected_content_version: int = Field(ge=0)
    reason: str = Field(min_length=8, max_length=500)


class AssemblyReconciliationAuthorization(AssemblyInput):
    operation_id: str = Field(min_length=1, max_length=100, pattern=r"^[A-Za-z0-9_.:-]+$")
    reason: str = Field(min_length=8, max_length=500)
    unaccepted_goods_removed: Literal[True]

    @field_validator("unaccepted_goods_removed", mode="before")
    @classmethod
    def actual_controller_confirmation(cls, value: object) -> bool:
        if value is not True:
            raise ValueError("Confirm actual removal after the hold acknowledgement")
        return True


class AssemblyReconciliationCapture(AssemblyCapture):
    phase: Literal["RECONCILE"]
    reconciliation_id: str = Field(min_length=1, max_length=100)
