# Общий Гант ресурсов и рабочее место старшего смены

Решение владельца15.10.2026. Дополняет [[retailcase_scoped_access_and_knowledge]] и [[roadmap/retailcase_access_knowledge_plan]].

## Гант

Единый временной масштаб для ричтраков, комплектовщиков, ворот и машин. Группировка по РЦ/складу/типу; фильтры интервала, волны и задания. Связанный выбор сцена ↔ Гант ↔ задание ↔ ресурс ↔ карточка. План и факт отдельны, занятость/выход/доступность только по источникам. Работа, потребляющая несколько ресурсов, имеет один event_id и несколько bindings; не удваивать суммы/объёмы. Пересечение подтверждённых интервалов — основание конфликта; оно не означает запрета любой параллельной работы без правила ресурса. Незавершённый факт не получает выдуманное время окончания. Задания без времени выводятся отдельной очередью. Нет данных или свежего сигнала — неизвестность, не свободный ресурс.

Времена с offset, UTC на границе API. У старых Oracle TIMESTAMP без пояса нужно подтвердить часовой пояс площадки; запрещено молча применять браузерный/server timezone. Ночной интервал определяется пересечением, не одной датой начала. Ограниченные окна/выборки, явное превышение лимита, bounded API и доступ по объекту. Никакого автоматического drag/drop изменения назначений без серверного мандата, версии и подтверждённой команды.

## Старший смены

В стиле существующего двойника: сцена, процессы/исключения, карточка объекта, общий Гант и ресурсы. Три связанные области: будущая подготовка волны; риски запуска и зависимые действия; текущее исполнение и блокировки. Использовать существующие planning/execution/workload/qualification и пополнение, не вводить вторую реализацию волны.

Подготовка: потребность и обеспеченность запасом/отборными ячейками, нужные пополнения, окна, квалифицированные люди/техника и доступность ворот. Отсутствие источника явно. Текущее исполнение: план/подтверждённый факт/остаток по SKU и базовой единице, состояние задания, блокировка и переход к пополнению/контролю. Не суммировать разные SKU и единицы в ложный процент. Риск показывает доказуемую причину, объект, влияние, владельца/срок при наличии, переход к действию. Проценты риска и KPI не утверждены.

## Ответственность и приёмка

Resources владеет публичной read model ресурсов/занятости; fulfillment — волной, transport — рейсами/операциями, platform — общим UI/авторизацией. Codex: контракты, API/Oracle, интеграция и проверки. Claude: UI/помощь в features/platform/workspaces, по [C0074](../../coordination/retailcase-claude/TASK_C0074.md). Новые контракты согласуются прежним журналом.

Включено в AK05: машины/ворота и переходы; AK06: комплектовщики/ричтраки и старший смены; AK07: остальные ресурсы/паспорта показателей; AK08: многоресурсная/ночная/конкурентная/сетевая приёмка и SQL. Расширение не создаёт новый календарный срок. Независимая/физическая приёмка отдельно. Состояние: зафиксировано, source mapping/API и UI в работе.

## Реализованный первый источник и идентичность задания

GET /api/resources/timeline: native resource_gantt_view на склад, дополнительные source rights раздельны, mixed warehouse требует допуска ко всем членам. [Контракт](../../coordination/retailcase-claude/RESOURCE_TIMELINE_API_V1.md).6liveHTTP/native checks PASS,7interval tests PASS,fixtures cleaned,stockNONE. Учебные данные не используются. Legacy clocks без подтверждённой зоны остаются unresolved; это ещё не полная готовность всех планов Ганта.

Уже существуют RRL_WAREHOUSE_TASK (размещение/пополнение/перемещение и др.) и RRL_CASE_PICK_TASK (специализированная сборка с CASE-строками и волной). Первое связано с ресурсом/сессией/техникой; второе — ASSIGNED_RESOURCE_ID/RESOURCE_SESSION_ID/EQUIPMENT_ID. Планировщик не создаёт третью копию работы. Единая read model показывает исходный source_id, волны и зависимости; одно задание с человеком и техникой — один event, несколько bindings. Пополнение и зависимая CASE-сборка — разные работы, а не дубли. [[components/retailcase_ni032_task_family_20261014]], [[components/retailcase_ni033_wave_workspace_20261013]].

Клод подтвердил C0074 (K0050), K0049 workplace entry подключён к основной оболочке; следующий результат — ResourceGantt/ShiftSupervisorDesk. Новая UI-приёмка и source timezone продолжаются. После кейсов RRL_SQL_SLOW_LOG за45мин по timeline записей нет; не считать это p95. Решение resources/Codex: сохранять warehouse+<=7d и hard bounds, не добавлять индекс без плана; повторный slowSQL review после многоресурсного UI.


### UI audit: actual execution states and incomplete preparation (15.10.2026)

The shift desk now retains native open CASE states `NEW`, `ASSIGNED`, `IN_PROGRESS`,
`PARTIAL`, `WAIT_REPLENISHMENT`, `PICKED`; `PICKED` is picked but not yet closed,
not an assertion of ongoing physical picking. Pending shortage risks use actual
`CREATED`/`PENDING_APPROVAL` decision states. A missing/failed readiness, stock,
time or replenishment read produces an explicit unverified preparation warning;
a launched wave cannot enter the green clear stage on a partial read.

The common Gantt adapter supports four actual families: registry resources/equipment
(`CASE_PICKER`, `REACHTRUCK`), warehouse dock registry (`DOCK`), and transport
operations with a real vehicle (`VEHICLE`). Each source remains separately scoped;
a family supported by UI is not proof that a live site has populated, timed or
accessible assignments for that family. Legacy times without offsets stay outside
the shared axis. No resource availability or wave forecast is fabricated.

The header no longer sums event quantities by UOM across different products.
The current native timeline DTO does not supply an SKU quantity identity; its
adapter emits `quantity:null`. Individual event quantities, when supplied by a
supported model source, remain in event cards without a false total volume.

Validation: `tests/retailcase/shift_gantt_model_test.cjs` (actual native statuses,
partial source failures, four adapter families, distinct event accounting);
admin TypeScript and UTF-8 checks. These are offline UI/model checks, not a new
live Oracle, hardware, physical throughput or SQL performance acceptance.
