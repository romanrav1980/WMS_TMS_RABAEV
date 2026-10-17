"""Actual unloading clocks and method facts; original receipt keeps its effects."""
import json
from typing import Any
import oracledb
from ...platform.public import read_oracle_json
from ..contracts import StoreReceiptError


def start_unloading(gateway: Any,body: dict[str,Any],actor: str)->dict[str,Any]:
    return _command(gateway,body,actor,"start_unloading")


def abandon_unloading(gateway: Any,body: dict[str,Any],actor: str)->dict[str,Any]:
    return _command(gateway,body,actor,"abandon_start")


def _command(gateway: Any,body: dict[str,Any],actor: str,procedure: str)->dict[str,Any]:
    operation=str(body["operation_id"])
    try:
        with gateway.transaction("Start unloading original departed store place")as cursor:
            result=cursor.var(oracledb.DB_TYPE_CLOB)
            cursor.callproc("RRL_STORE_UNLOAD_API."+procedure,[
                json.dumps(body,sort_keys=True,separators=(",",":"),ensure_ascii=False),actor,result])
            return read_oracle_json(result.getvalue())
    except oracledb.DatabaseError as exc:
        code=getattr(exc.args[0],"code",0)
        if 20800<=code<=20999:
            raise StoreReceiptError("STORE_UNLOAD_REJECTED",str(exc.args[0]).split("\n",1)[0],
                                    403 if code==20882 else 409,operation)from exc
        raise


def unloading_fact(cursor: Any,load: str,address: str)->dict[str,Any]|None:
    cursor.execute("""select s.RESULT_JSON,f.RECEIPT_OPERATION_ID,f.PAYLOAD_JSON,
        to_char(f.FINISHED_AT_INSTANT,'YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM')
        from RRL_STORE_UNLOAD_START s left join RRL_STORE_UNLOAD_FACT f on f.START_OPERATION_ID=s.OPERATION_ID
        where s.LOAD_OPERATION_ID=:load_id and s.STORE_ADDR=:address""",load_id=load,address=address)
    row=cursor.fetchone()
    if row is None:return None
    return {**read_oracle_json(row[0]),"status":"COMPLETED"if row[1]else "STARTED",
            "receipt_operation_id":row[1],"actual_details":read_oracle_json(row[2])if row[2]is not None else None,
            "finished_at_instant":row[3]}


def read_unloading(gateway: Any,load: str,address: str,actor: str)->dict[str,Any]:
    try:
        with gateway.transaction("Read original store unloading fact")as cursor:
            cursor.execute("set transaction read only")
            domain=cursor.var(oracledb.DB_TYPE_CLOB)
            cursor.callproc("RRL_STOCK_STORE_RECEIPT_READ.describe_load",[load,actor,address,domain])
            return {"load_operation_id":load,"store_address":address,"unloading":unloading_fact(cursor,load,address),
                    "stock_changed":False,"cost_posted":False}
    except oracledb.DatabaseError as exc:
        code=getattr(exc.args[0],"code",0)
        if code==20882 or code==1403 or 20800<=code<=20999:
            raise StoreReceiptError("STORE_UNLOAD_SOURCE_UNAVAILABLE",str(exc.args[0]).split("\n",1)[0],
                                    403 if code==20882 else 409)from exc
        raise
