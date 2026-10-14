"""Durable shortage recovery; existing Oracle commands own every reserve/stock effect."""
import json
from typing import Any, Callable
from uuid import uuid4
from ..contracts_stock import StockCommand, StockPostingError
from .stock_posting_uow import StockPosting
from ....transaction_gateway import TransactionGateway
from ....services.picking_service import PickingService
from ....modules.resources.public import sync_existing_wave_tasks, assign_existing_inventory_auditor, dispatch_existing_urgent_replenishment


class ShortRecoveryWorker:
    def __init__(self, gateway: Any, actor: str, worker_id: str, assign: Callable[[Any,int,Any],None]) -> None:
        self.gateway, self.actor, self.worker_id = gateway, actor, worker_id
        self.assign=assign

    def claim(self) -> dict[str, Any] | None:
        with self.gateway.transaction("Claim short recovery lease") as cursor:
            cursor.arraysize = 1
            cursor.prefetchrows = 0
            cursor.execute("select RRL_HAS_WRIGHT(:actor,'case_pick_short_approve') from dual", {"actor": self.actor})
            if cursor.fetchone()[0] != 1:
                raise PermissionError("Recovery worker lacks case_pick_short_approve")
            cursor.execute("""select CASE_PICK_SHORT_ID,PICK_WAVE_ID,REPLENISH_TASK_ID,
                   RECOVERY_SOURCE_REQUEST,RECOVERY_STATE
                from RRL_CASE_PICK_SHORT where RECOVERY_STATE in('WAIT_INVENTORY','WAIT_REPLENISHMENT')
                 and exists(select 1 from RRL_PICK_WAVE w where w.PICK_WAVE_ID=RRL_CASE_PICK_SHORT.PICK_WAVE_ID and w.STATUS='LAUNCHED')
                 and (RECOVERY_STATE!='WAIT_INVENTORY' or exists(select 1 from RRL_INVENTORY_TASK it
                     where it.INVENTORY_TASK_ID=RRL_CASE_PICK_SHORT.INVENTORY_TASK_ID and it.ASSIGNED_TO is null and it.STATUS='NEW'))
                 and (RECOVERY_LEASE_UNTIL is null or RECOVERY_LEASE_UNTIL<cast(systimestamp as timestamp))
                 order by RECOVERY_DEADLINE_AT,CASE_PICK_SHORT_ID for update skip locked""")
            row = cursor.fetchone()
            if row is None:
                return None
            short_id, wave_id, repl_id, frozen, state = row
            frozen = frozen.read() if hasattr(frozen, "read") else frozen
            cursor.execute("""update RRL_CASE_PICK_SHORT set RECOVERY_WORKER=:worker,
                RECOVERY_LEASE_UNTIL=cast(systimestamp as timestamp)+numtodsinterval(45,'SECOND'),
                RECOVERY_ATTEMPTS=RECOVERY_ATTEMPTS+1
                where CASE_PICK_SHORT_ID=:short_id""", {"worker": self.worker_id, "short_id": short_id})
        return {"short_id": int(short_id), "wave_id": int(wave_id),
                "repl_id": int(repl_id) if repl_id is not None else None, "frozen": frozen, "state": state}

    def release(self, short_id: int, error: str | None = None) -> None:
        self.gateway.execute("""update RRL_CASE_PICK_SHORT set RECOVERY_WORKER=null,
            RECOVERY_LEASE_UNTIL=cast(systimestamp as timestamp)+numtodsinterval(5,'SECOND'),
            RECOVERY_LAST_ERROR=:error where CASE_PICK_SHORT_ID=:short_id and RECOVERY_WORKER=:worker""",
            {"short_id": short_id, "worker": self.worker_id, "error": error[:1000] if error else None})

    def prepare_source(self, item: dict[str, Any]) -> str:
        with self.gateway.transaction("Prepare existing urgent replenishment") as cursor:
            try:
                cursor.execute("begin RRL_STOCK_METADATA_TX.begin_change(:actor,:permission);end;",
                               {"actor": self.actor, "permission": "pick_wave_launch"})
                PickingService(TransactionGateway(cursor))._enrich_replenishment_settings(item["wave_id"], self.actor)
                cursor.execute("""update RRL_PICK_WAVE_REPLENISH_TASK set
                    REPLENISHMENT_METHOD='IMMEDIATE',REPLENISHMENT_QTY_MODE='FILL_TO_VOLUME',
                    QTY=(select l.PLANNED_QTY-l.PICKED_QTY from RRL_CASE_PICK_SHORT sh join RRL_CASE_PICK_LINE l on l.CASE_PICK_LINE_ID=sh.CASE_PICK_LINE_ID where sh.REPLENISH_TASK_ID=RRL_PICK_WAVE_REPLENISH_TASK.PICK_WAVE_REPLENISH_TASK_ID),
                    STATUS=case when STATUS in('FAILED','WAIT_FREE_CELL','WAIT_MINIMAX','QUEUED') and SOURCE_RESERVATION_ID is null then 'RELEASED' else STATUS end
                    where PICK_WAVE_REPLENISH_TASK_ID=:repl_id""", {"repl_id": item["repl_id"]})
                cursor.execute("select RECOVERY_SOURCE_REQUEST from RRL_CASE_PICK_SHORT where CASE_PICK_SHORT_ID=:short_id for update",
                               {"short_id": item["short_id"]})
                old = cursor.fetchone()[0]
                if old is not None:
                    return old.read() if hasattr(old, "read") else old
                command = StockCommand(operation_id="SHORT.SOURCE:" + str(item["short_id"]) + ":" + uuid4().hex[:16],
                    command_type="WAVE_RESERVE_SOURCES", actor=self.actor, lines=(),
                    source={"type": "PICK_WAVE", "wave_id": item["wave_id"]},
                    metadata={"requested_row_ids": [item["repl_id"]]})
                payload = command.canonical_json()
                cursor.execute("""update RRL_CASE_PICK_SHORT set RECOVERY_SOURCE_REQUEST=:payload
                    where CASE_PICK_SHORT_ID=:short_id""", {"payload": payload, "short_id": item["short_id"]})
                return payload
            finally:
                cursor.execute("begin RRL_STOCK_METADATA_TX.end_change;end;")

    def post_frozen_source(self, item: dict[str, Any], payload: str) -> None:
        data = json.loads(payload)
        StockPosting().post(StockCommand(operation_id=data["operation_id"],
            command_type=data["command_type"], actor=data["actor"], lines=(),
            source=data["source"], units=(), metadata=data["metadata"]))
        # Only a confirmed response allows another source intent after a no-stock result.
        self.gateway.execute("""update RRL_CASE_PICK_SHORT set RECOVERY_SOURCE_REQUEST=null
            where CASE_PICK_SHORT_ID=:short_id and RECOVERY_WORKER=:worker""",
            {"short_id": item["short_id"], "worker": self.worker_id})

    def work(self, item: dict[str, Any]) -> dict[str, Any]:
        if item["state"] == "WAIT_INVENTORY":
            return {"state":"WAIT_INVENTORY", **assign_existing_inventory_auditor(self.gateway,item["short_id"],self.actor)}
        if item["frozen"]:
            self.post_frozen_source(item, item["frozen"])
        else:
            try:
                ready = StockPosting().post(StockCommand(operation_id="SHORT.READY:" + str(item["short_id"]) + ":" + str(item["repl_id"]),
                    command_type="CASE_SHORT_APPROVE", actor=self.actor, lines=(),
                    source={"short_id": item["short_id"]},
                    metadata={"decision": "READY", "reason": "Restore from confirmed stock at original pick cell"}))
                return {"short_id": item["short_id"], "state": ready["recovery_state"]}
            except StockPostingError as exc:
                cause = exc.__cause__
                note = getattr(cause.args[0], "message", "") if cause and cause.args else ""
                if exc.oracle_code != 20886 or not any(code in note for code in
                        ("SHORT_NO_ELIGIBLE_TARGET_STOCK", "SHORT_EXISTING_REPLENISHMENT_MUST_FINISH")):
                    raise
            rows = self.gateway.fetch_all("""select SOURCE_RESERVATION_ID from RRL_PICK_WAVE_REPLENISH_TASK
                where PICK_WAVE_REPLENISH_TASK_ID=:repl_id""", {"repl_id": item["repl_id"]})
            if rows and rows[0]["source_reservation_id"] is None:
                self.post_frozen_source(item, self.prepare_source(item))
        sync_existing_wave_tasks(self.gateway, item["wave_id"], self.actor)
        return {"short_id": item["short_id"], "state": "WAIT_REPLENISHMENT",
                "dispatch":dispatch_existing_urgent_replenishment(self.gateway,item["short_id"],self.actor,self.assign)}

    def process_one(self) -> dict[str, Any] | None:
        item = self.claim()
        if item is None:
            return None
        try:
            result = self.work(item)
            self.release(item["short_id"])
            return result
        except Exception as exc:
            message = str(exc)
            self.release(item["short_id"], message)
            return {"short_id": item["short_id"], "state": item["state"],
                    "error": message, "retry_same_saved_operation": True}
