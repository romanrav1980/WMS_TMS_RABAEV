from pathlib import Path
import json
files={}
p="api/wms_api_server/app/services/customer_order_service.py"
t=Path(p).read_text(encoding="utf-8")
start=t.index("    def list_customer_orders(")
end=t.index("    def import_legacy_order(",start)
methods=t[start:end]
methods=methods.replace("def list_customer_orders(", "def list_rows(").replace("def get_customer_order(", "def detail_rows(")
methods=methods.replace("        limit: int = 200,\n", "        limit: int = 200,\n        warehouse: int | None = None,\n")
methods=methods.replace("        if status:\n", '        if warehouse is not None:\n            conditions.append("co.WARE_ID = :scope_warehouse")\n            params["scope_warehouse"] = warehouse\n        if status:\n',1)
methods=methods.replace("                   ORDER_QTY,\n                   ORDER_WEIGHT,\n                   PACK_COUNT,", """                   ORDER_QTY,
                   to_char(ORDER_QTY,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') ORDER_QTY_EXACT,
                   ORDER_WEIGHT,
                   to_char(ORDER_WEIGHT,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') ORDER_WEIGHT_EXACT,
                   PACK_COUNT,
                   to_char(PACK_COUNT,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') PACK_COUNT_EXACT,""")
methods=methods.replace("             order by LINE_NO, CUSTOMER_ORDER_ROW_ID\n", "             order by LINE_NO, CUSTOMER_ORDER_ROW_ID fetch first 2001 rows only\n")
methods=methods.replace('        return order\n', '        if len(order["rows"]) > 2000:\n            raise ValueError("ORDER_DETAIL_LINE_BOUND_2000")\n        return order\n')
header='''"""Original customer order reads with one current native warehouse scope."""
from typing import Any
from ....transaction_gateway import TransactionGateway
from .store_source_scope import actor_warehouse, assert_store_scope


class CustomerOrderRead:
    def __init__(self, gateway: Any) -> None:
        self.gateway = gateway

    def list(self, actor: str, status: str | None = None, order_no: str | None = None,
             legacy_order_id: int | None = None, limit: int = 200) -> list[dict[str, Any]]:
        with self.gateway.transaction("Customer order list scoped READ ONLY") as cur:
            if not getattr(self.gateway, "transaction_bound", False):
                cur.execute("set transaction read only")
            warehouse, global_admin = actor_warehouse(cur, actor, "customer_order_view")
            return CustomerOrderRead(TransactionGateway(cur)).list_rows(
                status, order_no, legacy_order_id, limit, None if global_admin else warehouse)

    def get(self, order_id: int, actor: str) -> dict[str, Any]:
        if order_id < 1:
            raise ValueError("Positive order ID required")
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

'''
files["api/wms_api_server/app/modules/fulfillment/infrastructure/customer_order_read.py"]=header+methods
wrappers='''    def list_customer_orders(
        self, status: str | None = None, order_no: str | None = None,
        legacy_order_id: int | None = None, limit: int = 200,
    ) -> list[dict[str, Any]]:
        # Trusted legacy in-process reader; HTTP uses actor-scoped public service.
        from ..modules.fulfillment.public import build_customer_order_read_service
        return build_customer_order_read_service(self.gateway).list_rows(status, order_no, legacy_order_id, limit)

    def get_customer_order(self, customer_order_id: int) -> dict[str, Any] | None:
        # Trusted legacy in-process reader; HTTP uses actor-scoped public service.
        from ..modules.fulfillment.public import build_customer_order_read_service
        return build_customer_order_read_service(self.gateway).detail_rows(customer_order_id)

'''
files[p]=t[:start]+wrappers+t[end:]
p="api/wms_api_server/app/modules/fulfillment/public.py"
t=Path(p).read_text(encoding="utf-8")
t+='''

from .infrastructure.customer_order_read import CustomerOrderRead


def build_customer_order_read_service(gateway: Any | None = None) -> CustomerOrderRead:
    return CustomerOrderRead(gateway if gateway is not None else OracleGateway())


__all__.append("build_customer_order_read_service")
'''
files[p]=t
p="api/wms_api_server/app/routers/customer_orders.py"
t=Path(p).read_text(encoding="utf-8")
t=t.replace("from ..services.customer_order_service import CustomerOrderService", "from ..services.customer_order_service import CustomerOrderService\nfrom ..modules.fulfillment.public import build_customer_order_read_service")
old='''    return CustomerOrderService().list_customer_orders(
        status=status,
        order_no=order_no,
        legacy_order_id=legacy_order_id,
        limit=limit,
    )'''
new='''    try:
        return build_customer_order_read_service().list(
            _user.username, status=status, order_no=order_no,
            legacy_order_id=legacy_order_id, limit=limit,
        )
    except PermissionError as exc:
        raise HTTPException(403, str(exc)) from exc'''
assert old in t;t=t.replace(old,new)
old='''    order = CustomerOrderService().get_customer_order(customer_order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Customer order not found.")
    return order'''
new='''    try:
        return build_customer_order_read_service().get(customer_order_id, _user.username)
    except PermissionError as exc:
        raise HTTPException(403, str(exc)) from exc
    except LookupError as exc:
        raise HTTPException(404, str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(409, str(exc)) from exc'''
assert old in t;t=t.replace(old,new)
files[p]=t
print(json.dumps(files,ensure_ascii=True))
