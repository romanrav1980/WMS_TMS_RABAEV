"""Durable metadata progress; canonical StockPosting remains the only stock writer."""
from contextlib import contextmanager
from collections.abc import Iterator
from hashlib import sha256
import json
import oracledb
from typing import Any
from ....transaction_gateway import TransactionGateway
from ...inventory.public import StockCommand


class WaveStepGateway(TransactionGateway):
    def __init__(self, cursor: Any, wave: int, actor: str) -> None:
        super().__init__(cursor)
        self.wave_continuation_scope = (wave, actor)


class WaveContinuation:
    def __init__(self, gateway: Any, wave: int, operation: str, actor: str) -> None:
        self.gateway, self.wave, self.operation, self.actor = gateway, wave, operation, actor

    @contextmanager
    def step(self, number: int) -> Iterator[tuple[WaveStepGateway, bool]]:
        with self.gateway.transaction("Original wave launch continuation metadata") as cursor:
            run = cursor.var(int)
            try:
                cursor.callproc("RRL_WAVE_CONTINUE_API.begin_step",
                                [self.operation, self.wave, self.actor, number, run])
                yield WaveStepGateway(cursor, self.wave, self.actor), bool(run.getvalue())
            finally:
                cursor.callproc("RRL_WAVE_CONTINUE_API.end_step")

    @staticmethod
    def finish(bound: WaveStepGateway) -> None:
        bound.cursor.callproc("RRL_WAVE_CONTINUE_API.finish_step")

    def fail(self, number: int, code: str) -> None:
        with self.step(number) as (bound, run):
            if run:
                bound.cursor.callproc("RRL_WAVE_CONTINUE_API.fail_step", [code])

    def freeze_sources(self, bound: WaveStepGateway) -> None:
        cursor = bound.cursor
        cursor.execute("select SOURCES_FROZEN from RRL_WAVE_CONTINUE where LAUNCH_OPERATION_ID=:operation",
                       operation=self.operation)
        if cursor.fetchone()[0]:
            return
        from ...inventory.public import route_existing_alternative_pick_faces
        route_existing_alternative_pick_faces(bound, self.wave, self.actor)
        cursor.execute("""select rt.PICK_WAVE_REPLENISH_TASK_ID,rt.RESERVE_OPERATION_ID,
                dbms_lob.substr(rt.RESERVE_REQUEST_JSON,4000,1),dbms_lob.getlength(rt.RESERVE_REQUEST_JSON)
            from RRL_PICK_WAVE_REPLENISH_TASK rt where rt.PICK_WAVE_ID=:wave
              and(rt.SOURCE_RESERVATION_ID is null or not exists(select 1 from RRL_WAREHOUSE_TASK wh
                where wh.UID_PALLET=rt.PALLET_UID and wh.FROM_CELL=rt.SOURCE_CELL_CODE and wh.STATUS not in('DONE','CANCELLED')))
              and rt.STATUS in('RELEASED','QUEUED','WAIT_FREE_CELL','WAIT_MINIMAX','FAILED')
            order by rt.PICK_WAVE_REPLENISH_TASK_ID fetch first 201 rows only""", wave=self.wave)
        rows = cursor.fetchall()
        if len(rows) > 200:
            raise ValueError("WAVE_SOURCE_INTENT_BOUND_200")
        requests = [source_request(self.operation, self.wave, self.actor, *row) for row in rows]
        payload = cursor.var(oracledb.DB_TYPE_CLOB)
        payload.setvalue(0, json.dumps(requests, ensure_ascii=True))
        cursor.callproc("RRL_WAVE_CONTINUE_API.freeze_sources", [payload])

    def sources(self) -> list[dict[str, Any]]:
        with self.gateway.transaction("Read original frozen wave source intents") as cursor:
            cursor.execute("set transaction read only")
            cursor.callproc("RRL_WAVE_CONTINUE_API.assert_launch", [self.operation, self.wave, self.actor])
            cursor.execute("""select s.SOURCE_OPERATION_ID,dbms_lob.substr(s.CANONICAL_REQUEST,4000,1),
                dbms_lob.getlength(s.CANONICAL_REQUEST),o.STATE from RRL_WAVE_CONTINUE_SOURCE s
                left join RRL_STOCK_OPERATION o on o.OPERATION_ID=s.SOURCE_OPERATION_ID
                where s.LAUNCH_OPERATION_ID=:operation order by s.REPLENISH_TASK_ID""", operation=self.operation)
            rows = cursor.fetchall()
        result = []
        for operation, body, length, state in rows:
            if length > 4000:
                raise ValueError("WAVE_SOURCE_SAVED_REQUEST_BOUND_4000")
            result.append({"operation_id": operation, "body": body, "state": state})
        return result


def source_request(launch: str, wave: int, actor: str, row: int,
                   operation: str | None, saved: str | None, length: int | None) -> str:
    if operation or saved:
        if not operation or not saved or not length or length > 4000:
            raise ValueError("WAVE_SOURCE_EXISTING_INTENT_INCOMPLETE")
        data = json.loads(saved)
        if (data["operation_id"] != operation or data["source"]["wave_id"] != wave
                or data["metadata"]["requested_row_ids"] != [int(row)]):
            raise ValueError("WAVE_SOURCE_INTENT_IDENTITY_CONFLICT")
        return saved
    key = "WAVE.LAUNCH.SOURCE:" + sha256(launch.encode()).hexdigest()[:32] + ":" + str(row)
    return StockCommand(operation_id=key, command_type="WAVE_RESERVE_SOURCES", actor=actor,
                        lines=(), source={"type": "PICK_WAVE", "wave_id": wave},
                        metadata={"requested_row_ids": [int(row)], "allow_unissued_source_rebind": True,
                                  "launch_operation_id": launch}).canonical_json()
