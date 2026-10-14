from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .middleware.api_audit import ApiAuditMiddleware
from .modules.master_data import public as sku_receiving
from .modules.integrations import public as sap_retail
from .modules.inventory import public as inventory_receiving
from .modules.fulfillment import public as sap_fulfillment
from .routers import (
    admin_auth,
    admin_rights,
    api_audit,
    bom,
    case_pick,
    customer_orders,
    customer_rules,
    finished_goods,
    health,
    mes,
    picking,
    production,
    products,
    raw_material,
    resource_management,
    slow_sql,
    stock_reservations,
    traceability,
    transport,
    tserver,
    warehouse_map_drafts,
    warehouse_map,
    warehouse_topology,
    warehouse_tasks,
    warehouses,
)
from .routers import users as users_router
from . import driver_workspace_composition as driver_mobile
from .routers import notifications
from .routers import transport_kpi
from .routers import gps
from .routers import transport_tariffs
from .routers import export_1c
from .routers import maintenance


from .auth import require_permission, PICK_WAVE_VIEW_PERMISSION, get_current_admin
from .modules.resources import public as resource_qualification

settings = get_settings()

app = FastAPI(title=settings.api_title, version=settings.api_version)
inventory_receiving.install_stock_error_handlers(app)
app.include_router(resource_qualification.qualification_router)
app.dependency_overrides[resource_qualification.resource_view] = require_permission("resource_management_view")
app.dependency_overrides[resource_qualification.qualification_edit] = require_permission("warehouse_settings_edit")
app.dependency_overrides[resource_qualification.resource_position_user] = get_current_admin
app.dependency_overrides[resource_qualification.resource_dispatch_user] = require_permission("resource_dispatch_manage")
from .resource_composition import build_resource_qualification
app.dependency_overrides[resource_qualification.qualification_service] = build_resource_qualification
app.dependency_overrides[sap_fulfillment.store_order_service] = sap_fulfillment.build_store_order_service
app.dependency_overrides[sap_fulfillment.preparation_service] = sap_fulfillment.build_preparation_service
app.include_router(sap_fulfillment.router)
app.dependency_overrides[sap_fulfillment.execution_service] = sap_fulfillment.build_execution_service
app.include_router(sap_fulfillment.execution_router)
app.dependency_overrides[sku_receiving.policy_service] = sku_receiving.build_policy_service
app.dependency_overrides[sap_retail.artmas_service] = sap_retail.build_artmas_service
app.include_router(sku_receiving.router)
from .replenishment_composition import build_minimax_service
app.include_router(inventory_receiving.minimax_router)
app.dependency_overrides[inventory_receiving.minimax_view]=require_permission("pick_wave_view")
app.dependency_overrides[inventory_receiving.minimax_edit]=require_permission("pick_wave_launch")
app.dependency_overrides[inventory_receiving.minimax_service]=build_minimax_service
from .modules.resources import public as reach_shift_module
app.include_router(reach_shift_module.reach_shift_router)
app.dependency_overrides[reach_shift_module.reach_shift_view]=require_permission("resource_shift_view")
app.dependency_overrides[reach_shift_module.reach_shift_edit]=require_permission("resource_shift_edit")
app.dependency_overrides[reach_shift_module.reach_shift_service]=reach_shift_module.build_reach_shifts
app.include_router(inventory_receiving.investigation_router)
app.dependency_overrides[inventory_receiving.investigation_view]=require_permission("inventory_task_view")
app.dependency_overrides[inventory_receiving.investigation_edit]=require_permission("case_pick_short_approve")
app.dependency_overrides[inventory_receiving.camera_edit]=require_permission("warehouse_settings_edit")
app.dependency_overrides[inventory_receiving.investigation_service]=inventory_receiving.build_short_investigation
app.include_router(inventory_receiving.pool_router)
app.dependency_overrides[inventory_receiving.pool_view]=require_permission("stock_reservation_view")
app.dependency_overrides[inventory_receiving.pool_edit]=require_permission("stock_reservation_edit")
app.dependency_overrides[inventory_receiving.pool_service]=inventory_receiving.build_pool_service
app.include_router(sku_receiving.allocation_router)
app.dependency_overrides[sku_receiving.allocation_policy_view]=require_permission("stock_reservation_view")
app.dependency_overrides[sku_receiving.allocation_policy_edit]=require_permission("warehouse_settings_edit")
app.dependency_overrides[sku_receiving.allocation_policy_service]=sku_receiving.build_allocation_policy

