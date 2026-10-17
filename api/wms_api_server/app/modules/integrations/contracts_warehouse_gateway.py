"""A station profile binds the warehouse adapter to one registered sender/device."""
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field


class WarehouseGatewayProfile(BaseModel):
    model_config = ConfigDict(extra="forbid")
    device_id: str = Field(strict=True, min_length=1, max_length=100)
    warehouse_id: int = Field(strict=True, ge=1)
    post_cell: str = Field(strict=True, min_length=1, max_length=60)
    device_mode: Literal["TEST", "HARDWARE"]
    device_policy_version: int = Field(strict=True, ge=1)
    calibration_ref: str = Field(strict=True, min_length=1, max_length=100)
    basis: Literal["NET", "GROSS"]
