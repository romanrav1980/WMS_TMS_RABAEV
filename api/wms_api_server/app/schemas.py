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


class ResourceEquipmentCreateRequest(BaseModel):
    equipment_code: str
    equipment_type: str
    equipment_name: str | None = None
    ware_id: int | None = None
    home_zone_code: str | None = None
    capacity_class: str | None = None
    service_status: str | None = "ACTIVE"
    active: int = 1
    created_by: str | None = None


class ResourceCreateRequest(BaseModel):
    resource_code: str
    resource_name: str
    resource_type: str
    resource_class: str | None = None
    equipment_id: int | None = None
    user_id: str | None = None
    team_code: str | None = None
    ware_id: int | None = None
    zone_code: str | None = None
    status: str | None = "AVAILABLE"
    active: int = 1
    created_by: str | None = None


class ResourceShiftCreateRequest(BaseModel):
    shift_code: str
    shift_date: date
    start_at: datetime
    finish_at: datetime
    ware_id: int | None = None
    site_code: str | None = None
    status: str | None = "PLANNED"
    created_by: str | None = None


class ResourceSessionLoginRequest(BaseModel):
    shift_id: int
    resource_id: int
    equipment_id: int | None = None
    operator_user_id: str | None = None
    terminal_id: str | None = None
    zone_code: str | None = None
    created_by: str | None = None


class ResourceSessionStatusRequest(BaseModel):
    updated_by: str | None = None
    reason: str | None = None


class ResourceTsdLoginRequest(BaseModel):
    driver_code: str | None = None
    password: str | None = None
    barcode: str | None = None
    equipment_code: str | None = None
    terminal_id: str | None = None
    ware_id: int | None = None
    zone_code: str | None = None


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
    target_ware_id: int | None = None
    target_cell: str | None = "FG_RECEIVE"


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


class RawMaterialSkuSettingsUpdateRequest(BaseModel):
    is_raw_material: int | None = None
    raw_group: str | None = None
    mercury_required: int | None = None
    lot_required: int | None = None
    expiry_required: int | None = None
    min_stock_qty: float | None = Field(default=None, ge=0)
    target_stock_qty: float | None = Field(default=None, ge=0)
    allowed_ware_ids: str | None = None
    allowed_zone_codes: str | None = None
    technologist_comment: str | None = None
    active: int | None = None
    updated_by: str | None = None


class FinishedGoodsSkuSettingsUpdateRequest(BaseModel):
    is_finished_goods: int | None = None
    product_group: str | None = None
    gtin: str | None = None
    crpt_required: int | None = None
    aggregation_required: int | None = None
    sscc_required: int | None = None
    pallet_label_required: int | None = None
    quality_hold_required: int | None = None
    default_pallet_case_qty: float | None = Field(default=None, ge=0)
    default_layer_qty: float | None = Field(default=None, ge=0)
    default_layer_count: float | None = Field(default=None, ge=0)
    technologist_comment: str | None = None
    active: int | None = None
    updated_by: str | None = None


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


class CustomerProductRuleCreateRequest(BaseModel):
    customer_store_map_id: int | None = None
    articul: str | None = None
    product_group: str | None = None
    min_shelf_life_days: float | None = Field(default=None, ge=0)
    min_shelf_life_percent: float | None = Field(default=None, ge=0, le=100)
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


class VehicleTypeCreateRequest(BaseModel):
    vehicle_type_code: str
    vehicle_type_name: str
    max_pallet_count: float | None = Field(default=None, ge=0)
    max_weight: float | None = Field(default=None, ge=0)
    max_volume: float | None = Field(default=None, ge=0)
    active: int = 1
    created_by: str | None = None


class CustomerCreateRequest(BaseModel):
    customer_code: str
    customer_name: str
    customer_type: str = "STORE"
    inn: str | None = None
    kpp: str | None = None
    gln: str | None = None
    edi_id: str | None = None
    default_vehicle_type_id: int | None = None
    split_order_by_vehicle_capacity: int = 0
    default_min_shelf_life_days: float | None = Field(default=None, ge=0)
    default_min_shelf_life_percent: float | None = Field(default=None, ge=0, le=100)
    active: int = 1
    created_by: str | None = None