app.include_router(sap_retail.router)
app.include_router(sap_retail.regulatory_runtime_router)
app.dependency_overrides[sap_retail.regulatory_runtime_service]=sap_retail.regulatory_runtime_status
app.dependency_overrides[sap_retail.supply_service] = sap_retail.build_supply_service
app.include_router(sap_retail.supply_router)
app.dependency_overrides[sap_retail.acknowledgement_service] = sap_retail.build_acknowledgements
app.include_router(sap_retail.receipt_event_router)
app.dependency_overrides[inventory_receiving.receiving_service] = inventory_receiving.build_receiving_service
app.include_router(inventory_receiving.router)
app.include_router(inventory_receiving.stock_command_router)
app.include_router(inventory_receiving.inventory_count_router)
app.dependency_overrides[inventory_receiving.manual_stock_move_service] = inventory_receiving.build_manual_stock_move_service
app.dependency_overrides[inventory_receiving.receipt_reverse_service] = inventory_receiving.build_receipt_reverse_service
app.dependency_overrides[inventory_receiving.stock_queries_service] = inventory_receiving.build_stock_queries_service
app.include_router(inventory_receiving.stock_router)
app.include_router(inventory_receiving.task_scan_router)
app.dependency_overrides[inventory_receiving.scan_view] = require_permission("warehouse_task_view")
app.dependency_overrides[inventory_receiving.scan_execute] = require_permission("warehouse_task_execute")
app.dependency_overrides[inventory_receiving.scan_draft_service] = inventory_receiving.build_task_scan_drafts
app.include_router(inventory_receiving.replenishment_progress_router)
app.dependency_overrides[inventory_receiving.replenishment_view] = require_permission("pick_wave_view")
app.dependency_overrides[inventory_receiving.replenishment_progress_service] = inventory_receiving.build_replenishment_progress
app.include_router(inventory_receiving.recovery_router)
app.dependency_overrides[inventory_receiving.inventory_task_view] = require_permission("inventory_task_view")
app.dependency_overrides[inventory_receiving.inventory_task_execute] = require_permission("inventory_task_execute")
app.dependency_overrides[inventory_receiving.recovery_view] = require_permission("case_pick_view")
app.dependency_overrides[inventory_receiving.recovery_tasks_service] = inventory_receiving.build_recovery_tasks_service
app.include_router(inventory_receiving.source_router)
app.dependency_overrides[inventory_receiving.source_view_permission] = require_permission(PICK_WAVE_VIEW_PERMISSION)
app.dependency_overrides[inventory_receiving.source_availability_service] = inventory_receiving.build_source_availability_service
app.dependency_overrides[inventory_receiving.label_service] = inventory_receiving.build_label_service
app.dependency_overrides[inventory_receiving.configuration_service] = inventory_receiving.build_configuration_service
app.dependency_overrides[inventory_receiving.reconciliation_service] = inventory_receiving.build_reconciliation_service
app.dependency_overrides[inventory_receiving.query_service] = inventory_receiving.build_query_service
app.mount("/wms-admin", StaticFiles(directory=Path(__file__).resolve().parents[3] / "wiki-raw" / "wms_admin_ui_reference", html=True), name="wms-admin")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(ApiAuditMiddleware)

