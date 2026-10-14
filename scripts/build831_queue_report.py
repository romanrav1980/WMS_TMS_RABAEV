from pathlib import Path
import json
files={}
report="""# Продолжение NI07.2: очередь и карточка задания

13 октября 2026. По последнему поручению работа продолжается до завершения всех спринтов либо 20:00 Москвы.

Карточка после обновления использует актуальную серверную запись. Старый статус ASSIGNED не сохраняется при приходе DONE; старый ответ прогресса отвергается. Подтверждённое назначение ресурса отличено от ошибки последующего перечитывания очереди. Поля сканирования и кнопки разнесены по рядам.

Добавлены постоянные ссылки на очереди. В реальном браузере открыто warehouse-tasks.html?preset=waiting: PUTAWAY/MANUAL/ST_DEFER, одна строка1080 DONE, 3 EA / факт3 EA. Это подтверждает загрузку фильтра по URL; клики прежних кнопок через CUA не подтверждены и не выдаются за готовую приёмку.

![Реальная очередь ожидания](screenshots/08-waiting-queue.png)

JS810/828 PASS: прежний выбор фильтра, актуальная карточка и старый progress. Quality gate:24passed, оба TypeScript и architecture686/0cycles/76debt PASS. Было предупреждение прав pytest cache; тесты прошли. UTF8 encoding PASS.

Текущий SQL списка15.701мс/95buffers. Решение: сохранить ограниченную выдачу/фильтры и существующую проекцию, дополнительный индекс не вводить. Вложенное ожидание/CASE/capacity и полный день остаются открыты. Новых движений, назначений ресурсов или внешних ACK этим блоком не создавалось.
"""
files["reports/retailcase/2026-10-13/05-current-task-report.md"]=report
p=Path("reports/retailcase/2026-10-13/index.html")
files[str(p)]=p.read_text(encoding="utf-8").replace("</main>","<article><h2>05 · Актуальная карточка и очередь ожидания</h2><p>Серверный статус, защита прогресса и постоянная ссылка на очередь.</p><p><a href=\"05-current-task-report.md\">Отчёт №5</a></p><img src=\"screenshots/08-waiting-queue.png\" alt=\"Реальная очередь ожидания, одно задание1080 DONE\"></article></main>")
p=Path("wiki/components/retailcase_warehouse_task_ui_20261013.md")
files[str(p)]=p.read_text(encoding="utf-8")+"""
## Постоянные ссылки830 и результат831

Presets стали обычными ссылками с параметром preset; старт страницы восстанавливает whitelist фильтра. Обработчик обновляет URL без перезагрузки, штатная ссылка также допускает новое окно/закладку. Реальный browser734 goto ?preset=waiting подтвердил PUTAWAY/MANUAL/ST_DEFER и одну строку1080 DONE/3EA. Это подтверждает навигацию по URL, не старый неподтверждённый CUA click.

JS810/828PASS; полный gate83124passed/bothTS/arch686-0-76PASS (pytest-cache rights warning); UTF8PASS. [Отчёт05](../../reports/retailcase/2026-10-13/05-current-task-report.md), screenshot08. Original protected stock/task1080 unchanged.
"""
p=Path("wiki/requirements/retailcase_delivery_v55/implementation_plan.json")
plan=json.loads(p.read_text(encoding="utf-8"))
next(x for x in plan["increments"] if x["id"]=="NI07.2")["implementedSlices"].append("831 current card refresh/status and progress scope, server dispatch result retained, responsive scan rows, URL-based queue preset restored; real browser waiting1/task1080 DONE3EA, JS828/gatePASS; nested/CASE/capacity/dayclose remain")
files[str(p)]=json.dumps(plan,ensure_ascii=False,indent=2)+"\n"
p=Path("wiki/requirements/retailcase_delivery_v55/execution/active/ni07_2.md")
files[str(p)]=p.read_text(encoding="utf-8")+"\n13.10.2026:831 current task UI/source bounded queue, fresh selected status and old-progress guard, responsive scan rows and bookmark preset; actual browser waiting1/task1080DONE3EA; gatePASS24/bothTS/encoding. No stock effects/full closure. [Report05](../../../../../reports/retailcase/2026-10-13/05-current-task-report.md).\n"
p=Path("wiki/index.md")
files[str(p)]="- [Checkpoint831: очередь ожидания по ссылке](components/retailcase_warehouse_task_ui_20261013.md): browser1/task1080 DONE3EA, report05/screenshot08, gatePASS; до20:00 MSK.\n"+p.read_text(encoding="utf-8")
p=Path("wiki/log.md")
files[str(p)]=p.read_text(encoding="utf-8")+"\n- 2026-10-13 checkpoint831: original queue URL presets restored, real browser734waiting1/task1080DONE3EA; current-card/progress guards JS828PASS, responsive execution rows829. Gate24/bothTS/architecturePASS and encodingPASS; pytest cache rights warning explicit. Report05/screenshot08; no native writes/fullclosure.\n"
print(json.dumps(files,ensure_ascii=True))
