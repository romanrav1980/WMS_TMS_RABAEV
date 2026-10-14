"""SOFT allocation API adapter: all reservation effects enter the existing root."""
import json
from decimal import Decimal
from typing import Any
from fastapi import HTTPException
from ..contracts_stock import StockCommand,StockPostingError
from .pool_plan import plan_pool
from .stock_posting_uow import StockPosting

class PoolService:
    def __init__(self,gateway: Any) -> None:
        self.gateway=gateway

    def preview(self,warehouse: int,article: str) -> dict[str,Any]:
        with self.gateway.transaction("Read SOFT demand pool") as cursor:
            hints=plan_pool(cursor,{"source":{"warehouse":warehouse,"article":article}})
        snapshot=json.loads(hints["snapshot"])
        return {"warehouse":warehouse,"article":article,"unit":snapshot["unit"],
                "from_stock":bool(snapshot["from_stock"]),"policy_version":snapshot["policy_version"],
                "available_quantity":snapshot["available"],"pick_step":snapshot["step"],
                "orders":snapshot["orders"],"allocations":hints["allocations"],
                "reservations":snapshot["reservations"],"preview":True,"physical_reserve":False}

    def allocate(self,warehouse: int,article: str,operation_id: str,actor: str) -> dict[str,Any]:
        try:
            return StockPosting().post(StockCommand(operation_id=operation_id,
                command_type="RESERVATION_ALLOCATE_POOL",actor=actor,lines=(),
                source={"type":"DEMAND_POOL","warehouse":warehouse,"article":article},metadata={}))
        except StockPostingError as exc:
            uncertain=exc.code in {"RESULT_UNCERTAIN","REQUEST_DEADLINE","CONNECTION_UNUSABLE","LOCK_RETRY_EXHAUSTED","STOCK_RELEASE_NOT_ACTIVE"}
            raise HTTPException(503 if uncertain else 409,detail={"code":exc.code,"oracle_code":exc.oracle_code,
                "operation_id":exc.operation_id,"outcome_confirmed":not uncertain,"retry_same_operation_id":uncertain}) from exc
