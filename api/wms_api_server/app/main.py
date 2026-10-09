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
from .routers import driver_mobile
from .routers import notifications
from .routers import transport_kpi
from .routers import gps
from .routers import transport_tariffs
from .routers import export_1c
from .routers import maintenance


settings = get_settings()

app = FastAPI(title=settings.api_title, version=settings.api_version)
inventory_receiving.install_stock_error_handlers(app)
app.dependency_overrides[sap_fulfillment.store_order_service] = sap_fulfillment.build_store_order_service
app.dependency_overrides[sap_fulfillment.preparation_service] = sap_fulfillment.build_preparation_service
app.include_router(sap_fulfillment.router)
app.dependency_overrides[sku_receiving.policy_service] = sku_receiving.build_policy_service
app.dependency_overrides[sap_retail.artmas_service] = sap_retail.build_artmas_service
app.include_router(sku_receiving.router)
app.include_router(sap_retail.router)
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
app.include_router(stock_reservations.router)
app.include_router(warehouse_tasks.router)
app.include_router(resource_management.router)
app.include_router(warehouse_map_drafts.router)
app.include_router(warehouse_map.router)
app.include_router(warehouse_topology.router)
app.include_router(transport.router)
app.include_router(users_router.router)       # Sprint 99-100: user management
app.include_router(driver_mobile.router)      # Sprint 103-105: driver PWA
app.include_router(notifications.router)      # Sprint 106-107: push + email
app.include_router(transport_kpi.router)      # Sprint 108-109: KPI dashboard
app.include_router(gps.router)               # Sprint 110-111: GPS positions
app.include_router(transport_tariffs.router) # Sprint 112: tariff grid
app.include_router(export_1c.router)         # Sprint 113: 1C export
app.include_router(maintenance.router)       # Sprint 114: archiving
