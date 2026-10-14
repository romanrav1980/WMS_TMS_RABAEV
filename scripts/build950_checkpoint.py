from pathlib import Path
import json
read=lambda p:Path(p).read_text(encoding="utf-8")
page="""# NI01.1 — история приёмки и восстановление команды

935–947: добавлен GET supply-orders/{id}/receipt-history. Текущий пользователь/склад и исходный заказ проверяются в одной READ ONLY транзакции; страницы до100, курсор принадлежит заказу. Исторически принятое количество отдельно от текущего остатка и HARD на этом складе, ссылка на исходное задание. Запись запаса не производится.

Повреждённое локальное намерение блокирует новую приёмку. Восстановление перечитывает историю выбранного источника, сохраняет точный исходный текст и контекст в архив до удаления повреждённой записи. Изменение другой вкладки, ошибка квоты и смена пользователя сохраняют исходник. Корректная команда повторяется с прежним operation_id. Ответ OPERATION_CONFLICT не считается успешным проведением. Выбор товарной строки использует текущие ключи заказа/строки/артикула и делегированные события, поддерживает Enter/Space.

Actual936: original908 исторически3, сейчас P0/H0, источникREVERSED; чужой курсор910 и отсутствующий пользователь отказали, protected688 не изменён. HTTP941 послеrestart939: тот же результат, limit101→422, неизвестный курсор→409. JS940 повреждённый intent/archive, JS947 текущий выбор/stale scope PASS. Это авторские проверки, не независимая приёмка.

Реальные screenshots16/17 показывают REVERSED и историю3/current0/task1105 CANCELLED. Браузерный выбор строки автоматизацией не изменил состояние: ручной результат пока не подтверждён, вопрос пользователю открыт; PASS не заявляется. Screenshot fullPage завершился таймаутом и не сохранён.

SQL941:20.856ms/145buffers (3exec), child25.43ms/36buffers (1exec). Решение integration owner: bounded100/keyset/существующие ключи order+line, без нового индекса на остатки; промышленная нагрузка не доказана. Architecture692/0cycles/76 PASS. Все18 спринтов не закрыты; следующая функция — CASE-ожидание через существующее ядро.
"""
files={"wiki/components/nicora_receiving_history_20261013.md":page,"reports/nicora/2026-10-13/15-receiving-history-report.md":page}
files["reports/nicora/2026-10-13/15-receiving-history-evidence.json"]=json.dumps({k:json.loads(read(p))for k,p in (("native936","tmp/history936.json"),("http_sql941","tmp/history941.json"))},indent=2)
p="wiki/index.md";files[p]="- [Checkpoint950: история приёмки](components/nicora_receiving_history_20261013.md):935–947 current scope/keyset/history/damaged intent; report15/screenshots16–17, ручной выбор не подтверждён.\n"+read(p)
p="wiki/log.md";files[p]=read(p)+"\n- 2026-10-13 checkpoint950: receipt-history935/HTTP941 readonly/currentWARE/keyset100; damaged intent938 archive-before-remove/current history, delegated selection946/947. Native936/JS940947 PASS; browser screenshot17 actual history, manualselection pending. SQL20.856ms145buf retainbounds. Report15, no stock migration/publication.\n"
p="reports/nicora/2026-10-13/index.html";files[p]=read(p).replace("</main>",'<article><h2>15 · История приёмки</h2><a href="15-receiving-history-report.md">Отчёт №15</a><p>Исходная приёмка и текущий остаток, восстановление команды.</p><img src="screenshots/17-receiving-history.png" alt="История приёмки" style="max-width:100%"></article></main>')
p="wiki/runbooks/nicora_active_work.md";files[p]=read(p)+"\n## Checkpoint950,16:45MSK\n935–947 functional receipt history/damaged recovery/delegated selectors; report15/screenshots16–17. Actual936/941/JS940947 PASS, manualbrowserselection pending/question user. CurrentAPI939 includes935. Currenttab821857737 receivingTarget/receivingTab, reportFs bound; old734 unavailable. CurrentCASE waiting task: captures948physical/HU and949deferAPI/waitAPI/caseMove/root/taskAccess. NO CASE native edits yet. Read current949 before code; prefer existing CASE_CARRIER_MOVE for typed WHT, no second stockwriter. Deadline17:00UTC, continuefunctionality.\n"
p="wiki/requirements/nikora_delivery_v55/implementation_plan.json";v=json.loads(read(p));next(x for x in v["increments"]if x["id"]=="NI01.1")["implementedSlices"].append("935–950 scoped readonly receipt history100/keyset/current own-WARE P-H vs historical receipt, damaged archive/current history, keyed delegated selection; actual936/941/JS940947; manual browser pending")
files[p]=json.dumps(v,ensure_ascii=False,indent=2)
print(json.dumps(files,ensure_ascii=True))
