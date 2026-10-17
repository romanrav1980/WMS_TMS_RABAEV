"""Require all warehouses of a financial object before returning any amount."""
from typing import Any
from ..contracts import LogisticsCostError
from .cost_access import require_warehouse


def authorize_cost_object(cursor: Any, kind: str, object_id: int, actor: str) -> None:
    if kind not in {"TRIP", "INVOICE"}:
        raise ValueError("Unknown financial scope")
    cursor.execute("""select RRL_HAS_WRIGHT(ID,'transport_dispatch_view')
        from RUSERS where ID=:actor and nvl(DELETED,0)=0""", actor=actor)
    user = cursor.fetchone()
    if user is None:
        raise LogisticsCostError("COST_ACTIVE_ACTOR_REQUIRED", "Нет доступа к финансовой детализации", 403)
    table = "RRL_TRANSPORT_TASK" if kind == "TRIP" else "RRL_BILL_ORDERS"
    cursor.execute("select count(*) from " + table + " where ID=:id", id=object_id)
    if cursor.fetchone()[0] != 1:
        raise LogisticsCostError("COST_OBJECT_NOT_FOUND", "Документ не найден", 404)
    clause = "t.ID=:id" if kind == "TRIP" else "t.PAY_ORDER_ID=:id"
    cursor.execute("""select WARE_ID from (
        select s.WARE_ID from RRL_SBORKA_PALLETS s join RRL_TRANSPORT_TASK t on t.ID=s.TRANSTASK_ID where """ + clause + """
        union select l.WARE_ID from RRL_TT_HU_LOAD_FACT l join RRL_TRANSPORT_TASK t on t.ID=l.TT_ID where """ + clause + """
        union select r.WARE_ID from RRL_LOGISTICS_COST_RUN r join RRL_TRANSPORT_TASK t on t.ID=r.TT_ID where """ + clause + ") fetch first 201 rows only", id=object_id)
    warehouses = cursor.fetchall()
    if len(warehouses) > 200:
        raise LogisticsCostError("COST_WAREHOUSE_BOUND", "Слишком много складов; используйте детализацию рейса")
    if not warehouses and user[0] != 1:
        raise LogisticsCostError("COST_EMPTY_OBJECT_LEGACY_VIEW_REQUIRED", "Для документа не определена область склада", 403)
    for (warehouse,) in warehouses:
        if warehouse is None:
            raise LogisticsCostError("COST_WAREHOUSE_FORBIDDEN", "Не определён склад документа", 403)
        require_warehouse(cursor, warehouse, actor, "transport_dispatch_view")
