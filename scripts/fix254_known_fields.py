from pathlib import Path
import json
out={}
p=Path("api/wms_api_server/app/modules/finance/infrastructure/reconciliation_sources.py");s=p.read_text(encoding="utf-8")
s="\n".join(line for line in s.splitlines()if '"warehouse_tasks_finished"'not in line)+"\n";out[str(p)]=s
p=Path("api/wms_api_server/app/modules/finance/infrastructure/reconciliation_task_times.py");s=p.read_text(encoding="utf-8")
s=s.replace("FINISHED_AT is not null and FINISHED_AT_INSTANT is null","FINISHED_AT is not null")
s=s.replace('"legacy_wall_dates_reinterpreted":False,','"legacy_wall_dates_reinterpreted":False,\n            "finished_daily_count":None,\n            "finish_time_basis":"LEGACY_NAIVE_TIMESTAMP_UNCLASSIFIED",')
out[str(p)]=s
p=Path("wiki-raw/wms_admin_ui_reference/day-reconciliation.js");s=p.read_text(encoding="utf-8")
s=s.replace('warehouse_tasks_finished:"Завершено складских заданий",',"")
s=s.replace('"; окончаний: "','"; завершённых заданий с неподтверждённым часовым поясом: "')
s=s.replace('". Они не отнесены к выбранному дню предположительно.";','". Дневное количество завершений пока не определено; прежние даты не пересчитываются предположительно.";')
out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
