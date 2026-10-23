"""Mount assembled order composition and its SAP/SKM acknowledgments (TRADECASE T02, C-0164) on the native RRL_TRADE_COMPOSITION_API."""
from fastapi import FastAPI
from .oracle_gateway import OracleGateway
from .modules.integrations.public import CompositionAckPort, OracleCompositionAck, composition_ack_router, composition_ack_service


def build_composition_ack() -> CompositionAckPort:
    return OracleCompositionAck(OracleGateway())


def register_composition_ack(app: FastAPI) -> None:
    app.dependency_overrides[composition_ack_service] = build_composition_ack
    app.include_router(composition_ack_router)
