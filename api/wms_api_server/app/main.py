from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .middleware.api_audit import ApiAuditMiddleware
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
    tserver,
    warehouse_topology,
    warehouse_tasks,
    warehouses,
)


settings = get_settings()

app = FastAPI(title=settings.api_title, version=settings.api_version)

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
app.include_router(warehouse_topology.router)
