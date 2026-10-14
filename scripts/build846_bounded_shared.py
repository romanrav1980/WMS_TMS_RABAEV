from pathlib import Path
import json
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/shared_arrival_reconciliation.py")
s=p.read_text(encoding="utf-8").replace('from fastapi import HTTPException','from fastapi import HTTPException\nimport json',1)
s=s.replace("def reconcile_arrived_sources(gateway: TransactionGateway, wave_id: int, actor: str) -> int:","def reconcile_arrived_sources(gateway: TransactionGateway, wave_id: int, actor: str, row_ids: list[int] | None = None) -> int:")
s=s.replace("             and pending.REPLENISHMENT_QTY_MODE='FULL_PALLET'","             and (:selection is null or pending.PICK_WAVE_REPLENISH_TASK_ID in\n                (select id from json_table(:selection,'$[*]'columns(id number path '$'))))\n             and pending.REPLENISHMENT_QTY_MODE='FULL_PALLET'",1)
s=s.replace('{"wave": wave_id, "actor": actor})','{"wave": wave_id, "actor": actor, "selection":json.dumps(row_ids)if row_ids is not None else None})',1)
s=s.replace("waves=gateway.fetch_all", "rows=gateway.fetch_all",1).replace("select distinct rt.PICK_WAVE_ID","select rt.PICK_WAVE_REPLENISH_TASK_ID,rt.PICK_WAVE_ID",1)
s=s.replace("        order by rt.PICK_WAVE_ID fetch first 201 rows only","         and rt.PICK_TASK_ID is not null and sr.SOURCE_DOC_TYPE='PICK_WAVE'\n         and sr.SOURCE_DOC_ID=rt.PICK_WAVE_ID and sr.SOURCE_LINE_ID=rt.PICK_TASK_ID\n         and sr.RESERVATION_KIND='HARD' and sr.RESERVATION_DOMAIN='PICKING'\n         and sr.STATUS in('ACTIVE','ALLOCATED','PICKING') and sr.BASE_QTY>0\n         and RRL_STOCK_REPL_NEED.remaining_for_task(rt.PICK_TASK_ID,rt.TARGET_CELL_CODE)=0\n         and not exists(select 1 from RRL_WAREHOUSE_TASK wh where wh.TASK_SOURCE='WAVE'\n          and wh.TASK_TYPE='REPLENISHMENT' and wh.SOURCE_TASK_ID=rt.PICK_WAVE_REPLENISH_TASK_ID)\n        order by rt.PICK_WAVE_REPLENISH_TASK_ID fetch first 201 rows only",1)
s=s.replace("    if len(waves)>200:", "    if len(rows)>200:",1).replace("SHARED_ARRIVAL_WAVE_BOUND_200","SHARED_ARRIVAL_ROW_BOUND_200",1)
s=s.replace('    return sum(reconcile_arrived_sources(gateway,int(row["pick_wave_id"]),actor) for row in waves)','''    grouped: dict[int,list[int]]={}
    for row in rows:
        grouped.setdefault(int(row["pick_wave_id"]),[]).append(int(row["pick_wave_replenish_task_id"]))
    return sum(reconcile_arrived_sources(gateway,wave,actor,ids) for wave,ids in grouped.items())''',1)
print(json.dumps({str(p):s},ensure_ascii=True))
