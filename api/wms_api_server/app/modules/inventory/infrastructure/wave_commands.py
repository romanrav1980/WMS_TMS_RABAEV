"""Use existing wave replenishment rows through the stock coordinator."""
from ..contracts_stock import StockCommand, StockPostingError
from .stock_posting_uow import StockPosting
from fastapi import HTTPException


def reserve_wave_sources(gateway, wave_id: int, actor: str) -> bool:
    state = gateway.fetch_all("select STATE from RRL_STOCK_RELEASE where RELEASE_ID=1")
    if state and state[0]["state"] == "PREPARED":
        return False
    rows = gateway.fetch_all("""select PICK_WAVE_REPLENISH_TASK_ID,
        to_char(QTY,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') QTY,TARGET_CELL_CODE,STATUS,
        to_char(UPDATED_AT,'YYYYMMDDHH24MISS') UPDATED_AT
        from RRL_PICK_WAVE_REPLENISH_TASK where PICK_WAVE_ID=:wave
          and SOURCE_RESERVATION_ID is null
          and STATUS in('RELEASED','QUEUED','WAIT_FREE_CELL','WAIT_MINIMAX')
        order by PICK_WAVE_REPLENISH_TASK_ID fetch first 201 rows only""", {"wave": wave_id})
    if not rows:
        return True
    if len(rows) > 200:
        raise HTTPException(409, detail="Wave source reservation batch exceeds 200 rows")
    # No automatic replay of an old released reservation: each attempt has a fresh intent ID.
    # The database locks the wave/rows and rejects stale selection before any stock change.
    from uuid import uuid4
    operation = "WAVE.RESERVE:" + uuid4().hex
    try:
        StockPosting().post(StockCommand(
            operation_id=operation, command_type="WAVE_RESERVE_SOURCES", actor=actor,
            lines=(), source={"type": "PICK_WAVE", "wave_id": wave_id},
            metadata={"requested_row_ids": [r["pick_wave_replenish_task_id"] for r in rows]}))
    except StockPostingError as exc:
        raise HTTPException(409, detail={"code": exc.code, "operation_id": exc.operation_id,
                                        "oracle_code": exc.oracle_code}) from exc
    return True