class CustomerUpdateRequest(BaseModel):
    customer_code: str | None = None
    customer_name: str | None = None
    customer_type: str | None = None
    inn: str | None = None
    kpp: str | None = None
    gln: str | None = None
    edi_id: str | None = None
    default_vehicle_type_id: int | None = None
    split_order_by_vehicle_capacity: int | None = None
    default_min_shelf_life_days: float | None = Field(default=None, ge=0)
    default_min_shelf_life_percent: float | None = Field(default=None, ge=0, le=100)
    active: int | None = None
    updated_by: str | None = None


class CustomerAddressCreateRequest(BaseModel):
    address_type: str = "DELIVERY"
    address_text: str
    city: str | None = None
    region: str | None = None
    postal_code: str | None = None
    gln: str | None = None
    vehicle_type_id: int | None = None
    max_pallet_count: float | None = Field(default=None, ge=0)
    max_weight: float | None = Field(default=None, ge=0)
    max_volume: float | None = Field(default=None, ge=0)
    split_order_by_capacity: int = 1
    active: int = 1
    created_by: str | None = None


class PickingPlanCreateRequest(BaseModel):
    customer_order_id: int
    plan_strategy: str = "FEFO"
    created_by: str | None = None


class PickingPlanCancelRequest(BaseModel):
    updated_by: str | None = None


class WarehouseTopologyCreateRequest(BaseModel):
    ware_id: int
    topology_code: str
    topology_name: str | None = None
    comment_text: str | None = None
    created_by: str | None = None


class WarehouseTopologyGenerateRequest(BaseModel):
    zone_code: str = "PICK"
    zone_name: str | None = "Зона отбора"
    section_code: str = "S01"
    aisle_prefix: str = "A"
    aisle_count: int = Field(default=6, ge=1, le=80)
    bays_per_aisle: int = Field(default=24, ge=1, le=300)
    levels: int = Field(default=1, ge=1, le=10)
    start_aisle_no: int = Field(default=1, ge=1)
    start_x: float = 8
    start_y: float = 8
    aisle_spacing_m: float = 5
    bay_spacing_m: float = 1.4
    pick_face_depth_m: float = 1.1
    cell_width_m: float = 1.1
    cell_height_m: float = 1.4
    max_volume_m3: float | None = 1.5
    max_weight_kg: float | None = 900
    create_both_sides: int = 1
    cell_kind: str = "PICK_FACE"
    overwrite_existing: int = 0
    updated_by: str | None = None


class TopologyCellPatchRequest(BaseModel):
    x: float | None = None
    y: float | None = None
    z: float | None = None
    zone_code: str | None = None
    section_code: str | None = None
    aisle_code: str | None = None
    side_code: str | None = None
    cell_kind: str | None = None
    active: int | None = None
    updated_by: str | None = None


class PickRouteBuildRequest(BaseModel):
    topology_id: int
    pick_route_id: int | None = None
    route_code: str
    route_name: str | None = None
    ware_id: int
    zone_code: str | None = None
    aisle_codes: list[str] | None = None
    cell_ids: list[int] | None = None
    route_pattern: str = "Z"
    side_order: list[str] = Field(default_factory=lambda: ["LEFT", "RIGHT"])
    start_side: str = "LEFT"
    strict_sequence: int = 1
    updated_by: str | None = None


class TopologyGateGenerateRequest(BaseModel):
    gate_count: int = Field(default=10, ge=1, le=80)
    gate_prefix: str = "G"
    gate_kind: str = "SHIPPING"
    start_x: float = 4
    start_y: float = 34
    spacing_m: float = 4.2
    staging_zone_code: str | None = "DOCK"
    vehicle_class: str | None = None
    overwrite_existing: int = 0
    updated_by: str | None = None


