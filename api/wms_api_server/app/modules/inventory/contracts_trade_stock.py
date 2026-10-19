"""Legal stock facets reference the existing physical ledger."""
from typing import Any, Literal, Protocol

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, model_validator


class TradeStockRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    operation_id: str = Field(min_length=1, max_length=100, pattern=r"^[A-Za-z0-9_.:-]+$")


class TradeStockBind(TradeStockRequest):
    supply_id: str = Field(min_length=1, max_length=100)
    expected_supply_version: int = Field(strict=True, gt=0)
    scanned_pallet: str = Field(min_length=1, max_length=50)


class TradeCellPolicy(TradeStockRequest):
    expected_version: int = Field(strict=True, ge=0)
    zone_kind: Literal["RECEIVE", "STORAGE", "PICK", "WAIT", "EXPEDITION", "SORT", "DEFECT"]
    owner_id: str | None = Field(default=None, min_length=1, max_length=100)
    reason: str = Field(min_length=8, max_length=500)


    @model_validator(mode="after")
    def pick_owner(self) -> "TradeCellPolicy":
        if self.zone_kind == "PICK" and self.owner_id is None:
            raise ValueError("Picking cell requires its owner")
        return self


class TradeOwnerGrant(TradeStockRequest):
    expected_version: int = Field(strict=True, ge=0)
    username: str = Field(min_length=1, max_length=50)
    owner_id: str = Field(min_length=1, max_length=100)
    can_view: bool
    can_operate: bool
    reason: str = Field(min_length=8, max_length=500)


    @model_validator(mode="after")
    def operate_requires_view(self) -> "TradeOwnerGrant":
        if self.can_operate and not self.can_view:
            raise ValueError("Operating grant requires view access")
        return self


class TradeMarkItem(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    physical_unit_key: str = Field(pattern=r"^[0-9A-Fa-f]{64}$")
    expected_attribute_version: int = Field(strict=True, gt=0)
    verdict: Literal["VALID", "REJECTED"]
    external_reason: str | None = Field(default=None, min_length=1, max_length=500)

    @model_validator(mode="after")
    def rejection_reason(self) -> "TradeMarkItem":
        if self.verdict == "REJECTED" and not self.external_reason:
            raise ValueError("Rejected code requires external reason")
        return self


class TradeMarkConfirmation(TradeStockRequest):
    skm_id: str = Field(min_length=1, max_length=100, pattern=r"^[A-Za-z0-9_.:-]+$")
    external_event_id: str = Field(min_length=1, max_length=100, pattern=r"^[A-Za-z0-9_.:-]+$")
    expected_site_version: int = Field(strict=True, gt=0)
    occurred_at: AwareDatetime
    items: list[TradeMarkItem] = Field(min_length=1, max_length=1000)

    @model_validator(mode="after")
    def unique_units(self) -> "TradeMarkConfirmation":
        if len({item.physical_unit_key for item in self.items}) != len(self.items):
            raise ValueError("Duplicate physical unit")
        return self


class TradeSortScan(BaseModel):
    model_config = ConfigDict(extra="forbid")
    system_code: str = Field(strict=True, min_length=1, max_length=40)
    profile_code: str = Field(strict=True, min_length=1, max_length=80)
    code: str = Field(strict=True, min_length=1, max_length=4000)


class TradeSort(TradeStockRequest):
    source_pallet: str = Field(min_length=1, max_length=200)
    source_cell: str = Field(min_length=1, max_length=60)
    target_cell: str = Field(min_length=1, max_length=60)
    scans: list[TradeSortScan] = Field(min_length=1, max_length=10000)


class TradeStockError(RuntimeError):
    def __init__(self, code: str, status: int = 409) -> None:
        self.code, self.status = code, status
        super().__init__(code)


class TradeStockPort(Protocol):
    def transit(self, warehouse_id: int, load_operation_id: str, after: str, limit: int, actor: str) -> dict[str, Any]: ...
    def sort(self, warehouse_id: int, body: TradeSort, actor: str) -> dict[str, Any]: ...
    def summary(self, warehouse_id: int, after: str, limit: int, actor: str) -> dict[str, Any]: ...
    def confirm_marks(self, warehouse_id: int, body: TradeMarkConfirmation, actor: str) -> dict[str, Any]: ...
    def bind(self, warehouse_id: int, body: TradeStockBind, actor: str) -> dict[str, Any]: ...
    def cell(self, warehouse_id: int, cell: str, body: TradeCellPolicy, actor: str) -> dict[str, Any]: ...
    def grant(self, warehouse_id: int, body: TradeOwnerGrant, actor: str) -> dict[str, Any]: ...
    def view(self, warehouse_id: int, after: str, limit: int, actor: str, pallet_identifier: str | None = None) -> dict[str, Any]: ...