app.include_router(health.router)
app.include_router(production.router)
app.include_router(tserver.router)
app.include_router(admin_auth.router)
app.include_router(admin_rights.router)
app.include_router(api_audit.router)
app.include_router(slow_sql.router)
app.include_router(traceability.router)
app.include_router(bom.router)
app.include_router(mes.router)
app.include_router(warehouses.router)
app.include_router(products.router)
app.include_router(raw_material.router)
app.include_router(finished_goods.router)
app.include_router(customer_orders.router)
app.include_router(customer_rules.router)
app.include_router(picking.router)
app.include_router(case_pick.router)
app.include_router(inventory_receiving.weighted_case_router)
app.include_router(inventory_receiving.weighted_plan_router)
app.dependency_overrides[inventory_receiving.weighted_plan_service] = inventory_receiving.build_weighted_plan
app.include_router(inventory_receiving.warehouse_scale_router)
app.dependency_overrides[inventory_receiving.warehouse_scale_service] = inventory_receiving.build_warehouse_scales
app.dependency_overrides[inventory_receiving.weighted_case_service] = inventory_receiving.build_weighted_case
app.include_router(stock_reservations.router)
app.include_router(warehouse_tasks.router)
app.include_router(resource_management.router)
app.include_router(warehouse_map_drafts.router)
app.include_router(warehouse_map.router)
app.include_router(warehouse_topology.router)
app.include_router(transport.router)
app.include_router(users_router.router)       # Sprint 99-100: user management
driver_mobile.register(app)                  # Existing driver PWA and native fact owner
app.include_router(notifications.router)      # Sprint 106-107: push + email
app.include_router(transport_kpi.router)      # Sprint 108-109: KPI dashboard
app.include_router(gps.router)               # Sprint 110-111: GPS positions
app.include_router(transport_tariffs.router) # Sprint 112: tariff grid
app.include_router(export_1c.router)         # Sprint 113: 1C export
app.include_router(maintenance.router)       # Sprint 114: archiving

app.dependency_overrides[inventory_receiving.partial_layout_service] = inventory_receiving.build_partial_layout_service
app.include_router(inventory_receiving.partial_layout_router)

app.dependency_overrides[inventory_receiving.wave_pick_service] = inventory_receiving.build_wave_pick_service
app.include_router(inventory_receiving.wave_pick_router)

app.dependency_overrides[inventory_receiving.fullpal_shipment_service] = inventory_receiving.build_fullpal_shipment_service
app.include_router(inventory_receiving.fullpal_shipment_router)

app.dependency_overrides[inventory_receiving.wave_execution_service] = inventory_receiving.build_wave_execution_service
app.include_router(inventory_receiving.wave_execution_router)

app.dependency_overrides[inventory_receiving.warehouse_hu_service] = inventory_receiving.build_warehouse_hu_service
app.include_router(inventory_receiving.warehouse_hu_router)
app.include_router(inventory_receiving.warehouse_hu_repack_router)

app.dependency_overrides[inventory_receiving.outgoing_quality_service] = inventory_receiving.build_outgoing_quality_service
app.include_router(inventory_receiving.outgoing_quality_router)

app.dependency_overrides[sku_receiving.quality_weight_service] = sku_receiving.build_quality_weight_policy
app.include_router(sku_receiving.quality_weight_router)


from .modules.transport.public import transport_loading_router, transport_unloading_router, transport_loading_service
from .transport_composition import build_transport_loading
app.include_router(transport_loading_router)
app.include_router(transport_unloading_router)
app.dependency_overrides[transport_loading_service] = build_transport_loading

app.dependency_overrides[inventory_receiving.inventory_observations_service] = inventory_receiving.build_inventory_observations_service

from .modules.delivery.public import store_receipt_router,store_receipt_service
from .delivery_composition import build_delivery_receipt
app.include_router(store_receipt_router)
app.dependency_overrides[store_receipt_service]=build_delivery_receipt

from .modules.delivery.public import store_evidence_router,store_evidence_service
from .delivery_composition import build_delivery_evidence
app.include_router(store_evidence_router)
app.dependency_overrides[store_evidence_service]=build_delivery_evidence


from .modules.delivery.public import store_scales_router,store_scales_service
from .delivery_composition import build_delivery_scales
app.include_router(store_scales_router)
app.dependency_overrides[store_scales_service]=build_delivery_scales


from .modules.delivery.public import order_delivery_router,order_delivery_service
from .delivery_composition import build_delivery_progress
app.include_router(order_delivery_router)
app.dependency_overrides[order_delivery_service]=build_delivery_progress


from .modules.delivery.public import case_work_router,case_work_service
from .delivery_composition import build_delivery_case_work
app.include_router(case_work_router)
app.dependency_overrides[case_work_service]=build_delivery_case_work

from .modules.delivery.public import store_return_router,store_returns_service
from .delivery_composition import build_delivery_returns
app.include_router(store_return_router)
app.dependency_overrides[store_returns_service]=build_delivery_returns

