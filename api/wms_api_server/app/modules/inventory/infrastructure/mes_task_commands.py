"""MES operator facts reuse warehouse task posting; cancellation releases H in that same command."""
import json
from decimal import Decimal
from fastapi import HTTPException
from ..contracts_stock import StockCommand, StockPostingError
from .stock_posting_uow import StockPosting
from ....schemas import WarehouseTaskStatusRequest


def post_mes_task(gateway, action: str, task: dict, request):
    rows = gateway.fetch_all("select STATE from RRL_STOCK_RELEASE where RELEASE_ID=1")
    if rows and rows[0]["state"] == "PREPARED":
        return None
    identity = int(task["task_id"])
    actor = request.confirmed_by if action == "CONFIRM" else request.cancelled_by
    if not actor:
        raise ValueError("Authenticated MES actor required")
    if action == "CONFIRM":
        operation = request.operation_id
        if not operation:
            raise HTTPException(422, detail="operation_id is required for MES confirmation after cutover")
        saved = gateway.fetch_all("""select CANONICAL_REQUEST from RRL_STOCK_OPERATION
            where OPERATION_ID=:id and ACTOR=:actor""", {"id": operation, "actor": actor})
        if saved:
            raw = saved[0]["canonical_request"]
            saved_request = json.loads(raw.read() if hasattr(raw, "read") else raw)
            saved_id = saved_request.get("source", {}).get("task_id")
            if saved_request.get("command_type") != "TASK_COMPLETE" or saved_id is None:
                raise HTTPException(409, detail={"code": "OPERATION_CONFLICT", "operation_id": operation})
            pending = gateway.fetch_all("""select TASK_ID,QTY from RRL_WAREHOUSE_TASK
                where TASK_ID=:warehouse and TASK_SOURCE='MES_RAW_SUPPLY' and SOURCE_TASK_ID=:raw""",
                {"warehouse": saved_id, "raw": identity})
        else:
            pending = gateway.fetch_all("""select TASK_ID,QTY from RRL_WAREHOUSE_TASK
                where TASK_SOURCE='MES_RAW_SUPPLY' and SOURCE_TASK_ID=:id
                and STATUS not in('DONE','CANCELLED') order by TASK_ID""", {"id": identity})
        if len(pending) != 1:
            raise HTTPException(409, detail="Confirm the individual remaining warehouse tasks.")
        warehouse = pending[0]
        source = {"type": "WAREHOUSE_TASK", "task_id": int(warehouse["task_id"])}
        command = "TASK_COMPLETE"
        default_fact = saved_request["metadata"]["fact_qty"] if saved else warehouse["qty"]
        fact = Decimal(str(request.fact_qty if request.fact_qty is not None else default_fact))
        metadata = WarehouseTaskStatusRequest(fact_qty=fact).model_dump(mode="json",
            exclude={"updated_by", "assigned_to", "operation_id"})
        metadata["fact_qty"] = format(fact, "f")
        metadata["document_confirmation"] = 1
    else:
        source = {"type": "MES_RAW_TASK", "raw_task_id": identity}
        command = "MES_RAW_TASK_CANCEL"
        metadata = {"reason": request.reason}
        operation = request.operation_id or f"MES.TASK.CANCEL:{identity}"
    try:
        return StockPosting().post(StockCommand(operation_id=operation, command_type=command,
            actor=actor, lines=(), source=source, metadata=metadata))
    except StockPostingError as exc:
        raise HTTPException(409, detail={"code": exc.code, "operation_id": exc.operation_id,
                                       "oracle_code": exc.oracle_code}) from exc
