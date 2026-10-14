from __future__ import annotations
from ....oracle_gateway import OracleGateway
from ....transaction_gateway import TransactionGateway
"""Actual wave lifecycle: read blockers, finish only through the existing posting owner."""
from .wave_execution_reader import execution_snapshot
from ..contracts_stock import StockCommand
from .stock_posting_uow import StockPosting


class WaveExecution:
    def __init__(self, gateway: OracleGateway | TransactionGateway) -> None:
        self.gateway = gateway

    def preview(self, wave_id: int, actor: str) -> dict:
        return execution_snapshot(self.gateway, wave_id, actor)

    def finish(self, wave_id: int, operation_id: str, actor: str, disposition: str | None = None, reason: str | None = None) -> dict:
        return StockPosting().post(StockCommand(
            operation_id=operation_id, command_type="WAVE_EXECUTION_FINISH", actor=actor,
            lines=(), source={"wave_id": wave_id}, metadata=({"disposition": disposition, "reason": reason} if disposition else {})))
