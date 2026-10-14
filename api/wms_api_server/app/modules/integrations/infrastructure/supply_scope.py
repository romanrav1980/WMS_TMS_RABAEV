"""Current native SAP supply import authority and shared configuration fence."""
from contextlib import contextmanager
from typing import Any,Iterator
import oracledb

@contextmanager
def supply_transaction(gateway: Any,actor: str,warehouse: int,sender: str,order: str,message: str) -> Iterator[Any]:
    with gateway.transaction("Current scoped SAP supply source import")as cur:
        opened=False
        try:
            try:
                cur.callproc("RRL_STORE_ORDER_SCOPE.begin_supply",[actor,warehouse,sender,order,message])
                opened=True
            except oracledb.DatabaseError as exc:
                if getattr(exc.args[0],"code",0)==20882:
                    raise PermissionError("SAP_SUPPLY_CURRENT_WARE_ACTOR_REQUIRED")from exc
                raise
            yield cur
        finally:
            if opened:cur.callproc("RRL_STORE_ORDER_SCOPE.end_source")

def assert_supply_scope(cur: Any,actor: str,warehouse: int) -> None:
    try:cur.callproc("RRL_STORE_ORDER_SCOPE.assert_scope",[actor,"sap_supply_import",warehouse])
    except oracledb.DatabaseError as exc:
        if getattr(exc.args[0],"code",0)==20882:raise PermissionError("SAP_SUPPLY_CURRENT_WARE_ACTOR_REQUIRED")from exc
        raise