class TopologyDistanceRecalculateRequest(BaseModel):
    flow_kind: str = "BOTH"
    picker_speed_mps: float = Field(default=1.1, gt=0)
    reachtruck_speed_mps: float = Field(default=1.8, gt=0)
    use_reachtruck_for_storage: int = 1
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
    use_articul_replenish_rule: int = 1
    replenishment_method: str = "IMMEDIATE"
    replenishment_release_policy: str = "LAYER_TRIGGER"
    replenishment_qty_mode: str = "FILL_TO_VOLUME"
    min_trigger_box_qty: float | None = None
    min_trigger_layer_qty: float | None = None
    safety_layer_qty: float | None = None
    boxes_per_layer: float | None = None
    boxes_per_pallet: float | None = None
    box_volume_m3: float | None = None
    allow_partial_pallet: int = 1
    predictive_buffer_min: float | None = None
    pick_rate_source: str = "MIXED"
    recheck_on_pick_event: int = 1
    active: int = 1
    valid_from: date | None = None
    valid_to: date | None = None
    updated_by: str | None = None


class ArticulReplenishmentRuleUpsertRequest(BaseModel):
    articul_replenish_rule_id: int | None = None
    articul: str
    replenishment_method: str = "MINIMAX"
    replenishment_release_policy: str = "LAYER_TRIGGER"
    replenishment_qty_mode: str = "FILL_TO_VOLUME"
    min_trigger_box_qty: float | None = None
    min_trigger_layer_qty: float | None = 1
    safety_layer_qty: float | None = None
    boxes_per_layer: float | None = None
    boxes_per_pallet: float | None = None
    box_volume_m3: float | None = None
    allow_partial_pallet: int = 1
    predictive_buffer_min: float | None = None
    pick_rate_source: str = "MIXED"
    recheck_on_pick_event: int = 1
    active: int = 1
    comment_text: str | None = None
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


class PickTaskCompleteRequest(BaseModel):
    fact_qty: float | None = Field(default=None, ge=0)
    scanned_pallet: str | None = None
    scanned_from_cell: str | None = None
    scanned_to_cell: str | None = None
    adjust_pick_face_stock: bool = False
    completed_by: str | None = None


class PickWaveStagingReleaseRequest(BaseModel):
    to_cell: str
    updated_by: str | None = None


class CasePickTaskActionRequest(BaseModel):
    resource_id: int | None = None
    resource_session_id: int | None = None
    equipment_id: int | None = None
    actor: str | None = None
    reason: str | None = None


class CasePickLineConfirmRequest(BaseModel):
    fact_qty: float | None = Field(default=None, ge=0)
    scan_cell: str | None = None
    scan_product: str | None = None
    scan_box: str | None = None
    scan_container: str | None = None
    offline_event_id: str | None = None
    resource_id: int | None = None
    resource_session_id: int | None = None
    equipment_id: int | None = None
    actor: str | None = None


class CasePickLineShortRequest(BaseModel):
    picked_qty: float | None = Field(default=None, ge=0)
    short_qty: float | None = Field(default=None, ge=0)
    reason_text: str | None = None
    offline_event_id: str | None = None
    resource_id: int | None = None
    resource_session_id: int | None = None
    equipment_id: int | None = None
    actor: str | None = None


class CasePickTransferRequest(BaseModel):
    to_resource_id: int
    to_resource_session_id: int | None = None
    to_equipment_id: int | None = None
    reason: str | None = None
    actor: str | None = None


class CasePickShortDecisionRequest(BaseModel):
    reason_text: str | None = None
    actor: str | None = None


class PalletTypeUpsertRequest(BaseModel):
    pallet_type_id: int | None = None
    pallet_type_code: str
    pallet_type_name: str
    load_unit_class: str = "PALLET"
    default_volume_m3: float | None = Field(default=None, ge=0)
    default_weight_kg: float | None = Field(default=None, ge=0)
    length_mm: float | None = Field(default=None, ge=0)
    width_mm: float | None = Field(default=None, ge=0)
    height_mm: float | None = Field(default=None, ge=0)
    default_max_client_pallets: int = Field(default=1, ge=1, le=3)
    active: int = 1
    updated_by: str | None = None


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
    qty: float = Field(ge=0)
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


