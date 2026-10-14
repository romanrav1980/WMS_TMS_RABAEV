# NI03.2 — исполнение и восстановление заданий

09.10.2026. В работе с 13:45 MSK. [[nicora_ni031_stock_eligibility_20261009]] — предыдущий спринт.

## Первый ограниченный ticket: остаточное задание и потеря ответа

Владелец stock-effects — inventory; исполнитель проводки — существующий RRL_STOCK_POSTING_API/TASK_COMPLETE. Ресурсный механизм не создаётся заново. Подтверждённый остаток уже формируется атомарно, но у новой PLANNED задачи наследуются RESOURCE_ID/RESOURCE_SESSION_ID/EQUIPMENT_ID и плановые даты завершённого шага. UI не использует возвращаемый residual_task_id; количество пересылается через Number с потерей точности.

Изменение: очистить ресурсное назначение и времена нового остаточного шага; возвращать remaining_quantity в исходных единицах. API чтения /api/warehouse-tasks/{task_id}/progress показывает цепочку максимум 100 шагов, подтверждённое количество и остаток. Существующие права warehouse_task_view/execute и Oracle журнал сохраняются. Никакого самостоятельного stock commit.

UI хранит исходный запрос/operation_id до подтверждённого ответа, позволяет повторить тот же запрос после потери связи и показывает следующий шаг. Числовой факт пересылается строкой.

Миграция 2026-10-09-008-task-recovery: [apply](../../db/migrations/2026-10-09_ni032_task_recovery/apply.sql), [rollback](../../db/migrations/2026-10-09_ni032_task_recovery/rollback.sql), checkpoint 221 — исходный live RRL_STOCK_TASK_CORE. Область обратима, копия базы не создаётся. До фактического live apply и случая выполнения приёмка не объявляется.

Live fixture выявил три прежних блокера partial completion: Oracle JSON HAS при nonzero on_error отвергает отсутствующие optional keys; PART hash 69 символов не помещается в UID_PALLET(50 CHAR); legacy unique RRL_WAREHOUSE_TASK_U1 не допускает residual identity. Установлены явная проверка типов optional metadata, PART длиной 50 и новый unique U2 с PARENT_TASK_ID. Новый индекс ставится до удаления старого; rollback откажет до удаления защиты, если уже есть residual history. Checkpoint 222 — live TASK_PLAN. Обязательные scans/quantity проверяются прежними правилами; данные не удаляются.

Первый ticket установлен и адресно подтверждён: QA TASK_ID=558, частичный факт 1, residual 2, повтор без duplicate, итог 3, domain DONE после остатка; P=H=0 восстановлены явным INVENTORY_COUNT, история сохранена. Реальный API /558/progress: без auth 401, admin Basic 200/confirmed=3/remaining=0/DONE. UI Node lost-response/reload/exact-payload cases passed, JS syntax passed; полноценная браузерная/независимая приёмка ещё не выполнена. RESULT_UNCERTAIN у completion теперь 503; durable request не удаляется при неопределённом исходе. Общий спринт открыт: назначение/восстановление после shortage ещё дорабатываются.

Slow SQL ticket 1: v\$sql progress ancestors 37.76 ms, family 11.62 ms (по одному real HTTP execution). Решение: обе выборки ограничены 101/допуск 100 steps, сохранены существующие PK и PARENT_TASK_ID index I6; новый индекс ради чтения не нужен. Новый U2 нужен для корректности residual identity, не как предположение об ускорении. Поведение при production объёме не заявляется.

Ticket 2: существующие WarehouseTaskService.assign/start и TASK_COMPLETE подключаются к единственной read-only Oracle RRL_TASK_RESOURCE_POLICY.context_json. Владелец assignment adapter — resources/public.py, записи существующих заданий остаются в их outer transaction. Используются действующие resource_dispatch_manage/warehouse_task_force_assign, действующие RUSERS и ACTIVE/PAUSED session. Чужой исполнитель/сессия, неработающая техника и смена физического шага в IN_PROGRESS отвергаются; повтор start того же состояния не создаёт второго resource event. Source signature включает status/assignee/resource/session/equipment; resolved session входит в sorted anchor closure, caller блокирует row session после document/task в прежнем порядке. Политика не меняет P/H и не создаёт второго executor. MES document_confirmation сохраняет отдельное существующее право без фиктивного credit техники. Миграция 2026-10-09-009-task-resource-policy, checkpoints 223/224 и paired rollback подготовлены; приёмка ticket 2 пока не объявляется.

