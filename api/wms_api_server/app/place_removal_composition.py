"""Mount the removal of selected assembly places from a trip (C-0176) on the native command."""
from fastapi import FastAPI
from .oracle_gateway import OracleGateway
from .modules.transport.public import OraclePlaceRemoval, PlaceRemovalPort, place_removal_router, place_removal_service


def build_place_removal() -> PlaceRemovalPort:
    return OraclePlaceRemoval(OracleGateway())


def register_place_removal(app: FastAPI) -> None:
    app.dependency_overrides[place_removal_service] = build_place_removal
    app.include_router(place_removal_router)
