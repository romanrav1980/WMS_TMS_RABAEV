# NIKORA: план разработки архитектуры

Дата: 15.09.2026. Предлагаемый backlog; работы не выполнены. Целевая модель: [[architecture/nikora_minimal_extension]]. Функциональные спринты отдельно: [[roadmap/nikora_functional_sprints]].

## Принцип разделения

Исполнимые ТЗ: [10 архитектурных карточек в каталоге](../requirements/nikora_sprints/index.md), [[roadmap/nikora_agent_delivery_plan]], [[requirements/nikora_sprint_contract]]. A1/A2/A2.Q/A3 ниже остаются четырьмя семействами; их рабочие поставки разбиты на 2/3/2/3 спринта соответственно. Смета/агенты/тесты в индивидуальных карточках; архитектурный поток не смешан с 28 функциональными поставками.

Уточнение интерфейсов: [[requirements/nikora_ui_workplaces_tz]], [[roadmap/nikora_ui_subsprints]]. Четыре архитектурных инкремента A1/A2/A2.Q/A3 отделены от 23 функциональных. Порядок: A1 → F1 ERP master/order/status contracts → A2/A2.Q/A3 → остальные функции. Полная новая архитектура WMS не нужна.

Архитектурный поток создаёт устойчивые контракты, модели, транзакции и точки расширения. Функциональный поток добавляет бизнес-сценарии, экраны, алгоритмы и адаптеры. Архитектурный результат принимается через воспроизводимый sandbox/API/Oracle-тест, а не только диаграмму. Каждый спринт оставляет совместимую работающую систему; NIKORA закрыт feature flag до функционального допуска.

## A1. Контракт и надёжная обработка одной команды

Зависимости: доступный изолированный Oracle; владельцы Q01/Q02/Q03/Q05; рабочие договорённости по ключам и source registry.

Разработка архитектуры:

- Зафиксировать ADR, внешний ключ заказа/части, owner/store/site mapping и bootstrap Manifest→предварительная волна→AssemblyPlan.
- Специфицировать Manifest/version/completeness, профили получателей и матрицу полномочий источников. Это отдельный контракт, не восьмой «уже существующий» тип логистического XML.
- Специфицировать отдельный versioned XML API-контракт ERP↔TMS: входящие MasterDataSnapshot/Change (адреса, магазины, артикулы, GTIN/UoM и транспортные атрибуты), OrderManifest/revision/cancel и исходящие ORDER_ASSEMBLED, INTERNAL_MOVEMENT_PLANNED, ORDER_IN_TRANSIT, ORDER_DELIVERED_TO_STORE. Зафиксировать ownership, обязательные ключи, причинность, versioning и порядок статусов.
- Зафиксировать исправленную версию профиля с разными AGGREGATED/DISAGGREGATED cardinality; не менять старый опубликованный 1.1.0 без версии.
- Реализовать локальный schema registry/allowlist, безопасный parser и независимую проверку Context/семантики, без сетевой загрузки XSD.
- Inbox, raw payload/hash, entity revision/dependency, correlation/causation; переиспользовать EVENT_OUTBOX/ADAPTER_REQUEST.
- Общая транзакционная граница command handler: изменение + event + outbox в одном commit; ключи повторов, optimistic version, dead letter/retry.
- Подготовить additive миграции внешних ключей и стабильной FulfillmentPart/строк. До F1 это контракт и repository, не готовый бизнес-процесс.
- Тестовый adapter harness, конфигурация запрета mock в пилоте, роли и закрытый доступ к payload.

Законченный результат: MasterData и OrderManifest проходят ingress→inbox→тестовый доменный обработчик→outbox; повтор/сбой не удваивает эффект. Четыре тестовых ERP-статуса могут быть опубликованы только с валидной причинной ссылкой. APPLIED выдаётся только действительно применённой команде, не необработанному production-документу.

Приёмка A1:

