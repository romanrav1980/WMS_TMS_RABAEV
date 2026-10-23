# RESULT C-0156: бумажная сборка коробов CASE (Claude)

Статус: пакет готов к применению root. Checkpoint `ac0bfde0` (только локально). Native-комплект **NOT_APPLIED**: Oracle я не применял. API :8088 не перезапускал, поэтому новый endpoint на живом сервере пока не работает. Без применённого пакета бланк отвечает `503 CASE_PAPER_NOT_AVAILABLE`, а факт с бумаги сервер не защищает. До apply и restart у root сценарий считается открытой работой, а не готовой функцией.

## Фактический контракт CASE (что выяснено)
- Подтверждение строки делается существующей командой `POST /api/case-pick/tasks/{t}/lines/{l}/confirm` и native `CASE_PICK_CONFIRM` (RRL_STOCK_CASE_PICK_CMD):
  - количество накопленное;
  - сканы ячейки, SSCC короба и товара обязательны;
  - подтверждает исполнитель или сотрудник со штатным правом `case_pick_manage`;
  - задание должно быть в статусе IN_PROGRESS, PARTIAL или WAIT_REPLENISHMENT;
  - для маркированного товара нужны units, для весовой этикетки — `RRL_CASE_WEIGHT_SCAN`;
  - `CONTENT_VERSION` сверяется только между compile и execute.
- **Версии напечатанного бланка в CASE не было.** Поэтому подготовлен NOT_APPLIED native-hook.
- Повтор: в `RRL_STOCK_POSTING_API` уже проведённая операция обрабатывается до compile/execute (ветка `v_exists`). Это прочитано в живом USER_SOURCE. Значит, точный повтор подпись бланка не проверяет.
- `ASSIGNMENT_VERSION` нельзя брать в подпись. Триггер `RRL_CASE_ASSIGN_VERSION_GUARD` увеличивает её при любой смене статуса, старта, ресурса или сессии. Тогда старт задания или подтверждение соседней строки делали бы весь бланк устаревшим.

## Native (`db/migrations/2026-10-23_case_pick_paper/`, NOT_APPLIED)
- Новый пакет `RRL_CASE_PICK_PAPER`:
  - `line_signature(line)` — SHA-256 полей строки;
  - `assert_expected(line, expected)` — при несовпадении отказ `-20886 CASE_PAPER_LINE_CHANGED`; NULL означает «без бумаги», команда работает как прежде.
- Поля подписи:
  - задание: `CASE_PICK_TASK_ID`, `WARE_ID`, `SSCC`, `ASSIGNED_TO`;
  - строка: `CASE_PICK_LINE_ID`, `PICK_TASK_ID`, `ARTICUL`, `CELL_CODE`, `PLANNED_QTY`, `PICKED_QTY`, `STATUS`, `REQUIRED_SCAN_MODE`;
  - товар: `RRL_SKU_RECEIPT_POLICY.POLICY_VERSION` (переключает режимы маркировки и весовой этикетки).
- В подпись **не входят**: статус задания, `ASSIGNMENT_VERSION`, `CONTENT_VERSION`, другие строки. Подпись строки, а не всего бланка: подтверждение одной строки не портит остальные.
- `RRL_STOCK_CASE_PICK_CMD` получает **одну** строку-вызов `assert_expected` в execute:
  - после канонических блокировок задания и строки и после проверки `CASE_TASK_ACTOR_CONFLICT`;
  - до сверки сканов и любого update.
  - В compile проверки нет. Diff с живым исходником: +3 строки (2 комментария и вызов).
- Хэши:
  - before body `528383B6…000489`;
  - after body `53EA97EC…5E735F`;
  - paper spec `CFA6B9FF…91BD688`;
  - paper body `E7B8B94A…C3CE6CD`.
  - `000_preflight` сверяет before. `verify` сверяет все три after и отсутствие INVALID. `rollback` сначала восстанавливает before-тело, затем удаляет пакет. `rollback_verify` сверяет before.
  - `manifest.json` содержит поля подписи, ход повтора и `files_sha256` (по байтам рабочей копии, LF; git на Windows может перевести в CRLF).
- Проверка на живой БД (только чтение, анонимные блоки, функция без изменений):
  - подпись строк 921/936/937 стабильна, 2–7 мс;
  - покрытие полей (`case-signature-coverage-live.json`): picked, planned, cell, assigned_to, carrier, line status, scan mode меняют подпись; статус задания, ASSIGNMENT_VERSION и CONTENT_VERSION не меняют.
  - Изменённое тело CMD не компилировалось: его нельзя собрать без установленного пакета.

