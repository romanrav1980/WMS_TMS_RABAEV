from pathlib import Path
import json
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/shared_arrival_reconciliation.py")
s=p.read_text(encoding="utf-8")
marker='    return gateway.execute("""'
s=s.replace(marker,'    cancelled=gateway.execute("""',1)
end='        """, {"wave": wave_id, "actor": actor, "selection":json.dumps(row_ids)if row_ids is not None else None})'
assert end in s
s=s.replace(end,end+'\n    return cancelled+requeue_partial_sources(gateway,wave_id,actor,row_ids)',1)
s=s.replace("         and RRL_STOCK_REPL_NEED.remaining_for_task(rt.PICK_TASK_ID,rt.TARGET_CELL_CODE)=0\n","",1)
s+='''
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
         where pending.PICK_WAVE_ID=:wave and pending.STATUS='RELEASED'
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
'''
# For the selected warehouse path total200 includes cancelled+requeued disjoint rows.
files={str(p):s}
p=Path("scripts/check847_shared_bound.py")
s=p.read_text(encoding="utf-8")
s=s.replace('self.calls.append((sql,binds));return len(json.loads(binds["selection"]))','self.calls.append((sql,binds));return 0 if "SOURCE_RESERVATION_ID=null" in sql else len(json.loads(binds["selection"]))')
s=s.replace('==[[1,2],[3]]','==[[1,2],[1,2],[3],[3]]')
files[str(p)]=s
print(json.dumps(files,ensure_ascii=True))
