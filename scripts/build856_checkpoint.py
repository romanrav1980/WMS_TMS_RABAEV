from pathlib import Path
import json
files={}
def read(p):return Path(p).read_text(encoding="utf-8")
p="wiki-raw/wms_admin_ui_reference/warehouse-tasks.js"
s=read(p).replace("  if(warehouseTaskState.initialTaskId){","  let openLinkedDetail=false;\n  if(warehouseTaskState.initialTaskId){",1)
s=s.replace("warehouseTaskState.initialTaskId=null;warehouseTaskState.selectedTask=linked;","warehouseTaskState.initialTaskId=null;warehouseTaskState.selectedTask=linked;\n    openLinkedDetail=window.location.hash==='#warehouseTaskDetail';",1)
s=s.replace("  renderWarehouseTaskDetail();\n}","  renderWarehouseTaskDetail();\n  if(openLinkedDetail)warehouseTaskEl('warehouseTaskDetail')?.scrollIntoView?.({block:'start',behavior:'auto'});\n}",1)
files[p]=s
p="wiki-raw/wms_admin_ui_reference/warehouse-tasks.css";files[p]=read(p)+"\n#warehouseTaskDetail {scroll-margin-top:90px;}\n"
p="wiki-raw/wms_admin_ui_reference/warehouse-tasks.html";files[p]=read(p).replace("20261013-832","20261013-856")
ctx=json.loads(read("tmp/context850.json"))
files["reports/retailcase/2026-10-13/08-partial-shared-report.json"]=json.dumps(ctx,ensure_ascii=False,indent=2)
report="""# NI03.2 — частично обеспеченный заказ общей паллеты

На dev RABAEV/orcl применена migration852. Вместимость считает общую целую паллету один раз, обычные количественные задания остаются отдельными. Inventory продолжает невыданное ожидание в статусах RELEASED и QUEUED: сохраняет уже прибывший резерв и направляет недостающую потребность через существующий выбор источника.

Фактический свежий случай: задания1096 и1097 выполнены на20 и12 EA. Сохранены резервы заказов12 и8 EA, отдельной волны14 EA. Вместимость0.1 отказала без изменения остатков; вместимость0.5 разрешила движение. Повтор каждой физической команды вернул сохранённый результат. Все собственные остатки и активные резервы затем очищены штатными командами, история сохранена.

Второе физическое задание принадлежит более раннему заказу общей паллеты; продолжение первого заказа не должно получать дубликат. При подготовке второго источника свободный товар в отборе дополнительно уменьшил недостающее количество второго заказа с4 до2 EA. Проверяется итоговый резерв8, а не выдуманная неизменность промежуточной потребности.

Это адресное исполнение разработчика, не независимая приёмка полного спринта. Маркированный и weighted-capacity варианты, независимая конкуренция остаются открыты.
"""
files["reports/retailcase/2026-10-13/08-partial-shared-report.md"]=report
p="reports/retailcase/2026-10-13/index.html";files[p]=read(p).replace("</main>",'<article><h2>08 · Частичный заказ общей паллеты</h2><p>Две подачи20+12 EA; резервы12,8,14 сохранены.</p><a href="08-partial-shared-report.md">Отчёт №8</a> · <a href="08-partial-shared-report.json">Факты JSON</a></article></main>')
p="wiki/database/retailcase_ni032_shared_capacity_20261013.md";files[p]=read(p)+"\n## Применение и результат856\n\n852 применена, native compile ERRORS[]/INVALID[]. Свежий850 после исправления QUEUED helper: tasks1096/1097 DONE20/12, owner12/other8/third14, exact replay и own P/H cleanup. Второй canonical task принадлежит rt1603, исходный continuation rt1604 использует ту же физическую подачу. Свободное целевое количество уменьшает intermediate remaining другого заказа4→2; общий резерв8 сохранён. Это developer evidence, weighted branch/независимая маркированная конкуренция открыты.\n"
p="wiki/components/retailcase_ni032_shared_arrival_20261013.md";files[p]=read(p)+"\n## Partial shared856\n\nHelper849 теперь обрабатывает RELEASED и QUEUED, только неизданный physical task с исходным own HARD уже в target. Zero remaining снимается без fake DONE, positive remaining возвращается в прежний selector с очищенной stale source binding. Фактический850: shared20+12, owner12/8/14, replay/owncleanup. Sum200 warehouse selection выполнен live; независимый reviewer/marked race ещё не выполнялись.\n"
p="wiki/requirements/retailcase_delivery_v55/implementation_plan.json";plan=json.loads(read(p));inc=next(x for x in plan["increments"]if x["id"]=="NI03.2")
inc["implementedSlices"].append("849-856 partial shared RELEASED/QUEUED source requeue; native852 one physical incoming capacity; actual1096/1097 DONE20/12 owners12/8/14 exact replay owncleanup; developer evidence only")
files[p]=json.dumps(plan,ensure_ascii=False,indent=2)
p="wiki/index.md";files[p]="- [Checkpoint856: частичная общая подача](database/retailcase_ni032_shared_capacity_20261013.md): native852 VALID; actual1096/1097 DONE20/12, резервы12/8/14, replay/owncleanup; отчёт08.\n"+read(p)
p="wiki/log.md";files[p]=read(p)+"\n- 2026-10-13 checkpoint856: native852 applied VALID; partial shared helper RELEASED/QUEUED, actual850 task1096/1097 DONE20/12 owner12/8/14/replay/owncleanup. Fixed fixture to inspect canonical physical UID, not force original continuation as task owner. Report08; UI linked-card scroll after server load. NI03.2 not fully closed.\n"
print(json.dumps(files,ensure_ascii=True))