## Backend (мои файлы)
- `modules/inventory/domain/case_paper.py`: собственный Code128 B для `CPICK:<task>:<line>:<sig>` (PATTERNS из sscc_label). `task_paper.py` root не тронут.
- `modules/inventory/contracts_case_paper.py`, `infrastructure/case_paper.py`, `api/case_paper_routes.py`:
  - `GET /api/case-pick/tasks/{task}/paper?line=&expected_signature=`;
  - READ ONLY снимок с существующей областью CASE (`RRL_CASE_TASK_ACCESS.assert_scope`, case_pick_execute);
  - 5 SQL при любом числе строк; проекция маркировки и веса — одна на все уникальные артикулы (по ревью root);
  - предел 200 строк;
  - ответы: 409 `CASE_PAPER_LINE_CHANGED`, 404, 503 `CASE_PAPER_NOT_AVAILABLE`.
- `app/case_paper_composition.py`: guard и маппинг `CaseReadError` подключаются здесь. Плюс 2 строки в `main.py`, экспорт в `inventory/public.py`.
- `schemas.py:CasePickLineConfirmRequest.expected_case_signature` (64 HEX). Для бюджета размера файла удалена одна лишняя третья пустая строка.
- `case_pick_commands.post_case_pick`:
  - подпись попадает в metadata только если задана;
  - запрос без бумаги сравнивается при повторе так же, как до появления поля (старые сохранённые операции не дают ложный CONFLICT).

## UI (`workspaces/paper/**`, dev :3021)
- Переключатель «Складские задания / Сборка коробов CASE». Для CASE склад выбирается по возможности `picking`.
- Очередь CASE: существующий `GET /api/case-pick/tasks?scope=all&ware_id&limit=100`, только открытые статусы.
- Бланк: таблица строк и печать A4. На каждую незакрытую строку — штрихкод CPICK, поля «собрано всего» и «время/подпись», пометка «печать не подтверждает выполнение».
- Факт вносится **только по штрихкоду строки с бланка**:
  - сверка версии; поздний ответ прежней сверки не перетирает новую;
  - сканы ячейки, SSCC и товара, накопленное количество;
  - тело с operation_id сохраняется в localStorage до отправки, повтор отправляет те же байты;
  - журнал снимает только квитанция своей операции или подтверждённый отказ;
  - 503, 401/403 и сеть оставляют факт, он переживает перезагрузку.
- Ограничения ввода с бумаги:
  - маркированные строки: коды маркировки сканируются HID-сканером и уходят как существующие unit_scans (K-0126, `9d73f60a`); весовые этикетки с бумаги не вносятся (только ТСД);
  - весовой товар без этикетки вносится как показание весов, кг — существующий ручной канал;
  - если задание не начато, ввод заблокирован; бумага задание не начинает;
  - подтвердить за другого сотрудника можно только со штатным `case_pick_manage`; новое право не вводилось.
- Справка: `docs/help/authoring/paper-tasks.md`, раздел CASE.

## Проверки
- `tests/tradecase/test_case_paper.py`: **10 passed**. Покрывают:
  - barcode и снимок (только чтение, число SQL, флаги);
  - соответствие проекции и `case_pick_policy`;
  - маршрут и композицию;
  - metadata, точный повтор, legacy-повтор и конфликт;
  - native diff и hook после locks, поля подписи, хэши манифеста.
- `test_case_stock_command_replay` и release boundary: PASS.
- UI `C0156/scripts/c0156_ui.cjs`: **37/37** при 1440 и 390 (после K-0126).
  - **LIVE GET**: вход, склады, очередь CASE склада 6667491 (задания 1019/1020).
  - **FIXTURE TRANSPORT**: `/paper`. Ответ собран из живых строк 1019/1020 (`case_paper_fixture_live.py`); подпись посчитана функцией NOT_APPLIED; маршрут на :8088 ещё не загружен.
  - **SYNTHETIC/FIXTURE**: 409 устаревшей версии, все POST подтверждения (503 → перезагрузка → 403 → ack, три отправки одинаковых байтов; отказ CASE_PAPER_LINE_CHANGED; OPERATION_CONTENT_CONFLICT), маркированная строка, 403 очереди.
  - Живых записей 0.
  - Также: печать (popup, PDF `C0156/case-paper-print.pdf`, штрихкод в странице), отсутствие горизонтального скролла, title и help у всех кнопок.
- C0155 UI-регресс 19/19 PASS.
- Quality gate PASS (architecture debt 72, без роста). tsc PASS, encoding PASS.
- Долгие SQL: `C0156/sql-report.md`. Масштаб 200 строк **не проверен**: в БД нет CASE-задания больше 2 строк, создавать данные запрещено.

## Для root
1. Применить комплект (preflight → 001 → 002 → verify), затем общий restart API.
2. После этого выполнить живую сверку: `/paper` без fixture, затем native-отказ по старой подписи и успешное подтверждение на разрешённом QA-задании. Это делает root: подтверждение — запись, а мне мутации запрещены.
3. Не проверено физически: принтер, сканер, весы.