Ticket 2 установлен: QA565 с отдельным RUSERS/группой только warehouse_task_execute/view. Self assignment/start+повторы дают ровно два события; чужой completion отклонён 20882; переназначение IN_PROGRESS запрещено; следующий START на занятой сессии запрещён. Partial TASK_COMPLETE освобождает CURRENT_TASK_ID в своей stock transaction; residual хранит NULL resource/session/equipment, полный остаток выполнен. Исходная сессия/QA ресурсы закрыты, пользователи помечены deleted, запас 0, история сохранена. Миграция009 VALID. Неполадки fixture reserved bind :resource и STATUS=RETIRED вместо реального CLOSED исправлены; один оставшийся QA запас восстановлен через INVENTORY_COUNT без удаления истории. Общая независимая приёмка и квалификации/urgent recovery ещё открыты.

Ticket 3 prepared: RESTORE отделён от ACCEPT_SHORT; существующие RRL_CASE_PICK_SHORT/RRL_INVENTORY_TASK/RRL_PICK_WAVE_REPLENISH_TASK связаны recovery state. INV_COUNT сохраняет факт и inventory-task в одной транзакции, требует все партии SKU/ячейки и CELL X fence, 0 counts только для linked empty-cell task. Pending inventory запрещает новый source; чужой HARD не списывается, ниже HARD применяется прежний явный отказ. Срочное пополнение использует WAVE source allocator/warehouse TASK_COMPLETE, приоритет 0 и исходный deadline <=300 секунд. READY требует своего покрытия; прямой выбор реально найденного target stock — тот же CASE_SHORT_APPROVE/kernel, без второго executor. Переход RESUMED фиксируется после физического CASE pick. CASELOT identifier приведён к legacy 50 CHAR; checkpoint225 сохраняет прежний код. Миграция010 checkpoints225-233, paired rollback сохраняет добавленные поля/историю; worker остановить до rollback. Установка/приёмка ещё не объявляются.

## Установленный результат на 09.10.2026, продолжение рабочего окна

Записи выше отражают момент подготовки отдельных tickets. Актуальный результат: миграции 008–017 APPLIED в прежней RABAEV/orcl; общий NI03.2 остаётся in_progress. Второй экземпляр Oracle и копия базы не создавались. Записи движения не удалялись.

### Восстановление недостачи и исполнение по частям

010 связывает существующие SHORT → INVENTORY_TASK → WAVE_REPLENISH_TASK → WAREHOUSE_TASK → CASE. RESTORE восстанавливает заказ; ACCEPT_SHORT сохраняет прежнее отдельное решение принять недостачу. SELF требует настройки и прав на подтверждение инвентаризации; AUDITOR направляет срочное задание свободному допущенному аудитору с актуальной позицией. Пересчёт требует все положительные партии данного SKU в ячейке, защищён CELL X и не списывает чужой HARD. Pending inventory исключает ячейку из источников до подтверждения.

Worker сохраняет исходный SOURCE command до проводки, использует lease 45 секунд/retry 5 секунд и тот же operation_id после неопределённого ответа. Срочная задача имеет приоритет 0 и исходный deadline, по умолчанию 300 секунд; повтор, передача и новый шаг его не сбрасывают. 015 допускает восстановление несколькими физическими подачами: промежуточный CASE остаётся WAIT_REPLENISHMENT, RESTORED_AT ставится только после полного остатка заказа. Материал не считается восстановленным по одному созданию задания.

014 считает вместимость в базовых единицах через существующий BOX→BASE и объём коробки. Учитывает фактический запас, оставшуюся часть открытых пополнений и других поступающих заданий, под общим CELL X. DEMAND_BASE_QTY сохраняет исходную потребность, RT.QTY отражает реально выбранную подачу. FULL_PALLET должен целиком помещаться; FILL может подаваться частями. Нет места → WAIT_FREE_CELL. Без заданной вместимости сохраняется прежний неограниченный режим; это не подтверждение промышленной настройки адресов.

### Ресурсы, маркировка и интерфейсы

011 — явные действующие квалификации resource/task-type, смена, занятость, свежая позиция. Расстояние CELL_MANHATTAN по X/Y/Z; стены, граф проездов и реальное время пути этим показателем не доказаны. 016 распространяет серверную политику на CASE claim/start/report/physical confirmation/transfer. Передача записывает целевого оператора сессии, автор-диспетчер сохраняется в аудите; собранная паллета, количество и ячейка не меняются. Обычный исполнитель требует квалификации и сессии; прежний административный обход требует отдельных прав. 017 добавляет PUTAWAY в возможности существующих REACHTRUCK/FORKLIFT, но индивидуальный допуск автоматически никому не выдаётся. Физическое исполнение требует OPEN смену.