from .modules.integrations.public import sap_store_return_router,sap_store_returns_service
from .delivery_composition import build_sap_store_returns
app.include_router(sap_store_return_router)
app.dependency_overrides[sap_store_returns_service]=build_sap_store_returns

from .modules.delivery.public import return_transport_router,return_transport_service
from .delivery_composition import build_delivery_return_transport
app.include_router(return_transport_router)
app.dependency_overrides[return_transport_service]=build_delivery_return_transport

from .modules.transport.public import driver_binding_router,driver_binding_service
from .transport_composition import build_transport_driver_binding
app.include_router(driver_binding_router)
app.dependency_overrides[driver_binding_service]=build_transport_driver_binding
from .modules.delivery.public import return_custody_router,return_custody_service
from .delivery_composition import build_delivery_return_custody
app.include_router(return_custody_router)
app.dependency_overrides[return_custody_service]=build_delivery_return_custody

from .modules.inventory.public import store_return_receiving_router,store_return_receive_service
from .store_return_receiving_composition import build_return_receiving
app.include_router(store_return_receiving_router)
app.dependency_overrides[store_return_receive_service]=build_return_receiving

from .modules.inventory.public import return_putaway_router,return_putaway_service
from .store_return_receiving_composition import build_store_return_putaway
app.include_router(return_putaway_router)
app.dependency_overrides[return_putaway_service]=build_store_return_putaway

from .modules.inventory.public import tare_router,tare_service
from .tare_composition import build_tare_ledger
app.include_router(tare_router)
app.dependency_overrides[tare_service]=build_tare_ledger

from .modules.inventory.public import tare_policy_router,tare_policy_service
from .tare_composition import build_tare_return_policy
app.include_router(tare_policy_router)
app.dependency_overrides[tare_policy_service]=build_tare_return_policy

from .modules.inventory.public import tare_resolution_router
app.include_router(tare_resolution_router)

from .modules.inventory.public import tare_assembly_router,tare_assembly_service
from .tare_composition import build_tare_for_assembly
app.include_router(tare_assembly_router)
app.dependency_overrides[tare_assembly_service]=build_tare_for_assembly

from .modules.inventory.public import tare_loss_router
app.include_router(tare_loss_router)

from .modules.inventory.public import supplier_return_router,supplier_return_service
from .supplier_return_composition import build_supplier_return_service
app.include_router(supplier_return_router)
app.dependency_overrides[supplier_return_service]=build_supplier_return_service

from .modules.inventory.public import supplier_handover_router,supplier_handover_service
from .supplier_handover_composition import build_supplier_handover_service
app.include_router(supplier_handover_router)
app.dependency_overrides[supplier_handover_service]=build_supplier_handover_service

from .modules.inventory.public import return_disposal_router,return_disposal_service
from .return_disposal_composition import build_return_disposal_service
app.include_router(return_disposal_router)
app.dependency_overrides[return_disposal_service]=build_return_disposal_service

from .modules.finance.public import logistics_cost_router,logistics_cost_service
from .logistics_cost_composition import build_logistics_cost_service
app.include_router(logistics_cost_router)
app.dependency_overrides[logistics_cost_service]=build_logistics_cost_service

from .modules.finance.public import logistics_expense_router,logistics_expense_service
from .logistics_expense_composition import build_logistics_expense_service
app.include_router(logistics_expense_router)
app.dependency_overrides[logistics_expense_service]=build_logistics_expense_service

from .modules.finance.public import expense_allocation_router,expense_allocation_service
from .expense_allocation_composition import build_expense_allocation_service
app.include_router(expense_allocation_router)
app.dependency_overrides[expense_allocation_service]=build_expense_allocation_service

from .modules.finance.public import day_reconciliation_router,day_reconciliation_service
from .day_reconciliation_composition import build_day_reconciliation_service
app.include_router(day_reconciliation_router)
app.dependency_overrides[day_reconciliation_service]=build_day_reconciliation_service

from .modules.inventory.public import interwarehouse_router,interwarehouse_service
from .interwarehouse_composition import build_interwarehouse_service
app.include_router(interwarehouse_router)
app.dependency_overrides[interwarehouse_service]=build_interwarehouse_service


from .modules.inventory.public import trace_manifest_router,trace_manifest_service
from .trace_manifest_composition import build_trace_manifest_service
app.include_router(trace_manifest_router)
app.dependency_overrides[trace_manifest_service]=build_trace_manifest_service

