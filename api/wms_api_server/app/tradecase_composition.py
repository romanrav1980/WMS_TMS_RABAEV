"""Mount the independent trading/production document profile."""
from fastapi import FastAPI
from .modules.inventory.public import trade_stock_router, trade_stock_service, build_trade_stock
from .modules.integrations.public import tradecase_router, tradecase_documents, build_tradecase_documents


def register_tradecase(app: FastAPI) -> None:
    app.include_router(tradecase_router)
    app.include_router(trade_stock_router)
    app.dependency_overrides[trade_stock_service] = build_trade_stock
    app.dependency_overrides[tradecase_documents] = build_tradecase_documents
