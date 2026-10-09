"""One connection and one deadline for all retries; only this runner commits."""
from collections.abc import Callable
from dataclasses import dataclass
from time import monotonic
from typing import Any
import json
import logging
import random
import oracledb
from ....db import _oracle_pool
from ..contracts_stock import StockCommand, StockPostingError

RETRY_CODES = {54, 60, 20840, 20846, 20890, 30006}
REQUEST_BUDGET = 30.0
_LOG = logging.getLogger(__name__)


@dataclass
class _Lease:
    connection: Any
    discard: bool = False


def _oracle_code(exc: Exception) -> int | None:
    detail = exc.args[0] if exc.args else None
    return getattr(detail, "code", None)


def _discard(pool: Any, connection: Any) -> None:
    try:
        pool.drop(connection)
    except Exception:
        try:
            connection.close()
        except Exception:
            _LOG.error("Stock connection disposal failed; the poisoned lease is withheld from the pool")


def _attempt(lease: _Lease, payload: str, actor: str, operation_id: str,
             deadline: float) -> dict[str, Any]:
    connection = lease.connection
    cursor = None
    committing = False
    posting_started = False
    try:
        remaining = deadline - monotonic()
        if remaining <= 0:
            raise StockPostingError("REQUEST_DEADLINE", operation_id)
        connection.autocommit = False
        connection.call_timeout = max(1, int(min(remaining, 3.0) * 1000))
        cursor = connection.cursor()
        cursor.execute("select STATE from RRL_STOCK_RELEASE where RELEASE_ID=1")
        state = cursor.fetchone()
        if state is None or state[0] != "ACTIVE":
            raise StockPostingError("STOCK_RELEASE_NOT_ACTIVE", operation_id)
        command_document = json.loads(payload)
        birth_captures = {}
        receipt_marks = None
        resolution = None
        if command_document["command_type"] == "SAP_RECEIPT":
            cursor.execute("select OPERATION_ID from RRL_STOCK_OPERATION where OPERATION_ID=:i", i=operation_id)
            if cursor.fetchone() is None:
                from .receipt_commands import plan_receipt
                try:
                    hints, receipt_marks = plan_receipt(cursor, command_document)
                    resolution = json.dumps(hints, ensure_ascii=True, separators=(",", ":"), allow_nan=False)
                except Exception:
                    # Pure preview can fail after another identical receipt has committed.
                    # Defer immutable actor/body comparison to the core replay path.
                    cursor.execute("select OPERATION_ID from RRL_STOCK_OPERATION where OPERATION_ID=:i", i=operation_id)
                    if cursor.fetchone() is None:
                        raise
        if command_document["command_type"] in {"INVENTORY_REGISTER_LOT","MES_MOVEMENTS"}:
            cursor.execute("select OPERATION_ID from RRL_STOCK_OPERATION where OPERATION_ID=:i",i=operation_id)
            if cursor.fetchone() is None:
                from .birth_capture import plan_births
                try:
                    hints,birth_captures=plan_births(cursor,command_document)
                    resolution=json.dumps(hints,ensure_ascii=True,separators=(",",":"),allow_nan=False)
                except Exception:
                    cursor.execute("select OPERATION_ID from RRL_STOCK_OPERATION where OPERATION_ID=:i",i=operation_id)
                    if cursor.fetchone() is None:raise
        posting_started = True
        result = cursor.var(oracledb.DB_TYPE_CLOB)
        payload_bind = cursor.var(oracledb.DB_TYPE_CLOB)
        payload_bind.setvalue(0, payload)
        resolution_bind = cursor.var(oracledb.DB_TYPE_CLOB)
        resolution_bind.setvalue(0, resolution)
        cursor.execute(
            "begin RRL_STOCK_POSTING_API.prepare_command(:payload,:actor,:result,:resolution); end;",
            {"payload": payload_bind, "actor": actor, "result": result, "resolution": resolution_bind},
        )
        value = result.getvalue()
        if value is None:
            remaining = deadline - monotonic()
            if remaining <= 0:
                raise StockPostingError("REQUEST_DEADLINE", operation_id)
            connection.call_timeout = max(1, int(remaining * 1000))
            if command_document["command_type"] == "SAP_RECEIPT":
                from .receipt_commands import stage_receipt
                stage_receipt(cursor, command_document, receipt_marks)
            if birth_captures:
                from .birth_capture import stage_births
                stage_births(cursor,command_document,birth_captures)
            cursor.execute("begin RRL_STOCK_POSTING_API.execute_prepared(:result); end;", {"result": result})
            value = result.getvalue()
        text = value.read() if hasattr(value, "read") else value
        response = json.loads(text)
        remaining = deadline - monotonic()
        if remaining <= 0:
            raise StockPostingError("REQUEST_DEADLINE", operation_id)
        connection.call_timeout = max(1, int(remaining * 1000))
        committing = True
        connection.commit()
        committing = False
        return response
    except Exception as exc:
        try:
            connection.call_timeout = 5000
            connection.rollback()
        except Exception:
            lease.discard = True
        if committing:
            # A rollback on a reconnected/broken session cannot disprove a previous commit.
            lease.discard = True
            raise StockPostingError("RESULT_UNCERTAIN", operation_id) from exc
        raise
    finally:
        if cursor is not None:
            try:
                connection.call_timeout = 5000
                if posting_started:
                    cursor.execute("begin RRL_STOCK_POSTING_API.reset_connection; end;")
                cursor.close()
            except Exception:
                lease.discard = True


class StockPosting:
    def __init__(self, wait: Callable[[float], None] | None = None) -> None:
        from time import sleep
        self.wait = wait or sleep

    def post(self, command: StockCommand) -> dict[str, Any]:
        payload = command.canonical_json()
        deadline = monotonic() + REQUEST_BUDGET
        pool = _oracle_pool()
        # Acquire once: retries must not restart a 30-second pool wait.
        lease = _Lease(pool.acquire())
        old_timeout = lease.connection.call_timeout
        try:
            for attempt in range(3):
                try:
                    return _attempt(lease, payload, command.actor, command.operation_id, deadline)
                except oracledb.DatabaseError as exc:
                    code = _oracle_code(exc)
                    if lease.discard:
                        raise StockPostingError("CONNECTION_UNUSABLE", command.operation_id, code) from exc
                    if code in {1403, 1422}:
                        raise StockPostingError("RESOURCE_NOT_FOUND" if code == 1403 else "DATA_AMBIGUOUS",
                                                command.operation_id, code) from exc
                    if code not in RETRY_CODES:
                        if code is not None and 20800 <= code <= 20899:
                            raise StockPostingError("STOCK_RULE_REJECTED", command.operation_id, code) from exc
                        raise
                    if attempt == 2:
                        raise StockPostingError("LOCK_RETRY_EXHAUSTED", command.operation_id, code) from exc
                    delay = random.uniform(*((0.05, 0.2) if attempt == 0 else (0.2, 0.8)))
                    if monotonic() + delay >= deadline:
                        raise StockPostingError("REQUEST_DEADLINE", command.operation_id) from exc
                    self.wait(delay)
            raise StockPostingError("REQUEST_DEADLINE", command.operation_id)
        finally:
            if lease.discard:
                _discard(pool, lease.connection)
            else:
                try:
                    lease.connection.call_timeout = old_timeout
                    pool.release(lease.connection)
                except Exception:
                    _discard(pool, lease.connection)
