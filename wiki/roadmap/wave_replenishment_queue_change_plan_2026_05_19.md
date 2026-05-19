# Стратегический И Тактический Файл Изменений: Очередь Пополнений Волны

Статус: актуальный change plan после принятия модели same-SKU очереди и dynamic/generic pick-face релиза.

Дата: 2026-05-19.

Связанные документы:

- [Пополнение ячеек отбора под покоробочную комплектацию волны](../requirements/wave_case_pick_replenishment_tz.md)
- [Пользовательские сценарии проверки волны](../requirements/wave_user_scenarios_functional_tz.md)
- [Складские задания для водителей ричтраков](../requirements/warehouse_tasks_reachtruck_tz.md)
- [Доменная синхронизация складских заданий](../requirements/warehouse_task_domain_sync_tz.md)
- [API Method Library](../concepts/api_method_library.md)

## 1. Принятое Решение

Если в рамках одной волны один SKU нужно спустить из нескольких мест хранения, система больше не схлопывает повторные пополнения в одну строку.

Принятая модель:

- создаются несколько доменных строк `RRL_PICK_WAVE_REPLENISH_TASK`;
- под каждую строку создается hard source reservation;
- в `RRL_WAREHOUSE_TASK` выпускаются только строки, которые реально можно дать водителю сейчас;
- fixed pick-face выпускает одну конфликтующую задачу за раз;
- остальные строки ждут в `QUEUED`, `WAIT_MINIMAX` или `WAIT_FREE_CELL`;
- если есть свободная неприкрепленная dynamic/generic ячейка отбора, часть queued-строк сразу выпускается туда водителю.

## 2. Стратегическая Цель

Сделать волну единственным управляющим документом физического исполнения комплектации.

Целевое состояние:

- волна управляет full-pallet staging, case-pick replenishment и будущей отгрузочной готовностью;
- `RRL_WAREHOUSE_TASK` остается единой очередью физической работы водителей;
- `RRL_PICK_WAVE_REPLENISH_TASK` остается доменным расчетом и очередью пополнения;
- hard reservations защищают source pallets от двойного назначения еще до выпуска задачи водителю;
- fixed pick-face защищена от коллизий;
- dynamic/generic pick-face используется как расширение емкости отбора, если склад реально имеет свободное место;
- доменная синхронизация закрывает бизнес-шаг только после водительского факта.

## 3. Тактические Изменения Уже Выполнены

### 3.1. База Данных

Добавлена миграция:

```text
db/migrations/2026-05-17_feed_factory_traceability/032_apply.sql
db/migrations/2026-05-17_feed_factory_traceability/032_verify.sql
db/migrations/2026-05-17_feed_factory_traceability/032_rollback.sql
```

Миграция расширяет `RRL_PICK_WAVE_REPLENISH_TASK.STATUS`:

- `QUEUED`;
- `WAIT_FREE_CELL`.

Live Oracle apply/verify:

```text
032_apply.sql  -> Statements=3; Errors=0
032_verify.sql -> Statements=3; Errors=0
```

### 3.2. Backend

Изменен `api/wms_api_server/app/services/picking_service.py`:

- `_refresh_replenishment_deficit` больше не отменяет повторные same-SKU строки как дубли;
- повторные строки переводятся в `QUEUED`;
- `_reserve_replenishment_sources` создает hard source reservations не только для `RELEASED`, но и для `QUEUED`, `WAIT_FREE_CELL`, `WAIT_MINIMAX`;
- `_sync_replenishment_warehouse_tasks` создает водительские задачи только для `RELEASED`, `ASSIGNED`, `IN_PROGRESS`;
- `_release_next_replenishment_queue` выпускает:
  - dynamic/generic queued rows в свободные неприкрепленные ячейки;
  - fixed Minimax rows по одной строке, если достигнут порог;
- wave launch выпускает immediate fixed-строку и dynamic/generic строки, но не выпускает Minimax до триггера.

