"""Warehouse confirmation enters the stock coordinator before any domain locks or writes."""
from decimal import Decimal
from fastapi import HTTPException
from ..contracts_stock import StockCommand, StockPostingError
from .stock_posting_uow import StockPosting
from ....transaction_gateway import TransactionGateway


def complete_existing_task(gateway, task_id: int, request, actor: str) -> dict:
    rows = gateway.fetch_all("select STATE from RRL_STOCK_RELEASE where RELEASE_ID=1")
    if rows and rows[0]["state"] == "PREPARED":
        # One global cutover; dormant sources must not disable the running legacy system.
        from ....services.warehouse_task_service import WarehouseTaskService
        with gateway.transaction("Warehouse completion before global cutover") as cursor:
            bound = TransactionGateway(cursor)
            service = WarehouseTaskService(bound)
            task = service.get_task_or_404(task_id)
            lock_domain(bound, task)
            bound.fetch_all("select TASK_ID from RRL_WAREHOUSE_TASK where TASK_ID=:id for update", {"id": task_id})
            service._complete_task_locked(task_id, request, actor)
            return {"task_id": task_id, "status": "DONE"}
    metadata = request.model_dump(mode="json", exclude={"updated_by", "assigned_to", "operation_id"})
    if request.fact_qty is not None:
        metadata["fact_qty"] = format(Decimal(str(request.fact_qty)), "f")
    operation = request.operation_id or f"TASK.COMPLETE:{task_id}"
    try:
        return StockPosting().post(StockCommand(
            operation_id=operation, command_type="TASK_COMPLETE", actor=actor, lines=(),
            source={"type": "WAREHOUSE_TASK", "task_id": task_id}, metadata=metadata,
        ))
    except StockPostingError as exc:
        code = 503 if exc.code in {"STOCK_RELEASE_NOT_ACTIVE", "REQUEST_DEADLINE",
                                   "CONNECTION_UNUSABLE", "LOCK_RETRY_EXHAUSTED"} else 409
        raise HTTPException(code, detail={"code": exc.code, "operation_id": exc.operation_id,
                                         "oracle_code": exc.oracle_code}) from exc


def lock_domain(gateway, task: dict) -> None:
    # Nonphysical assignment/start/cancellation retains its existing document serialization.
    source = task.get("task_source")
    if source == "WAVE":
        table, key, identity = "RRL_PICK_WAVE", "PICK_WAVE_ID", task.get("source_doc_id")
    elif source in {"MES_RAW_SUPPLY", "MES_COMPLETION"}:
        table, key, identity = "RRL_PRODUCTION_ORDER", "PRODUCTION_ORDER_ID", task.get("production_order_id") or task.get("source_doc_id")
    else:
        return
    rows = gateway.fetch_all(f"select {key},STATUS from {table} where {key}=:id for update",
                             {"id": identity}) if identity is not None else []
    if not rows or rows[0].get("status") == "CANCELLED":
        raise HTTPException(409, detail="Warehouse task source document is unavailable.")


def run_existing_task_action(gateway, task_id: int, action: str, request) -> None:
    from ....services.warehouse_task_service import WarehouseTaskService
    if action not in {"assign_task", "start_task", "cancel_task"}:
        raise ValueError("Unsupported warehouse task action.")
    with gateway.transaction("Warehouse " + action) as cursor:
        bound = TransactionGateway(cursor)
        service = WarehouseTaskService(bound)
        task = service.get_task_or_404(task_id)
        lock_domain(bound, task)
        bound.fetch_all("select TASK_ID from RRL_WAREHOUSE_TASK where TASK_ID=:id for update", {"id": task_id})
        getattr(service, action)(task_id, request)
