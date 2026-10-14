from pathlib import Path
import json
out={}
p=Path("api/wms_api_server/app/modules/finance/infrastructure/reconciliation_sources.py");s=p.read_text(encoding="utf-8")
needle=' ("warehouse_tasks_started",'
a=s.index(needle);e=s.index("\n",a)
s=s[:e+1]+' ("warehouse_tasks_finished","select count(*)from RRL_WAREHOUSE_TASK where(FROM_WARE_ID=:ware or TO_WARE_ID=:ware)and STATUS=\'DONE\'and FINISHED_AT_INSTANT>=:day_from and FINISHED_AT_INSTANT<:day_to"),\n'+s[e+1:]
out[str(p)]=s
p=Path("api/wms_api_server/app/modules/finance/infrastructure/reconciliation_task_times.py");s=p.read_text(encoding="utf-8")
s=s.replace("when FINISHED_AT is not null then","when FINISHED_AT is not null and FINISHED_AT_INSTANT is null then")
s=s.replace('            "finished_daily_count":None,\n','').replace('"finish_time_basis":"LEGACY_NAIVE_TIMESTAMP_UNCLASSIFIED"','"finish_time_basis":"NATIVE_DONE_TRANSACTION_INSTANT"')
out[str(p)]=s
p=Path("wiki-raw/wms_admin_ui_reference/day-reconciliation.js");s=p.read_text(encoding="utf-8")
s=s.replace('const labels={','const labels={warehouse_tasks_finished:"Завершено заданий с подтверждённым временем",',1)
s=s.replace('warehouse_tasks_started:"Начато складских заданий"','warehouse_tasks_started:"Начато заданий с подтверждённым временем"')
s=s.replace('". Дневное количество завершений пока не определено; прежние даты не пересчитываются предположительно.";','". Дневная сводка не включает записи без подтверждённого часового пояса.";')
out[str(p)]=s
for line in Path("tmp/source254.log").read_text(encoding="utf-16").splitlines():
 if line.startswith("SOURCE254_JSON:"):out["tmp/context254.json"]=line.partition(":")[2]+"\n"
assert "tmp/context254.json"in out
print(json.dumps(out,ensure_ascii=True))
