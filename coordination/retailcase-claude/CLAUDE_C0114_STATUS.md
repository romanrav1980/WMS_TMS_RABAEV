# Claude — статус C0114 (независимый review текущего store app)

Обновляет только Claude (сессия C0114, инструменты Read/Edit/Write/Glob/Grep; Bash/сеть/Oracle/git недоступны).

**Статус:** ACK + RESULT/RELEASE до 18:30 МСК.
**Роль:** независимый ревьюер АКТУАЛЬНОГО кода `terminal/wms_terminal_web/src/features/delivery/` (приложение приёмки магазина), не переписываю поток и не меняю бизнес-политику стратегий BARCODE/WEIGHT_PHOTO/PAPER_COUNT.

## Метод

Прочитал `wiki/runbooks/retailcase_store_receiving_app.md`, затем весь актуальный код по явному списку из промпта и связанные компоненты: `StoreReceivingApp.tsx`, `useStoreNavigation.ts`, `useStoreReceivingFlow.ts`, `receiptDraft.ts`, `receiptIntentValidation.ts`, `receiptFlowActions.ts`, `api.ts`, `scaleRequests.ts`, `useStoreWeighing.ts`, `ScaleConnection.tsx`, `WeightEvidencePanel.tsx`, `DeliveryDetail.tsx`, `ReceiptRecovery.tsx`, `UnloadingStep.tsx`, `DeliveryScanner.tsx`, `DeliveriesList.tsx`, `StoreSelector.tsx`, `ReceiptVerification.tsx`, `MarkedGoodsPanel.tsx`. Для спорного пункта про `outcome_confirmed` на статусах <500 прочитал (только Read, не редактировал) backend `api/wms_api_server/app/modules/delivery/api/store_receipt_routes.py` и `contracts.py`, чтобы не гадать, какие статусы реально достижимы.

## Проверено и подтверждено верным (без изменений)

- **Навигация/journal (приоритет 1).** `useStoreNavigation` — реальный `location.hash`, Back браузера работает нативно (`hash` пишется в историю). `DeliveryDetail` монтируется с `key={route.storeId + ":" + route.load}` в `StoreReceivingApp.tsx` — смена магазина/поставки всегда даёт полный remount, старый `useStoreReceivingFlow`/intent предыдущего места не может просочиться в новый контекст.
- `receiptDraft.ts`/`receiptIntentValidation.ts`: черновик привязан к `storeAppApiBase():username:storeId:loadOperationId`; `parseReceiptIntent` строго проверяет форму (operation_id/pattern, store_address точное совпадение, signature-формат, границы байт UTF-8 для `paper_reference`/`case_note`, вложенные `scans`/`observations`/`unloading`). Повреждённая запись → `corrupt=true`, отправка блокируется (`send()` проверяет `corrupt` и результат `draftMatchesSaved`), автоотправка при монтировании не происходит (`open()` только читает черновик).
- `runSend`/`runCheckStatus`/`runRestart` (`receiptFlowActions.ts`): точный повтор того же `intent.body` (operation_id не создаётся заново); квитанция `NOT_VISIBLE` явно НЕ считается подтверждённым отказом/отменой (текст: «это не подтверждение отмены»); `restart()` только после `pending.confirmedRejection`, перечитывает состав и либо возвращает старый ввод для сверки (если состав/режим/маркировка изменились — без автопереноса), либо снимает только подтверждённую командy.
- `api.ts`: `confirmed` вычисляется только если тело — объект, `detail.outcome_confirmed===true` И `detail.operation_id`/`request_id` совпадает с ПОЛЕМ ИЗ ОТПРАВЛЕННОГО тела. Для чистых GET (`body===undefined`) `requestBody` всегда `undefined`, поэтому `confirmed` физически не может стать `true` на GET-404 — специально проверил этот путь, т.к. это ровно класс ошибки из C0113. Для POST-путей (`/store-receipts/confirm`, `/unloading/start`) проверил backend (`store_receipt_routes.py`, `contracts.py`): `StoreReceiptError` статусы — только 422/403/409(default); ни один реальный путь сейчас не бросает 404 с этим телом, так что совпадение по id+`outcome_confirmed` на 404 сегодня НЕ достижимо текущим backend. Не придумываю здесь дефект, которого не нахожу в реальном коде.
- `useStoreWeighing.ts`/`scaleRequests.ts`: ключ черновика включает `composition_signature` — смена состава обязательно даёt новый scope и сброс `capture`/`pending`. `confirmedCapture()` жёстко сверяет `capture_key`/`device_id`/`capture_id`/`load_operation_id`/`store_address` с запросом. `newMeasurement()` запрещён, пока факт не `EXPIRED/CAPTURED/STALE` (нельзя начать новое измерение, пока прежнее не разрешилось). Нигде нет поля для ручного ввода массы. `connectivity` всегда типизирован как `"UNKNOWN"` — не изобретает «подключено».
- `UnloadingStep.tsx`: тот же паттерн persist-before-POST, `archiveDamaged()` переносит повреждённую запись в архив с отдельным ключом вместо тихого удаления, `recover()` только перечитывает фактическое состояние (`onStarted()`), не создаёт новую команду сама.
- Компактность 360/390 (приоритет 3): дата поставки — короткая строка + значок ⓘ с `title` (не банер); текущий магазин/поставка всегда в заголовке (`store_address`, `root_scan_identifier`); явные кнопки «← Поставки» / «Магазин» / «Выйти» на каждом экране.
- Сканер/камера (приоритет 2): `DeliveryScanner`/маркировка используют общий `ScanField` из `features/platform` (не дублируют реализацию); код места в `MarkedGoodsPanel` сверяется с профилями маркировки сервера (`isValidScan`) до добавления; серверная сверка полноты состава явно указана текстом, не эмулируется на клиенте.
- Каждый `<button>/<select>/<input>` в проверенных файлах — с `title`+`data-help-id`; `HelpHint`/`NativeHelp` ссылаются на опубликованные статьи (`store-receiving-app`/`-barcode`/`-weight-photo`/`-paper-count`).
- Размеры: ни один прочитанный файл не превышает ~134 строк (`useStoreReceivingFlow.ts` — самый большой из проверенных), отдельные функции не превышают ориентировочно 30–40 строк — в пределах 600/100 с большим запасом. Привожу фактические цифры, а не округлённую оценку, с учётом замечания о неточности в C0113.

