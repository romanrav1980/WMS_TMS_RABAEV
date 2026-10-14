"""Passive public inventory DTOs; schemas.py retains compatibility aliases."""
from decimal import Decimal
from pydantic import BaseModel, Field
from .contracts_case_short import CasePickShortDecisionRequest

class StockReservationCreateRequest(BaseModel):
    reservation_kind: str = "SOFT"
    reservation_scope: str = "QTY"
    reservation_domain: str
    source_doc_type: str
    source_doc_id: int
    source_line_id: int | None = None
    task_id: int | None = None
    customer_id: int | None = None
    customer_order_id: int | None = None
    production_order_id: int | None = None
    pick_plan_id: int | None = None
    pick_plan_line_id: int | None = None
    pick_wave_id: int | None = None
    pick_wave_line_id: int | None = None
    articul: str
    qty: Decimal = Field(ge=0)
    unit_code: str | None = None
    ware_id: int | None = None
    cell: str | None = None
    batch_id: str | None = None
    prod_batch_id: int | None = None
    uid_pallet: str | None = None
    sscc: str | None = None
    status: str = "ACTIVE"
    priority: float = 100
    created_by: str | None = None

    operation_id: str | None = Field(default=None, max_length=100)
    unit_keys: list[str] = Field(default_factory=list, max_length=10000)


class StockReservationPromoteRequest(BaseModel):
    reservation_scope: str = "PALLET"
    ware_id: int
    cell: str
    batch_id: str | None = None
    prod_batch_id: int | None = None
    uid_pallet: str | None = None
    sscc: str | None = None
    qty: Decimal | None = Field(default=None, ge=0)
    updated_by: str | None = None

    operation_id: str | None = Field(default=None, max_length=100)
    unit_keys: list[str] = Field(default_factory=list, max_length=10000)


class StockReservationStatusRequest(BaseModel):
    reason: str | None = None
    updated_by: str | None = None

    operation_id: str | None = Field(default=None, max_length=100)
    unit_keys: list[str] = Field(default_factory=list, max_length=10000)


from .contracts_pallet_types import PalletTypeUpsertRequest
