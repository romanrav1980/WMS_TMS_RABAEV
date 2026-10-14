# NI03.3: явная отмена пустого CASE

Ticket170, в реализации. Расширяется существующая CASE_CARRIER_RETURN allow_empty=true + reason, сохраняются scan_container/expected_content_version/immutable OP. Новый движок запасов/отмены не создаётся. Обычный request canonical JSON остаётся прежним: новые defaults исключены для physical return.

Допуск empty: исторический picked0/header и lines, нет carrier graph/parent nesting/shared or executed pick task/неотменённого физического отбора;1–200 исходных lines. Запас физически не перемещается. Неиспользованный собственный HARD снимается прежним native return core в той же транзакции. Менеджер отменяет исходные CASE/PT/waveTask, текущий scope165 сохраняется. Итог CANCELLED_EMPTY не называется возвратом физического товара.

Бронь исправной тары остаётся отдельной существующей TARE_BOOK_CANCEL. После empty cancel её можно освободить по прежнему статусу CANCELLED; завершение deferred wave блокируется до освобождения HELD. Это сохраняет прежний tare ledger/право tare_plan, не выдаёт отмену CASE за движение тары.

Миграция2026-10-10-170-case-empty-cancel: checkpoint affected live return/wave access, paired rollback/versioned SQL/no copy. Применение ещё не подтверждено.

Реализовано/API/ТСД/APPLIED: packages VALID, USER_ERRORS empty, ledgerAPPLIED. Actual1033: own inventory fixtureP1H1, native execute before commit → P1H0/CANCELLED, rollback вернулP1H1/ASSIGNED; concurrentHTTP one durable CANCELLED_EMPTY, replay/changed409/reason422. Root count удалил только собственную fixturequantity, исходный P20H20 не изменён. Physical quantity не переносилась, H released той же проводкой.

Actual1034: existingGOODtare count1/book → empty cancellation → wave399 returned-decision409 WAVE_DEFER_TARE_BOOK_REMAINS → original book-cancel → existing finish UNFULFILLED_RETURNED_TO_PLANNING. Tare native count0 после случая, источник заказа остаётся открытым. Первое обращение авторского скрипта ошибочно использовало /api/tare вместо /api/inventory/tare (404); исправлен URL, данные не менялись до исправления. Повтор сценариев проверяет сохранённые receipts; H1/HELD first-time proof не заявляется выполненным повторно.

Собственные slots RESERVED или mismatched OCCUPIED блокируют empty cancellation; отсутствие nativePT/waveTask и общий PT также блокируют. Физические picking tasks query ограничен текущей wave, а не всей таблицей. Active parent должен быть отдельно отсоединён. Последние дополнительные predicate guards compiled; новый positive placed/shared/marked topology не заявлен.

LongestSQL source CASE sibling/execution count3.946ms/7, physicalWT1.949ms/7, tareHELD2.428ms/4. Решение: wave predicate добавлен для physicalWT; сохранить case-first bounded200 и существующие PK/links. Owner inventory; load-level plan/index decision при большом количестве shared lines остаётся backlog, coldparse не capacity evidence. Full gate535files/0cycles/76debt/24tests/bothTS PASS, encodingPASS, JSsyntaxPASS. Qwen tasks170 записаны, модель не запускалась. Mixed fulfilled/deferred wave remains open, весь NI03.3 не закрыт.
