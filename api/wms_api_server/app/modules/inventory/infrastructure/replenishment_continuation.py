"""Resume durable generic wave demand through existing source reservation and task sync."""
from typing import Any, Callable
from fastapi import HTTPException
from ....transaction_gateway import TransactionGateway
from .shared_arrival_reconciliation import reconcile_warehouse_arrivals


class ReplenishmentContinuation:
    def __init__(self, gateway: Any, sync_tasks: Callable[[Any, int, str], None]) -> None:
        self.gateway, self.sync_tasks = gateway, sync_tasks

    def reconcile(self, warehouse: int, actor: str) -> dict[str, Any]:
        with self.gateway.transaction("Resume existing replenishment remainder") as cursor:
            entered = False
            try:
                cursor.execute("begin RRL_STOCK_METADATA_TX.begin_change(:actor,'pick_wave_launch');end;", {"actor": actor})
                entered = True
                reconcile_warehouse_arrivals(TransactionGateway(cursor),warehouse,actor)
                cursor.execute("""select rt.PICK_WAVE_REPLENISH_TASK_ID,rt.PICK_WAVE_ID,rt.STATUS,rt.RESERVE_OPERATION_ID
                    from RRL_PICK_WAVE_REPLENISH_TASK rt join RRL_PICK_WAVE w on w.PICK_WAVE_ID=rt.PICK_WAVE_ID
                    where w.WARE_ID=:ware and w.STATUS='LAUNCHED' and (rt.PARENT_REPLENISH_TASK_ID is not null or rt.PICK_TASK_ID is not null)
                      and rt.SOURCE_RESERVATION_ID is null and rt.STATUS in('RELEASED','QUEUED','WAIT_FREE_CELL','FAILED')
                      and not exists(select 1 from RRL_WAREHOUSE_TASK wh where wh.TASK_SOURCE='WAVE'
                        and wh.SOURCE_DOC_ID=rt.PICK_WAVE_ID and wh.SOURCE_TASK_ID=rt.PICK_WAVE_REPLENISH_TASK_ID
                        and wh.TASK_TYPE='REPLENISHMENT' and wh.STATUS not in('DONE','CANCELLED'))
                      and ((rt.PICK_TASK_ID is not null and RRL_STOCK_REPL_NEED.remaining_for_task(rt.PICK_TASK_ID,rt.TARGET_CELL_CODE)=0)
                       or exists(select 1 from RRL_REMAINS tr join RRL_PALLETS tp on tp.UID_PALLET=tr.UID_POLETA
                         where tr.CELL=rt.TARGET_CELL_CODE and tp.ARTICUL=rt.ARTICUL and rt.PICK_TASK_ID is not null
                           and tr.REMAIN-tr.HARD_RESERVED_BASE>=RRL_STOCK_REPL_NEED.remaining_for_task(rt.PICK_TASK_ID,rt.TARGET_CELL_CODE)
                           and tr.REMAIN>tr.HARD_RESERVED_BASE
                           and RRL_STOCK_ELIGIBILITY.reason(tr.UID_POLETA,tr.CELL,w.WARE_ID,0,
                             rt.MIN_SHELF_LIFE_DAYS,rt.MIN_SHELF_LIFE_PERCENT,'ALLOCATE',null,rt.ARTICUL) is null)
                       or exists(select 1 from RRL_STOCK_RESERVATION sr join RRL_REMAINS r
                         on r.UID_POLETA=sr.UID_PALLET and r.CELL=sr.CELL
                         where sr.SOURCE_DOC_TYPE='PICK_WAVE' and sr.SOURCE_DOC_ID=rt.PICK_WAVE_ID
                           and sr.SOURCE_LINE_ID=rt.PICK_TASK_ID and sr.RESERVATION_DOMAIN='PICKING'
                           and sr.RESERVATION_KIND='HARD' and sr.STATUS in('ACTIVE','ALLOCATED','PICKING') and sr.BASE_QTY>0
                           and sr.CELL!=rt.TARGET_CELL_CODE
                           and RRL_STOCK_ELIGIBILITY.reason(sr.UID_PALLET,sr.CELL,w.WARE_ID,0,
                             rt.MIN_SHELF_LIFE_DAYS,rt.MIN_SHELF_LIFE_PERCENT,'REPLENISH',sr.RESERVATION_ID,rt.ARTICUL) is null
                           and (RRL_STOCK_REPL_CAPACITY.remaining_base_quantity(rt.TARGET_CELL_CODE,rt.ARTICUL,rt.PICK_WAVE_REPLENISH_TASK_ID) is null
                             or RRL_STOCK_REPL_CAPACITY.remaining_base_quantity(rt.TARGET_CELL_CODE,rt.ARTICUL,rt.PICK_WAVE_REPLENISH_TASK_ID)>0)
                           and (RRL_STOCK_REPL_ADMISSION.mode_for(rt.PICK_WAVE_REPLENISH_TASK_ID)!='FULL_PALLET'
                             or (RRL_STOCK_REPL_SHARED.allowed(sr.UID_PALLET,sr.CELL,rt.TARGET_CELL_CODE,w.WARE_ID,sr.RESERVATION_ID)=1
                               and (RRL_STOCK_REPL_CAPACITY.remaining_base_quantity(rt.TARGET_CELL_CODE,rt.ARTICUL,rt.PICK_WAVE_REPLENISH_TASK_ID) is null
                                 or r.REMAIN<=RRL_STOCK_REPL_CAPACITY.remaining_base_quantity(rt.TARGET_CELL_CODE,rt.ARTICUL,rt.PICK_WAVE_REPLENISH_TASK_ID)))))
                       or exists(select 1 from RRL_REMAINS r join RRL_PALLETS p on p.UID_PALLET=r.UID_POLETA
                        join RRL_CELLS c on c.CELL=r.CELL where p.ARTICUL=rt.ARTICUL and c.WARE_ID=w.WARE_ID
                         and r.CELL!=rt.TARGET_CELL_CODE and r.REMAIN>r.HARD_RESERVED_BASE
                         and RRL_STOCK_ELIGIBILITY.reason(r.UID_POLETA,r.CELL,w.WARE_ID,0,
                           rt.MIN_SHELF_LIFE_DAYS,rt.MIN_SHELF_LIFE_PERCENT,'REPLENISH',null,rt.ARTICUL) is null
                         and RRL_STOCK_REPL_ADMISSION.reason(r.UID_POLETA,rt.TARGET_CELL_CODE,w.WARE_ID,rt.ARTICUL) is null
                         and (RRL_STOCK_REPL_CAPACITY.remaining_base_quantity(rt.TARGET_CELL_CODE,rt.ARTICUL,rt.PICK_WAVE_REPLENISH_TASK_ID) is null
                           or RRL_STOCK_REPL_CAPACITY.remaining_base_quantity(rt.TARGET_CELL_CODE,rt.ARTICUL,rt.PICK_WAVE_REPLENISH_TASK_ID)>0)
                         and (RRL_STOCK_REPL_ADMISSION.mode_for(rt.PICK_WAVE_REPLENISH_TASK_ID)!='FULL_PALLET'
                           or (r.HARD_RESERVED_BASE=0 and (RRL_STOCK_REPL_CAPACITY.remaining_base_quantity(rt.TARGET_CELL_CODE,rt.ARTICUL,rt.PICK_WAVE_REPLENISH_TASK_ID) is null
                            or r.REMAIN<=RRL_STOCK_REPL_CAPACITY.remaining_base_quantity(rt.TARGET_CELL_CODE,rt.ARTICUL,rt.PICK_WAVE_REPLENISH_TASK_ID))))))
                    order by rt.PICK_WAVE_REPLENISH_TASK_ID fetch first 201 rows only""", {"ware": warehouse})
                rows = cursor.fetchall()
                if len(rows) > 200:
                    raise HTTPException(409, detail="REPLENISHMENT_CONTINUATION_BOUND_200")
                pending = [(int(row_id),int(wave_id)) for row_id,wave_id,_status,_operation in rows]
            finally:
                if entered:
                    cursor.execute("begin RRL_STOCK_METADATA_TX.end_change;end;")
        from .wave_commands import reserve_wave_sources
        grouped = {}
        for row_id,wave_id in pending:
            grouped.setdefault(wave_id,[]).append(row_id)
        from .alternative_pick_faces import AlternativePickFaces
        for wave_id,row_ids in grouped.items():
            AlternativePickFaces(self.gateway).route_wave(wave_id,actor)
            reserve_wave_sources(self.gateway,wave_id,actor,row_ids)
        waves=set(grouped)
        for wave_id in sorted(waves):
            self.sync_tasks(self.gateway, wave_id, actor)
        return {"warehouse": warehouse, "processed": len(pending), "wave_ids": sorted(waves)}
