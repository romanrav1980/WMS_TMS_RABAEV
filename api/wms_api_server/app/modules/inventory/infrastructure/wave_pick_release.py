from __future__ import annotations
import json
import oracledb
from fastapi import HTTPException
from ....oracle_gateway import OracleGateway
from ....transaction_gateway import TransactionGateway
from ..contracts_stock import StockCommand
from .stock_posting_uow import StockPosting
from .wave_execution_reader import assert_wave_view


class WavePickRelease:
    """Picking admission uses the original command and current warehouse access."""

    def __init__(self, gateway: OracleGateway | TransactionGateway) -> None:
        self.gateway = gateway

    def preview(self, wave_id: int, actor: str) -> dict:
        with self.gateway.transaction("Current wave pick readiness READ ONLY") as cursor:
            if not getattr(self.gateway, "transaction_bound", False):
                cursor.execute("set transaction read only")
            assert_wave_view(cursor, wave_id, actor)
            try:
                cursor.execute("""select distinct a.OWNER_ID,c.WARE_ID from RRL_STOCK_RESERVATION sr
                    join RRL_WMS_RECEIPT_UNIT u on u.HARD_RESERVATION_ID=sr.RESERVATION_ID
                    join RRL_TRADE_STOCK_ATTR a on a.PHYSICAL_UNIT_KEY=u.PHYSICAL_UNIT_KEY
                    join RRL_CELLS c on c.CELL=u.CURRENT_CELL
                    where sr.SOURCE_DOC_TYPE='PICK_WAVE'and sr.SOURCE_DOC_ID=:wave
                    and sr.STATUS in('ACTIVE','ALLOCATED','PICKING')""",wave=wave_id)
                for owner,warehouse in cursor.fetchall():
                    cursor.callproc("RRL_TRADE_STOCK_GUARD.assert_owner",[actor,warehouse,owner,0])
            except oracledb.DatabaseError as exc:
                raise HTTPException(403 if getattr(exc.args[0],"code",0)==20882 else 503,detail="TRADE_WAVE_LEGAL_VIEW_DENIED")from exc
            cursor.execute("select RRL_STOCK_WAVE_READY.snapshot_json(:wave,:actor,0) from dual",wave=wave_id,actor=actor)
            raw=cursor.fetchone()[0]
            return json.loads(raw.read() if hasattr(raw,"read") else raw)

    def release(self, wave_id: int, operation_id: str, actor: str) -> dict:
        result = StockPosting().post(StockCommand(
            operation_id=operation_id, command_type="WAVE_PICK_RELEASE", actor=actor,
            lines=(), source={"wave_id": wave_id}, metadata={},
        ))

        return {**result, "command_operation_id": operation_id}
