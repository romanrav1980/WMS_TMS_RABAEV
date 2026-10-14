"""Retire unissued whole-pallet placeholders already covered by an original shared arrival."""
from ....transaction_gateway import TransactionGateway
from fastapi import HTTPException
import json


def reconcile_arrived_sources(gateway: TransactionGateway, wave_id: int, actor: str, row_ids: list[int] | None = None) -> int:
    # The caller owns the existing metadata CONFIG6 fence and commit. No stock write.
    cancelled=gateway.execute("""
        update RRL_PICK_WAVE_REPLENISH_TASK rt
           set STATUS='CANCELLED',DEMAND_BASE_QTY=0,
               WAIT_REASON='Own target coverage delivered with shared whole-pallet arrival; no additional physical task',
               UPDATED_AT=sysdate,UPDATED_BY=:actor
         where rt.PICK_WAVE_REPLENISH_TASK_ID in (
          select pending.PICK_WAVE_REPLENISH_TASK_ID
            from RRL_PICK_WAVE_REPLENISH_TASK pending
            join RRL_STOCK_RESERVATION sr on sr.RESERVATION_ID=pending.SOURCE_RESERVATION_ID
           where pending.PICK_WAVE_ID=:wave and pending.STATUS in('RELEASED','QUEUED')
             and (:selection is null or pending.PICK_WAVE_REPLENISH_TASK_ID in
                (select id from json_table(:selection,'$[*]'columns(id number path '$'))))
             and pending.REPLENISHMENT_QTY_MODE='FULL_PALLET' and pending.PICK_TASK_ID is not null
             and sr.SOURCE_DOC_TYPE='PICK_WAVE' and sr.SOURCE_DOC_ID=pending.PICK_WAVE_ID
             and sr.SOURCE_LINE_ID=pending.PICK_TASK_ID and sr.RESERVATION_DOMAIN='PICKING'
             and sr.RESERVATION_KIND='HARD' and sr.STATUS in('ACTIVE','ALLOCATED','PICKING')
             and sr.BASE_QTY>0 and sr.UID_PALLET=pending.PALLET_UID and sr.ARTICUL=pending.ARTICUL
             and sr.CELL=pending.TARGET_CELL_CODE and pending.SOURCE_CELL_CODE!=pending.TARGET_CELL_CODE
             and RRL_STOCK_REPL_NEED.remaining_for_task(pending.PICK_TASK_ID,pending.TARGET_CELL_CODE)=0
             and not exists(select 1 from RRL_WAREHOUSE_TASK wh where wh.TASK_SOURCE='WAVE'
                and wh.TASK_TYPE='REPLENISHMENT' and wh.SOURCE_DOC_ID=pending.PICK_WAVE_ID
                and wh.SOURCE_TASK_ID=pending.PICK_WAVE_REPLENISH_TASK_ID)
           order by pending.PICK_WAVE_REPLENISH_TASK_ID fetch first 200 rows only)
        """, {"wave": wave_id, "actor": actor, "selection":json.dumps(row_ids)if row_ids is not None else None})
    return cancelled+requeue_partial_sources(gateway,wave_id,actor,row_ids)


def reconcile_warehouse_arrivals(gateway: TransactionGateway, warehouse: int, actor: str) -> int:
    scope=gateway.fetch_all("""select count(*)ALLOWED from RUSERS u where u.ID=:actor
        and nvl(u.DELETED,0)=0 and(u.WARE_ID=:ware or upper(trim(u.USER_GROUP))='GLOBAL_ADMIN')""",
        {"actor":actor,"ware":warehouse})
    if not scope or scope[0]["allowed"]!=1:
        raise HTTPException(403,detail="REPLENISHMENT_CURRENT_WAREHOUSE_REQUIRED")
    rows=gateway.fetch_all("""select rt.PICK_WAVE_REPLENISH_TASK_ID,rt.PICK_WAVE_ID from RRL_PICK_WAVE_REPLENISH_TASK rt
        join RRL_PICK_WAVE w on w.PICK_WAVE_ID=rt.PICK_WAVE_ID
        join RRL_STOCK_RESERVATION sr on sr.RESERVATION_ID=rt.SOURCE_RESERVATION_ID
        where w.WARE_ID=:ware and w.STATUS='LAUNCHED' and rt.STATUS in('RELEASED','QUEUED')
         and rt.REPLENISHMENT_QTY_MODE='FULL_PALLET' and sr.CELL=rt.TARGET_CELL_CODE
         and rt.SOURCE_CELL_CODE!=rt.TARGET_CELL_CODE and sr.UID_PALLET=rt.PALLET_UID
         and rt.PICK_TASK_ID is not null and sr.SOURCE_DOC_TYPE='PICK_WAVE'
         and sr.SOURCE_DOC_ID=rt.PICK_WAVE_ID and sr.SOURCE_LINE_ID=rt.PICK_TASK_ID
         and sr.RESERVATION_KIND='HARD' and sr.RESERVATION_DOMAIN='PICKING'
         and sr.STATUS in('ACTIVE','ALLOCATED','PICKING') and sr.BASE_QTY>0
         and not exists(select 1 from RRL_WAREHOUSE_TASK wh where wh.TASK_SOURCE='WAVE'
          and wh.TASK_TYPE='REPLENISHMENT' and wh.SOURCE_TASK_ID=rt.PICK_WAVE_REPLENISH_TASK_ID)
        order by rt.PICK_WAVE_REPLENISH_TASK_ID fetch first 201 rows only""", {"ware":warehouse})
    if len(rows)>200:
        raise HTTPException(409,detail="SHARED_ARRIVAL_ROW_BOUND_200")
    grouped: dict[int,list[int]]={}
    for row in rows:
        grouped.setdefault(int(row["pick_wave_id"]),[]).append(int(row["pick_wave_replenish_task_id"]))
    return sum(reconcile_arrived_sources(gateway,wave,actor,ids) for wave,ids in grouped.items())

