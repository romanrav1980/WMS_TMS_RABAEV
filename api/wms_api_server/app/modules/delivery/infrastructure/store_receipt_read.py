"""Shared current receiver authorization and frozen load reader."""
from typing import Any
import oracledb
from ..contracts import StoreReceiptError
from ...platform.public import read_oracle_json
from .store_unloading import unloading_fact


def read_store_preview(gateway: Any, load_operation_id: str, store_address: str, actor: str) -> dict[str,Any]:
    try:
        with gateway.transaction("Read receipt and unloading in one snapshot")as cursor:
            cursor.execute("set transaction read only")
            cursor.execute("select RRL_STOCK_STORE_RECEIPT_READ.preview_json(:op,:actor,:addr)from dual",
                           op=load_operation_id,actor=actor,addr=store_address)
            result=read_oracle_json(cursor.fetchone()[0])
            return {**result,"unloading":unloading_fact(cursor,load_operation_id,store_address)}
    except oracledb.DatabaseError as exc:
        code=getattr(exc.args[0],"code",0)
        if code==20882:
            raise StoreReceiptError("STORE_RECEIPT_FORBIDDEN",str(exc.args[0]).split("\n",1)[0],403) from exc
        if code==1403 or 20800<=abs(code)<=20999:
            raise StoreReceiptError("STORE_RECEIPT_SOURCE_UNAVAILABLE",str(exc.args[0]).split("\n",1)[0]) from exc
        raise