Изменен `api/wms_api_server/app/services/warehouse_task_domain_sync_service.py`:

- после закрытия `WAVE / REPLENISHMENT / PICK_WAVE` запускается проверка следующей queued/Minimax строки.

### 3.3. Тесты

Расширен `tests/load/wave/wave_replenishment_load_test.py`:

- тест допускает доменные queued rows без `warehouse_task_id`;
- проверяет, что `source_reservations == wave_replenishment_tasks`;
- добавлен параметр `--dynamic-pick-faces N`;
- добавлена проверка, что dynamic/generic ячейки реально получают водительские задачи.

Проверенные сценарии:

```text
python tests/load/wave/wave_replenishment_load_test.py --waves 1 --orders-per-wave 10 --concurrency 1 --replenishment-method IMMEDIATE --execute-tasks --cleanup --report tests/load/wave/user_scenario_replenishment_queue_after_change_report.json
```

Результат:

- `10` доменных строк;
- `10` hard source reservations;
- `1` driver-facing warehouse task;
- `9` queued rows;
- duplicate warehouse tasks `0`;
- invalid objects `0`.

```text
python tests/load/wave/wave_replenishment_load_test.py --waves 1 --orders-per-wave 3 --concurrency 1 --replenishment-method MINIMAX --auto-minimax-trigger --execute-tasks --cleanup --report tests/load/wave/minimax_queue_regression_report.json
```

Результат:

- `3` доменные строки;
- `3` hard source reservations;
- первая задача выпущена после `CASE_PICK` факта;
- `2` queued rows;
- duplicate warehouse tasks `0`;
- invalid objects `0`.

```text
python tests/load/wave/wave_replenishment_load_test.py --waves 1 --orders-per-wave 10 --concurrency 1 --replenishment-method IMMEDIATE --dynamic-pick-faces 3 --cleanup --report tests/load/wave/dynamic_pick_face_queue_report.json
```

Результат:

- `10` доменных строк;
- `10` hard source reservations;
- `3` свободные dynamic pick-face ячейки;
- `4` driver-facing warehouse tasks сразу: `1` fixed + `3` dynamic;
- `6` queued rows;
- duplicate warehouse tasks `0`;
- invalid objects `0`.

```text
python tests/load/wave/wave_replenishment_load_test.py --waves 1 --orders-per-wave 10 --concurrency 1 --replenishment-method IMMEDIATE --drain-replenishment-queue --cleanup --report tests/load/wave/replenishment_queue_drain_report.json
```

Результат:

- `10` доменных строк;
- `10` hard source reservations;
- `10` warehouse replenishment tasks последовательно;
- `10` warehouse tasks `DONE`;
- `10` domain replenishment rows `DONE`;
- `10` sync rows `SYNCED`;
- `10` source reservations `CONSUMED`;
- active source reservations `0`;
- duplicate warehouse tasks `0`;
- invalid objects `0`.

## 4. Тактический План Следующих Изменений

### Завершено. Перенести Очередь В UI Оператора

Цель: диспетчер должен видеть, почему строка не у водителя.

Выполнено:

- в `wave-replenishment.html/js` добавлен фильтр строк: все, у водителя, ожидают, `QUEUED`, `WAIT_FREE_CELL`, `WAIT_MINIMAX`, `RELEASED`, `DONE`, `FAILED`;
- добавлены KPI `Queued`, `Wait`, `Driver`, `Done`;
- таблица пополнений показывает queue state, source pallet/cell, target cell, source reservation, warehouse task status и причину ожидания;
- строка с hard source reservation, но без warehouse task, отображается как ожидающая доменная строка, а не как ошибка;
- кнопка `Minimax` продолжает выполнять ручной queue/minimax check.

Проверка:

```text
node --check wiki-raw/wms_admin_ui_reference/wave-replenishment.js
```

Результат: JavaScript syntax check passed.

