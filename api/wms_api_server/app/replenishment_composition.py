"""Inject existing task synchronization into the inventory minimax lifecycle."""
from .oracle_gateway import OracleGateway
from .modules.inventory.public import MinimaxService
from .modules.resources.public import sync_existing_wave_tasks
def build_minimax_service()->MinimaxService:
    return MinimaxService(OracleGateway(),sync_existing_wave_tasks)

from .modules.inventory.public import ReplenishmentContinuation

def build_replenishment_continuation() -> ReplenishmentContinuation:
    return ReplenishmentContinuation(OracleGateway(), sync_existing_wave_tasks)
