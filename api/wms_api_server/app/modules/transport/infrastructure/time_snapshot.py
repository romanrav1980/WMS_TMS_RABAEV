"""Current original trip scope and bounded temporal rows, no transaction ownership."""
from typing import Any
from ..contracts_plan import TransportPlanError

def trip_scope(cur: Any, trip: int, actor: str) -> tuple[Any, ...]:
    from .preflight_scope import dispatcher
    dispatcher(cur, actor)
    cur.execute("""select ID,TRANSPORT,VODITEL_ID,CONDITION,USER_ID,DELETED
        from RRL_TRANSPORT_TASK where ID=:trip_id""", trip_id=trip)
    header = cur.fetchone()
    if header is None:
        raise TransportPlanError("PLAN_CURRENT_SOURCE_NOT_FOUND", "Рейс отсутствует", 404)
    cur.execute("select distinct WARE_ID from RRL_SBORKA_PALLETS where TRANSTASK_ID=:trip_id fetch first 201 rows only", trip_id=trip)
    warehouses = cur.fetchall()
    if len(warehouses) > 200:
        raise TransportPlanError("TIME_SOURCE_WARE_BOUND_200", "Превышена граница складов")
    if warehouses:
        import oracledb
        for (warehouse,) in warehouses:
            try:
                cur.callproc("RRL_TRANSPORT_PLAN_RULES.assert_actor", [actor, warehouse])
            except oracledb.DatabaseError as exc:
                code = getattr(exc.args[0], "code", 0)
                if code == 20882:
                    raise TransportPlanError("PLAN_CURRENT_WARE_ACTOR_REQUIRED", "Недоступный склад рейса", 403) from exc
                raise
    elif header[4] != actor:
        cur.execute("select count(*) from RUSERS where ID=:actor and upper(trim(USER_GROUP))='GLOBAL_ADMIN'", actor=actor)
        if cur.fetchone()[0] != 1:
            raise TransportPlanError("TIME_EMPTY_TRIP_OWNER_REQUIRED", "Недоступный пустой рейс", 403)
    return header

def original_operations(cur: Any, trip: int, zone: str) -> list[dict[str, Any]]:
    cur.execute("""select ID,OPERATION_CODE,ORD,
        to_char(from_tz(cast(PLAN_START as timestamp),:zone),'YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM'),
        to_char(from_tz(cast(PLAN_END as timestamp),:zone),'YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM'),
        to_char(from_tz(cast(FACT_START as timestamp),:zone),'YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM'),
        to_char(from_tz(cast(FACT_END as timestamp),:zone),'YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM')
        from RRL_TT_OPERATIONS where TT_ID=:trip_id order by ORD,ID fetch first 201 rows only""",
        zone=zone, trip_id=trip)
    records = cur.fetchall()
    if len(records) > 200:
        raise TransportPlanError("TIME_OPERATION_BOUND_200", "Превышена граница операций рейса")
    return [dict(zip(("operation_id","operation_code","ordinal","plan_start_at","plan_end_at",
                     "fact_start_at","fact_end_at"), record)) for record in records]

