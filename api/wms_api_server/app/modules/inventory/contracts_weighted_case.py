"""One barcode is one physical net-KG box; the server derives cumulative quantity."""
from decimal import Decimal
from typing import Protocol, Any
from pydantic import BaseModel, Field, ConfigDict
from ...schemas import CasePickUnitScan


class WeightedCaseRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    operation_id: str = Field(min_length=1, max_length=100)
    warehouse_scale_capture: str | None = Field(default=None, pattern=r"^[A-F0-9]{64}$")
    weighted_box_barcode: str = Field(min_length=1, max_length=512)
    scan_cell: str = Field(min_length=1, max_length=60)
    scan_container: str = Field(min_length=1, max_length=150)
    unit_scans: list[CasePickUnitScan] = Field(default_factory=list, max_length=50)


class WeighedLineRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    operation_id: str = Field(min_length=1, max_length=100)
    warehouse_scale_capture: str = Field(pattern=r"^[A-F0-9]{64}$")
    scan_cell: str = Field(min_length=1, max_length=60)
    scan_container: str = Field(min_length=1, max_length=150)


class ManualNetLineRequest(BaseModel):
    """C-0188: the operator's own NET kg for a KG CASE line when the integrated scale is unavailable. A separate variant: no scale capture
    can be sent here (extra=forbid), and the server derives the cumulative fact from the current line, never from the client."""
    model_config = ConfigDict(extra="forbid")
    operation_id: str = Field(min_length=1, max_length=100)
    net_weight_kg: Decimal = Field(gt=0, max_digits=27, decimal_places=9, allow_inf_nan=False)  # the CASE quantity precision
    scan_cell: str = Field(min_length=1, max_length=60)
    scan_container: str = Field(min_length=1, max_length=150)
    unit_scans: list[CasePickUnitScan] = Field(default_factory=list, max_length=50)


class WeightedCasePort(Protocol):
    def short_weight_preview(self, short: int, actor: str) -> dict[str, Any]: ...
    def weight_preview(self, task: int, line: int, actor: str) -> dict[str, Any]: ...
    def weigh_line(self, task: int, line: int, request: WeighedLineRequest, actor: str) -> dict[str, Any]: ...
    def confirm(self, task: int, line: int, request: WeightedCaseRequest, actor: str) -> dict[str, Any]: ...
    def weigh_line_manual(self, task: int, line: int, request: ManualNetLineRequest, actor: str) -> dict[str, Any]: ...


def weighted_case_service() -> WeightedCasePort:
    raise RuntimeError("Weighted CASE service not wired")