class StockReservationPromoteRequest(BaseModel):
    reservation_scope: str = "PALLET"
    ware_id: int
    cell: str
    batch_id: str | None = None
    prod_batch_id: int | None = None
    uid_pallet: str | None = None
    sscc: str | None = None
    qty: float | None = Field(default=None, ge=0)
    updated_by: str | None = None


class StockReservationStatusRequest(BaseModel):
    reason: str | None = None
    updated_by: str | None = None


class MesRawSupplyCalculateRequest(BaseModel):
    calculated_by: str | None = None


class MesReleaseToProductionRequest(BaseModel):
    to_ware_id: int | None = None
    to_cell: str = "MES_PROD"
    allow_partial: int = 0
    created_by: str | None = None


class MesRawTransferTaskConfirmRequest(BaseModel):
    fact_qty: float | None = Field(default=None, ge=0)
    confirmed_by: str | None = None


class MesRawTransferTaskCancelRequest(BaseModel):
    reason: str | None = None
    cancelled_by: str | None = None


class WarehouseTaskStatusRequest(BaseModel):
    assigned_to: str | None = None
    resource_id: int | None = None
    resource_session_id: int | None = None
    equipment_id: int | None = None
    fact_qty: float | None = Field(default=None, ge=0)
    scanned_pallet: str | None = None
    scanned_from_cell: str | None = None
    scanned_to_cell: str | None = None
    reason: str | None = None


# ---------------------------------------------------------------------------
# Large warehouse map drafts
# ---------------------------------------------------------------------------

class WarehouseMapGrid(BaseModel):
    aisle_count: int = Field(default=35, ge=1, le=500)
    slots_per_aisle: int = Field(default=90, ge=1, le=1000)
    levels: int = Field(default=6, ge=1, le=50)


class WarehouseMapDraftCreateRequest(BaseModel):
    draft_name: str = "Рисование карты больших складов"
    grid: WarehouseMapGrid = Field(default_factory=WarehouseMapGrid)
    roles_base64: str | None = None
    created_by: str | None = None


class WarehouseMapDraftCellsPatchRequest(BaseModel):
    roles_base64: str
    expected_revision: int | None = Field(default=None, ge=1)
    updated_by: str | None = None


class WarehouseMapDraftMetadataPatchRequest(BaseModel):
    expected_revision: int | None = Field(default=None, ge=1)
    draft_metadata: dict[str, Any] | None = None
    canvas_objects: list[dict[str, Any]] | None = None
    passages: list[dict[str, Any]] | None = None
    camera_links: list[dict[str, Any]] | None = None
    updated_by: str | None = None


class WarehouseMapSelectionRequest(BaseModel):
    aisle_from: int = Field(ge=1)
    aisle_to: int = Field(ge=1)
    slot_from: int = Field(ge=1)
    slot_to: int = Field(ge=1)
    level_from: int = Field(default=1, ge=1)
    level_to: int = Field(default=1, ge=1)


class WarehouseMapDraftRouteBuildRequest(BaseModel):
    selection: WarehouseMapSelectionRequest
    route_code: str = "DRAFT-PICK"
    route_name: str | None = None
    route_pattern: str = Field(default="Z", pattern="^(LINEAR|Z|U_SHAPE|P_SHAPE|MANUAL)$")
    start_sequence: float = 1
    step: float = Field(default=1, gt=0)
    expected_revision: int | None = Field(default=None, ge=1)
    updated_by: str | None = None


class WarehouseMapDraftRoutePatchRequest(BaseModel):
    route_rows: list[dict[str, Any]] = Field(default_factory=list, max_length=20000)
    expected_revision: int | None = Field(default=None, ge=1)
    updated_by: str | None = None


class WarehouseMapDraftLoadFromDbRequest(BaseModel):
    canvas_id: int = Field(gt=0)
    draft_name: str | None = Field(default=None, max_length=200)
    created_by: str | None = None


