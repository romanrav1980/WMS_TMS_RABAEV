# Важное изменение: переход на единое ядро проводки остатков

09.10.2026. Фактическое переключение существующей **RABAEV@127.0.0.1:1521/orcl выполнено**. Release **ACTIVE**, baseline **B0-20261009-STOCK-V2**, **STOCK_LEGACY_TRIGGER_ENABLED=0**. Новая схема, второй экземпляр Oracle и копия VM не создавались.

Это актуальный статус вместо PREPARED в исторических страницах [[nicora_stock_posting_case_shipment_20261009]], [[nicora_stock_posting_native_quality_20261008]], [[nicora_stock_posting_revision_20261008]] и [[nicora_stock_posting_implementation]]. Данные прежних установок там сохранены как история.

## Исполнитель и существующие клиенты

Одна явная команда RRL_STOCK_POSTING_API выполняет проверку/план, упорядоченные fences и anchors, изменение P/H и состава, журнал, доменный результат и обязательный RRL_EVENT_OUTBOX в одной транзакции. Caller делает один commit. Повтор operation_id возвращает сохранённый результат; иное содержимое отвергается. Прямой UPDATE остатка после переключения запрещён охранным триггером. Старый event-trigger не является вторым исполнителем: compatibility OFF, управляется отдельной аудируемой настройкой.

Writer registry: **25 ADAPTED / 6 RETIRED / 0 UNCONVERTED**, всего 31 известный источник. Закрыт последний прямой UPDATE в Form1: редактирование количества открывает существующую инвентаризацию, где оператор подтверждает измеренный факт. picking_service направляет физические эффекты в действующие команды задания/волны/CASE; старые приватные builders доступны только до ACTIVE.

WinForms успешно собран Framework MSBuild и обновлён bin/Debug/WindowsApplication2.exe. Удалены неиспользуемые COM-ссылки DAO, ADODB, Office.Core и VBIDE, блокировавшие сборку; используемый Excel interop сохранён. API перезапущен через корневой serv.bat в скрытом окне, /health отвечает ok.

## Завершённые стыки

208/212/213: INVENTORY_REGISTER_LOT и MES FG_PALLET_RELEASE используют существующие WMS marking policy, unit/code tables и локальный regulatory journal. По маркированному SKU обязателен полный захват уникальных единиц; quantity/base identity сверяются с фактическим domain plan. UNIT/unique-code anchors входят в полный план до любых вставок; CAPTURED переводится в AVAILABLE только вместе с физическим запасом. API передаёт точные decimal strings. Скан агрегата требует известного состава; нового non-SAP manifest resolver здесь нет.

209/210: CASE_CARRIER_RETURN возвращает весь положительный состав carrier в исходные ячейки по фактическим сканам, снимает собственный HARD, отменяет оставшиеся задания/short requests и связь с СТ одной транзакцией. Чужой HARD и уже отгруженный carrier запрещают возврат. ТСД сохраняет operation_id/body до HTTP и удерживает неизвестный результат до повтора.

211: закрыты последние writer registry entries. 216: реальная первая проводка обнаружила ORA-00904 для зарезервированного имени UID в JSON_TABLE; транзакция откатилась полностью. Колонка переименована STOCK_UID_JSON, исходный live package сохранён в paired rollback до исправления. После исправления реальные команды прошли.

## B0 и восстановление

[Runner](../../scripts/stock_posting_cutover.py) захватил эксклюзивные RELEASE/CONFIG fences и NOWAIT table locks, проверил пустые RRL_REMAINS/RRL_EVENTS/receipt units/новый журнал. 73 устаревших ACTIVE SOFT MES_RAW с неуказанной базовой единицей отменены как тестовые прогнозы; их полные строки сохранены в runtime/stock_posting_20261009/cutover-checkpoint/legacy_soft_reservations.json. Физический запас не суммировался и не пересчитывался.

B0 содержит SCN и manifest SHA256 исходников, stock/unit baseline пуст. CUTOVER → B0 READY → ACTIVE зафиксированы одним commit. Snapshot не меняется после последующих исправлений: 216 отдельно записан в ledger, актуальные исходники остаются в current_runtime_manifest.json.

Ошибка до commit автоматически возвращает прежние данные. До первой проводки восстановление PREPARED возможно по checkpoint под теми же эксклюзивными fences. После первой проводки откат к старому исполнителю запрещён: история остаётся, применяются обратные/корректирующие команды. 214_cutover_rollback.sql специально останавливает слепой rollback, а не скрыто сбрасывает release.

Миграции 2026-10-09-003-marked-stock-birth, 004-case-carrier-return, 005-stock-posting-cutover и 006-invariant-json-column записаны APPLIED. SQL/checkpoint/paired rollback находятся в db/migrations/2026-10-08_stock_posting_core (историческое имя каталога).

## Подтверждённый результат и границы

Реальные committed Oracle cases: измерение 0 → 1 → 0; неизменный повтор без нового события; две конкурирующие команды одного UID/cell/version — ровно одна применена, другая отвергнута INVENTORY_SNAPSHOT_STALE/CLOSURE_CHANGED; другое содержимое того же operation_id отвергается. После реально выполненного birth DML искусственная ошибка до commit откатила PALLET, P, журнал, operation и outbox. Прямой UPDATE P отвергнут.

Итог: **8 APPLIED операций, 8 append-only движений, P=0, H=0**, release ACTIVE. Восемь включают повторные запуски конкуренции после исправления двух ошибок самого диагностического скрипта; ложных stock изменений нет. Failed/rejected commands не добавлены в committed журнал. 24 локальных теста API/replay/Decimal/CASE/wave прошли. Количество не является доказательством пропускной способности.

Помарочный положительный birth, полный CASE-return/shipping браузерный сценарий, arbitrary nested HU и составные новые складские процессы не объявляются принятыми этим переключением. Это завершение перехода существующих stock writers, не завершение всего NICORA и не государственное подтверждение кодов. Миллионы операций/день не измерялись.

## Решение по SQL

RRL_SQL_SLOW_LOG за последние два часа пуст: CLI cases не проходят API SQL instrumentation. В Oracle v$sql самый долгий обнаруженный запрос — одноразовый regexp-обзор USER_SOURCE, 1210.5 ms; решение: оставить только инструментом выпуска, не выполнять на request path. Stock operation INSERT: 14 executions суммарно 52.7 ms (~3.8 ms); bounded stock-case selection ~6.2 ms/вызов. Оснований вводить новый индекс по этим малым dev cases нет.

Владелец дальнейшего capacity review — разработчик ядра. Решение: при первом реальном объёме проверять execution plans UID/cell, own reservations и closure queries; API slow SQL + audit анализировать после API business case. Промышленный load и внешние Track & Trace сервисы этим выпуском не проверялись.

Проверка кодировки выполнена: единственная ошибка — прежний raw TRANSPORT_TASK_PACKAGE_BODY.sql (маркер Р+NBSP), не исправлялся как исходное свидетельство. Новые поддерживаемые файлы этого выпуска ошибок не дали. /db/ping подтвердил RABAEV / orcl / ORCL, OpenAPI содержит новые inventory/lots и return-carrier endpoints.
