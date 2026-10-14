"""Bounded capture preparation and errors; immutable root decides replay."""
from typing import Any
import json
import oracledb
from ..contracts_stock import StockPostingError
from .birth_capture import plan_births,stage_births

def prepare_birth_capture(cursor: Any,document: dict[str,Any],operation_id: str) -> tuple[str|None,dict[str,Any]]:
    try:
        hints,captures=plan_births(cursor,document)
        return json.dumps(hints,ensure_ascii=True,separators=(",",":"),allow_nan=False),captures
    except Exception as exc:
        cursor.execute("select OPERATION_ID from RRL_STOCK_OPERATION where OPERATION_ID=:op",op=operation_id)
        if cursor.fetchone() is not None:
            return None,{}
        if isinstance(exc,(ValueError,TypeError,KeyError)):
            raise StockPostingError("BIRTH_CAPTURE_REJECTED",operation_id,20886,str(exc)) from exc
        raise

def stage_checked_births(cursor: Any,document: dict[str,Any],captures: dict[str,Any]) -> None:
    try:
        stage_births(cursor,document,captures)
    except (ValueError,TypeError,KeyError) as exc:
        raise StockPostingError("BIRTH_CAPTURE_REJECTED",document["operation_id"],20886,str(exc)) from exc

    except oracledb.IntegrityError as exc:
        if exc.args[0].code == 1 and "RRL_RECEIPT_UNIT_PHYSICAL_UK" in str(exc):
            raise StockPostingError("PHYSICAL_UNIT_ALREADY_RECEIVED", document["operation_id"], 20886, "The same physical unit cannot be born twice.") from exc
        raise