Срочное пополнение автоматически назначается через существующий WarehouseTaskService ближайшему свободному квалифицированному ресурсу с позицией/heartbeat не старше 300 секунд. Нет кандидата → явное ожидание, физический запас от назначения не меняется. Вставка operational tasks ограничена 200 строками за проход; выбор кандидатов — 20.

012 — immutable server scan draft: actor/task/source/version/profile signature и canonical physical unit keys. Повтор ID с иным составом отклоняется; изменившийся профиль запрещает проведение. CRPT + EGAIS на одной физической единице считаются одной штукой. UNIT/UNIT_OR_AGG поддержаны для этого шага; aggregation-only partial и полная матрёшка остаются NI04. 013 исправляет ранее невозможную регистрацию маркированного inventory/MES lot: unit FK связан с общей RRL_PALLETS, а не только SAP receipt. История non-SAP birth сохраняется; rollback запрещён при несовместимых retained units.

Новые API: warehouse progress/scan-context/scan-drafts; inventory tasks/recovery-shorts/replenishment-progress; qualifications/position/candidates/dispatch-nearest. Используются существующие права и Basic-auth shell. Raw ARM/ТСД получили остаточный шаг, повтор сохранённого подтверждения, сохранение сканов, inventory queue, recovery monitor и фактический прогресс подачи. CASE transfer запрашивает реальную целевую сессию. Полная браузерная приёмка пока не объявлена.

### Адресные доказательства

- TASK fixtures: 558 partial 1+2/replay; 575 квалификации/занятость; 591 marked 3 физических единицы с двумя профилями, stale-profile refusal; 593 arrival capacity/no overfill. Отдельный источник: запрос 3 при свободной ёмкости 1 даёт delivery 1 и сохраняет demand 3.
- CASE 928/SHORT10: две подачи по 1, промежуточное ожидание и конечный факт 3, исходный deadline сохранён.
- CASE 929: обычные отдельные комплектовщики, отказ без квалификации, повтор start, явная передача после первой штуки.
- CASE 932/WAVE220/SHORT14: независимые комплектовщики, аудитор и ричтрак; автоматическое назначение task601/ресурс25, две подачи по 1, итог CASE3/replay, deadline неизменен.
- Ошибки адресных случаев исправлены до успешного повторного выполнения: reserved SQL binds/UID alias; CLOB JSON уже dict; JSON_ARRAY put требует overwrite=true; inline bounded INSERT переносит sequence наружу и различает FROM/TO_WARE aliases.
- Fixtures очищают собственный запас через ядро INVENTORY_COUNT/CASE_RETURN/release, закрывают ресурсы/сессии и помечают QA users deleted. Журналы остаются.

### Незакрытый объём

NS21 общий SOFT пул открытых заказов и привязка generic WAVE HARD без PICK_TASK к конечному потребителю ещё требуют доведения. NS26–30: согласование полной мини/MAX автоматики, начала смены и всех комбинаций ролей/техники, дежурства в последние два часа. NS31: физическое подтверждение передачи уже собранной паллеты и полный ТСД handoff. NS38: ссылка на расследование по камере. NS39: альтернативная свободная ячейка и дежурная политика. Независимая приёмка, полный browser flow, реальный SAP и государственные квитанции отсутствуют. Следующий NI03.3 не начат, пока NI03.2 имеет эти функциональные пробелы.

Изменения локальные, без нового commit/push. Архитектурный gate имеет прежние нарушения зависимостей/размера; baseline не повышался, полное качество спринта не объявлено. Текущий runtime manifest содержит актуальные владельцы Oracle; historical apply сохраняют согласованные снимки до следующих зависимостей. Откат выполнять в обратном порядке с остановленным worker и соответствующим application code, не стирать физическую историю.

### Дополнение: handoff, модульность и рабочий runtime

Передача физически собранной CASE теперь требует scan_container, expected_content_version, ожидаемого владельца/его сессии и offline_event_id. Под CONFIG X и CASE row lock проверяется фактическая паллета и прежний владелец. Повтор точного запроса читает исходное TRANSFERRED событие; другой payload/actor/task с тем же ID даёт409. Неверный скан и устаревшая версия не меняют назначение. UI хранит исходный запрос в localStorage до подтверждения; повтор после неизвестного ответа использует тот же ID/body. Это подтверждение диспетчером по скану; отдельная двухсторонняя подпись и реальное оборудование не заявлены.

CASE934/WAVE222/SHORT16: квалификации, start replay, отказ wrong carrier/stale version, успешная передача, exact handoff replay/changed-body409/одна event row, независимые аудитор и ричтрак, две capacity1 подачи, итог CASE3, deadline сохранён. Новый адресный случай после extraction прошёл; свой P/H возвращён через ядро. API /case-pick/tasks/934 и replenishment-progress/wave222 дают200; обе подачи confirmed1, case order remaining0. /api/resources доступен с правом, anonymous401; resource HTML обслуживается200. Browser MCP не ответил, вызов прекращён; DOM/console/screenshot evidence отсутствует.