### Завершено. Усилить Dynamic Pick-Face Модель

Цель: сделать dynamic/generic ячейки полноценной операционной емкостью.

Выполнено:

- добавлена миграция `033` с таблицей `RRL_PICK_FACE_ASSIGNMENT`;
- dynamic/generic queue release создает активное назначение `cell -> wave/articul/replenishment_task`;
- уникальный active-cell индекс защищает dynamic ячейку от двойного назначения;
- fixed immediate release больше не выпускает вторую fixed-строку до создания/закрытия предыдущей active domain row;
- cancel/release reservations освобождает active assignments.

Проверка:

```text
python tests/load/wave/wave_replenishment_load_test.py --waves 1 --orders-per-wave 10 --concurrency 1 --replenishment-method IMMEDIATE --dynamic-pick-faces 3 --cleanup --report tests/load/wave/dynamic_pick_face_assignment_report.json
```

Результат:

- `3` dynamic warehouse tasks;
- `3` active dynamic assignments;
- `4` total warehouse tasks: `1` fixed + `3` dynamic;
- duplicate warehouse tasks `0`;
- invalid objects `0`.

Регрессия fixed drain после изменения:

```text
python tests/load/wave/wave_replenishment_load_test.py --waves 1 --orders-per-wave 10 --concurrency 1 --replenishment-method IMMEDIATE --drain-replenishment-queue --cleanup --report tests/load/wave/replenishment_queue_drain_report.json
```

Результат:

- `10` domain rows `DONE`;
- `10` warehouse tasks `DONE`;
- `10` sync rows `SYNCED`;
- `10` source reservations `CONSUMED`;
- active source reservations `0`;
- duplicate warehouse tasks `0`;
- invalid objects `0`.

### Шаг 1. Связать Пополнение С Готовностью Отгрузки

Цель: фура не должна закрываться, пока queued/waiting replenishment блокирует case-pick.

Статус: runtime API готов как `GET /api/picking/waves/{pick_wave_id}/readiness`; shipment/fura API остается следующим внешним слоем поверх волны.

Работы:

- readiness-проверка волны добавлена;
- учитываются открытые `REPLENISHMENT`, `FULL_PALLET` / `PICKING_MOVE`, `CASE_PICK`, неуспешный `RRL_WAREHOUSE_TASK_SYNC` и shortage;
- `QUEUED`, `WAIT_FREE_CELL`, `WAIT_MINIMAX`, `RELEASED`, `ASSIGNED`, `IN_PROGRESS`, `FAILED` блокируют готовность как незакрытое пополнение;
- отличать блокирующее пополнение от необязательного overflow в будущей модели overflow;
- подготовить будущий shipment readiness API.

Критерий приемки:

- wave readiness показывает, что мешает закрытию;
- незакрытые critical replenishment rows блокируют dispatch/readiness;
- full-pallet staging и case-pick readiness видны вместе;
- нагрузочный drain-сценарий проверяет, что после закрытия очереди нет replenishment и sync blockers.

### Шаг 2. Нагрузочный Пакет Multi-Wave

Цель: проверить очередь не только на одной волне, а на параллельных волнах и пересекающихся source pallets.

Статус: базовый multi-wave drain выполнен; тестовый fixture теперь создает изолированный SKU и source pallets в разных ячейках.

Работы:

- drain-тест расширен на `--waves 2+`;
- добавлена диагностика `source_reservation_duplicates`;
- hard source reservation теперь выдается в сериализованном участке, чтобы параллельные волны не выбрали один source pallet одновременно;
- source selection учитывает `CONSUMED` hard reservations до полноценного stock bridge;
- проверить, что dynamic cells не назначаются двум волнам одновременно после появления временного assignment.

Критерий приемки:

- нет двойного hard reservation;
- нет дублей `RRL_WAREHOUSE_TASK`;
- все выполненные задачи доходят до `SYNCED`.

