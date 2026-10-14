"""Pure hints/captures on the posting cursor; root alone decides immutable replay."""
import json
from typing import Any
import oracledb

def prepare_staging_inputs(cursor: oracledb.Cursor,command_document: dict[str,Any],
                           operation_id: str) -> tuple[str|None,dict[str,Any],dict[str,Any]|None]:
    birth_captures = {}
    receipt_marks = None
    resolution = None
    if command_document["command_type"]=="RESERVATION_ALLOCATE_POOL":
        cursor.execute("select OPERATION_ID from RRL_STOCK_OPERATION where OPERATION_ID=:i",i=operation_id)
        if cursor.fetchone() is None:
            from .pool_plan import plan_pool
            try:
                resolution=json.dumps(plan_pool(cursor,command_document),ensure_ascii=True,separators=(",",":"),allow_nan=False)
            except Exception:
                cursor.execute("select OPERATION_ID from RRL_STOCK_OPERATION where OPERATION_ID=:i",i=operation_id)
                if cursor.fetchone() is None:raise
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
            from .birth_capture_commands import prepare_birth_capture
            resolution,birth_captures=prepare_birth_capture(cursor,command_document,operation_id)
    return resolution,birth_captures,receipt_marks
