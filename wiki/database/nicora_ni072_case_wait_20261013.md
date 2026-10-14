# NI07.2 — подготовленный CASE в ожидание, 953–954

PREPARED, live apply ещё не выполнен. RABAEV/orcl. Migration2026-10-13-004-ni072-case-waiting.

Добавляется nullable CASE_TASK_ID к существующему append-only RRL_ST_DEFER_WAIT_PLAN. Старые FULLPAL-планы сохраняются. Для первой поддержанной ветви: один ST-member, один связанный завершённый CASE и один PICKED fulfillment; до200 физических партий, каждая полностью зарезервирована тем же заказом. Количества разных артикулов/единиц не суммируются: само задание1CASE, партии хранят собственные quantity/base. NestedCASE, ресурсный сеанс, опубликованные slots и ограничения высоты/массы требуют отдельного плана и отказа.

RRL_ST_DEFER_PHYSICAL сначала обнаруживает физический CASE, включая случай без скалярного FACT_QTY, и формирует PREPARED_CASE. Переназначение ST использует прежний RRL_TRANSPORT_PLAN_API; только подготовленный source snapshot допускает CASE. Существующий plan_waiting регистрирует PUTAWAY/MANUAL/ST_DEFER_CASE и immutable origin в прежних WAIT_RUN/WAIT_PLAN.

Task completion bridge выбирает существующую CASE_CARRIER_MOVE по зарегистрированному CASE_TASK_ID. В metadata сохраняются physical_task_id, исходный content_version из плана, сканы исходника/приёмника/CASE и quantity1. Root проверяет текущий warehouse_task_execute/scope/assignee до cached replay и после получения locks. CASE_CARRIER_MOVE декларирует WHT/WAIT_PLAN/RUN/decision/ST/FF/trip/config/sync resources вместе с прежними lot/reservation/units locks, перечитывает frozen source до перемещения. Обычная storage-ячейка разрешается только typed waiting task.

Все партии перемещает прежний TRANSFER_CORE в одной Root транзакции: сохраняет UID/количество/HARD/состав маркировки. CASE CURRENT_CELL/content_version, fulfillment picked version, WHT DONE/FACT1 и SYNCED меняются в этой же транзакции; обязательный Root outbox остаётся прежним. Исходные pick events/facts не переписываются, старый QC допуск по старой версии требует повторного контроля.

Capture948/949 + SHA manifest/checkpoint + paired rollback, без копииБД. Rollback отказывается при зарегистрированных CASE планах; не испытан. Сначала compile/current native scenario, затем actual own-fixture flow и slow SQL решение. ПолныйNI07.2 не объявляется завершённым.

953 apply/current USER_ERRORS[]/INVALID[]. Actual955 stopped beforewave; retained956/959 reused same source through existing reconcile + tare count/book, CASE1129/1130 picked12+8, ST originaldeferral succeeded. WAIT registration rejected40573 before stock move;961 extracts JSON SQL scalar values. Current stageDEFERRED, own P12H12 + P8H8 intact; nofactoryrerun. Finish proof pending.

Actual964: тот же source955/CASE1129/task1110, positive native movement rollback leaves PLANNED/originalCELL/version; public bridge commit+exact replay → DONE1CASE/SYNCED/currentcellWAIT/version2/P12H12/старые pickfacts неизменны. Result outbox5096. Последний assertion harness обращался к ошибочно названной RRL_STOCK_OUTBOX, отказ00942 послеcommit; не полныйPASS. Проверяется существующая RRL_EVENT_OUTBOX.965 добавляет к прежнему WHT stock-move журналу по одной строке на фактическую партию/base и отказывает partial unit_keys; исходный Root товарный журнал уже сохранён. Второй retainedCASE1130qty8 позволит доказать текущую функцию безfactory/source rebirth.

## Checkpoint972 — фактический результат

# NI07.2 — перенос готового CASE в ожидание

953–971 применены в RABAEV/orcl. Поддержанная ветвь: один подготовленный CASE, один memberСТ, один PICKED fulfillment; до200 фактических партий. Задание учитывает1CASE, товарный журнал — количество каждой партии в её базовой единице. Переназначение рейса и подготовка задания используют прежние TMS/WAIT_API, проведение — прежнюю CASE_CARRIER_MOVE и TRANSFER_CORE. Нового механизма изменения запаса нет.

Root проверяет текущий склад, права и исполнителя до повторного ответа и после блокировок. Фиксированный состав источника, версия CASE, решение переноса, будущий рейс, настройка waiting-cell и задание перепроверяются до проведения. В одной транзакции перемещаются партии/HARD/состав маркировки, обновляются CASE cell/version и fulfillment version, завершаются WHT/SYNC и записывается обязательный outbox. Старые факты отбора сохранены.

Actual964/967: retained955 CASE1129/task1110 перемещён с12EA/H12, FACT1CASE/DONE/SYNCED/version2/outbox5096; положительный rollback возвращал PLANNED и исходное расположение, затем public bridge commit/replay. Этот первый случай проведён до добавления подробного WHT-lot journal965: Root журнал сохранён, WHT stock-move rows0; backfill не выполнялся.

Actual966/967: тот же исходный источник, второй CASE1130/task1111 с8EA/H8 → waiting-cell, FACT1CASE/DONE/SYNCED/version2/outbox5097. Товарный WHT журнал8EA; partial unit selection отказ, exact replay сохранён, изменённое содержимое того же OP409, пользователь другого склада403 до cache. ProtectedWARE6667491 P20/H20 неизменён. Источники955/966 не пересоздавались и сейчас сохранены в ожидании для продолжения, не очищены.

HTTP971 послеrestart970: queue_group=DEFER_WAITING возвращает3 задания (flat1080 + CASE1110/1111), прежний точный source_doc_type=ST_DEFER не расширен; complete возвращает прежний result в штатной оболочке status=ok. Raw UI ожидания поддерживает обе ветви, CASE и одна единица товара различаются в карточке. Реальный screenshot18 показывает DONE/1CASE/маршрут; это визуальное подтверждение просмотра, не независимая операторская приёмка.

Неуспешные этапы отражены:955 пропущена подготовка CASE/сверка очереди;956 tare booking required;959 SQL JSON40573;962 sync_key shadowing01422;964/966 последние asserts harness неправильно называли outbox таблицу/SQL константу;971 первый assert не учитывал штатную оболочку. Исправлены код и phase-continuation, финальные967/971 прошли. Старый955 factory не запускать.

Quality968:24 checks/both TS/architecture692,0cycles,76debt PASS; warning толькоpytest cache permissions. Encoding PASS. Current USER_ERRORS[]/INVALID[]. Rollback сохранён/отказывает при существующихCASE планах, не испытан; копияБД не создавалась.

SQL967 actualcarrier queries0.29–3.957ms,1.7–49.6buffers; решение inventory owner: сохранить200-lot bound/существующие carrier+UID ключи, дополнительный индекс не нужен. Семейная очередь bounded150/500; более крупная производственная нагрузка не заявляется.

ПолныйNI07.2 открыт: несколько мест однойСТ, nestedHU/CASE, slots/capacity/resource sessions, полный контроль дня. Маркированные партии проходят существующий transfer closure, но отдельный маркированный CASE-waiting сценарий не выполнен. Следующий функциональный пробел: связанный CASE после движения в контроль должен сохранять актуальную fulfillment version для последующей отгрузки.
