"""Original ARM operations; native generator preserves IDs and execution facts."""
from typing import Any
import oracledb
from ...platform.public import read_oracle_json
from .trip_edit import trip_error

def generate_existing_operations(gateway: Any,trip: int,actor: str) -> list[dict[str,Any]]:
    try:
        with gateway.transaction("Plan existing ARM operations without deleting facts") as cur:
            result=cur.var(oracledb.DB_TYPE_CLOB)
            cur.callproc("RRL_TT_OPERATION_PLAN_API.generate",[trip,actor,result])
            rows=read_oracle_json(result.getvalue())
            if not isinstance(rows,list):raise RuntimeError("OP_PLAN_RESULT_ARRAY_REQUIRED")
            return rows
    except oracledb.DatabaseError as exc:raise trip_error(exc) from exc
