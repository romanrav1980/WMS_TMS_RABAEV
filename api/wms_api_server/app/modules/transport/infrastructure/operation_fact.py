"""Keep the existing fact edit with current dispatcher/warehouse and row serialization."""
import json
from typing import Any
import oracledb
from ...platform.public import read_oracle_json
from .trip_edit import trip_error

def update_existing_operation_fact(gateway: Any,operation: int,fields: dict[str,Any],actor: str) -> dict[str,Any]:
    try:
        with gateway.transaction("Existing ARM fact metadata with current warehouse scope") as cur:
            result=cur.var(oracledb.DB_TYPE_CLOB)
            cur.callproc("RRL_TT_OPERATION_PLAN_API.write_fact",
                [operation,actor,json.dumps(fields,sort_keys=True,separators=(",",":"),ensure_ascii=False),result])
            return read_oracle_json(result.getvalue())
    except oracledb.DatabaseError as exc:raise trip_error(exc) from exc
