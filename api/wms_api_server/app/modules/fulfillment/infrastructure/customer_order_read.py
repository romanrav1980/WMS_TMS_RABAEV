"""Original customer order reads with one current native warehouse scope."""
from __future__ import annotations
from typing import Any
from ....transaction_gateway import TransactionGateway
from .store_source_scope import actor_warehouse, assert_store_scope


class CustomerOrderRead:
    def __init__(self, gateway: Any) -> None:
        self.gateway = gateway

    def list(self, actor: str, status: str | None = None, order_no: str | None = None,
             legacy_order_id: int | None = None, limit: int = 200,
             before_id: int | None = None) -> list[dict[str, Any]]:
        if before_id is not None and before_id == 0:
            raise ValueError("Non-zero order cursor required")
        with self.gateway.transaction("Customer order list scoped READ ONLY") as cur:
            if not getattr(self.gateway, "transaction_bound", False):
                cur.execute("set transaction read only")
            warehouse, global_admin = actor_warehouse(cur, actor, "customer_order_view")
            return CustomerOrderRead(TransactionGateway(cur)).list_rows(
                status, order_no, legacy_order_id, limit, None if global_admin else warehouse, before_id)

    def get(self, order_id: int, actor: str) -> dict[str, Any]:
        if order_id == 0:
            raise ValueError("Non-zero order ID required")
        with self.gateway.transaction("Customer order detail scoped READ ONLY") as cur:
            if not getattr(self.gateway, "transaction_bound", False):
                cur.execute("set transaction read only")
            cur.execute("select WARE_ID from RRL_CUSTOMER_ORDER where CUSTOMER_ORDER_ID=:id", id=order_id)
            row = cur.fetchone()
            if row is None:
                raise LookupError("Customer order not found")
            assert_store_scope(cur, actor, "customer_order_view", row[0])
            order = CustomerOrderRead(TransactionGateway(cur)).detail_rows(order_id)
            if order is None:
                raise LookupError("Customer order not found")
            return order

    def list_rows(
        self,
        status: str | None = None,
        order_no: str | None = None,
        legacy_order_id: int | None = None,
        limit: int = 200,
        warehouse: int | None = None,
        before_id: int | None = None,
    ) -> list[dict[str, Any]]:
        conditions: list[str] = ["exists(select 1 from RRL_CUSTOMER cx where cx.CUSTOMER_ID=co.CUSTOMER_ID)"]
        params: dict[str, Any] = {"limit": min(max(limit, 1), 500)}
        if before_id is not None:
            conditions.append("co.CUSTOMER_ORDER_ID < :before_id")
            params["before_id"] = before_id
        if warehouse is not None:
            conditions.append("co.WARE_ID = :scope_warehouse")
            params["scope_warehouse"] = warehouse
        if status:
            conditions.append("upper(co.STATUS) = :status")
            params["status"] = status.upper()
        if order_no:
            conditions.append("upper(co.ORDER_NO) like :order_no")
            params["order_no"] = f"%{order_no.upper()}%"
        if legacy_order_id is not None:
            conditions.append("co.LEGACY_ORDER_ID = :legacy_order_id")
            params["legacy_order_id"] = legacy_order_id
        where_sql = " where " + " and ".join(conditions) if conditions else ""
        return self.gateway.fetch_all(
            f"""
                select co.CUSTOMER_ORDER_ID,
                       co.LEGACY_ORDER_ID,
                       co.ORDER_NO,
                       co.STATUS,
                       co.WARE_ID,
                       co.ORDER_DATE,
                       co.SHIPMENT_DATE,
                       c.CUSTOMER_ID,
                       c.CUSTOMER_NAME,
                       m.LEGACY_ADDR,
                       count(r.CUSTOMER_ORDER_ROW_ID) ROW_COUNT,
                       nvl(sum(r.ORDER_QTY), 0) TOTAL_ORDER_QTY,
                       to_char(nvl(sum(r.ORDER_QTY),0),'TM9','NLS_NUMERIC_CHARACTERS=''.,''') TOTAL_ORDER_QTY_EXACT,
                       count(distinct r.UNIT_CODE) ORDER_UOM_COUNT,
                       min(r.UNIT_CODE) ORDER_UOM,
                       count(case when r.UNIT_CODE is null then 1 end) UNKNOWN_UOM_ROWS,
                       nvl(sum(r.PACK_COUNT), 0) TOTAL_PACK_COUNT,
                       co.CREATED_AT
                  from (select co.* from RRL_CUSTOMER_ORDER co {where_sql}
                        order by co.CUSTOMER_ORDER_ID desc fetch first :limit rows only) co
                  join RRL_CUSTOMER c
                    on c.CUSTOMER_ID = co.CUSTOMER_ID
                  left join RRL_CUSTOMER_STORE_MAP m
                    on m.CUSTOMER_STORE_MAP_ID = co.CUSTOMER_STORE_MAP_ID
                  left join RRL_CUSTOMER_ORDER_ROW r
                    on r.CUSTOMER_ORDER_ID = co.CUSTOMER_ORDER_ID
                 group by co.CUSTOMER_ORDER_ID,
                          co.LEGACY_ORDER_ID,
                          co.ORDER_NO,
                          co.STATUS,
                          co.WARE_ID,
                          co.ORDER_DATE,
                          co.SHIPMENT_DATE,
                          c.CUSTOMER_ID,
                          c.CUSTOMER_NAME,
                          m.LEGACY_ADDR,
                          co.CREATED_AT
                 order by co.CUSTOMER_ORDER_ID desc
            """,
            params,
        )

    def detail_rows(self, customer_order_id: int) -> dict[str, Any] | None:
        rows = self.gateway.fetch_all(
            """
            select co.CUSTOMER_ORDER_ID,
                   co.LEGACY_ORDER_ID,
                   co.ORDER_NO,
                   co.STATUS,
                   co.WARE_ID,
                   co.ORDER_DATE,
                   co.SHIPMENT_DATE,
                   co.ROUTE_ID,
                   co.DOCK_ID,
                   c.CUSTOMER_ID,
                   c.CUSTOMER_NAME,
                   m.CUSTOMER_STORE_MAP_ID,
                   m.LEGACY_ADDR,
                   m.ADDRESS_TEXT,
                   co.CREATED_AT,
                   co.UPDATED_AT
              from RRL_CUSTOMER_ORDER co
              join RRL_CUSTOMER c
                on c.CUSTOMER_ID = co.CUSTOMER_ID
              left join RRL_CUSTOMER_STORE_MAP m
                on m.CUSTOMER_STORE_MAP_ID = co.CUSTOMER_STORE_MAP_ID
             where co.CUSTOMER_ORDER_ID = :customer_order_id
            """,
            {"customer_order_id": customer_order_id},
        )
        if not rows:
            return None
        order = rows[0]
        order["rows"] = self.gateway.fetch_all(
            """
            select CUSTOMER_ORDER_ROW_ID,
                   LEGACY_ORDER_ROW_ID,
                   LINE_NO,
                   ARTICUL,
                   PRODUCT_NAME,
                   UNIT_CODE,
                   ORDER_QTY,
                   to_char(ORDER_QTY,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') ORDER_QTY_EXACT,
                   ORDER_WEIGHT,
                   to_char(ORDER_WEIGHT,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') ORDER_WEIGHT_EXACT,
                   PACK_COUNT,
                   to_char(PACK_COUNT,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') PACK_COUNT_EXACT,
                   WARE_ID,
                   MOD_ID,
                   STATUS
              from RRL_CUSTOMER_ORDER_ROW
             where CUSTOMER_ORDER_ID = :customer_order_id
             order by LINE_NO, CUSTOMER_ORDER_ROW_ID fetch first 2001 rows only
            """,
            {"customer_order_id": customer_order_id},
        )
        if len(order["rows"]) > 2000:
            raise ValueError("ORDER_DETAIL_LINE_BOUND_2000")
        return order