Ресурсные actions извлечены в modules/resources/infrastructure/case_actions.py; CASE event writer — inventory/infrastructure/case_events.py. Legacy class делегирует через public. Resource assignment получает существующий WarehouseTaskService через явный callable из resource_composition.py; resources не импортирует этот legacy service обратно. Новые циклы ресурсов устранены и рост CASE файла выше baseline устранён. Осталась прежняя общая cyclic component и прежние API/legacy violations; общий architecture FAIL не скрыт и allowance не увеличен (248 файлов/209 debt items после извлечения).

CASE listing/detail выдают количества строками из Oracle. ARM сохраняет точные строки для индивидуальных фактов и BigInt decimal sum для итогов списка; 1.5 не отображается как2. Проверка больших decimal сумм за пределами JS safe integer прошла. Number остаётся только для визуального процента прогресса. Выдавать процент сборки за производительность по времени прекращено; без временного расчёта отображается отсутствие метрики.

Reservation adapter исправлен: RESULT_UNCERTAIN →503/outcome_confirmed=false/retry_same_operation_id=true, а не подтверждённый409. Малый injected-error contract case подтвердил сохранение исходного ID; реальный lost-commit этим отдельным случаем не моделировался.

Background worker запущен скрытым локальным процессом через scripts/start-short-recovery.ps1, PID25448 на момент записи, heartbeat не выдумывается. Повторный launcher проверяет PID+время старта и не запускает вторую копию. Loop переживает ошибки DB claim с задержкой до30s, permissions failure останавливает процесс; SIGINT/SIGTERM запрашивают завершение после текущей итерации. Windows Stop-Process не является этим graceful сигналом. [Runbook](../runbooks/nicora_short_recovery_worker.md). Надёжный Windows service supervisor остаётся вне dev подтверждения.

Для Qwen подготовлены [адресные задания](../../задания%20на%20проведения%20тестов/NI03.2/README.md). Они не запускались независимой моделью.

### SQL после последнего функционального случая

v$sql выборки ресурсов/SHORT: самый долгий candidate SQL f57a0wuwxgrnu — средние251.97ms, 2 исполнения; urgent task lookup2z0p5am2vquca —5.15ms; frozen intent lock25pa9jyst0nvf —2.51ms. Это малое dev окно, не p95/production capacity. В RRL_SQL_SLOW_LOG за текущую дату по новым inventory/resources/warehouse paths записей нет; HTTP slow-sql endpoint обслуживается200, старые записи отдельно от нового evidence. Oracle top SQL использован для прямых fixtures, местный API audit подтверждает read HTTP calls.

Решение: сохранить bounded candidates<=20/fresh-position300s, source/arrival scopes<=200 и batch tasks<=200. Для candidate owner resources: при устойчивом >500ms или росте active pool снять execution plan и уменьшить вычисления прав/пул до сортировки; индекс/кэш вводить только по плану и профилю. Сейчас новый индекс на предположении не добавляется. PK/qualification key/short queue/task source-parent indexes остаются. Окно source/recovery фиксируется по идентификаторам, широкий нагрузочный прогон не проводился.

Последний SELECT фактического состояния: P=0/H=0, текущие изменённые packages VALID. Encoding check passed. Изменения остаются локальными без новой публикации.

### Последний ticket рабочего окна: residual deadline

018 APPLIED: остаточный шаг PRIORITY=0 наследует исходный PLANNED_FINISH_AT; новое назначение resource/session/equipment и PLANNED_START_AT очищаются. У обычного задания обе плановые даты очищаются, как раньше. Это устраняет потерю SLA при partial urgent delivery. Checkpoint250 и paired rollback сохранены, apply018 использует собственный согласованный source snapshot. Реальный TASK607:1+2/replay/domain DONE, exact original deadline у residual подтверждён, QA запас возвращён через ядро. Само наследование deadline не реализует ещё открытую duty policy.

Worker после проверки штатной остановки/повторного запуска: PID55116; PID/time в runtime/short_recovery/worker.json является актуальным источником. Предыдущие PID выше — исторические. Stop marker прекращает цикл после текущей итерации; количество/журнал от этого не меняются.

SQL после TASK607: gt5h1s6kq0d2b family средние5.91ms и7u181v9a7vgru ancestors5.34ms (по2 исполнения). Решение: прежний bound100/I6; индекс не добавлять. [Карта исходников](../components/nicora_ni032_source_map.md).
