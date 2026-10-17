from fastapi import FastAPI
from .oracle_gateway import OracleGateway
from .modules.fulfillment.public import consolidation_router, consolidation_service, build_consolidation_service


def build_service():
    return build_consolidation_service(OracleGateway())


def register_consolidation(app: FastAPI) -> None:
    app.dependency_overrides[consolidation_service] = build_service
    app.include_router(consolidation_router)
