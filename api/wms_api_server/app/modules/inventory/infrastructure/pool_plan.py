"""Trusted planning hints: query Oracle rules, apportion once, and let the core verify the snapshot."""
import json
from decimal import Decimal
from typing import Any
from ..domain.pool_allocation import PoolDemand,TradeDemand,allocate_pool,allocate_trade_pool

def plan_pool(cursor: Any,document: dict[str,Any]) -> dict[str,Any]:
    source=document["source"]
    cursor.execute("select RRL_STOCK_POOL_READ.snapshot_json(:ware,:article) from dual",
                   {"ware":source["warehouse"],"article":source["article"]})
    raw=cursor.fetchone()[0];raw=raw.read() if hasattr(raw,"read") else raw
    snapshot=json.loads(raw)
    orders=snapshot["orders"]
    if orders and snapshot["from_stock"] and snapshot.get("trade")==1:
        # C-0160: a trade site names the physical classes behind every share; rows with a pool_reason get nothing.
        demands=tuple(TradeDemand(int(o["line_id"]),Decimal(o["quantity"]),int(o["dispatch_order"]),tuple(o.get("classes") or ()))
                      for o in orders if "pool_reason" not in o)
        free={c["key"]:Decimal(c["free"]) for c in snapshot["classes"]}
        result=allocate_trade_pool(demands,free,Decimal(snapshot["step"]))
        allocated={str(o["line_id"]):format(result.quantities.get(int(o["line_id"]),Decimal(0)),"f") for o in orders}
        sources={str(line):{key:format(value,"f") for key,value in split.items()} for line,split in result.sources.items()}
        return {"snapshot":raw,"allocations":allocated,"sources":sources,"algorithm":"PROPORTIONAL_WHOLE_STEP_V1"}
    if orders and snapshot["from_stock"]:
        result=allocate_pool(tuple(PoolDemand(int(o["line_id"]),Decimal(o["quantity"]),int(o["dispatch_order"])) for o in orders),
                             Decimal(snapshot["available"]),Decimal(snapshot["step"]))
        allocated={str(key):format(value,"f") for key,value in result.quantities.items()}
    else:
        allocated={str(o["line_id"]):"0" for o in orders}
    return {"snapshot":raw,"allocations":allocated,"algorithm":"PROPORTIONAL_WHOLE_STEP_V1"}