class WarehouseMapDraftSaveToDbRequest(BaseModel):
    ware_id: int = Field(gt=0)
    canvas_id: int | None = Field(default=None, gt=0)
    canvas_code: str | None = Field(default=None, max_length=80)
    canvas_name: str | None = Field(default=None, max_length=200)
    camera_code: str | None = Field(default=None, max_length=80)
    camera_name: str | None = Field(default=None, max_length=200)
    comment_text: str | None = Field(default=None, max_length=1000)
    expected_revision: int | None = Field(default=None, ge=1)
    idempotency_key: str | None = Field(default=None, max_length=120)
    updated_by: str | None = None


class WarehouseMapDraftProjectionSaveRequest(BaseModel):
    ware_id: int = Field(gt=0)
    topology_code: str | None = Field(default=None, max_length=80)
    topology_name: str | None = Field(default=None, max_length=200)
    comment_text: str | None = Field(default=None, max_length=1000)
    expected_revision: int | None = Field(default=None, ge=1)
    idempotency_key: str | None = Field(default=None, max_length=120)
    updated_by: str | None = None


class WarehouseMapDraftRouteSaveToDbRequest(BaseModel):
    ware_id: int = Field(gt=0)
    topology_id: int | None = Field(default=None, gt=0)
    route_code: str | None = Field(default=None, max_length=80)
    route_name: str | None = Field(default=None, max_length=200)
    route_pattern: str | None = Field(default=None, pattern="^(LINEAR|Z|U_SHAPE|P_SHAPE|MANUAL)$")
    strict_sequence: int = Field(default=1, ge=0, le=1)
    expected_revision: int | None = Field(default=None, ge=1)
    idempotency_key: str | None = Field(default=None, max_length=120)
    updated_by: str | None = None


class WarehouseMapDraftOraclePublishRequest(BaseModel):
    canvas_id: int | None = Field(default=None, gt=0)
    topology_id: int | None = Field(default=None, gt=0)
    pick_route_id: int | None = Field(default=None, gt=0)
    expected_revision: int | None = Field(default=None, ge=1)
    idempotency_key: str | None = Field(default=None, max_length=120)
    published_by: str | None = Field(default=None, max_length=50)


class WarehouseMapBulkRoleRequest(BaseModel):
    selection: WarehouseMapSelectionRequest | None = None
    selections: list[WarehouseMapSelectionRequest] | None = None
    role: str
    updated_by: str | None = None


class WarehouseMapCellRef(BaseModel):
    aisle: int = Field(ge=1)
    slot: int = Field(ge=1)
    level: int = Field(default=1, ge=1)


class WarehouseMapPickFaceAddressRequest(BaseModel):
    selection: WarehouseMapSelectionRequest
    anchor_cell: WarehouseMapCellRef
    focus_cell: WarehouseMapCellRef
    aisle_no: int = Field(ge=1)
    start_pick_no: int = Field(default=1, ge=1)
    step: int = Field(default=1, ge=1)
    direction: str = Field(default="START_TO_END", pattern="^(START_TO_END|END_TO_START)$")
    side: str | None = Field(default=None, pattern="^(LEFT|RIGHT)$")
    code_mask: str = "A{aisle}-P{pick_no}-L{level}"
    updated_by: str | None = None


class WarehouseMapSmallPickFaceGenerateRequest(BaseModel):
    physical_cell: WarehouseMapCellRef | None = None
    physical_cells: list[WarehouseMapCellRef] | None = None
    fraction_cell_count: int = Field(ge=2, le=9)
    sub_level_count: int = Field(default=1, ge=1, le=9)
    sub_column_count: int = Field(default=3, ge=1, le=9)
    order_mode: str = Field(default="SUB_LEVEL_THEN_COLUMN", pattern="^(SUB_LEVEL_THEN_COLUMN|COLUMN_THEN_SUB_LEVEL)$")
    start_order: int = Field(default=1, ge=1)
    step: int = Field(default=1, ge=1)
    side: str | None = Field(default=None, pattern="^(LEFT|RIGHT)$")
    code_mask: str = "{physical_cell}-F{sub_level}{sub_column}"
    updated_by: str | None = None


