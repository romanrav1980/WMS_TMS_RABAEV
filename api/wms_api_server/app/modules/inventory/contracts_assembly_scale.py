"""Assembly scale API v1: operator consent, immutable evidence, one stock writer."""
from __future__ import annotations
from typing import Any, Literal, Protocol, TYPE_CHECKING
if TYPE_CHECKING:
    from .contracts_assembly_recovery import AssemblyReconciliationRequest, AssemblyReconciliationAuthorization, AssemblyReconciliationCapture
from pydantic import BaseModel, ConfigDict, Field, field_validator
from .contracts_warehouse_scale import WarehouseScaleSample, UTC_PATTERN, DECIMAL_PATTERN


class AssemblyScaleError(RuntimeError):
    def __init__(self, code: str, message: str, status: int = 409, details: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.code, self.status, self.details = code, status, details or {}


class AssemblyInput(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class AssemblyStationPolicy(AssemblyInput):
    operation_id: str = Field(min_length=1, max_length=100, pattern=r"^[A-Za-z0-9_.:-]+$")
    expected_version: int = Field(ge=0)
    confirmation_mode: Literal["AUTO", "BUTTON"]
    max_session_seconds: int = Field(ge=60, le=28800)
    cumulative_tolerance_kg: str = Field(pattern=DECIMAL_PATTERN)
    active: bool
    reason: str = Field(min_length=8, max_length=500)


class AssemblySkuPolicy(AssemblyInput):
    operation_id: str = Field(min_length=1, max_length=100, pattern=r"^[A-Za-z0-9_.:-]+$")
    warehouse_id: int = Field(ge=1)
    article: str = Field(min_length=1, max_length=100)
    base_uom: Literal["EA"]
    expected_version: int = Field(ge=0)
    min_unit_kg: str = Field(pattern=DECIMAL_PATTERN)
    max_unit_kg: str = Field(pattern=DECIMAL_PATTERN)
    min_delta_kg: str = Field(pattern=DECIMAL_PATTERN)
    tolerance_kg: str = Field(pattern=DECIMAL_PATTERN)
    active: bool
    evidence_reference: str = Field(min_length=8, max_length=200)
    reason: str = Field(min_length=8, max_length=500)


class AssemblySessionOpen(AssemblyInput):
    session_id: str = Field(min_length=1, max_length=100, pattern=r"^[A-Za-z0-9_.:-]+$")
    task_id: int = Field(ge=1)
    device_id: str = Field(min_length=1, max_length=100)
    expected_content_version: int = Field(ge=0)
    tare_capture_key: str = Field(pattern=r"^[A-F0-9]{64}$")
    scan_container: str = Field(min_length=1, max_length=150)


class AssemblyStepOpen(AssemblyInput):
    step_id: str = Field(min_length=1, max_length=100, pattern=r"^[A-Za-z0-9_.:-]+$")
    operation_id: str = Field(min_length=1, max_length=100, pattern=r"^[A-Za-z0-9_.:-]+$")
    case_line_id: int = Field(ge=1)
    quantity: str = Field(pattern=r"^[1-9][0-9]{0,8}$")
    scan_source_cell: str = Field(min_length=1, max_length=60)
    scan_product: str = Field(min_length=1, max_length=512)
    scan_container: str = Field(min_length=1, max_length=150)
    expected_content_version: int = Field(ge=0)
    consent_to_auto: bool = False


class AssemblyCapture(AssemblyInput):
    session_id: str = Field(min_length=1, max_length=100)
    step_id: str = Field(min_length=1, max_length=100)
    capture_id: str = Field(min_length=1, max_length=100)
    phase: Literal["BEFORE", "AFTER"]
    device_id: str = Field(min_length=1, max_length=100)
    device_policy_version: int = Field(ge=1)
    calibration_ref: str = Field(min_length=1, max_length=100)
    unit: Literal["KG"]
    basis: Literal["GROSS"]
    preset_tare_kg: Literal["0"]
    tare_mode_clear: Literal[True]
    quality_confirmed: Literal[True]
    measured_at: str = Field(pattern=UTC_PATTERN)
    samples: list[WarehouseScaleSample] = Field(min_length=5, max_length=25)

    @field_validator("tare_mode_clear", "quality_confirmed", mode="before")
    @classmethod
    def actual_boolean_confirmation(cls, value: Any) -> bool:
        if value is not True:
            raise ValueError("An actual true boolean is required")
        return True


class AssemblyFinish(AssemblyInput):
    final_capture_key: str = Field(pattern=r"^[A-F0-9]{64}$")


class AssemblyScalePort(Protocol):
    def context(self, task: int, actor: str) -> dict[str, Any]: ...
    def read_session(self, session: str, actor: str) -> dict[str, Any]: ...
    def read_step(self, step: str, actor: str) -> dict[str, Any]: ...
    def station_policy(self, device: str, body: AssemblyStationPolicy, actor: str) -> dict[str, Any]: ...
    def sku_policy(self, body: AssemblySkuPolicy, actor: str) -> dict[str, Any]: ...
    def open_session(self, body: AssemblySessionOpen, actor: str) -> dict[str, Any]: ...
    def open_step(self, session: str, body: AssemblyStepOpen, actor: str) -> dict[str, Any]: ...
    def gateway_requests(self, device: str, sender: str) -> dict[str, Any]: ...
    def capture(self, body: AssemblyCapture | AssemblyReconciliationCapture, sender: str) -> dict[str, Any]: ...
    def placed(self, step: str, actor: str) -> dict[str, Any]: ...
    def request_reconciliation(self, session: str, body: AssemblyReconciliationRequest, actor: str) -> dict[str, Any]: ...
    def authorize_reconciliation(self, identity: str, body: AssemblyReconciliationAuthorization, actor: str) -> dict[str, Any]: ...
    def read_reconciliation(self, identity: str, actor: str) -> dict[str, Any]: ...
    def finish(self, session: str, body: AssemblyFinish, actor: str) -> dict[str, Any]: ...


def assembly_scale_service() -> AssemblyScalePort:
    raise RuntimeError("Assembly scales are not wired")
