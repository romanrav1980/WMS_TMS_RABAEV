from typing import Any, Literal, Protocol
from pydantic import BaseModel, ConfigDict, Field


class ReceivingWindow(BaseModel):
    model_config = ConfigDict(extra="forbid")
    weekday: int = Field(strict=True, ge=1, le=7)
    from_minute: int = Field(strict=True, ge=0, le=1439)
    to_minute: int = Field(strict=True, ge=1, le=1440)


class StoreProfileInput(BaseModel):
    """Только явно задаваемые параметры; null = не задано и ни на что не влияет."""
    model_config = ConfigDict(extra="forbid")
    operation_id: str = Field(strict=True, min_length=1, max_length=100, pattern=r"^[A-Za-z0-9_.:-]+$")
    store_addr: str = Field(min_length=1, max_length=255)
    expected_version: int = Field(strict=True, ge=0)
    reason: str = Field(min_length=8, max_length=1000)
    receiving_window_mode: Literal["UNCONFIGURED", "WEEKLY"] = "UNCONFIGURED"
    timezone_region: str | None = Field(default=None, max_length=64)
    backroom_flag: bool | None = None
    backroom_pallets: int | None = Field(default=None, ge=0, le=100000)
    backroom_rolls: int | None = Field(default=None, ge=0, le=100000)
    unattended_drop_flag: bool | None = None
    storage_temp_class: Literal["AMBIENT", "CHILLED", "FROZEN"] | None = None
    ramp_flag: bool | None = None
    ramp_height_mm: int | None = Field(default=None, ge=0, le=100000)
    # Внешние габариты ТС на подъезде (не размеры кузова); null — ограничение не задано.
    max_vehicle_outer_height_mm: int | None = Field(default=None, ge=1, le=100000)
    max_vehicle_outer_length_mm: int | None = Field(default=None, ge=1, le=100000)
    default_unload_method: Literal["PALLET", "ROLL_CAGE", "MANUAL"] | None = None
    loader_required: bool | None = None
    access_note: str | None = Field(default=None, max_length=1000)
    windows: list[ReceivingWindow] = Field(default_factory=list, max_length=56)


class StoreProfileError(Exception):
    def __init__(self, code: str, status: int = 409, message: str | None = None) -> None:
        super().__init__(message or code)
        self.code, self.status = code, status


class StoreProfilePort(Protocol):
    def read(self, address: str) -> dict[str, Any]: ...
    def save(self, actor: str, body: dict[str, Any]) -> dict[str, Any]: ...


def store_profile_service() -> StoreProfilePort:
    raise RuntimeError("Store profile service not wired")