class WarehouseMapSmallPickFacePatchRequest(BaseModel):
    logical_cell_code: str | None = None
    sub_level: int | None = Field(default=None, ge=1, le=9)
    sub_column: int | None = Field(default=None, ge=1, le=9)
    pick_order: int | None = Field(default=None, ge=1)
    side: str | None = Field(default=None, pattern="^(LEFT|RIGHT)$")
    active: int | None = Field(default=None, ge=0, le=1)
    updated_by: str | None = None


class WarehouseMapSmallPickFaceRenumberRequest(BaseModel):
    physical_cell: WarehouseMapCellRef
    order_mode: str = Field(default="SUB_LEVEL_THEN_COLUMN", pattern="^(SUB_LEVEL_THEN_COLUMN|COLUMN_THEN_SUB_LEVEL)$")
    start_order: int = Field(default=1, ge=1)
    step: int = Field(default=1, ge=1)
    updated_by: str | None = None


class WarehouseMapStorageSlotGenerateRequest(BaseModel):
    physical_cell: WarehouseMapCellRef | None = None
    physical_cells: list[WarehouseMapCellRef] | None = None
    fraction_cell_count: int = Field(default=1, ge=1, le=3)
    sub_level_count: int = Field(default=1, ge=1, le=1)
    sub_column_count: int = Field(default=1, ge=1, le=3)
    start_order: int = Field(default=1, ge=1)
    step: int = Field(default=1, ge=1)
    code_mask: str = "{physical_cell}-ST{sub_column}"
    updated_by: str | None = None


class WarehouseMapStorageSlotPatchRequest(BaseModel):
    slot_code: str | None = None
    storage_order: int | None = Field(default=None, ge=1)
    max_pallet_count: float | None = Field(default=None, ge=0)
    max_weight_kg: float | None = Field(default=None, ge=0)
    max_volume_m3: float | None = Field(default=None, ge=0)
    capacity_json: dict[str, Any] | None = None
    active: int | None = Field(default=None, ge=0, le=1)
    updated_by: str | None = None


class WarehouseMapCanvasCreateRequest(BaseModel):
    canvas_code: str | None = Field(default=None, max_length=80)
    canvas_name: str | None = Field(default=None, max_length=200)
    topology_id: int | None = None
    grid_cell_width_m: float = Field(default=1.2, gt=0)
    grid_cell_depth_m: float = Field(default=0.8, gt=0)
    levels: int = Field(default=6, ge=1, le=50)
    viewport_json: dict[str, Any] | None = None
    renderer_state_json: dict[str, Any] | None = None
    comment_text: str | None = Field(default=None, max_length=1000)
    created_by: str | None = None


class WarehouseMapCameraCreateRequest(BaseModel):
    camera_code: str = Field(max_length=80)
    camera_name: str = Field(max_length=200)
    camera_kind: str = Field(default="DRY", pattern="^(DRY|COLD|FREEZER|DOCK|SERVICE|MIXED)$")
    origin_x_m: float = 0
    origin_y_m: float = 0
    origin_z_m: float = 0
    width_m: float = Field(gt=0)
    depth_m: float = Field(gt=0)
    height_m: float = Field(gt=0)
    grid_cell_width_m: float = Field(default=1.2, gt=0)
    grid_cell_depth_m: float = Field(default=0.8, gt=0)
    levels: int = Field(default=6, ge=1, le=50)
    boundary_json: dict[str, Any] | None = None
    default_passage_width_m: float = Field(default=3, gt=0)
    default_aisle_spacing_m: float | None = Field(default=None, gt=0)
    created_by: str | None = None


class WarehouseMapCameraCloneRequest(BaseModel):
    camera_code: str | None = Field(default=None, max_length=80)
    camera_name: str | None = Field(default=None, max_length=200)
    origin_x_m: float | None = None
    origin_y_m: float | None = None
    origin_z_m: float | None = None
    created_by: str | None = None


class WarehouseMapArchiveRequest(BaseModel):
    reason: str | None = Field(default=None, max_length=500)
    updated_by: str | None = None


