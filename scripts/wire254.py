from pathlib import Path
import json
out={}
p=Path("api/wms_api_server/app/modules/finance/infrastructure/day_reconciliation.py");s=p.read_text(encoding="utf-8")
needle="from .reconciliation_regulatory import regulatory_snapshot"
assert s.count(needle)==1;s=s.replace(needle,needle+"\nfrom .reconciliation_task_times import task_time_coverage")
needle="            blockers=["
assert s.count(needle)==1;s=s.replace(needle,"            task_times=task_time_coverage(cur,ware)\n"+needle)
assert s.count('"regulatory":regulatory,')==1;s=s.replace('"regulatory":regulatory,','"regulatory":regulatory,"warehouse_task_time_coverage":task_times,')
out[str(p)]=s
p=Path("wiki-raw/wms_admin_ui_reference/day-reconciliation.html");s=p.read_text(encoding="utf-8")
assert s.count('<div id="drFacts"></div>')==1
out[str(p)]=s.replace('<div id="drFacts"></div>','<div id="drFacts"></div><p id="drTaskTimes"></p>')
p=Path("wiki-raw/wms_admin_ui_reference/day-reconciliation.js");s=p.read_text(encoding="utf-8")
s=s.replace('const labels={','const labels={warehouse_tasks_started:"Начато складских заданий",warehouse_tasks_finished:"Завершено складских заданий",',1)
s=s.replace('["drFacts","drBacklog","drStock","drErp","drRegulatory"]','["drFacts","drBacklog","drStock","drErp","drRegulatory","drTaskTimes"]')
needle='el("drBacklog").replaceChildren'
assert s.count(needle)==1
s=s.replace(needle,'el("drTaskTimes").textContent="Дневные показатели используют подтверждённое время заданий. Старых начал без часового пояса: "+d.warehouse_task_time_coverage.legacy_unclassified_start_count+"; окончаний: "+d.warehouse_task_time_coverage.legacy_unclassified_finish_count+". Они не отнесены к выбранному дню предположительно.";'+needle)
out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
