"""Reuse the single legacy ST writer, serialized TT -> actual ST ID."""
import oracledb
from ....oracle_gateway import OracleGateway


def _lock_trip(cursor: oracledb.Cursor, task_id: int) -> None:
    cursor.execute("select CONDITION,PAY_ORDER_ID,DELETED from RRL_TRANSPORT_TASK where ID=:id for update", {"id":task_id})
    task=cursor.fetchone()
    if not task or task[2] or task[0]=="Отгружен":
        raise ValueError("Existing active unshipped trip is required")
    if task[1]:
        raise ValueError("Trip included in billing cannot change its STs")


def _lock_members(cursor: oracledb.Cursor, task_id: int, numbers: list[str], removing: bool) -> None:
    binds={"n"+str(i):number for i,number in enumerate(numbers)}
    cursor.execute("select ID,ST_NUMBER from RRL_SBORKA_PALLETS where ST_NUMBER in ("+
                   ",".join(":"+key for key in binds)+") order by ID fetch first 201 rows only",binds)
    members=cursor.fetchall()
    if len(members)>200 or {row[1] for row in members}!=set(numbers):
        raise ValueError("Select existing STs with at most 200 actual pallet rows")
    for member_id,number in members:
        cursor.execute("select TRANSTASK_ID,CONDITION from RRL_SBORKA_PALLETS where ID=:id for update",{"id":member_id})
        member=cursor.fetchone()
        if not member or member[1]==2:
            raise ValueError("ST already shipped or missing: "+number)
        if removing and member[0]!=task_id:
            raise ValueError("ST does not belong to this trip: "+number)
        if not removing and member[0] not in (None,0,task_id):
            raise ValueError("ST already belongs to another trip: "+number)


def _write_members(cursor: oracledb.Cursor, target: int, numbers: list[str]) -> None:
    for number in numbers:
        result=cursor.callfunc("RRL_TT_ADD_PALL",oracledb.DB_TYPE_VARCHAR,[target,number])
        if str(result or "").lower().startswith("err"):
            raise ValueError("Existing ST writer failed: "+str(result))


def assign_sts(gateway: OracleGateway, task_id: int, st_numbers: list[str], actor: str) -> dict:
    from .plan_application import assign_validated_sts
    return assign_validated_sts(gateway,task_id,st_numbers,actor)


def unassign_st(gateway: OracleGateway, task_id: int, st_number: str) -> None:
    with gateway.transaction("Existing transport ST removal") as cursor:
        _lock_trip(cursor,task_id)
        _lock_members(cursor,task_id,[st_number],True)
        _write_members(cursor,0,[st_number])
        cursor.callfunc("RRL_TT_REORDER_ADR",oracledb.DB_TYPE_NUMBER,[task_id])

def cancel_trip(gateway: OracleGateway, task_id: int, actor: str) -> None:
    with gateway.transaction("Existing transport trip cancellation") as cursor:
        _lock_trip(cursor,task_id)
        cursor.execute("select count(*) from RRL_TT_HU_LOAD_FACT where TT_ID=:id and STATUS in ('LOADED','DEPARTED')",{"id":task_id})
        if cursor.fetchone()[0]:
            raise ValueError("Confirmed physical unloading is required before cancellation")
        cursor.execute("select ID,ST_NUMBER,CONDITION from RRL_SBORKA_PALLETS where TRANSTASK_ID=:id order by ID fetch first 201 rows only",{"id":task_id})
        rows=cursor.fetchall()
        if len(rows)>200 or any(row[2]==2 for row in rows):
            raise ValueError("Cancellation requires at most 200 unshipped actual ST rows")
        numbers=sorted({row[1] for row in rows})
        if numbers:
            _lock_members(cursor,task_id,numbers,True)
            _write_members(cursor,0,numbers)
        cursor.execute("update RRL_TRANSPORT_TASK set DELETED=1,USER_ID=:actor where ID=:id",{"actor":actor,"id":task_id})