class WarehouseMapObjectPatchItem(BaseModel):
    object_code: str | None = Field(default=None, max_length=100)
    object_kind: str = Field(pattern="^(CELL_BLOCK|WALL|COLUMN|PASSAGE|ZONE|LABEL|MEASURE|DOCK|SERVICE|BACKGROUND_REF)$")
    object_name: str | None = Field(default=None, max_length=200)
    topology_cell_id: int | None = None
    level_no: int | None = Field(default=None, ge=1)
    x_m: float = 0
    y_m: float = 0
    z_m: float = 0
    width_m: float | None = Field(default=None, gt=0)
    depth_m: float | None = Field(default=None, gt=0)
    height_m: float | None = Field(default=None, gt=0)
    angle_deg: float = 0
    geometry_json: dict[str, Any] | None = None
    style_json: dict[str, Any] | None = None


class WarehouseMapObjectsPatchRequest(BaseModel):
    objects: list[WarehouseMapObjectPatchItem] = Field(default_factory=list, max_length=5000)
    updated_by: str | None = None


class WarehouseMapPassagePatchItem(BaseModel):
    passage_code: str | None = Field(default=None, max_length=80)
    passage_name: str | None = Field(default=None, max_length=200)
    passage_kind: str = Field(default="PICK_AISLE", pattern="^(PICK_AISLE|CROSS_AISLE|MAIN_TRANSPORT|DOCK_PASSAGE|SERVICE)$")
    x1_m: float = 0
    y1_m: float = 0
    z1_m: float = 0
    x2_m: float = 0
    y2_m: float = 0
    z2_m: float = 0
    width_m: float = Field(default=3, gt=0)
    aisle_spacing_m: float | None = Field(default=None, gt=0)
    geometry_json: dict[str, Any] | None = None
    allowed_resource_mask: str | None = Field(default=None, max_length=200)


class WarehouseMapPassagesPatchRequest(BaseModel):
    passages: list[WarehouseMapPassagePatchItem] = Field(default_factory=list, max_length=1000)
    updated_by: str | None = None


class WarehouseMapCameraLinkPatchItem(BaseModel):
    link_code: str | None = Field(default=None, max_length=80)
    link_kind: str = Field(default="DOOR", pattern="^(DOOR|CORRIDOR|GATE|LIFT|STAGING_PASSAGE|SERVICE)$")
    from_camera_id: int
    to_camera_id: int
    from_point_x_m: float = 0
    from_point_y_m: float = 0
    from_point_z_m: float = 0
    to_point_x_m: float = 0
    to_point_y_m: float = 0
    to_point_z_m: float = 0
    distance_m: float = Field(default=0, ge=0)
    travel_time_sec: float | None = Field(default=None, ge=0)
    direction_code: str = Field(default="BOTH", pattern="^(BOTH|FROM_TO|TO_FROM)$")
    allowed_resource_mask: str | None = Field(default=None, max_length=200)


class WarehouseMapCameraLinksPatchRequest(BaseModel):
    camera_links: list[WarehouseMapCameraLinkPatchItem] = Field(default_factory=list, max_length=1000)
    updated_by: str | None = None


# ---------------------------------------------------------------------------
# Transport dispatch — Phase 1 (manual operator assignment)
# ---------------------------------------------------------------------------

class TransportTaskCreateRequest(BaseModel):
    transtype: str = Field(..., description="Тип транспорта (TRANSTYPE), например '10', '15', '20реф'")
    shipment_date: date = Field(..., description="Дата отгрузки")


class TransportTaskUpdateRequest(BaseModel):
    transport: str | None = None        # гос. номер ТС
    voditel_id: int | None = None       # ID водителя из RRL_TR_VODITEL
    dock: str | None = None             # докстанция
    shipment_time: str | None = None    # запланированное время отгрузки HH:MM
    shipment_date: date | None = None   # дата отгрузки
    transtype: str | None = None        # тип транспорта (TRANSTYPE)
    primechanie: str | None = None      # примечание диспетчера


