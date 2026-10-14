"""Addressed warehouse scale evidence; device packets do not post inventory."""
from typing import Any, Literal, Protocol
from pydantic import BaseModel, ConfigDict, Field

UTC_PATTERN = r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]{6}\+00:00$"
DECIMAL_PATTERN = r"^[0-9]{1,18}(\.[0-9]{1,9})?$"


class WarehouseScaleError(RuntimeError):
    def __init__(self, code: str, message: str, status: int = 409) -> None:
        super().__init__(message)
        self.code, self.status = code, status


class WarehouseScaleConfiguration(BaseModel):
    model_config = ConfigDict(extra="forbid")
    warehouse_id: int = Field(strict=True, ge=1)
    post_cell: str = Field(strict=True, min_length=1, max_length=60)
    sender_id: str = Field(strict=True, min_length=1, max_length=50)
    expected_version: int = Field(strict=True, ge=0)
    active: bool = Field(strict=True)
    device_mode: Literal["TEST", "HARDWARE"]
    basis: Literal["NET", "GROSS"]
    capacity_kg: str = Field(strict=True, pattern=DECIMAL_PATTERN)
    resolution_kg: str = Field(strict=True, pattern=DECIMAL_PATTERN)
    calibration_ref: str = Field(strict=True, min_length=1, max_length=100)
    calibrated_until: str = Field(strict=True, pattern=UTC_PATTERN)


class WarehouseScaleSample(BaseModel):
    model_config = ConfigDict(extra="forbid")
    offset_ms: int = Field(strict=True, ge=0, le=10000)
    weight_kg: str = Field(strict=True, pattern=DECIMAL_PATTERN)


class WarehouseScalePacket(BaseModel):
    model_config = ConfigDict(extra="forbid")
    device_id: str = Field(strict=True, min_length=1, max_length=100)
    capture_id: str = Field(strict=True, min_length=1, max_length=100)
    post_cell: str = Field(strict=True, min_length=1, max_length=60)
    case_task_id: int = Field(strict=True, ge=1)
    case_line_id: int = Field(strict=True, ge=1)
    expected_content_version: int = Field(strict=True, ge=0)
    scan_source_cell: str = Field(strict=True, min_length=1, max_length=60)
    scan_container: str = Field(strict=True, min_length=1, max_length=150)
    scan_product: str = Field(strict=True, min_length=1, max_length=512)
    device_policy_version: int = Field(strict=True, ge=1)
    calibration_ref: str = Field(strict=True, min_length=1, max_length=100)
    unit: Literal["KG"]
    basis: Literal["NET", "GROSS"]
    preset_tare_kg: Literal["0"]
    zero_confirmed: bool = Field(strict=True)
    zero_check_kg: str = Field(strict=True, pattern=r"^-?[0-9]{1,18}(\.[0-9]{1,9})?$")
    zero_check_at: str = Field(strict=True, pattern=UTC_PATTERN)
    measured_at: str = Field(strict=True, pattern=UTC_PATTERN)
    samples: list[WarehouseScaleSample] = Field(min_length=5, max_length=25)


class WarehouseFinalScalePacket(BaseModel):
    model_config = ConfigDict(extra="forbid")
    device_id: str = Field(strict=True,min_length=1,max_length=100)
    capture_id: str = Field(strict=True,min_length=1,max_length=100)
    post_cell: str = Field(strict=True,min_length=1,max_length=60)
    case_task_id: int = Field(strict=True,ge=1)
    expected_content_version: int = Field(strict=True,ge=0)
    scan_container: str = Field(strict=True,min_length=1,max_length=150)
    purpose: Literal["EMPTY_TARE","FINAL_GROSS"]
    tare_capture_key: str|None = Field(default=None,pattern=r"^[A-F0-9]{64}$")
    device_policy_version: int = Field(strict=True,ge=1)
    calibration_ref: str = Field(strict=True,min_length=1,max_length=100)
    unit: Literal["KG"]
    basis: Literal["GROSS"]
    preset_tare_kg: Literal["0"]
    zero_confirmed: bool = Field(strict=True)
    zero_check_kg: str = Field(strict=True,pattern=r"^-?[0-9]{1,18}(\.[0-9]{1,9})?$")
    zero_check_at: str = Field(strict=True,pattern=UTC_PATTERN)
    measured_at: str = Field(strict=True,pattern=UTC_PATTERN)
    samples: list[WarehouseScaleSample] = Field(min_length=5,max_length=25)


class WarehouseScalePort(Protocol):
    def configure(self, device: str, body: WarehouseScaleConfiguration, actor: str) -> dict[str, Any]: ...
    def capture(self, body: WarehouseScalePacket|WarehouseFinalScalePacket, actor: str) -> dict[str, Any]: ...
    def readings(self, task: int, line: int, actor: str) -> dict[str, Any]: ...
    def reading(self, key: str, actor: str) -> dict[str, Any]: ...
    def final_readings(self, task: int, actor: str) -> dict[str, Any]: ...


def warehouse_scale_service() -> WarehouseScalePort:
    raise RuntimeError("Warehouse scales not wired")
