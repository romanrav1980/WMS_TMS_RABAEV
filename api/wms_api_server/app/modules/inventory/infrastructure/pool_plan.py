"""Trusted planning hints: query Oracle rules, apportion once, and let the core verify the snapshot."""
import json
from decimal import Decimal
from typing import Any
from ..domain.pool_allocation import PoolDemand,allocate_pool

def plan_pool(cursor: Any,document: dict[str,Any]) -> dict[str,Any]:
    source=document["source"]
    cursor.execute("select RRL_STOCK_POOL_READ.snapshot_json(:ware,:article) from dual",
                   {"ware":source["warehouse"],"article":source["article"]})
    raw=cursor.fetchone()[0];raw=raw.read() if hasattr(raw,"read") else raw
    snapshot=json.loads(raw)
    orders=snapshot["orders"]
    if orders and snapshot["from_stock"]:
        result=allocate_pool(tuple(PoolDemand(int(o["line_id"]),Decimal(o["quantity"]),int(o["dispatch_order"])) for o in orders),
                             Decimal(snapshot["available"]),Decimal(snapshot["step"]))
        allocated={str(key):format(value,"f") for key,value in result.quantities.items()}
    else:
        allocated={str(o["line_id"]):"0" for o in orders}
    return {"snapshot":raw,"allocations":allocated,"algorithm":"PROPORTIONAL_WHOLE_STEP_V1"}
