"""Read-only resolution followed by the sole Oracle posting unit of work."""
import json
from typing import Any
from ..contracts_observations import CountSubmission, InventoryObservationError
from ..contracts_stock import StockCommand
from .inventory_scan_codes import resolve_count_codes
from .stock_posting_uow import StockPosting
from .inventory_scope import assert_inventory_scope
from .inventory_lot_reads import inventory_lots


class InventoryObservations:
    def __init__(self, gateway: Any, posting: StockPosting) -> None:
        self.gateway = gateway
        self.posting = posting

    def lots(self, revision_id: int, cell: str, article: str | None, actor: str, *, task_id: int | None = None) -> dict[str, Any]:
        return inventory_lots(self.gateway, revision_id, cell, article, actor, task_id)

    def count(self, request: CountSubmission, actor: str) -> dict[str, Any]:
        assert_inventory_scope(self.gateway,actor,revision=request.revision_id,task=request.inventory_task_id)
        counts = [line.wire(False) for line in request.counts]
        requested = [line.wire() for line in request.counts]
        gateway = self.gateway
        saved = gateway.fetch_all("select CANONICAL_REQUEST from RRL_STOCK_OPERATION where OPERATION_ID=:operation and ACTOR=:actor", {"operation": request.operation_id, "actor": actor})
        if saved:
            payload = saved[0]["canonical_request"]
            payload = payload if isinstance(payload,dict) else json.loads(payload.read() if hasattr(payload, "read") else payload)
            old = payload["metadata"]
            original = old.get("requested_counts", [{**line, "scans": []} for line in old.get("counts", [])])
            if payload["command_type"] != "INVENTORY_COUNT" or payload["source"] != {"revision_id": request.revision_id} or old.get("reason") != request.reason or original != requested or old.get("inventory_task_id") != request.inventory_task_id:
                raise InventoryObservationError("OPERATION_CONTENT_CONFLICT",operation_id=request.operation_id)
            metadata = old
        else:
            for index, keys in enumerate(resolve_count_codes(gateway, request.counts)):
                counts[index]["unit_keys"] = keys
            metadata = {"reason": request.reason, "counts": counts, "requested_counts": requested}
            if request.inventory_task_id is not None: metadata["inventory_task_id"] = request.inventory_task_id
        return self.posting.post(StockCommand(
            operation_id=request.operation_id, command_type="INVENTORY_COUNT", actor=actor,
            source={"revision_id": request.revision_id}, lines=(),
            metadata=metadata,
        ))

    def create_revision(self, warehouse_id: int, actor: str, *, task_id: int | None = None) -> dict[str, Any]:
        assert_inventory_scope(self.gateway,actor,warehouse=warehouse_id,task=task_id)
        gateway = self.gateway
        cells = gateway.fetch_all("select 1 PRESENT from RRL_CELLS where WARE_ID=:ware fetch first 1 row only", {"ware": warehouse_id})
        if not cells:
            raise InventoryObservationError("WAREHOUSE_HAS_NO_CELLS",422)
        revision = gateway.call_number_plsql("begin :result:=REVIZION.create_revizion(:ware,:actor);end;", {"ware": warehouse_id, "actor": actor})
        return {"revision_id": revision, "warehouse_id": warehouse_id}
    def register_lot(self, operation_id: str, revision_id: int, metadata: dict[str, Any], actor: str) -> dict[str, Any]:
        assert_inventory_scope(self.gateway,actor,revision=revision_id)
        from ..contracts_stock import StockPostingError
        try:
            return self.posting.post(StockCommand(operation_id=operation_id,
                command_type="INVENTORY_REGISTER_LOT",actor=actor,lines=(),
                source={"revision_id":revision_id},metadata=metadata))
        except StockPostingError as exc:
            status=403 if exc.oracle_code==20882 else 409 if exc.oracle_code is not None and 20800<=exc.oracle_code<=20999 else 503
            raise InventoryObservationError(exc.rule_reason or exc.code,status,operation_id) from exc
