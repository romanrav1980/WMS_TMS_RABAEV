"""Authorize every actual warehouse before materializing physical trip contents."""
from typing import Any
from ..contracts import TransportLoadingError


def authorized_trip_header(cursor: Any, trip: int, actor: str) -> tuple:
    cursor.execute("""select WARE_ID,USER_GROUP,RRL_HAS_WRIGHT(ID,'transport_dispatch_view')
        from RUSERS where ID=:actor and nvl(DELETED,0)=0""", actor=actor)
    user = cursor.fetchone()
    if user is None:
        raise TransportLoadingError("LOADING_CURRENT_VIEW_ACTOR_REQUIRED", "Недоступен просмотр погрузки", status=403)
    cursor.execute("select ID,TRANSPORT,DOCK,CONDITION,VODITEL_ID,USER_ID from RRL_TRANSPORT_TASK where ID=:trip_id", trip_id=trip)
    header = cursor.fetchone()
    if header is None:
        raise TransportLoadingError("TRIP_NOT_FOUND", "Рейс не найден", status=404)
    cursor.execute("""select WARE_ID from (
        select WARE_ID from RRL_SBORKA_PALLETS where TRANSTASK_ID=:trip_id
        union select WARE_ID from RRL_TT_HU_LOAD_FACT where TT_ID=:trip_id)
        fetch first 201 rows only""", trip_id=trip)
    warehouses = cursor.fetchall()
    if len(warehouses) > 200:
        raise TransportLoadingError("TRIP_WAREHOUSE_BOUND_200", "Слишком много складов рейса")
    global_scope = str(user[1] or "").strip().upper() == "GLOBAL_ADMIN"
    if not warehouses and not global_scope and not (user[2] == 1 and header[5] == actor):
        raise TransportLoadingError("LOADING_EMPTY_TRIP_OWNER_REQUIRED", "Недоступный пустой рейс", status=403)
    for (warehouse,) in warehouses:
        cursor.execute("""select count(*),nvl(max(RRL_ACCESS_API.allowed(:actor,
            'transport_dispatch_view','WAREHOUSE',RRL_STOCK_PLAN_HELPER.decimal_text(ID))),0)
            from RRL_WARES where ID=:ware_id""", actor=actor, ware_id=warehouse)
        exists, scoped = cursor.fetchone()
        legacy = user[2] == 1 and user[0] == warehouse
        if exists != 1 or not (global_scope or legacy or scoped == 1):
            raise TransportLoadingError("LOADING_CURRENT_WARE_REQUIRED", "Недоступный склад рейса", status=403)
    return header