1. 11 положительных/8 отрицательных примеров baseline и новые contract cases; после исправления профиля — новый эталонный набор.
2. Неизвестный root/version/Context, DTD/внешняя сущность, чужой sourceSystem и превышение 10 MiB отклоняются.
3. Два параллельных worker и 100 повторов одного сообщения дают один бизнес-эффект.
4. Обрыв до commit → нет эффекта; после commit до ответа → повтор возвращает сохранённый результат.
5. N+2 ждёт N+1; конфликт hash и старая версия не меняют состояние; PROCESSING_RESULT не зацикливается.
6. Upgrade/rollback на тестовом Oracle, существующие outbox/регуляторные тесты без регресса; slow-SQL review.
7. Изменение адреса/артикула, ревизия/отмена заказа и четыре ERP-события имеют XML contract tests; причинность проверяется по part/leg/version. INTERNAL_MOVEMENT_PLANNED допускается до сборки в PLAN; ORDER_IN_TRANSIT только после DEPARTED, а не LOADED; delivery — по магазинной приёмке.

Не включать: scheduler, экран диспетчера консолидации, полный адаптер действующей WMS.

## A2. Универсальный HU и атомарные преобразования

Зависимости: A1; согласованы Q04/Q09, маппинг единиц, партий, срока и тары.

Разработка архитектуры:

- Реестр HU, content, внешний SSCC/внутренний ID и nullable mapping к legacy pallet.
- Активная вложенность, журнал операций и происхождения; контроль одного parent/циклов.
- API команд aggregate, seam-split, repack как транзакции с version/lock, без привязки к регуляторному batch.
- Staging группы связанных snapshots: parent/output не становится доступным до полного согласования.
- Баланс строк заказа/части/SKU/партии/UoM, net/gross mass и утверждённые допуски.
- Read model «верхние HU» для capacity/сканера и поиск истории исходного SSCC.
- Extension seam для CRPT и legacy, без переписывания регуляторного lifecycle.

Законченный результат: через sandbox API два HU одного магазина объединяются, разбираются по прежним границам и перераскладываются в новые HU; каждый исходный состав прослеживается.

Приёмка A2:

1. Aggregate 2→1 → seam-split 1→2 восстанавливает исходные единицы.
2. Repack 2→3 с частями заказных строк сохраняет количества/партии; parent и child не дают двойную вместимость.
3. Цикл, два parent, чужой магазин, несовместимая температура, duplicate SSCC и изменение loaded HU отклоняются.
4. Сбой между событием и snapshots не создаёт доступного неполного HU.
5. Конкурирующие repack одной единицы: один результат, второй conflict/retry без потери.
6. Legacy UID остаётся допустимым в обычной WMS, NIKORA требует валидный SSCC.
7. Oracle balance queries, история, regression CRPT/picking; slow-SQL review.

Не включать: финальные терминальные экраны, график ворот, реальная работа склада без WMS. Это F2–F4.

## A2.Q. Доказательства контроля и пригодность HU к отгрузке

Зависимости: A1/A2. Переиспользовать задания, resource session, lot-check и scan journal, добавляя только отсутствующее: QualitySession, два независимых ScanPass, scan facts, InspectionResult, WeightMeasurement и решение по HU+contentVersion+policyVersion. Детали: [[requirements/nikora_ui_quality_tz]]. Это логическая модель, не обязательное количество таблиц.

Законченный результат: API сессия проходит два независимых пересчёта, осмотр и тестовое измерение; несовпадение блокирует отгрузку, изменение состава инвалидирует прежний PASS. Устройство весов и продуктовые экраны — F2.4/F2.5. Приёмка: Q-01…10, права второго оператора, scanId/idempotency, конкуренция/rollback, Oracle verify, slow-SQL review. Без нового stock ledger.

## A3. Многоплечевая перевозка и версионируемая волна

Зависимости: A1/A2; Q06/Q07, физические объекты и модель доступности ворот.

Разработка архитектуры:

