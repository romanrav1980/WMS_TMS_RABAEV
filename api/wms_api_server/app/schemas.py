from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, Field


class DbPingResponse(BaseModel):
    user_name: str
    service_name: str
    db_name: str


class LegacyBlockModel(BaseModel):
    function_name: str
    values: dict[str, str] = Field(default_factory=dict)


class LegacyExecuteRequest(BaseModel):
    payload: str


class LegacyExecuteResponse(BaseModel):
    payload: str
    blocks: list[LegacyBlockModel]


class ProductionBatchCreate(BaseModel):
    prod_batch_no: str
    articul: str | None = None
    mod_id: int | None = None
    gtin: str | None = None
    product_name: str | None = None
    total_quantity: float | None = None
    total_pack_count: float | None = None
    unit_code: str | None = "PCS"
    ware_id: int | None = None
    source_system: str | None = None
    source_message_id: str | None = None
    external_operation_id: str | None = None
    external_batch_id: str | None = None
    production_order_id: int | None = None
    produced_date_from: date | None = None
    produced_date_to: date | None = None
    expiry_date_from: date | None = None
    expiry_date_to: date | None = None
    production_line: str | None = None
    shift_id: str | None = None
    mercury_required: int = 0
    crpt_required: int = 0
    created_by: str | None = None


class IdResponse(BaseModel):
    id: int


class PalletAttachRequest(BaseModel):
    uid_pallet: str
    pallet_no: int | None = None
    quantity: float | None = None
    pack_count: float | None = None
    net_weight: float | None = None
    gross_weight: float | None = None
    sscc: str | None = None
    quality_status: str | None = None
    created_by: str | None = None


class RawUsageRequest(BaseModel):
    raw_batch_id: int | None = None
    raw_articul: str | None = None
    quantity_planned: float | None = None
    quantity_fact: float | None = None
    unit_code: str | None = "PCS"
    used_by: str | None = None


class CrptCodeRequest(BaseModel):
    uid_pallet: str | None = None
    gtin: str
    cis: str
    serial_no: str | None = None
    datamatrix_full: str | None = None
    parent_sscc: str | None = None


class AggregationCreateRequest(BaseModel):
    sscc: str
    uid_pallet: str | None = None
    parent_sscc: str | None = None
    aggregation_level: str | None = "PALLET"


class MercuryBatchRequest(BaseModel):
    mercury_operation_id: str | None = None
    stock_entry_uuid: str | None = None
    stock_entry_guid: str | None = None
    vet_document_uuid: str | None = None
    vet_document_status: str | None = None
    vet_document_type: str | None = None
    vet_document_form: str | None = None
    product_item_guid: str | None = None
    product_item_name: str | None = None
    last_error: str | None = None


class TerminalErrorLine(BaseModel):
    uid: str
    qty: float
    condition: str
    ean: str | None = None
    plan_qty: float | None = None
    usscc: str | None = None


class TerminalVpLine(BaseModel):
    pallet_uid: str
    uid: str
    checked_at: datetime | str


class LotCheckRequest(BaseModel):
    user_id: str
    error_count: int = 0
    errors: list[TerminalErrorLine] = Field(default_factory=list)
    vp_lines: list[TerminalVpLine] = Field(default_factory=list)


class PlaceInventoryAuditLine(BaseModel):
    uid: str
    qty: float
    pallet_id: str
    user_id: str


class PlaceCheckRequest(BaseModel):
    pallet_id: str
    errors: list[TerminalErrorLine] = Field(default_factory=list)
    inventory_lines: list[PlaceInventoryAuditLine] = Field(default_factory=list)


class OrderCheckRequest(BaseModel):
    order: str
    errors: list[TerminalErrorLine] = Field(default_factory=list)


class CallSpfRequest(BaseModel):
    spf_name: str
    params: dict[str, Any] = Field(default_factory=dict)
