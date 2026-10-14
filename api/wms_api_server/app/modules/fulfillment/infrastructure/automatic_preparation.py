"""Automatic layout adapter; existing source locks and legacy writer own all effects."""
from hashlib import sha256
import json
from typing import Any
import oracledb
from ....transaction_gateway import TransactionGateway
from ...platform.public import read_oracle_json
from ..application.ports import StoreOrderConflict
from ..domain.automatic_layout import automatic_layout, STRATEGY
from .preparation_readiness import preparation_readiness
from .store_source_scope import source_transaction, assert_store_scope

def digest(value: dict) -> str:
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()

def lock_layout_inputs(cur: oracledb.Cursor, order: int) -> None:
    # Missing sequence rows must remain missing too: the table fence prevents insert phantoms.
    # All preparation paths acquire sequence -> article -> legacy order locks in this order.
    cur.execute("lock table RRL_COMPL_SEQ in share mode wait 3")
    cur.execute("""select a.ROWID from RRL_ARTICULS a where a.ACTICUL in
        (select r.ARTICUL from RRL_CUSTOMER_ORDER_ROW r where r.CUSTOMER_ORDER_ID=:o)
        order by a.ACTICUL,a.ROWID for update wait 3""", o=order)
    cur.fetchall()

class AutomaticPreparation:
    def __init__(self, legacy: Any) -> None:
        self.legacy = legacy

    def _layout(self, cur: oracledb.Cursor, order: int, limits: dict, actor: str, permission: str) -> dict:
        source = preparation_readiness(TransactionGateway(cur), order, actor, permission)
        if not source["ready_for_operator_layout"]:
            reasons = source["blockers"] + [x for l in source["lines"] for x in l["blockers"]]
            raise ValueError("SOURCE_PREPARATION_NOT_READY: " + ",".join(reasons))
        cur.execute("""select ARTICUL,SEQ_GROUP,SEQ from RRL_COMPL_SEQ
            where WARE_ID=:w and ARTICUL in
            (select ARTICUL from RRL_CUSTOMER_ORDER_ROW where CUSTOMER_ORDER_ID=:o)
            order by ARTICUL,SEQ_GROUP,SEQ fetch first 1001 rows only""",
            w=source["warehouse_id"], o=order)
        raw = cur.fetchall()
        if len(raw) > 1000:
            raise ValueError("AUTO_LAYOUT_SEQUENCE_BOUND_1000")
        sequence = {}
        for article, group, position in raw:
            if article in sequence or group is None or int(group) != group or (position is not None and int(position) != position):
                raise ValueError("AUTO_LAYOUT_SEQUENCE_AMBIGUOUS: " + article)
            sequence[article] = (int(group), int(position) if position is not None else None)
        result = automatic_layout(source["lines"], sequence, limits)
        signature = digest({"source": source, "sequence": sequence, "strategy": STRATEGY, "limits": limits})
        return {**result, "customer_order_id": order, "warehouse_id": source["warehouse_id"],
                "source_signature": signature, "limits": limits, "st_created": False,
                "consistent_snapshot": True}

    def preview(self, order: int, limits: dict, actor: str) -> dict:
        with self.legacy.gateway.transaction("Automatic original ST layout READ ONLY") as cur:
            cur.execute("set transaction read only")
            return self._layout(cur, order, limits, actor, "customer_order_view")

    def _saved(self, cur: oracledb.Cursor, order: int, request: dict, actor: str) -> dict | None:
        cur.execute("""select s.PREPARATION_HASH,s.PREPARATION_JSON,c.WARE_ID
            from RRL_SAP_STORE_ORDER s join RRL_CUSTOMER_ORDER c
            on c.CUSTOMER_ORDER_ID=s.CUSTOMER_ORDER_ID where c.CUSTOMER_ORDER_ID=:o""", o=order)
        row = cur.fetchone()
        if row is None:
            raise LookupError("SAP source order not found")
        assert_store_scope(cur, actor, "customer_order_import", row[2])
        if not row[0]:
            return None
        saved = read_oracle_json(row[1])
        if saved.get("auto_request_hash") != digest(request) or saved.get("operation_id") != request["operation_id"]:
            raise StoreOrderConflict("Source was prepared by a different saved command; inspect its existing ST")
        return {**saved, "idempotent": True}

    def prepare(self, order: int, request: dict, actor: str) -> dict:
        with source_transaction(self.legacy.gateway, "Automatic SAP demand to existing ST",
                                actor, "customer_order_import", order=order) as cur:
            saved = self._saved(cur, order, request, actor)
            if saved is not None:
                return saved
            lock_layout_inputs(cur, order)
            layout = self._layout(cur, order, request["limits"], actor, "customer_order_import")
            if layout["source_signature"] != request["source_signature"]:
                raise StoreOrderConflict("AUTO_LAYOUT_SOURCE_CHANGED_READ_NEW_PREVIEW")
            payload = {"operation_id": request["operation_id"], "pallets": layout["pallets"]}
            metadata = {"operation_id": request["operation_id"], "layout_source": STRATEGY,
                        "auto_request_hash": digest(request), "auto_request": request,
                        "pallet_statistics": layout["pallet_statistics"], "planned_pallets": layout["pallets"], "stock_changed": False}
            return self.legacy._prepare_locked(cur, order, payload, actor, metadata)

    def resolve(self, order: int, request: dict, actor: str) -> dict:
        with source_transaction(self.legacy.gateway, "Resolve automatic ST preparation",
                                actor, "customer_order_import", order=order) as cur:
            saved = self._saved(cur, order, request, actor)
            return {"state": "ST_PREPARED" if saved else "NOT_PREPARED",
                    "customer_order_id": order, "operation_id": request["operation_id"],
                    "result": saved, "stock_changed": False}
