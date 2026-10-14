from pathlib import Path
import json
read=lambda p:Path(p).read_text(encoding="utf-8");files={}
page="""# NI04.1 — согласованное исполнение CASE внутри HU

В существующую матрёшку подключена привязка CASE к исполнению заказа. Упаковка, распаковка и перемещение целого HU теперь согласованно обновляют версии CASE и активного исполнения заказа внутри одной транзакции существующего ядра. Новый механизм изменения остатка не создавался.

Миграция 2026-10-13-008-ni041-hu-case-binding (993) применена в RABAEV/orcl. USER_ERRORS пуст, изменённые пакеты VALID. Перед изменением сохранены текущие определения 990/992, SHA и парный rollback. Rollback не запускался. Исторические SHIPPED/CANCELLED исполнения не повышаются; положительный сценарий исторического CASE отдельно не выполнен.

## Фактически выполнено

Источник987 с двумя CASE: 1131 — 12 EA, 1132 — 8 EA, одна СТ/склад, действующие собственные резервы. Исходник не пересоздавался. После штатной упаковки в HU994:4bb85f1f15 CASE/исполнение имеют версии4/4. Первый запрос без подтверждения сохранённого бронирования тары корректно отклонён; новый исправленный запрос содержит исходные идентификаторы бронирования.

Существующее задание1138 переместило целый HU из QW4bb85f1f15 в QH4bb85f1f15: DONE, факт1HU, журнал партий12+8EA, CASE/исполнение5/5 обоих. Положительная проводка с rollback восстановила исходное состояние; штатная команда и её точный повтор сохранили один результат.

Распаковка996 выделила CASE1131: версия CASE6 и исполнения6, связь удалена, исходное бронирование тары осталось HELD. Текущий HU версии4 содержит CASE1132 с8EA/HARD8; отдельный CASE1131 содержит12EA/HARD12. Суммарно остаток20 и резерв20. Историческое задание1138 перемещало20EA; текущий состав после распаковки отличается.

## Интерфейс

997–998: режим HU · одно место, ссылка «Текущий состав HU» из задания, автоматическая загрузка выбранного места по URL после входа. Планирование HU открывает конкретное созданное задание. Обновлена адаптивная форма состава/упаковки/перемещения; создание пустого места и операции со слотами свёрнуты, существующие поля/команды/права сохранены.

Скриншоты19: DONE1138;20: текущий состав;21: обновлённый рабочий экран. Адресная навигация и автоматическая загрузка реально показаны. Автоматизированное нажатие ссылки19 не вызвало наблюдаемой навигации; затем открыт точный URL ссылки, поэтому ручное нажатие не объявляется подтверждённым.

## Ограничения и SQL

Полный NI04.1 остаётся открыт: смешанные/маркированные составы, ресурсные и физические ограничения, оборудование и независимая приёмка требуют оставшихся работ. Подтверждённая масса этих двух CASE отсутствует, пригодность ограниченного слота не заявлена. Широкие прогоны и копия БД не выполнялись.

CASE996 сохранил результаты V$SQL, совпадающего запроса не получено. Решение владельца inventory: сохранить существующие ключи CASE/FF/ST и ограниченное дерево; измерить конкретный HU binding source_snapshot при следующем значимом HU-сценарии, индекс без плана и измерения не добавлять. Это не нагрузочная приёмка.

Источники: tmp/context994.json, tmp/context996.json и SQL миграции; копии результатов в19-hu-binding-evidence.json.
"""
files["reports/nicora/2026-10-13/19-hu-binding-report.md"]=page
a=json.loads(read("tmp/context994.json"));b=json.loads(read("tmp/context996.json"))
files["reports/nicora/2026-10-13/19-hu-binding-evidence.json"]=json.dumps({"move":a,"detach":b,"independent_acceptance":False},indent=2)
p="db/migrations/2026-10-13_ni041_hu_case_binding/checkpoint.json";v=json.loads(read(p));v.update(state="APPLIED_DEV_VALID",evidence="994/995 attach+existingWHT1138 DONE1HU/20EA/CTFF5/rollback/replay;996 detachCTFF6/H20/P20/tareHELD");files[p]=json.dumps(v,indent=2)
p="wiki/database/nicora_ni041_hu_case_binding_20261013.md";files[p]=read(p)+"\n## Checkpoint999 — применено\n\n"+page
p="wiki/index.md";files[p]="- [Checkpoint999: HU и исполнение CASE](database/nicora_ni041_hu_case_binding_20261013.md):993VALID/1138DONE1HU/20EA/996detach8+12/H20; новый UI/report19/screenshots19–21.\n"+read(p)
p="wiki/log.md";files[p]=read(p)+"\n- 2026-10-13 checkpoint999:993APPLIEDVALID originalHU binder/oneactiveFFversion owner; actual9952CASE attach/WHT1138DONE1HU20EA/CTFF5/rollback/replay,996detachCTFF6/tareHELD/currentHU8+standalone12/P20H20. UI997998 scoped forms/deeplink/current-vs-history explanation, browserautoactual/screens19–21/report19; plan41/fullNI04.1 open.\n"
p="wiki/requirements/nikora_delivery_v55/implementation_plan.json";v=json.loads(read(p));v["planRevision"]=41
next(x for x in v["increments"]if x["id"]=="NI04.1")["implementedSlices"].append("993–999 existingHU activeCASE/FFversion sameTX; actual1138DONE1HU20EA/CTFF5/996detachCTFF6/currentHU8+CASE12/H20/P20; currentcompositiondeeplink/updatedUI/screens19–21/report19. Fullmixedmarkedslot/equipment/independent open")
files[p]=json.dumps(v,ensure_ascii=False,indent=2)
p="wiki/requirements/nikora_delivery_v55/implementation_plan.md";files[p]=read(p).replace("**Revision 40,","**Revision 41,")+"\nCheckpoint999: HU binding993 реализован/VALID. Actual1138 переместил20EA в1HU,996 выделил12EA/версия6. UI состава/упаковки997998 и screenshots19–21, отчёт19. ПолныйNI04.1 открыт.\n"
p="wiki/requirements/nikora_delivery_v55/execution/active/ni04_1.md";files[p]=read(p)+"\n13.10.2026,993–999: действующие CASE/fulfillment версии согласованы при HU attach/detach/move. Actual2CASE12+8/1138DONE1HU/20EA/P20H20/rollback/replay/detach12CTFF6; текущий состав HU8+отдельныйCASE12. Интерфейс автоматически открывает текущий состав места из задания. [Отчёт19](../../../../../reports/nicora/2026-10-13/19-hu-binding-report.md). Полный статусin_progress сохранён.\n"
p="reports/nicora/2026-10-13/index.html";files[p]=read(p).replace("</main>",'<article><h2>19 · HU, CASE и исполнение заказа</h2><a href="19-hu-binding-report.md">Отчёт №19</a><p>Целое HU:20EA; после распаковки8+12, резерв сохранён.</p><a href="screenshots/19-hu-task-completed.png">Задание1138</a> · <a href="screenshots/21-hu-workspace.png">Новый экран HU</a></article></main>')
p="wiki/runbooks/nicora_active_work.md";files[p]=read(p)+"\n## Checkpoint999,15:35UTC=18:35MSK — до дедлайна17UTC остаётся85минут\n993HU binding APPLIEDVALID/currentnativeErrors[]Invalid[]. Actual995 retained987twoCASE1131/1132 attach originalTAREbook/CTFF4; existingWHT1138DONE1HU20EA/CTFF5 both/Rootrollback/cache.996detachedCASE1131CTFF6/bookHELD/currentRootversion4 containsCASE1132qty8/H8;1131standalone12/H12; totalP20H20. ctx994/996 authoritative; neverrerunfactories/movement differentOP. UI997998 HUmode/currentcompositionURL/authautoload/nativehandlers retained/scopedCSS/compactdetails; screenshots19/20/21actual, linkclick itself notproved but exactURLloaded. Report19/plan41/currentNI03.3. Full18notcomplete; noGithubtrigger. CurrentbrowsercaseTarget821857740 HU?identifier=HU994...&v=998;reportFs available/noreset. SQL996empty ->boundedexistingkeys/ownerinventory nextquery measurement.\n"
qroot=list(Path(".").glob("*/NI01.1"))[0].parent
files[str(qroot/"NI04.1"/"19-HU-CASE-binding.md")]="""# Qwen: HU и активное исполнение CASE
Не пересоздавать источники987/994 и не запускать фабрики. Прочитать отчёт19 и миграцию993. Только чтением сверить текущий HU8/H8 и самостоятельный CASE1131 12/H12 вQH4bb85f1f15, CASE/FF версии6/6 и5/5. Сверить исторический WHT1138 DONE1HU и партии12+8EA; это не текущие20EA внутри HU после распаковки.
Независимый изменяющий сценарий выполняйте на собственном новом источнике: attach/move/detach/replay; активная привязка версии меняется один раз в общей транзакции, положительный rollback не меняет P/H/CASE/FF/outbox. Отдельно проверить исторический SHIPPED CASE без изменения истории, смену состава перед выполнением, отказ прав и чужой склад. Ошибки/непроверенное явно отделять от PASS. Зафиксировать медленные SQL и решение. Не использовать старые DONE как повод повторно родить товар.
"""
print(json.dumps(files,ensure_ascii=True))
