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


class RawBatchCreate(BaseModel):
    raw_batch_no: str
    articul: str | None = None
    supplier_id: str | None = None
    producer_name: str | None = None
    produced_date_from: date | None = None
    produced_date_to: date | None = None
    expiry_date_from: date | None = None
    expiry_date_to: date | None = None
    quantity_initial: float | None = None
    quantity_available: float | None = None
    unit_code: str | None = "PCS"
    ware_id: int | None = None
    mercury_site_id: int | None = None
    mercury_stock_entry_uuid: str | None = None
    mercury_vsd_uuid: str | None = None
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


class AggregationItemRequest(BaseModel):
    child_type: str
    child_cis: str | None = None
    child_sscc: str | None = None
    gtin: str | None = None
    prod_batch_id: int | None = None


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


class MercurySiteRequest(BaseModel):
    site_code: str
    site_name: str | None = None
    ware_id: int | None = None
    enterprise_guid: str | None = None
    enterprise_uuid: str | None = None
    business_guid: str | None = None
    business_uuid: str | None = None
    address_text: str | None = None
    active: int = 1
    updated_by: str | None = None


class MercuryOperationCreateRequest(BaseModel):
    raw_batch_id: int | None = None
    mercury_site_id: int | None = None
    operation_type: str
    mercury_operation_id: str | None = None
    external_operation_id: str | None = None
    status: str | None = "DRAFT"
    request_json: str | None = None
    created_by: str | None = None


class MercuryOperationUpdateRequest(BaseModel):
    status: str | None = None
    mercury_operation_id: str | None = None
    external_operation_id: str | None = None
    response_json: str | None = None
    last_error: str | None = None
    updated_by: str | None = None


class CrptCodeStatusRequest(BaseModel):
    cis: str
    code_status: str
    event_type: str | None = None
    document_id: str | None = None
    document_no: str | None = None
    payload_json: str | None = None
    error_text: str | None = None
    updated_by: str | None = None


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


class ApiReplayRequest(BaseModel):
    call_ids: list[int] = Field(default_factory=list)
    from_call_id: int | None = None
    to_call_id: int | None = None
    from_at: str | None = None
    to_at: str | None = None
    method: str | None = None
    path_like: str | None = None
    status: str | None = None
    dry_run: bool = True
    max_calls: int = 100
    continue_on_error: bool = True


class ExternalOutboxRetryRequest(BaseModel):
    dry_run: bool = True
    reason: str | None = None


class BomCreateRequest(BaseModel):
    bom_code: str
    bom_name: str | None = None
    target_articul: str
    target_mod_id: int | None = None
    target_gtin: str | None = None
    bom_kind: str = "FINISHED_GOODS"
    base_qty: float
    base_unit_code: str = "KG"
    is_primary: int = 0
    valid_from: date
    valid_to: date | None = None
    ware_id: int | None = None
    production_line: str | None = None
    comment_text: str | None = None
    created_by: str | None = None


class BomUpdateRequest(BaseModel):
    bom_code: str | None = None
    bom_name: str | None = None
    target_articul: str | None = None
    target_mod_id: int | None = None
    target_gtin: str | None = None
    bom_kind: str | None = None
    base_qty: float | None = None
    base_unit_code: str | None = None
    is_primary: int | None = None
    valid_from: date | None = None
    valid_to: date | None = None
    ware_id: int | None = None
    production_line: str | None = None
    comment_text: str | None = None
    updated_by: str | None = None


class BomLineRequest(BaseModel):
    line_no: int | None = None
    component_type: str = "RAW"
    component_articul: str | None = None
    component_mod_id: int | None = None
    component_name: str | None = None
    qty_per_base: float | None = None
    unit_code: str | None = None
    loss_percent: float | None = 0
    min_tolerance_pct: float | None = None
    max_tolerance_pct: float | None = None
    is_required: int | None = 1
    substitution_group: str | None = None
    replacement_ratio: float | None = None
    comment_text: str | None = None
    created_by: str | None = None
    updated_by: str | None = None


class BomLifecycleRequest(BaseModel):
    reason: str | None = None
    user_name: str | None = None


class BomCloneRequest(BaseModel):
    bom_code: str
    valid_from: date
    valid_to: date | None = None
    created_by: str | None = None


class BomCalculateRequest(BaseModel):
    planned_qty: float
    unit_code: str | None = None


class RightsGroupRequest(BaseModel):
    id: str
    name: str


class RightsUserGroupRequest(BaseModel):
    user_group: str
    pravo_admin_login: int | None = None


class RightsGrantRequest(BaseModel):
    right_name: str
    description: str | None = None


class MesProductionOrderCreateRequest(BaseModel):
    order_no: str
    target_articul: str
    planned_qty: float
    bom_id: int | None = None
    unit_code: str | None = "KG"
    ware_id: int | None = None
    production_line: str | None = None
    shift_id: str | None = None
    planned_start_at: datetime | None = None
    planned_finish_at: datetime | None = None
    source_system: str | None = None
    source_message_id: str | None = None
    idempotency_key: str | None = None
    comment_text: str | None = None
    created_by: str | None = None


class MesRawIssueRequest(BaseModel):
    uid_pallet: str | None = None
    raw_batch_id: int | None = None
    raw_articul: str | None = None
    quantity: float
    unit_code: str | None = "KG"
    source_location: str | None = None
    production_location: str | None = "MES_PROD"
    created_by: str | None = None


class MesCompletionPallet(BaseModel):
    uid_pallet: str
    pallet_no: int | None = None
    quantity: float | None = None
    pack_count: float | None = None
    sscc: str | None = None


