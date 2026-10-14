from __future__ import annotations
from ....oracle_gateway import OracleGateway
from ....transaction_gateway import TransactionGateway
from typing import Any
from ....schemas import MesRawSupplyCalculateRequest
"""Calculate existing MES demand/candidates atomically without making a physical reservation."""
from uuid import uuid4
from fastapi import HTTPException
from ..contracts_stock import StockCommand, StockPostingError
from .stock_posting_uow import StockPosting
from .release_boundary import require_active_release


def calculate_supply(gateway: OracleGateway | TransactionGateway, order_id: int, request: MesRawSupplyCalculateRequest) -> dict[str, Any]:
    require_active_release(gateway,request.operation_id)
    try:
        result = StockPosting().post(StockCommand(
            operation_id=request.operation_id or "MES.CALCULATE:" + uuid4().hex,
            command_type="MES_CALCULATE_SUPPLY", actor=request.calculated_by,
            lines=(), source={"production_order_id": order_id},
            metadata={"to_cell": None, "to_ware_id": None, "allow_partial": 0}))
        return {"status": "ok", "production_order_id": order_id, **result}
    except StockPostingError as exc:
        raise HTTPException(409, detail={"code": exc.code, "operation_id": exc.operation_id,
                                       "oracle_code": exc.oracle_code}) from exc