from .modules.transport.public import warehouse_forecast_router,warehouse_forecast_service
from .forecast_composition import forecast_service
app.include_router(warehouse_forecast_router)
app.dependency_overrides[warehouse_forecast_service]=forecast_service

from .modules.resources.public import workload_config_router,workload_config_service
from .workload_composition import workload_service
app.include_router(workload_config_router)
app.dependency_overrides[workload_config_service]=workload_service

from .modules.resources.public import workload_monitor_router,workload_monitor_service
from .workload_composition import workload_monitor
app.include_router(workload_monitor_router)
app.dependency_overrides[workload_monitor_service]=workload_monitor

from .modules.inventory.public import stock_compatibility_service
from .stock_settings_composition import stock_settings_service
app.dependency_overrides[stock_compatibility_service]=stock_settings_service

from .modules.resources.public import wave_time_router,wave_time_service
from .workload_composition import wave_time
app.include_router(wave_time_router)
app.dependency_overrides[wave_time_service]=wave_time

from .modules.inventory.public import slotting_router,slotting_demand_service
from .slotting_composition import slotting_demand
app.include_router(slotting_router)
app.dependency_overrides[slotting_demand_service]=slotting_demand

from .modules.transport.public import operation_fact_router, operation_fact_service
from .transport_operation_composition import build_operation_fact_service
app.dependency_overrides[operation_fact_service]=build_operation_fact_service
app.include_router(operation_fact_router)

from .modules.resources.public import workload_history_router,workload_history_service
from .workload_history_composition import attendance_history
app.dependency_overrides[workload_history_service]=attendance_history
app.include_router(workload_history_router)

from .modules.inventory.public import range_proposal_router,range_proposal_service
from .range_proposal_composition import range_proposal
app.include_router(range_proposal_router)
app.dependency_overrides[range_proposal_service]=range_proposal
from .modules.transport.public import transport_preflight_router, transport_preflight_service
from .transport_preflight_composition import preflight_service
app.include_router(transport_preflight_router)
app.dependency_overrides[transport_preflight_service] = preflight_service

from .modules.resources.public import case_read_service
from .case_read_composition import scoped_case_reads
app.dependency_overrides[case_read_service] = scoped_case_reads

from .modules.inventory.public import case_label_router,case_label_dependency,case_label_service
app.include_router(case_label_router)

app.dependency_overrides[case_label_dependency]=case_label_service


from .modules.fulfillment.public import store_decision_router, store_admission_service, build_store_admission_service
app.include_router(store_decision_router)
app.dependency_overrides[store_admission_service] = build_store_admission_service

from .modules.fulfillment.public import preparation_read_router
app.include_router(preparation_read_router)

from .modules.finance.public import day_review_router,day_reviews_service,build_day_reviews
app.include_router(day_review_router)
from .day_reconciliation_composition import build_day_reviews_service
app.dependency_overrides[day_reviews_service]=build_day_reviews_service

from .modules.transport.public import st_deferral_router,st_deferral_service
from .st_deferral_composition import build_st_deferral_service
app.include_router(st_deferral_router)
app.dependency_overrides[st_deferral_service]=build_st_deferral_service

from .modules.transport.public import warehouse_depot_router,warehouse_depot_service
from .warehouse_depot_composition import build_warehouse_depot_service
app.include_router(warehouse_depot_router)
app.dependency_overrides[warehouse_depot_service]=build_warehouse_depot_service

from .modules.transport.public import vehicle_profile_router,vehicle_profile_service
from .vehicle_profile_composition import build_vehicle_profile_service
app.include_router(vehicle_profile_router)
app.dependency_overrides[vehicle_profile_service]=build_vehicle_profile_service

from .modules.inventory.public import waiting_task_router,waiting_task_dependency,waiting_task_service
app.include_router(waiting_task_router)
app.dependency_overrides[waiting_task_dependency]=waiting_task_service


from .prepared_carrier_routes import register_prepared_carrier_routes
register_prepared_carrier_routes(app)

from .modules.inventory.public import quality_scope_router,quality_scope_service
from .quality_scope_composition import quality_scope
app.include_router(quality_scope_router)
app.dependency_overrides[quality_scope_service]=quality_scope
