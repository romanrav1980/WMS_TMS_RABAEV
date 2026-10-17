# Прекращение неизвестного START разгрузки

Статус dev APPLIED,7 exact source SHA/ERROR0/INVALID0. Migration `2026-10-16-unloading-intent`, frozen SHA `3c0cbb7a102e462950e86275b848f780699d3758ec60e10d4c3c64f8fda56f67`.

Actual HTTP6 PASS: ABANDONED/replay/changed conflict/late START blocked/foreign403/RECORDED с прежним фактом. Caller rollback не оставляет control history; второй connection получает ORA54 на exclusive REV; direct INSERT запрещён; два concurrent control для одного original дают ровно ABANDONED+ALREADY_RESOLVED. Тесты используют новую законченную поставку CASE1147: это проверка неизвестного START и сохранённого старта; гонка двух ещё не принятых original/control на новой незавершённой поставке остаётся отдельной проверкой. Native не объявлен проверенным на аппаратуре.

В UI добавлена durable control команда: после её подготовки исходный повтор отключён; потерянный control ответ повторяется неизменно. Удаление исходной локальной записи разрешено только после RECORDED/ABANDONED и сохранения архива квитанции. Повреждённая запись не сбрасывается. Браузерная проверка390px PASS: lost response/reload/exact retry, блокировка исходного повтора, архив до очистки и сохранение повреждённого журнала; `delivery-time/ui/report.json`, fixtures без native writes.

Отдельная реальная гонка двух connections на ещё не принятой новой погрузке CASE1148: original START против abandon. START победил; control вернул RECORDED того же факта, оба повтора сохранили одну квитанцию. Затем магазин принял25EA без повторного списания; `route-subtree/ordinary-flow/store-race.json`. Это закрывает ранее открытый original/control race, аппаратная приёмка не заявляется.

`RRL_STORE_UNLOAD_API.abandon_start` принимает отдельный control operation_id и точное исходное тело START. Текущий приёмщик проверяется по исходной погрузке/магазину. Используются те же OP, load и STORE.RECEIPT.LOAD fences, что у START; добавлена shared REV защита от гонки отзыва. Native owner не проводит товар или стоимость.

Если START уже записан, ответ RECORDED содержит исходную квитанцию; факт не отменяется. Если исходного факта нет, immutable `RRL_STORE_UNLOAD_INTENT` сохраняет ABANDONED. Поздний исходный запрос после этого отклоняется; удаление локального журнала не является механизмом прекращения. Изменение тела прежнего control operation_id отклоняется. Триггер разрешает INSERT только из native owner и запрещает UPDATE/DELETE.

API POST `/api/delivery/store-receipts/unloading/abandon-start`: `{operation_id,original:{...исходный START...},reason}`. Повреждённый исходный журнал без доказанного тела не сбрасывается. Для новых команд нужен подтверждённый ответ сервера, а не тайм-аут.

SQL `db/migrations/2026-10-16_unloading_intent`; rollback только без control history, затем forward repair. Before6 sources, включая зависимый guard trigger; после применения сверяются exact sources, ограничения, INVALID/ERROR и ledger. Результаты — `reports/retailcase/2026-10-16/unloading-intent/`.

См. [[retailcase_resource_metadata_intents_20261015]], [[../roadmap/retailcase_finish_two_claude_20261016]].
