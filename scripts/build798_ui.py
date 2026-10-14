from pathlib import Path
import json
files={}
p=Path("wiki-raw/wms_admin_ui_reference/warehouse-tasks.js");t=p.read_text(encoding="utf-8")
t=t.replace('function classifyTask(task) {','function classifyTask(task) {\n  if (task.task_type === "PUTAWAY" && task.source_doc_type === "ST_DEFER") return "Перемещение в ожидание рейса";')
t=t.replace('parts.push(task.source_doc_type);','parts.push(task.source_doc_type === "ST_DEFER" ? "Перенос СТ" : task.source_doc_type);')
files[str(p)]=t
p=Path("wiki-raw/wms_admin_ui_reference/st-trip-picker.js");t=p.read_text(encoding="utf-8").replace("\u2026","...")
t=t.replace("button.setAttribute('aria-label','Выбрать рейс '+trip.trip_id);","button.setAttribute('aria-label','Выбрать рейс '+trip.trip_id);button.title='Подставить рейс в форму переноса; сохранение выполняется отдельно';")
files[str(p)]=t
p=Path("wiki-raw/wms_admin_ui_reference/day-reconciliation.html");t=p.read_text(encoding="utf-8")
titles={'sdPickTrip':'Открыть существующие рейсы ТМС и выбрать получателя СТ','tpClose':'Закрыть окно без переноса СТ','tpFrom':'Начальная дата поиска допустимых рейсов','tpTo':'Конечная дата поиска; период до 31 календарного дня','tpDistrict':'Фильтр по району магазина в составе рейса','tpStore':'Точный код магазина; ведущие нули сохраняются','tpSearch':'Прочитать подходящие рейсы из существующей ТМС'}
for k,v in titles.items():t=t.replace('id="'+k+'"','id="'+k+'" title="'+v+'"')
files[str(p)]=t
p=Path("wiki/runbooks/retailcase_active_work.md");t=p.read_text(encoding="utf-8")
files[str(p)]="# Checkpoint798 — 13Oct2026\n\n- Trip picker791/792 delivered against existing TMS; API793 current46932/23180 before date-window fix797 (restart needed). HTTP794 PASS bounds/empty filters, real screenshot04/selection33564 no write. New report02/wiki component; positive district/store matches remain unproven due missing candidate mappings. SQL headers31-34ms/stopbatch11.5ms: retain bounded31calendar/100 and batching; plan/index SHIPMENT_DATE-ID backlog transport owner, V$SQL_PLAN unavailable.\n- UI797/798 validates exact pending ST command shape, blocks malformed, same-raw cross-tab success guard; TSD/task registry ST_DEFER labels accurate. Syntax/architecture797 PASS686/0/76; encoding795 false positive Cyrillic+ellipsis fixed798, rerun pending.\n- Earlier788 protected native/source cases unchanged; all18 incomplete, work through18:30 MSK or actual completion, no push yet.\n\n"+t
print(json.dumps(files,ensure_ascii=True))
