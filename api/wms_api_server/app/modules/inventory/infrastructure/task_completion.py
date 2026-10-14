"""Warehouse confirmation enters the stock coordinator before any domain locks or writes."""
from decimal import Decimal
from collections.abc import Callable
from typing import Any
from ....oracle_gateway import OracleGateway
from ....schemas import WarehouseTaskStatusRequest
from fastapi import HTTPException
import oracledb
from ..contracts_stock import StockCommand, StockPostingError
from ..contracts_task_actions import TaskActionHandler
from .stock_posting_uow import StockPosting
from ....transaction_gateway import TransactionGateway


def complete_existing_task(gateway: OracleGateway | TransactionGateway, task_id: int, request: WarehouseTaskStatusRequest, actor: str) -> dict[str, Any]:
    rows = gateway.fetch_all("select STATE from RRL_STOCK_RELEASE where RELEASE_ID=1")
    if not rows or rows[0]["state"] != "ACTIVE":
        raise HTTPException(503, detail="STOCK_RELEASE_NOT_ACTIVE")
    metadata = request.model_dump(mode="json", exclude={"updated_by", "assigned_to", "operation_id"})
    if metadata.get('scanned_to_slot_code') is None:
        metadata.pop('scanned_to_slot_code',None)
    if request.scan_draft_id is None:
        metadata.pop("scan_draft_id",None)
    else:
        drafts=gateway.fetch_all("select TASK_ID,ACTOR,UNIT_KEYS_JSON from RRL_TASK_SCAN_DRAFT where DRAFT_ID=:draft",{"draft":request.scan_draft_id})
        if not drafts or drafts[0]["task_id"]!=task_id or drafts[0]["actor"]!=actor:
            raise HTTPException(409,detail="TASK_SCAN_DRAFT_IDENTITY_CONFLICT")
        import json
        saved_keys=json.loads(drafts[0]["unit_keys_json"])
        if request.unit_keys and request.unit_keys!=saved_keys:
            raise HTTPException(409,detail="TASK_SCAN_DRAFT_SELECTION_CHANGED")
        metadata["unit_keys"]=saved_keys
    if request.fact_qty is not None:
        metadata["fact_qty"] = format(Decimal(str(request.fact_qty)), "f")
    operation = request.operation_id or f"TASK.COMPLETE:{task_id}"
    case_wait = gateway.fetch_all(
        "select p.CASE_TASK_ID,p.STOCK_VERSION,t.UID_PALLET,t.TO_CELL from RRL_ST_DEFER_WAIT_PLAN p "
        "join RRL_WAREHOUSE_TASK t on t.TASK_ID=p.TASK_ID where p.TASK_ID=:task and p.CASE_TASK_ID is not null",
        {"task": task_id})
    if case_wait:
        plan = case_wait[0]
        metadata.update({"physical_task_id": task_id, "scan_container": metadata.get("scanned_pallet"),
                         "target_cell": plan["to_cell"], "expected_content_version": int(plan["stock_version"])})
        if metadata.get("fact_qty") is None:
            metadata["fact_qty"] = "1"
        return _post_completion(StockCommand(operation_id=operation, command_type="CASE_CARRIER_MOVE",
            actor=actor, lines=(), source={"case_task_id": int(plan["case_task_id"])}, metadata=metadata))
    container = gateway.fetch_all(
        "select t.HU_CONTENT_VERSION,t.UID_PALLET,p.HU_KIND from RRL_WAREHOUSE_TASK t "
        "join RRL_PALLETS p on p.UID_PALLET=t.UID_PALLET where t.TASK_ID=:task", {"task": task_id})
    command_type = "HU_TASK_COMPLETE" if container and container[0]["hu_kind"] == "CONTAINER" else "TASK_COMPLETE"
    if command_type == "HU_TASK_COMPLETE" and metadata.get("scanned_pallet") != container[0]["uid_pallet"]:
        from ..domain.pallet_identifiers import normalize_incoming_sscc
        metadata["scanned_pallet"] = normalize_incoming_sscc(metadata.get("scanned_pallet"))
    return _post_completion(StockCommand(
        operation_id=operation, command_type=command_type, actor=actor, lines=(),
        source={"type": "WAREHOUSE_TASK", "task_id": task_id}, metadata=metadata,
    ))


def _post_completion(command: StockCommand) -> dict[str, Any]:
    try:
        return StockPosting().post(command)
    except StockPostingError as exc:
        code = 503 if exc.code in {"STOCK_RELEASE_NOT_ACTIVE", "REQUEST_DEADLINE",
                                   "CONNECTION_UNUSABLE", "RESULT_UNCERTAIN", "LOCK_RETRY_EXHAUSTED"} else 409
        if exc.oracle_code == 20882:
            code = 403
        raise HTTPException(code, detail={"code": exc.code, "operation_id": exc.operation_id,
                                         "oracle_code": exc.oracle_code, "reason": exc.rule_reason}) from exc


def lock_domain(gateway: OracleGateway | TransactionGateway, task: dict[str, Any]) -> None:
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




def run_existing_task_action(
    gateway: OracleGateway | TransactionGateway, task_id: int, action: str,
    request: WarehouseTaskStatusRequest,
    service_factory: Callable[[TransactionGateway], TaskActionHandler],
) -> None:
    if action not in {"assign_task", "start_task", "cancel_task"}:
        raise ValueError("Unsupported warehouse task action.")
    with gateway.transaction("Warehouse " + action) as cursor:
        try:
            permission = "warehouse_task_edit" if action == "cancel_task" else "warehouse_task_execute"
            cursor.execute("begin RRL_STOCK_METADATA_TX.begin_change(:actor,:permission);end;",
                           {"actor":request.updated_by,"permission":permission})
            bound = TransactionGateway(cursor)
            service = service_factory(bound)
            task = service.get_task_or_404(task_id)
            lock_domain(bound, task)
            bound.fetch_all("select TASK_ID from RRL_WAREHOUSE_TASK where TASK_ID=:id for update", {"id": task_id})
            try:
                cursor.execute(
                    "begin RRL_WAREHOUSE_TASK_ACCESS.assert_scope(:task,:actor,:assignee);end;",
                    {"task": task_id, "actor": request.updated_by,
                     "assignee": request.assigned_to if action == "assign_task" else None},
                )
            except oracledb.DatabaseError as exc:
                if getattr(exc.args[0], "code", None) == 20882:
                    raise HTTPException(403, detail="TASK_USER_WAREHOUSE_FORBIDDEN") from exc
                raise
            getattr(service, action)(task_id, request)
        finally:
            cursor.execute("begin RRL_STOCK_METADATA_TX.end_change;end;")
