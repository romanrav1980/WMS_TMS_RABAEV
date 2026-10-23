"""SOFT allocation API adapter: all reservation effects enter the existing root."""
import json
from typing import Any
from ..contracts_stock import StockCommand
from .pool_plan import plan_pool
from .stock_posting_uow import StockPosting

class PoolAccessError(PermissionError):
    """C-0162: the reader has no current pool view right on this warehouse."""


def _visible_lines(cursor: Any, warehouse: int, actor: str, lines: list[int]) -> set[int]:
    """Trade rows whose source or target owner the reader may view (as the capacity read decides); rows without a trade line keep the
    warehouse scope only. One bounded query per 500 rows and one owner check per distinct owner."""
    owners: dict[int, tuple[str, str]] = {}
    for start in range(0, len(lines), 500):
        part = lines[start:start + 500]
        binds = {f"r{i}": v for i, v in enumerate(part)}
        cursor.execute("select CUSTOMER_ORDER_ROW_ID,SOURCE_OWNER_ID,TARGET_OWNER_ID from RRL_TRADE_ORDER_LINE where CUSTOMER_ORDER_ROW_ID in("
                       + ",".join(":" + k for k in binds) + ")", binds)
        owners.update({int(r): (s, t) for r, s, t in cursor.fetchall()})
    allowed: dict[str, bool] = {}

    def can(owner: str) -> bool:
        if owner not in allowed:
            cursor.execute("select RRL_TRADE_STOCK_GUARD.owner_allowed(:a,:w,:o,0) from dual", {"a": actor, "w": warehouse, "o": owner})
            allowed[owner] = cursor.fetchone()[0] == 1
        return allowed[owner]
    return {line for line in lines if line not in owners or can(owners[line][0]) or can(owners[line][1])}


class PoolService:
    def __init__(self,gateway: Any) -> None:
        self.gateway=gateway

    def preview(self,warehouse: int,article: str,actor: str) -> dict[str,Any]:
        """C-0162: the plan is computed from the whole reader-independent snapshot; the reader sees it only with the current warehouse
        right, and on a trade site only the rows and source classes of owners it may view (complete=False says something is hidden)."""
        with self.gateway.transaction("Read SOFT demand pool") as cursor:
            cursor.execute("set transaction read only")
            cursor.execute("select RRL_ACCESS_API.allowed(:a,'stock_reservation_view','WAREHOUSE',:w) from dual",{"a":actor,"w":str(warehouse)})
            if cursor.fetchone()[0]!=1:
                raise PoolAccessError("POOL_WAREHOUSE_ACCESS_DENIED")
            hints=plan_pool(cursor,{"source":{"warehouse":warehouse,"article":article}})
            snapshot=json.loads(hints["snapshot"])
            orders,classes=snapshot["orders"],snapshot.get("classes")
            if snapshot.get("trade")==1:
                seen=_visible_lines(cursor,warehouse,actor,[int(o["line_id"]) for o in orders])
                orders=[o for o in orders if int(o["line_id"]) in seen]
                owner_ok:dict[str,bool]={}
                for c in classes or []:
                    if c["owner"] not in owner_ok:
                        cursor.execute("select RRL_TRADE_STOCK_GUARD.owner_allowed(:a,:w,:o,0) from dual",{"a":actor,"w":warehouse,"o":c["owner"]})
                        owner_ok[c["owner"]]=cursor.fetchone()[0]==1
                classes=[c for c in classes or [] if owner_ok[c["owner"]]]
        lines={str(o["line_id"]) for o in orders}
        complete=len(orders)==len(snapshot["orders"]) and (classes is None or len(classes)==len(snapshot.get("classes") or []))
        result={"warehouse":warehouse,"article":article,"unit":snapshot["unit"],
                "from_stock":bool(snapshot["from_stock"]),"policy_version":snapshot["policy_version"],
                "available_quantity":snapshot["available"] if complete else None,"pick_step":snapshot["step"],
                "orders":orders,"allocations":{k:v for k,v in hints["allocations"].items() if k in lines},
                "reservations":[r for r in snapshot["reservations"] if str(r["line_id"]) in lines],
                "complete":complete,"preview":True,"physical_reserve":False}
        if classes is not None:
            result["classes"]=classes
        return result

    def allocate(self,warehouse: int,article: str,operation_id: str,actor: str) -> dict[str,Any]:
        return StockPosting().post(StockCommand(operation_id=operation_id,
            command_type="RESERVATION_ALLOCATE_POOL",actor=actor,lines=(),
            source={"type":"DEMAND_POOL","warehouse":warehouse,"article":article},metadata={}))
