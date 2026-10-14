"""Same-cursor native invocation shared by draft and configuration publication."""
import json
from typing import Any
import oracledb
from ...platform.public import read_oracle_json

def range_command(cur: Any, ware: int, article: str, operation: str, action: str, actor: str,
                  body: dict[str, Any], source: dict[str, Any] | None = None) -> dict[str, Any]:
    request = json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)
    request_var = cur.var(oracledb.DB_TYPE_CLOB); request_var.setvalue(0, request)
    source_var = cur.var(oracledb.DB_TYPE_CLOB)
    if source is not None:
        source_var.setvalue(0, json.dumps(source, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False))
    result = cur.var(oracledb.DB_TYPE_CLOB)
    cur.callproc("RRL_PICK_RANGE_PROPOSAL_API.execute_command",
        [operation, actor, action, ware, article, request_var, source_var, result])
    return read_oracle_json(result.getvalue())
