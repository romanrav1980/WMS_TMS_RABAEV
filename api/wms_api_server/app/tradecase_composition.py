"""Mount the independent trading/production document profile."""
from fastapi import FastAPI
from .modules.integrations.public import tradecase_router, tradecase_documents, build_tradecase_documents


def register_tradecase(app: FastAPI) -> None:
    app.include_router(tradecase_router)
    app.dependency_overrides[tradecase_documents] = build_tradecase_documents