## 5. Стратегический План Дальше

### Этап 1. Операционная Надежность Волны

Фокус:

- очереди пополнения;
- idempotent release;
- последовательное закрытие driver tasks;
- clear sync status;
- load tests по коллизиям.

Результат:

- волну можно запускать под реальную складскую нагрузку без двойного назначения паллет и без дублей задач.

### Этап 2. Рабочее Место Диспетчера

Фокус:

- operator UI для волн;
- статусы пополнения и staging;
- причины ожидания;
- ручной retry/check;
- мониторинг `RRL_WAREHOUSE_TASK_SYNC`.

Результат:

- диспетчер может управлять волной без SQL и без ручной диагностики в базе.

### Этап 3. ТСД Водителя

Фокус:

- компактный экран для reachtruck;
- scan-first flow;
- полный паллет и коробочное количество;
- partial box completion;
- запрет partial pallet;
- понятные ошибки неправильного паллета/ячейки.

Результат:

- функциональные и нагрузочные тесты можно проводить через тот же UX, который будет у водителя.

### Этап 4. Shipment/Fura Readiness

Фокус:

- shipment как контекст волны, а не источник ричтрак-задачи;
- готовность грузовой зоны;
- запрет dispatch при незавершенных wave tasks;
- будущая связка с Mercury/CRPT readiness.

Результат:

- отгрузка закрывается только после физической готовности волны.

## 6. Риски И Контроль

Риск: source reservations для queued rows могут держать паллеты слишком долго.

Контроль:

- таймауты/операторская отмена;
- release reservations при отмене волны;
- отчет активных queued reservations.

Риск: dynamic/generic ячейка может стать временно приколоченной к SKU, но это не отражено явно.

Контроль:

- следующий инкремент должен добавить явное временное назначение dynamic cell.

Риск: Minimax и dynamic release могут конфликтовать по емкости.

Контроль:

- добавить расчет емкости и negative tests на занятую/переполненную dynamic ячейку.

## 7. Definition Of Done Для Ближайшего Пакета

Пакет считается завершенным, когда:

- есть полный drain-тест очереди до закрытия всех `10` строк;
- UI показывает queued/wait statuses и причины;
- dynamic/generic ячейки имеют явную временную привязку;
- readiness волны учитывает незакрытые replenishment/staging/case-pick задачи, sync blockers и shortage;
- `scripts/check-encoding.ps1`, `git diff --check`, Oracle invalid objects и load tests проходят.

## 8. Runtime Checkpoint 2026-05-19

Реализовано:

- `GET /api/picking/waves/{pick_wave_id}/readiness`;
- readiness summary и blockers для replenishment, full-pallet staging, case-pick, domain sync и shortage;
- проверка readiness в `tests/load/wave/wave_replenishment_load_test.py`.

Проверено:

- `python tests\load\wave\wave_replenishment_load_test.py --waves 1 --orders-per-wave 10 --concurrency 1 --replenishment-method IMMEDIATE --drain-replenishment-queue --cleanup --report tests/load/wave/replenishment_queue_readiness_report.json`
- результат: `10` replenishment domain rows, `10` warehouse tasks `DONE`, `10` sync rows `SYNCED`, `0` duplicate warehouse tasks, `0` invalid Oracle objects, после drain `open_replenishment_count = 0` и `sync_error_count = 0`.

Multi-wave:

- `python tests\load\wave\wave_replenishment_load_test.py --waves 2 --orders-per-wave 10 --concurrency 2 --replenishment-method IMMEDIATE --drain-replenishment-queue --cleanup --report tests/load/wave/replenishment_queue_multi_wave_report.json`
- результат: `2` launched waves, `18` replenishment domain rows, `18` hard source reservations, `18` warehouse tasks `DONE`, `18` sync rows `SYNCED`, `source_reservation_duplicates = 0`, duplicate warehouse tasks `0`, invalid Oracle objects `0`.
