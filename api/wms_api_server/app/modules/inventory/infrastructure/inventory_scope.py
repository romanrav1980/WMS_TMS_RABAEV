"""Current actor scope for inventory reads and commands, including saved-result replay."""
from typing import Any
import oracledb
from ..contracts_observations import InventoryObservationError

def assert_inventory_cursor_scope(cursor: Any,actor: str,*,revision: int|None=None,warehouse: int|None=None,task: int|None=None,cell: str|None=None,article: str|None=None) -> None:
    try:
        cursor.callproc("RRL_INVENTORY_TASK_ACCESS.assert_read", [actor, revision, warehouse, task, cell, article])
    except oracledb.DatabaseError as exc:
        code = exc.args[0].code
        status = 403 if code == 20882 else 404 if code in (1403, 20884) else 503
        raise InventoryObservationError("INVENTORY_CURRENT_SCOPE_REQUIRED" if status < 500 else "INVENTORY_SCOPE_UNAVAILABLE",status) from exc


def assert_inventory_scope(gateway: Any,actor: str,*,revision: int|None=None,warehouse: int|None=None,task: int|None=None) -> None:
    with gateway.transaction("Current native inventory scope") as cursor:
        cursor.execute("set transaction read only")
        assert_inventory_cursor_scope(cursor,actor,revision=revision,warehouse=warehouse,task=task)