- Trip roles, stopFrom/To, CargoAssignment и состояния по плечу, связь с существующим TRANSPORT_TASK.
- OutboundWave/scheduleVersion/freeze, immutable snapshot и отношения к локальным PICK_WAVE.
- Единый command handler calculate/confirm/release/change/exception, доступный ручному и будущему автоматическому режиму.
- Resource booking на основе RESOURCE_ASSIGNMENT: поддержать ворота/линии, интервалы, capacity и конкурентный lock. Если person/session lifecycle нельзя безопасно расширить — узкая связанная таблица facility booking с письменным ADR, не полный новый ресурсный модуль.
- Vehicle compartments/нормативы/правила упаковки как справочники и расширения существующей модели.
- Общий deterministic hard-validator: груз по каждому участку/секции, hard windows, температура, геометрия, stackability и loaded state.
- Idempotent apply и общая транзакция назначения; исправление найденной неатомарности/повторного создания в переиспользуемом пути.
- Совместимые views/API состава рейса; TRANSTASK_ID legacy остаётся нетронутым для старых сценариев, PAY_ORDER_ID guard сохраняется.
- Унифицированный operational event/receipt/exception contract для F4/F6; trace query API. LOADED и DEPARTED раздельны; контроль применимой HU version включён в серверный gate погрузки/release.
- Read models рабочих очередей по site/shift/resource, queueVersion/optimistic reorder, атомарный claim существующего WAREHOUSE_TASK. Назначение/старт/груз на технике/завершение — разные состояния; перенос груза только с подтверждением custody. Не создавать второй движок задач для диспетчера ричтраков.

Законченный результат: один HU планируется на шаттл и основной рейс, последовательно исполняет два плеча; исходящий release фиксирует версию; legacy рейс и биллинг продолжают работать.

Приёмка A3:

1. Два плеча не перетирают историю; ошибочная одновременная погрузка блокируется.
2. Повтор apply возвращает те же IDs; ошибка на второй операции не оставляет частично применённую команду.
3. RELEASED защищён от обычного изменения; logged exception не переписывает исходный snapshot.
4. Два планировщика не занимают одно место/ворота сверх capacity; проверка внутри lock, не только предварительный SELECT.
5. Ручная и автоматическая тестовые команды получают одинаковый отказ на overweight/температуру/неизвестную геометрию.
6. Старая WMS wave→warehouse task→sync и billed-защита проходят регресс.
7. Upgrade с реальными legacy fixtures и clean install, rollback; Oracle verify и slow-SQL review.

Не включать: алгоритм оптимизации/календарь/операторский продуктовый экран. Это F3/F5; интерфейс диспетчера ричтраков — F2.7.

## Общий Definition of Done архитектуры

- Исполняемый код + миграция/индексы + контракт + unit/contract/concurrency tests, а не только схема.
- Миграция имеет apply/verify/rollback, зеркало wiki/database и протокол live Oracle на изолированном стенде.
- Не теряются legacy identifiers, stock ledger, права, CRPT/Mercury и billing.
- Роли, payload access, audit, idempotency и error codes проверены отрицательными тестами.
- Feature flag по site/source выключает новые команды; rollback не удаляет физические факты.
- Артефакты: Git SHA, версии схем, fixtures, test JSON/HTML, Oracle assertions, slow SQL до/после и решения.
- Обновлены wiki/index и wiki/log; encoding и diff check пройдены.

## SQL и эксплуатационные gates

Измерения выполнять на узком пилотном окне и затем на пиковом профиле, а не на случайной полной базе.

| Путь | Предлагаемая мера / основание | Ответственный |
|---|---|---|
| Inbox, версии и retry | Уникальные ключи message/entity-version; индекс status+next_retry; bounded claim с блокировкой; проверить план и contention | Backend + DBA, A1 |
| Состав/история HU | Индексы SSCC, active parent/child, order-line, event time; set-based traversal с ограничением глубины; избегать N+1 | Backend + DBA, A2 |
| Готовность wave и manifest | Ограничить site/serviceDate/status, считать set-based; cache только с version invalidation | Backend + DBA, A3/F2 |
| Бронирования | Индекс resourceId/time/status; проверка пересечений в блокировке; стресс двух диспетчеров | Backend + DBA, A3 |
| Транспортная матрица | Переиспользовать cache; bounded нужные пары; не full N² rebuild при каждом plan | Backend, F5 |
| Trace/OTIF/cost | Индексы корреляции и окна дат, пагинация; отдельные read models только после измеренного узкого места | Backend + DBA, F6/F7 |

Это решения для проектирования, не заявление о применённых индексах. После каждого значимого live gate: RRL_SQL_SLOW_LOG, /api/admin/slow-sql, Oracle top SQL, local audit. Запрос >1000 мс или частый >500 мс получает решение rewrite/window/batch/cache/index/stats/backlog с владельцем. Не считать offline-probe доказательством SQL-производительности.
