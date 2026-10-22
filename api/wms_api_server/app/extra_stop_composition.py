"""Mount the extra-stop decision (TRADECASE program section 12) on the native route recalculation (C-0154)."""
from fastapi import FastAPI
from .oracle_gateway import OracleGateway
from .modules.transport.public import ExtraStopPort, OracleExtraStop, extra_stop_router, extra_stop_service


def build_extra_stop() -> ExtraStopPort:
    return OracleExtraStop(OracleGateway())


def register_extra_stop(app: FastAPI) -> None:
    app.dependency_overrides[extra_stop_service] = build_extra_stop
    app.include_router(extra_stop_router)
