"""Read-only resolution followed by the sole Oracle posting unit of work."""
import json
from typing import Any
from ..contracts_observations import CountSubmission, InventoryObservationError
from ..contracts_stock import StockCommand
from .inventory_scan_codes import resolve_count_codes
from .stock_posting_uow import StockPosting
from .inventory_scope import assert_inventory_scope


class InventoryObservations:
    def __init__(self, gateway: Any, posting: StockPosting) -> None:
        self.gateway = gateway
        self.posting = posting

    def lots(self, revision_id: int, cell: str, article: str | None, actor: str) -> dict[str, Any]:
        assert_inventory_scope(self.gateway,actor,revision=revision_id)
        gateway = self.gateway
        rows = gateway.fetch_all("""
            select r.UID_POLETA LOT_UID,p.ARTICUL ARTICLE,r.CELL,to_char(r.REMAIN,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') PHYSICAL_QTY,
                   to_char(r.HARD_RESERVED_BASE,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') HARD_QTY,r.STOCK_VERSION,p.EXPIRY_DATE,
                   r.BASE_UOM UNIT
              from RRL_REMAINS r join RRL_PALLETS p on p.UID_PALLET=r.UID_POLETA
             where r.CELL=:cell and (:article is null or p.ARTICUL=:article) and exists(
               select 1 from RRL_REVIZION d join RRL_CELLS c on c.CELL=r.CELL
                where d.ID=:revision and d.WARE_ID=c.WARE_ID and d.CONDITION in (0,1))
             order by p.ARTICUL,p.EXPIRY_DATE,r.UID_POLETA fetch first 201 rows only
        """, {"cell": cell, "revision": revision_id,"article":article})
        if len(rows) > 200:
            raise InventoryObservationError("INVENTORY_CELL_BATCH_BOUND")
        for row in rows: row["uid"]=row.pop("lot_uid")
        articles = sorted({row["article"] for row in rows})
        if articles:
            params = {"article" + str(index): article for index, article in enumerate(articles)}
            profiles = gateway.fetch_all("select ARTICUL,SYSTEM_CODE,PROFILE_CODE from RRL_SKU_RECEIPT_PROFILE where ARTICUL in (" + ",".join(":" + key for key in params) + ") order by ARTICUL,SYSTEM_CODE,PROFILE_CODE", params)
            for row in rows:
                row["marking_profiles"] = [{"system_code": profile["system_code"], "profile_code": profile["profile_code"]} for profile in profiles if profile["articul"] == row["article"]]
        return {"revision_id": revision_id, "cell": cell, "lots": rows}

    def count(self, request: CountSubmission, actor: str) -> dict[str, Any]:
        assert_inventory_scope(self.gateway,actor,revision=request.revision_id)
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

    def create_revision(self, warehouse_id: int, actor: str) -> dict[str, Any]:
        assert_inventory_scope(self.gateway,actor,warehouse=warehouse_id)
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