class MesCompleteOrderRequest(BaseModel):
    prod_batch_no: str | None = None
    fact_qty: float
    unit_code: str | None = "KG"
    pallets: list[MesCompletionPallet] = Field(default_factory=list)
    idempotency_key: str | None = None
    created_by: str | None = None


class MesApplyWmsRequest(BaseModel):
    applied_by: str | None = None


class MesRetryMovementRequest(BaseModel):
    updated_by: str | None = None


class WarehouseSettingsUpdateRequest(BaseModel):
    flag_raw_material: int | None = None
    flag_production: int | None = None
    flag_production_buffer: int | None = None
    flag_finished_goods: int | None = None
    mes_enabled: int | None = None
    default_receive_cell: str | None = None
    default_issue_cell: str | None = None
    ware_comment: str | None = None


class ProductShipmentSettingsUpdateRequest(BaseModel):
    shipment_aging_hours: float | None = Field(default=None, ge=0)
    shipment_aging_comment: str | None = None


class CustomerShelfLifeRuleCreateRequest(BaseModel):
    customer_store_map_id: int | None = None
    articul: str | None = None
    product_group: str | None = None
    min_shelf_life_days: float | None = Field(default=None, ge=0)
    min_shelf_life_percent: float | None = Field(default=None, ge=0, le=100)
    rule_priority: int = 100
    active: int = 1
    valid_from: date | None = None
    valid_to: date | None = None
    created_by: str | None = None


class CustomerStackRuleCreateRequest(BaseModel):
    customer_store_map_id: int | None = None
    articul: str | None = None
    product_group: str | None = None
    pallet_case_qty: float | None = Field(default=None, ge=0)
    pallet_layer_qty: float | None = Field(default=None, ge=0)
    pallet_layer_count: float | None = Field(default=None, ge=0)
    max_pallet_weight: float | None = Field(default=None, ge=0)
    max_pallet_volume: float | None = Field(default=None, ge=0)
    max_pallet_height: float | None = Field(default=None, ge=0)
    pallet_type: str | None = None
    allow_top_stacking: int = 0
    must_be_separate_pallet: int = 0
    stack_compatibility_group: str | None = None
    rule_priority: int = 100
    active: int = 1
    valid_from: date | None = None
    valid_to: date | None = None
    created_by: str | None = None


class CustomerVehicleRuleCreateRequest(BaseModel):
    customer_store_map_id: int | None = None
    vehicle_type_id: int
    max_pallet_count: float | None = Field(default=None, ge=0)
    max_weight: float | None = Field(default=None, ge=0)
    max_volume: float | None = Field(default=None, ge=0)
    split_order_by_capacity: int = 1
    rule_priority: int = 100
    active: int = 1
    valid_from: date | None = None
    valid_to: date | None = None
    created_by: str | None = None


class VehicleTypeCreateRequest(BaseModel):
    vehicle_type_code: str
    vehicle_type_name: str
    max_pallet_count: float | None = Field(default=None, ge=0)
    max_weight: float | None = Field(default=None, ge=0)
    max_volume: float | None = Field(default=None, ge=0)
    active: int = 1
    created_by: str | None = None


class PickingPlanCreateRequest(BaseModel):
    customer_order_id: int
    plan_strategy: str = "FEFO"
    created_by: str | None = None


class PickingPlanCancelRequest(BaseModel):
    updated_by: str | None = None


class PickRouteUpsertRequest(BaseModel):
    pick_route_id: int | None = None
    route_code: str
    route_name: str | None = None
    ware_id: int
    route_kind: str = "PICK"
    active: int = 1
    updated_by: str | None = None


class PickRouteCellUpsertRequest(BaseModel):
    pick_route_cell_id: int | None = None
    pick_route_id: int
    cell_code: str
    pick_sequence: float
    zone_code: str | None = None
    aisle_code: str | None = None
    side_code: str | None = None
    level_no: float | None = None
    active: int = 1
    updated_by: str | None = None


class PickFaceUpsertRequest(BaseModel):
    pick_face_id: int | None = None
    ware_id: int
    cell_code: str
    pick_face_code: str | None = None
    pick_face_type: str = "REGULAR"
    pick_route_id: int | None = None
    pick_route_cell_id: int | None = None
    pick_sequence: float | None = None
    min_case_qty: float | None = None
    max_case_qty: float | None = None
    replenishment_trigger_qty: float | None = None
    max_weight: float | None = None
    max_volume: float | None = None
    allow_dynamic_assignment: int = 0
    active: int = 1
    comment_text: str | None = None
    updated_by: str | None = None


class PickFaceArticulUpsertRequest(BaseModel):
    pick_face_articul_id: int | None = None
    pick_face_id: int | None = None
    articul: str
    priority: float = 100
    min_qty: float | None = None
    max_qty: float | None = None
    case_pick_enabled: int = 1
    active: int = 1
    valid_from: date | None = None
    valid_to: date | None = None
    updated_by: str | None = None


class PickWaveCreateRequest(BaseModel):
    wave_code: str | None = None
    wave_name: str | None = None
    ware_id: int | None = None
    route_id: int | None = None
    dock_id: int | None = None
    planned_start_at: datetime | None = None
    planned_finish_at: datetime | None = None
    max_customers: int = Field(default=30, ge=1, le=500)
    created_by: str | None = None


class PickWaveAddPlanRequest(BaseModel):
    pick_plan_id: int
    created_by: str | None = None


class PickWaveActionRequest(BaseModel):
    reason: str | None = None
    updated_by: str | None = None