## Найденный и исправленный конкретный дефект

**`MarkedGoodsPanel.tsx`: кнопка «Добавить скан» не была визуально disabled**, хотя функция `add()` уже содержит полноценную защиту (`if (disabled || invalid || !profile || !effective || !code) return;`). На сенсорном экране 360/390px кнопка выглядела активной и нажимаемой, когда код не введён/профиль не выбран/панель повреждена — молчаливый no-op вместо понятного запрета. Добавил `disabled={disabled || invalid || !profile || !effective || !code}` на сам `<button>`, повторяя логику guard'а без изменения правил. Это выравнивание интерфейса с уже существующим правилом, не новая бизнес-логика.

## Проверено и признано НЕ дефектом (не трогал)

- Общая форма `confirmed` в `api.ts` (статус<500 вместо точного allowlist статусов, как в case-work) — теоретически шире, чем в case-work, но backend `store_receipt_routes.py`/`contracts.py` сегодня никогда не даёт 404 с подходящим телом для `/confirm`/`/unloading/start`; GET-пути защищены отдельно (нет тела запроса → `confirmed` не может стать true). Фиксирую наблюдение для root на будущее ужесточение backend-контракта, но не переписываю рабочий frontend-код под не воспроизводимый сегодня сценарий.
- Один устаревший черновик `pending` для `already_received` поставки в `runOpen` не очищается явно (строка не содержит `clearReceiptDraft`), но это не создаёт ложный успех/отказ — при повторном открытии той же уже принятой поставки ветка `already_received` снова выигрывает первой; черновик просто остаётся лежать в localStorage без эффекта. Не нашёл сценарий, где это искажает текущий результат — не стал трогать ради риска.

## Не делал / ограничения

Не запускал `tsc`/gate/браузер (нет Bash). Не трогал backend/Oracle/API/policy/baseline/git/entry/vite/serviceworker/help-публикацию. Не писал в assembly/case-work. Это статический review — не заявляю приёмку физического оборудования/native.

**Занятые файлы:** `terminal/wms_terminal_web/src/features/delivery/components/MarkedGoodsPanel.tsx` (единственная правка), `coordination/retailcase-claude/CLAUDE_C0114_STATUS.md`, `CLAUDE_C0114_TO_CODEX.md`.
