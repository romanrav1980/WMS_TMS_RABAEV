"""Compose existing source readers; each retains its authoritative readiness calculation."""
from fastapi import FastAPI
from .oracle_gateway import OracleGateway
from .services.picking_service import PickingService
from .modules.inventory.public import (build_shift_overview, shift_overview_service, shift_overview_router,
                                       WavePickRelease, ReplenishmentProgress)
from .modules.resources.public import build_wave_time


def register_shift_overview(app: FastAPI) -> None:
    readers = {
        "readiness": lambda bound, wave, actor: PickingService(bound).get_wave_readiness(wave),
        "pick": lambda bound, wave, actor: WavePickRelease(bound).preview(wave, actor),
        "time": lambda bound, wave, actor: build_wave_time(bound).context(wave, actor),
        "replenishment": lambda bound, wave, actor: ReplenishmentProgress(bound).list_rows(wave, 100),
    }
    service = build_shift_overview(OracleGateway(), readers)
    app.include_router(shift_overview_router)
    app.dependency_overrides[shift_overview_service] = lambda: service