class TransportStAssignRequest(BaseModel):
    st_numbers: list[str] = Field(..., min_length=1, description="Список номеров СТ для назначения в рейс")
    updated_by: str | None = None


class TransportStLoadTypeRequest(BaseModel):
    load_type: str = Field(
        default="",
        description="Способ погрузки: '' = стандарт, 'Г' = гос. борт, 'П' = прицеп",
        pattern="^(|Г|П)$",
    )


class TransportStOrderRequest(BaseModel):
    ord: int = Field(..., ge=0, description="Порядковый номер адреса доставки в рейсе (ORD)")


# ---------------------------------------------------------------------------
# VRP / Planner (Sprint 8)
# ---------------------------------------------------------------------------

class VrpRouteStop(BaseModel):
    st_number: str
    addr: str | None
    lat: float | None
    lon: float | None
    pallets: int
    weight_kg: float
    ware_id: int
    unload_norm_min: int
    tw_from: int
    tw_to: int
    tw_strict: bool


class VrpRouteItem(BaseModel):
    vehicle_id: int
    vehicle_num: str
    vehicle_type: str
    max_pallets: int
    total_pallets: int
    total_kg: float
    total_km: float
    total_duration_min: int
    utilization_pct: float
    stops: list[VrpRouteStop]


class VrpPlanResponse(BaseModel):
    plan_id: int | None = None
    routes: list[VrpRouteItem]
    unassigned_sts: list[str]
    total_km: float
    fleet_utilization_pct: float
    tw_violations: int
    score: float
    solver_used: str
    solve_time_ms: int


class VrpSolveRequest(BaseModel):
    plan_date: date = Field(..., description="Дата СТ для планирования")
    ware_ids: list[int] | None = None
    transport_type: str | None = None
    time_limit_s: int = Field(default=30, ge=5, le=120)
    source: str = Field(default="auto", description="Провайдер матрицы: auto|haversine|osrm|valhalla")
    solver: str = Field(default="auto", description="Решатель: auto|ortools|cluster|savings")


class VrpApplyRequest(BaseModel):
    plan_id: int = Field(..., description="ID плана из RRL_PLANNER_PLANS для применения")
    shipment_date: date = Field(..., description="Дата отгрузки создаваемых рейсов")
    dock: str | None = None


# ---------------------------------------------------------------------------
# Sprint 11 — ARM: модель операций и нормативы
# ---------------------------------------------------------------------------

class OperationPlan(BaseModel):
    op_id: int
    tt_id: int
    operation_code: str
    ord: int
    duration_min: float
    plan_start: str | None = None
    plan_end: str | None = None
    fact_start: str | None = None
    fact_end: str | None = None
    delta_min: float | None = None
    note: str | None = None


class OperationFactUpdate(BaseModel):
    fact_start: str | None = Field(None, description="ISO datetime YYYY-MM-DD HH:MM")
    fact_end: str | None = Field(None, description="ISO datetime YYYY-MM-DD HH:MM")
    note: str | None = None


class VehicleGanttDay(BaseModel):
    vehicle_id: int
    vehicle_num: str
    vehicle_type: str
    operations: list[OperationPlan]


# ---------------------------------------------------------------------------
# Sprint 15 — Биллинг: создание счёта
# ---------------------------------------------------------------------------

class BillingOrderCreate(BaseModel):
    company: str = Field(..., description="Транспортная компания (перевозчик)")
    date_from: str = Field(..., description="Начало периода YYYY-MM-DD")
    date_to: str = Field(..., description="Конец периода YYYY-MM-DD")


class BillingAddTasksRequest(BaseModel):
    tt_ids: list[int] = Field(..., description="Список ID рейсов для привязки к заказу")


class BillingOrder(BaseModel):
    order_id: int
    num: str | None = None
    company: str | None = None
    date_of_order: str | None = None
    date_from: str | None = None
    date_to: str | None = None
    closed: int = 0
    payed: int = 0
    task_count: int | None = None
    total_price: float | None = None
    num_plat: str | None = None


class PriceUpdateRequest(BaseModel):
    price: float = Field(..., ge=0, description="Новая стоимость рейса в рублях")
