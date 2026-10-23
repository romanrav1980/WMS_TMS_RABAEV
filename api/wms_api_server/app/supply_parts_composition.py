"""Mount SUPPLY composition in parts (TRADECASE T02, C-0163) on the native RRL_TRADE_SUPPLY_PARTS_API and the existing intake."""
from fastapi import FastAPI
from .oracle_gateway import OracleGateway
from .modules.integrations.public import OracleSupplyParts, SupplyPartsPort, supply_parts_router, supply_parts_service


def build_supply_parts() -> SupplyPartsPort:
    return OracleSupplyParts(OracleGateway())


def register_supply_parts(app: FastAPI) -> None:
    app.dependency_overrides[supply_parts_service] = build_supply_parts
    app.include_router(supply_parts_router)