def requeue_partial_sources(gateway: TransactionGateway, wave_id: int, actor: str, row_ids: list[int] | None = None) -> int:
    # Original immutable source command/history still identifies the arrived reserve.
    # A confirmed APPLIED source intent is rotated by the existing intent writer.
    return gateway.execute("""
        update RRL_PICK_WAVE_REPLENISH_TASK rt set
         QTY=RRL_STOCK_REPL_NEED.remaining_for_task(rt.PICK_TASK_ID,rt.TARGET_CELL_CODE),
         DEMAND_BASE_QTY=RRL_STOCK_REPL_NEED.remaining_for_task(rt.PICK_TASK_ID,rt.TARGET_CELL_CODE),
         SOURCE_RESERVATION_ID=null,PALLET_UID=null,SOURCE_CELL_CODE=null,
         SOURCE_AVAILABLE_QTY=null,SOURCE_PRODUCED_DATE=null,SOURCE_EXPIRY_DATE=null,
         WAIT_REASON='Shared whole-pallet arrival confirmed; remaining own demand queued through original source selection',
         UPDATED_AT=sysdate,UPDATED_BY=:actor
        where rt.PICK_WAVE_REPLENISH_TASK_ID in(
         select pending.PICK_WAVE_REPLENISH_TASK_ID from RRL_PICK_WAVE_REPLENISH_TASK pending
         join RRL_STOCK_RESERVATION sr on sr.RESERVATION_ID=pending.SOURCE_RESERVATION_ID
         where pending.PICK_WAVE_ID=:wave and pending.STATUS in('RELEASED','QUEUED')
          and pending.REPLENISHMENT_QTY_MODE='FULL_PALLET' and pending.PICK_TASK_ID is not null
          and (:selection is null or pending.PICK_WAVE_REPLENISH_TASK_ID in
           (select id from json_table(:selection,'$[*]'columns(id number path '$'))))
          and sr.SOURCE_DOC_TYPE='PICK_WAVE' and sr.SOURCE_DOC_ID=pending.PICK_WAVE_ID
          and sr.SOURCE_LINE_ID=pending.PICK_TASK_ID and sr.RESERVATION_DOMAIN='PICKING'
          and sr.RESERVATION_KIND='HARD' and sr.STATUS in('ACTIVE','ALLOCATED','PICKING')
          and sr.BASE_QTY>0 and sr.UID_PALLET=pending.PALLET_UID and sr.ARTICUL=pending.ARTICUL
          and sr.CELL=pending.TARGET_CELL_CODE and pending.SOURCE_CELL_CODE!=pending.TARGET_CELL_CODE
          and RRL_STOCK_REPL_NEED.remaining_for_task(pending.PICK_TASK_ID,pending.TARGET_CELL_CODE)>0
          and not exists(select 1 from RRL_WAREHOUSE_TASK wh where wh.TASK_SOURCE='WAVE'
           and wh.TASK_TYPE='REPLENISHMENT' and wh.SOURCE_TASK_ID=pending.PICK_WAVE_REPLENISH_TASK_ID)
         order by pending.PICK_WAVE_REPLENISH_TASK_ID fetch first 200 rows only)
        """, {"wave":wave_id,"actor":actor,"selection":json.dumps(row_ids)if row_ids is not None else None})
