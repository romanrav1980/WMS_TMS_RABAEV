"""Explicit transfer between existing prepared ST places; original Oracle writer."""
from typing import Any
import oracledb
from ...platform.public import read_oracle_json
from ...inventory.public import StockCommand, StockPostingError


class PreparedLayout:
    def __init__(self, gateway: Any, posting: Any) -> None:
        self.gateway, self.posting = gateway, posting

    def read(self, order: int, actor: str) -> dict[str, Any]:
        try:
            with self.gateway.transaction("Read current prepared ST layout") as cur:
                cur.execute("set transaction read only")
                ware = cur.callfunc("RRL_ST_LAYOUT_READ.scope_order", oracledb.DB_TYPE_NUMBER, [order, actor])
                cur.execute("""select s.ID,s.PALLET_UID,s.ST_NUMBER,s.TRANSTASK_ID,s.CONDITION,f.STATUS,
                    r.ID,r.ARTICUL,r.EI,RRL_STOCK_PLAN_HELPER.decimal_text(r.QUANTITY),
                    RRL_STOCK_PLAN_HELPER.decimal_text(r.PACK_COUNT),
                    RRL_STOCK_PLAN_HELPER.decimal_text(r.ORDER_WEIGHT)
                    from RRL_CUSTOMER_ORDER_FULFILLMENT f join RRL_SBORKA_PALLETS s on s.ID=f.LEGACY_SBORKA_PALLET_ID
                    left join RRL_SBORKA_PALLET_ROWS r on r.PALLET_UID=s.PALLET_UID
                    where f.CUSTOMER_ORDER_ID=:order_id order by s.ID,r.ID fetch first 201 rows only""", order_id=order)
                rows = cur.fetchall()
                keys = ("shipment_id", "pallet_identifier", "st_number", "trip_id", "shipment_status",
                        "fulfillment_status", "row_id", "article", "unit", "quantity", "packs", "weight")
                return {"order_id": order, "warehouse": int(ware), "rows": [dict(zip(keys, r)) for r in rows[:200]],
                        "truncated": len(rows) > 200, "stock_changed": False}
        except oracledb.Error as exc:
            self._failure(exc)

    def preview(self, order: int, row: int, target: int, actor: str) -> dict[str, Any]:
        try:
            with self.gateway.transaction("Preview conserved existing ST row move") as cur:
                cur.execute("set transaction read only")
                return read_oracle_json(cur.callfunc("RRL_ST_LAYOUT_READ.snapshot",
                    oracledb.DB_TYPE_CLOB, [order, row, target, actor]))
        except oracledb.Error as exc:
            self._failure(exc)

    def move(self, order: int, body: dict[str, Any], actor: str) -> dict[str, Any]:
        return self.posting.post(StockCommand(operation_id=body["operation_id"], command_type="ST_PREPARED_ROW_MOVE",
            actor=actor, lines=(), source={"order_id": order, "row_id": body["row_id"],
            "target_shipment_id": body["target_shipment_id"]},
            metadata={"expected_signature": body["expected_signature"], "reason": body["reason"]}))

    @staticmethod
    def _failure(exc: Exception) -> None:
        code = getattr(exc.args[0], "code", None)
        if code is not None and 20800 <= code <= 20999:
            raise StockPostingError("ST_LAYOUT_REJECTED", "READ", code, str(exc.args[0]).split("\n", 1)[0]) from exc
        raise exc
