"""Mount the independent trading/production document profile."""
from fastapi import FastAPI
from .modules.inventory.public import trade_stock_router, trade_stock_service, build_trade_stock, trade_planning_router, trade_planning_service, build_trade_planning, trade_buyout_router, trade_buyout_service
from .modules.integrations.public import tradecase_router, tradecase_documents, build_tradecase_documents, trade_transport_router, trade_transport_service, build_trade_transport


def register_tradecase(app: FastAPI) -> None:
    app.include_router(tradecase_router)
    app.include_router(trade_transport_router)
    app.dependency_overrides[trade_transport_service] = build_trade_transport
    app.include_router(trade_stock_router)
    app.include_router(trade_planning_router)
    app.include_router(trade_buyout_router)
    app.dependency_overrides[trade_buyout_service] = build_trade_stock
    app.dependency_overrides[trade_planning_service] = build_trade_planning
    app.dependency_overrides[trade_stock_service] = build_trade_stock
    app.dependency_overrides[tradecase_documents] = build_tradecase_documents
