import json
from pathlib import Path
out={}
p=Path("api/wms_api_server/app/modules/finance/infrastructure/reconciliation_sources.py");v=p.read_text(encoding="utf-8")
v=v.replace("DAILY=[","""DAILY=[
 ("store_unloads_started","select count(*)from RRL_STORE_UNLOAD_START s join RRL_TT_HU_LOAD_FACT l on l.LOAD_OPERATION_ID=s.LOAD_OPERATION_ID where l.WARE_ID=:ware and s.STARTED_AT_INSTANT>=:day_from and s.STARTED_AT_INSTANT<:day_to"),
 ("store_unloads_completed_by_start_day","select count(*)from RRL_STORE_UNLOAD_START s join RRL_TT_HU_LOAD_FACT l on l.LOAD_OPERATION_ID=s.LOAD_OPERATION_ID join RRL_STORE_UNLOAD_FACT f on f.START_OPERATION_ID=s.OPERATION_ID where l.WARE_ID=:ware and s.STARTED_AT_INSTANT>=:day_from and s.STARTED_AT_INSTANT<:day_to"),
""")
v=v.replace("BACKLOG=[","""BACKLOG=[
 ("store_unloads_open","select count(*)from RRL_STORE_UNLOAD_START s join RRL_TT_HU_LOAD_FACT l on l.LOAD_OPERATION_ID=s.LOAD_OPERATION_ID where l.WARE_ID=:ware and not exists(select 1 from RRL_STORE_UNLOAD_FACT f where f.START_OPERATION_ID=s.OPERATION_ID)"),
""")
out[str(p)]=v
print(json.dumps(out))
