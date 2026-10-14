"""Registration of existing carrier metadata and prepared-layout workspaces."""
from fastapi import FastAPI
from .modules.inventory.public import pallet_floor_router, pallet_floor_service, case_type_router, case_type_service
from .pallet_floor_composition import build_pallet_floor_service
from .case_type_composition import build_case_type_service
from .modules.fulfillment.public import prepared_layout_router, prepared_layout_service
from .prepared_layout_composition import build_prepared_layout_service


def register_prepared_carrier_routes(app: FastAPI) -> None:
    for router, dependency, factory in (
        (pallet_floor_router, pallet_floor_service, build_pallet_floor_service),
        (case_type_router, case_type_service, build_case_type_service),
        (prepared_layout_router, prepared_layout_service, build_prepared_layout_service),
    ):
        app.include_router(router)
        app.dependency_overrides[dependency] = factory
