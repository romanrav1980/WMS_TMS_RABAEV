"""Evaluate capacity before DML; Oracle functions cannot read a table being updated by their caller."""
from typing import Any
from .metadata_transactions import begin_wave_metadata


def hold_unissued_capacity(gateway: Any, wave_id: int, actor: str) -> int:
    with gateway.transaction("Hold unissued replenishment without target capacity") as cursor:
        entered = False
        try:
            entered = begin_wave_metadata(gateway, cursor, wave_id, actor)
            cursor.execute("""
                select rt.PICK_WAVE_REPLENISH_TASK_ID,rt.QTY,
                    RRL_STOCK_REPL_CAPACITY.remaining_base_quantity(
                        rt.TARGET_CELL_CODE,rt.ARTICUL,rt.PICK_WAVE_REPLENISH_TASK_ID) AVAILABLE_BASE
                from RRL_PICK_WAVE_REPLENISH_TASK rt
                where rt.PICK_WAVE_ID=:wave and rt.STATUS='RELEASED' and rt.SOURCE_RESERVATION_ID is not null
                  and not exists(select 1 from RRL_WAREHOUSE_TASK t where t.TASK_SOURCE='WAVE'
                    and t.TASK_TYPE='REPLENISHMENT' and t.SOURCE_DOC_ID=rt.PICK_WAVE_ID
                    and t.SOURCE_TASK_ID=rt.PICK_WAVE_REPLENISH_TASK_ID and t.STATUS not in('DONE','CANCELLED'))
                order by rt.PICK_WAVE_REPLENISH_TASK_ID fetch first 201 rows only""", {"wave": wave_id})
            rows = cursor.fetchall()
            if len(rows) > 200:
                raise ValueError("REPLENISHMENT_CAPACITY_HOLD_BOUND_200")
            blocked = [(row_id,) for row_id, quantity, available in rows
                       if available is not None and quantity > available]
            if blocked:
                cursor.executemany("""
                    update RRL_PICK_WAVE_REPLENISH_TASK set STATUS='WAIT_FREE_CELL',
                        WAIT_REASON='Waiting for target capacity including physical stock and open arrivals',
                        UPDATED_AT=sysdate,UPDATED_BY=:actor
                    where PICK_WAVE_REPLENISH_TASK_ID=:row_id and STATUS='RELEASED'""",
                    [{"actor": actor, "row_id": row[0]} for row in blocked])
            return len(blocked)
        finally:
            if entered:
                cursor.execute("begin RRL_STOCK_METADATA_TX.end_change;end;")
