"""Same native source authority for current reads and shared-config-bound source writes."""
from contextlib import contextmanager
from typing import Any, Iterator
import oracledb


def assert_store_scope(cur: Any, actor: str, permission: str, warehouse: int) -> None:
    try:
        cur.callproc("RRL_STORE_ORDER_SCOPE.assert_scope", [actor, permission, warehouse])
    except oracledb.DatabaseError as exc:
        if getattr(exc.args[0], "code", 0) == 20882:
            raise PermissionError("STORE_ORDER_CURRENT_WARE_ACTOR_REQUIRED") from exc
        raise


def actor_warehouse(cur: Any, actor: str, permission: str) -> tuple[int | None, bool]:
    own = cur.var(oracledb.DB_TYPE_NUMBER)
    global_admin = cur.var(oracledb.DB_TYPE_NUMBER)
    try:
        cur.callproc("RRL_STORE_ORDER_SCOPE.actor_scope", [actor, permission, own, global_admin])
    except oracledb.DatabaseError as exc:
        if getattr(exc.args[0], "code", 0) == 20882:
            raise PermissionError("STORE_ORDER_CURRENT_WARE_ACTOR_REQUIRED") from exc
        raise
    return own.getvalue(), global_admin.getvalue() == 1


@contextmanager
def source_transaction(gateway: Any, label: str, actor: str, permission: str,
                       warehouse: int | None = None, order: int | None = None) -> Iterator[Any]:
    with gateway.transaction(label) as cur:
        if warehouse is None:
            cur.execute("select WARE_ID from RRL_CUSTOMER_ORDER where CUSTOMER_ORDER_ID=:order_id", order_id=order)
            row = cur.fetchone()
            if row is None:
                raise LookupError("SAP customer source order not found")
            warehouse = row[0]
        opened = False
        try:
            try:
                cur.callproc("RRL_STORE_ORDER_SCOPE.begin_source", [actor, permission, warehouse, order])
                opened = True
            except oracledb.DatabaseError as exc:
                if getattr(exc.args[0], "code", 0) == 20882:
                    raise PermissionError("STORE_ORDER_CURRENT_WARE_ACTOR_REQUIRED") from exc
                raise
            yield cur
        finally:
            if opened:
                cur.callproc("RRL_STORE_ORDER_SCOPE.end_source")
