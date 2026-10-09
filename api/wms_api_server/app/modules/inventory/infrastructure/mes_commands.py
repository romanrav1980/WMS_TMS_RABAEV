"""Existing MES movements enter one bounded, replayable physical command."""
from hashlib import sha256
import json
from fastapi import HTTPException
from ..contracts_stock import StockCommand, StockPostingError
from .stock_posting_uow import StockPosting


def _post(command):
    try:
        return StockPosting().post(command)
    except StockPostingError as exc:
        uncertain = exc.code in {"RESULT_UNCERTAIN", "STOCK_RELEASE_NOT_ACTIVE", "REQUEST_DEADLINE",
                                 "CONNECTION_UNUSABLE", "LOCK_RETRY_EXHAUSTED"}
        raise HTTPException(503 if uncertain else 409, detail={
            "code": exc.code, "operation_id": exc.operation_id,
            "oracle_code": exc.oracle_code, "outcome_confirmed": not uncertain,
        }) from exc


def apply_mes_movements(gateway, production_order_id: int, request, actor: str | None):
    state = gateway.fetch_all("select STATE from RRL_STOCK_RELEASE where RELEASE_ID=1")
    if state and state[0]["state"] == "PREPARED":
        return None
    if not actor:
        raise ValueError("Authenticated MES actor required")
    if sum(len(values) for values in request.units_by_movement.values()) > 10000:
        raise HTTPException(422, detail="At most 10000 physical units per command")
    ids = request.movement_ids
    if ids is not None and (len(ids) > 200 or len(ids) != len(set(ids))):
        raise HTTPException(422, detail="At most 200 distinct MES movements per atomic batch")
    if ids is None and not request.operation_id:
        raise HTTPException(422, detail={"code": "OPERATION_ID_REQUIRED"})
    if request.operation_id:
        saved = gateway.fetch_all(
            "select CANONICAL_REQUEST from RRL_STOCK_OPERATION where OPERATION_ID=:id",
            {"id": request.operation_id},
        )
        if saved:
            value = saved[0]["canonical_request"]
            original = json.loads(value.read() if hasattr(value, "read") else value)
            source = original.get("source", {})
            metadata = original.get("metadata", {})
            if (original.get("command_type") != "MES_MOVEMENTS"
                or original.get("actor") != actor
                or source.get("production_order_id") != production_order_id
                or metadata != {"units_by_movement": request.units_by_movement, **({"birth_captures": request.birth_captures} if request.birth_captures else {})}
                or (ids is not None and sorted(ids) != source.get("movement_ids"))):
                raise HTTPException(409, detail={"code": "OPERATION_CONFLICT",
                    "operation_id": request.operation_id, "outcome_confirmed": True})
            # Do not re-resolve a changing pending set after a successful commit.
            return _post(StockCommand(
                operation_id=request.operation_id, command_type="MES_MOVEMENTS", actor=actor,
                lines=(), source=source, metadata=metadata,
            ))
    if ids is None:
        rows = gateway.fetch_all("""
            select MOVEMENT_ID from RRL_MES_MOVEMENT
             where PRODUCTION_ORDER_ID=:i and STATUS in('MES_POSTED','ERROR')
               and MOVEMENT_TYPE in('RAW_ISSUE_TO_PRODUCTION','RAW_CONSUMPTION','FG_PALLET_RELEASE')
             order by MOVEMENT_ID fetch first 201 rows only
        """, {"i": production_order_id})
        ids = [int(r["movement_id"]) for r in rows]
    if len(ids) > 200:
        raise HTTPException(422, detail="At most 200 MES movements per atomic batch")
    if not ids:
        return {"production_order_id": production_order_id, "status": "NO_PENDING_MOVEMENTS"}
    ids = sorted(ids)
    identity = sha256(json.dumps(ids, separators=(",", ":")).encode()).hexdigest()
    operation = request.operation_id or f"MES.APPLY:{identity}"
    return _post(StockCommand(
        operation_id=operation, command_type="MES_MOVEMENTS", actor=actor, lines=(),
        source={"type": "PRODUCTION_ORDER", "production_order_id": production_order_id, "movement_ids": ids},
        metadata={"units_by_movement": request.units_by_movement, **({"birth_captures": request.birth_captures} if request.birth_captures else {})},
    ))
