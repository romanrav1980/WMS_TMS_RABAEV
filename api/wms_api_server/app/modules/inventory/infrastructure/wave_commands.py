from __future__ import annotations
from ....oracle_gateway import OracleGateway
from ....transaction_gateway import TransactionGateway
"""Durable per-row source intents, shared by normal waves and replenishment continuation."""
import json
from uuid import uuid4
from fastapi import HTTPException
from ..contracts_stock import StockCommand, StockPostingError
from .stock_posting_uow import StockPosting
from .release_boundary import require_active_release


def reserve_wave_sources(gateway: OracleGateway | TransactionGateway, wave_id: int, actor: str, row_ids: list[int] | None = None) -> bool:
    require_active_release(gateway,None)
    requested = json.dumps(row_ids) if row_ids is not None else None
    pending = []
    with gateway.transaction("Prepare durable existing wave source intents") as cursor:
        entered = False
        try:
            cursor.execute("begin RRL_STOCK_METADATA_TX.begin_change(:actor,'pick_wave_launch');end;", {"actor": actor})
            entered = True
            cursor.execute("""select rt.PICK_WAVE_REPLENISH_TASK_ID,rt.RESERVE_OPERATION_ID,rt.RESERVE_REQUEST_JSON
                from RRL_PICK_WAVE_REPLENISH_TASK rt join RRL_PICK_WAVE w on w.PICK_WAVE_ID=rt.PICK_WAVE_ID
                where rt.PICK_WAVE_ID=:wave and w.STATUS='LAUNCHED'
                  and(rt.SOURCE_RESERVATION_ID is null or not exists(
                    select 1 from RRL_WAREHOUSE_TASK wh where wh.UID_PALLET=rt.PALLET_UID
                     and wh.FROM_CELL=rt.SOURCE_CELL_CODE and wh.STATUS not in('DONE','CANCELLED')))
                  and rt.STATUS in('RELEASED','QUEUED','WAIT_FREE_CELL','WAIT_MINIMAX','FAILED')
                  and (:requested is null or rt.PICK_WAVE_REPLENISH_TASK_ID in
                    (select id from json_table(:requested,'$[*]' columns(id number path '$'))))
                order by rt.PICK_WAVE_REPLENISH_TASK_ID fetch first 201 rows only""", {"wave": wave_id, "requested": requested})
            rows = cursor.fetchall()
            if len(rows) > 200:
                raise HTTPException(409, detail="WAVE_SOURCE_INTENT_BOUND_200")
            for row_id, operation, saved in rows:
                if operation:
                    cursor.execute("select STATE from RRL_STOCK_OPERATION where OPERATION_ID=:op", {"op": operation})
                    committed = cursor.fetchone()
                    if committed and committed[0] == "APPLIED":
                        # A committed decision is finished; re-evaluating an unissued source uses a new ID.
                        operation, saved = None, None
                    elif committed:
                        raise HTTPException(409, detail="SOURCE_INTENT_STATE_UNRESOLVED")
                if saved is None:
                    operation = operation or "WAVE.REPL.SOURCE:" + uuid4().hex
                    command = StockCommand(operation_id=operation, command_type="WAVE_RESERVE_SOURCES",
                        actor=actor, lines=(), source={"type": "PICK_WAVE", "wave_id": wave_id},
                        metadata={"requested_row_ids": [int(row_id)], "allow_unissued_source_rebind": True})
                    saved = command.canonical_json()
                    cursor.execute("""update RRL_PICK_WAVE_REPLENISH_TASK set RESERVE_OPERATION_ID=:op,
                        RESERVE_REQUEST_JSON=:body,STATUS=case when STATUS='FAILED' then 'RELEASED' else STATUS end,
                        UPDATED_AT=sysdate,UPDATED_BY=:actor where PICK_WAVE_REPLENISH_TASK_ID=:id""",
                        {"op": operation, "body": saved, "actor": actor, "id": row_id})
                else:
                    saved = saved.read() if hasattr(saved, "read") else saved
                data = json.loads(saved)
                if data["operation_id"] != operation or data["source"]["wave_id"] != wave_id or data["metadata"]["requested_row_ids"] != [int(row_id)]:
                    raise HTTPException(409, detail="SOURCE_INTENT_IDENTITY_CONFLICT")
                pending.append(StockCommand(operation_id=data["operation_id"], command_type=data["command_type"],
                    actor=data["actor"], lines=(), source=data["source"], metadata=data["metadata"]))
        finally:
            if entered:
                cursor.execute("begin RRL_STOCK_METADATA_TX.end_change;end;")
    for command in pending:
        try:
            StockPosting().post(command)
        except StockPostingError as exc:
            uncertain = exc.code in {"RESULT_UNCERTAIN","REQUEST_DEADLINE","CONNECTION_UNUSABLE","LOCK_RETRY_EXHAUSTED"}
            raise HTTPException(503 if uncertain else 409, detail={
                "code":exc.code,"operation_id":exc.operation_id,"oracle_code":exc.oracle_code,
                "outcome_confirmed":not uncertain,"retry_same_operation_id":uncertain}) from exc
    return True
