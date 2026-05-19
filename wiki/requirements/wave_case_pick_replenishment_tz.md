# ТЗ: пополнение ячеек отбора под покоробочную комплектацию волны

Статус: реализован runtime-инкремент для `IMMEDIATE`, `WAIT_MINIMAX`, ручного/API Minimax-релиза, выбора паллеты-источника, hard reservation, последовательной выдачи водительских задач и автоматического Minimax-триггера после факта `CASE_PICK`.

Дата: 2026-05-18.

Связанные документы:

- [Сборка по волнам / Wave Picking](wave_picking_tz.md)
- [Складские задания для водителей ричтраков](warehouse_tasks_reachtruck_tz.md)
- [Доменная синхронизация складских заданий](warehouse_task_domain_sync_tz.md)

## 1. Архитектурное Правило

Единственный управляющий документ для комплектации - волна.

Волна может быть создана:

- по заказам на отгрузку;
- по производственным заказам;
- вручную оператором;
- автоматически по окну, маршруту или производственному плану.

Но для физического исполнения источник остается один:

```text
TASK_SOURCE = WAVE
SOURCE_DOC_TYPE = PICK_WAVE
SOURCE_DOC_ID = RRL_PICK_WAVE.PICK_WAVE_ID
```

Заказы на отгрузку, производственные заказы, маршруты и грузовые зоны являются контекстом волны, а не отдельными владельцами задач ричтрака.

## 2. Назначение

Пополнение ячеек отбора нужно для покоробочной комплектации.

Система должна видеть, что по некоторым артикулам в pick face не хватает свободного остатка для волны, и создавать доменные задачи пополнения под волну.

Физическое исполнение пополнения выполняется через `RRL_WAREHOUSE_TASK`, потому что для водителя ричтрака это обычное перемещение:

```text
ячейка хранения -> ячейка отбора
```

## 3. Бизнес-Сценарий

1. Волна рассчитана или запускается.
2. Система агрегирует покоробочную потребность по артикулам.
3. Для каждого артикула система проверяет свободный остаток в ячейках отбора.
4. Если свободного остатка не хватает, создается доменная строка пополнения волны.
5. В зависимости от стратегии артикула:
   - задача сразу передается водителю;
   - или ждет Minimax-триггера.
6. Когда задача передана водителю, создается или активируется `RRL_WAREHOUSE_TASK`.
7. Водитель выполняет перемещение на ТСД.
8. Handler закрывает доменную строку пополнения волны.
9. После обязательных пополнений волна может продолжить покоробочный отбор.

## 4. Типы Пополнения

### 4.1. Immediate / При Первой Потребности

Артикул пополняется при первом возникновении потребности в волне.

Правило:

- как только расчет волны показал дефицит pick face, система создает задачу пополнения;
- задача сразу доступна водителю;
- количество пополнения рассчитывается до полного набивания ячейки отбора по объему, если доступный паллет и емкость ячейки это позволяют.

### 4.2. Minimax

Артикул находится на способе пополнения `MINIMAX`.

Правило:

- доменная потребность пополнения создается при расчете волны;
- водительская задача не передается сразу;
- задача становится доступна водителю только когда фактически отобранный остаток в ячейке отбора становится меньше заданного порога.

Пример:

```text
Порог: 1 слой.
Если фактический свободный остаток в pick face <= 1 слой, задача пополнения выпускается водителю.
```

## 5. Количество Пополнения

Пополнение в pick face может идти:

- полным паллетом;
- полупаллетом;
- объемом, который добивает ячейку отбора до полной емкости в кубометрах.

Расчет должен учитывать:

- текущий свободный остаток в pick face;
- максимальную емкость pick face в кубометрах;
- объем одной коробки или упаковки артикула;
- количество коробок в слое;
- количество коробок на паллете;
- доступный остаток на паллете-источнике;
- допустимость частичного паллета для артикула.

## 6. Настройки Артикула / Pick Face

Настройки хранятся на уровне артикула в pick face, потому что разные SKU в одной зоне отбора могут пополняться по разным правилам.

Реализованные поля `RRL_PICK_FACE_ARTICUL` в миграции `2026-05-17-029-wave-case-pick-replenishment-settings`:

- `REPLENISHMENT_METHOD`: `IMMEDIATE`, `MINIMAX`;
- `REPLENISHMENT_QTY_MODE`: `FULL_PALLET`, `HALF_PALLET`, `FILL_TO_VOLUME`;
- `MIN_TRIGGER_BOX_QTY`;
- `MIN_TRIGGER_LAYER_QTY`;
- `BOXES_PER_LAYER`;
- `BOXES_PER_PALLET`;
- `BOX_VOLUME_M3`;
- `ALLOW_PARTIAL_PALLET`;

Емкость ячейки по объему берется из уже существующего `RRL_PICK_FACE.MAX_VOLUME`; отдельное поле `PICK_FACE_MAX_VOLUME_M3` не заводится, чтобы не дублировать топологию.

## 7. Доменные Строки Пополнения

Доменная строка пополнения волны хранится в `RRL_PICK_WAVE_REPLENISH_TASK`.

Реализованные статусы:

- `NEW` - рассчитано и готово к передаче водителю;
- `QUEUED` - строка пополнения имеет потребность и источник, но ждет своей очереди, чтобы не выпустить несколько конфликтующих задач в одну fixed pick-face ячейку;
- `WAIT_FREE_CELL` - строка ждет свободную dynamic/generic ячейку отбора, если fixed pick face уже занята и Minimax еще не дает окно;
- `WAIT_MINIMAX` - потребность рассчитана, но водительская задача ждет порога;
- `RELEASED` - задача передана в `RRL_WAREHOUSE_TASK`;
- `ASSIGNED`;
- `IN_PROGRESS`;
- `DONE`;
- `CANCELLED`;
- `FAILED`.

Для `MINIMAX` доменная строка может существовать без активной `RRL_WAREHOUSE_TASK`.

Когда порог достигнут, система создает или активирует warehouse task.

Инвариант source reservation:

- `HARD` reservation может создаваться заранее для доменной строки пополнения, чтобы удержать конкретный паллет/источник под волну.
- Предварительный `HARD` reservation не означает, что паллет физически спускается в pick face сразу.
- Водительская `RRL_WAREHOUSE_TASK` выпускается только когда строка реально получает право на физическое исполнение: первая строка очереди, свободная dynamic/generic ячейка или достигнутый Minimax-порог.
- Перед выпуском водительской задачи WMS проверяет физический объем pick face: `текущий остаток ячейки * BOX_VOLUME_M3 + QTY строки * BOX_VOLUME_M3 <= PICK_FACE_MAX_VOLUME`. Если объем не помещается, строка остается в `QUEUED` или `WAIT_MINIMAX` с причиной ожидания физической емкости.
- Для одной доменной строки действует связка `1 replenishment row -> 1 source reservation -> 1 warehouse task`.
- Две активные `HARD` reservations на один и тот же source pallet/source cell недопустимы.
- Строка `CANCELLED` из-за достаточного свободного остатка pick face не должна держать `SOURCE_RESERVATION_ID`, если водительская задача по ней еще не выпускалась.

Миграция `029` добавляет в `RRL_PICK_WAVE_REPLENISH_TASK` снимок настроек, примененных на запуске волны:

- `REPLENISHMENT_METHOD`;
- `REPLENISHMENT_QTY_MODE`;
- `RELEASE_TRIGGER_QTY`;
- `BOXES_PER_LAYER`;
- `BOXES_PER_PALLET`;
- `BOX_VOLUME_M3`;
- `PICK_FACE_MAX_VOLUME`;
- `WAIT_REASON`;
- `RELEASED_AT`, `RELEASED_BY`.

Backend `launch_wave` после вызова `RRL_PICK_WAVE_API.launch_wave` обогащает строки пополнения этими настройками. Затем он пересчитывает свободный остаток pick face:

```text
free_qty = RRL_REMAINS by target cell/articul - active HARD RRL_STOCK_RESERVATION
deficit_qty = max(wave_case_demand - free_qty, 0)
```

Если дефицита нет, строка пополнения отменяется с причиной `Pick-face has enough free stock for wave demand`.

Если дефицит есть:

- `IMMEDIATE` переводится в `RELEASED` и создает водительскую `RRL_WAREHOUSE_TASK`;
- `MINIMAX` переводится в `WAIT_MINIMAX`, и `_sync_replenishment_warehouse_tasks` не создает по ней водительскую задачу до релиза.

### 7.1. Очередь Пополнений Одного SKU

Если в рамках одной волны один SKU нужно спустить из нескольких мест хранения, система должна создавать несколько доменных строк пополнения и несколько жестких source reservations, но не должна одновременно отдавать водителю все конфликтующие задания в одну fixed pick-face ячейку.

Правило для fixed pick face:

1. Создаются доменные строки `RRL_PICK_WAVE_REPLENISH_TASK` под каждый физический спуск паллета или части паллета.
2. Для каждой строки заранее подбирается источник и создается `HARD` reservation на source pallet. Это резерв источника, а не разрешение одновременно спускать все паллеты.
3. В `RRL_WAREHOUSE_TASK` выпускается только первая исполнимая строка.
4. Остальные строки получают `QUEUED` или `WAIT_MINIMAX`.
5. Следующая строка выпускается только когда нет активной водительской задачи по той же группе `PICK_WAVE_ID + ARTICUL + TARGET_CELL_CODE` и выполняется одно из условий:
   - fixed pick face освободилась или ушла ниже Minimax-порога;
   - оператор вручную запустил проверку Minimax/очереди;
   - предыдущая ричтрак-задача закрыта и доменная синхронизация подтвердила `DONE/SYNCED`.

Правило для dynamic/generic pick face:

- если на складе есть активная ячейка отбора, которой не назначен жестко приколоченный SKU, и она свободна по остатку, hard reservations и активным warehouse tasks, то система должна сразу выпускать следующую ричтрак-задачу на спуск в эту свободную ячейку;
- в этом случае задача не ждет Minimax fixed-ячейки, потому что свободное место уже существует;
- система может спустить только ту часть поддонов/коробок, которая понадобится волне и помещается в свободную ячейку по объему;
- если свободная dynamic/generic ячейка исчезла до релиза задачи, строка остается `WAIT_FREE_CELL` до следующей проверки.

Таким образом, очередь защищает fixed pick face от коллизий, но не блокирует склад, когда есть свободная неприкрепленная ячейка отбора.

## 8. Warehouse Task

Водительская задача создается так:

```text
TASK_TYPE = REPLENISHMENT
TASK_SOURCE = WAVE
SOURCE_DOC_TYPE = PICK_WAVE
SOURCE_DOC_ID = PICK_WAVE_ID
SOURCE_TASK_ID = PICK_WAVE_REPLENISH_TASK_ID
FROM_CELL = ячейка хранения
TO_CELL = pick face
QTY_MODE = PALLET или BOX
```

Правила:

- полный паллет: `QTY_MODE = PALLET`;
- полупаллет или добивка до объема: `QTY_MODE = BOX`;
- частичное выполнение `BOX` создает residual warehouse task;
- доменная строка пополнения становится `DONE` только когда активных residual task больше нет.

## 9. Алгоритм Расчета

Для каждого артикула покоробочной потребности волны:

1. Найти pick face артикула.
2. Рассчитать потребность волны в коробках.
3. Рассчитать свободный остаток в pick face.
4. Рассчитать дефицит:

```text
deficit_qty = max(wave_case_demand - free_pick_face_qty, 0)
```

5. Если дефицита нет - задачу не создавать.
6. Если стратегия `IMMEDIATE`:
   - рассчитать количество пополнения;
   - выбрать паллет-источник;
   - создать `RRL_PICK_WAVE_REPLENISH_TASK`;
   - создать `RRL_WAREHOUSE_TASK`.
7. Если стратегия `MINIMAX`:
   - создать `RRL_PICK_WAVE_REPLENISH_TASK` со статусом `WAIT_MINIMAX`;
   - не передавать задачу водителю до достижения порога.

## 10. Алгоритм Minimax-Триггера

Minimax-триггер вызывается:

- после каждого подтвержденного отбора из pick face через `POST /api/picking/waves/{wave_id}/tasks/{pick_task_id}/complete`;
- при пересчете волны;
- по расписанию;
- вручную оператором.

Проверка:

```text
current_pick_face_qty <= trigger_qty
```

Если условие выполнено:

1. Проверить, что нет уже активной warehouse task по той же доменной строке.
2. Проверить, что волна не отменена.
3. Выбрать свободный паллет-источник.
4. Рассчитать количество пополнения.
5. Создать `RRL_WAREHOUSE_TASK`.
6. Перевести `RRL_PICK_WAVE_REPLENISH_TASK.STATUS = RELEASED`.

Реализованный API-факт отбора:

```text
POST /api/picking/waves/{pick_wave_id}/tasks/{pick_task_id}/complete
```

Фиксирует `FACT_QTY`, `DONE_AT`, `DONE_BY` на `RRL_PICK_TASK` и `RRL_PICK_WAVE_TASK`, закрывает связанные hard reservations как `CONSUMED`, затем запускает тот же Minimax-релиз, что и ручной supervisor check.

Поле `adjust_pick_face_stock = true` используется для отладочного/load-сценария, когда тест сам моделирует снижение остатка pick face в `RRL_REMAINS`. В промышленном сценарии физический остаток должен приходить из штатного WMS-факта/legacy bridge, а API-факт только запускает проверку.

## 11. Расчет Количества

### FULL_PALLET

```text
replenish_qty = boxes_per_pallet
QTY_MODE = PALLET
```

Используется, если:

- ячейка отбора может принять целый паллет;
- паллет-источник полный;
- артикул настроен на полнопалетное пополнение.

### HALF_PALLET

```text
replenish_qty = boxes_per_pallet / 2
QTY_MODE = BOX
```

Используется, если:

- ячейка не должна получать полный паллет;
- артикулам разрешено частичное пополнение;
- источник допускает частичный отбор.

### FILL_TO_VOLUME

```text
free_volume_m3 = pick_face_max_volume_m3 - current_pick_face_volume_m3
fit_boxes = floor(free_volume_m3 / box_volume_m3)
replenish_qty = min(fit_boxes, available_source_qty)
QTY_MODE = BOX
```

Используется, если нужно добить ячейку отбора до полной емкости.

## 12. Выбор Паллеты-Источника

Паллет-источник должен быть:

- свободным от активных жестких резервов;
- доступным в зоне хранения;
- подходящим по артикулу;
- подходящим по партии и сроку годности;
- разрешенным для отгрузки;
- не заблокированным качеством, вылежкой или маркировкой;
- не назначенным в другую активную warehouse task.

Сортировка кандидатов:

1. FEFO/FIFO.
2. Ближайшая складская зона.
3. Полнота паллета под выбранный режим.
4. Меньшее количество дробления паллета.

Текущий runtime-алгоритм выбирает источник из `RRL_REMAINS` / `RRL_PALLETS`:

- артикул должен совпадать с артикулом строки пополнения;
- ячейка-источник не должна совпадать с pick face;
- доступное количество = `RRL_REMAINS.REMAIN` минус активные hard `RRL_STOCK_RESERVATION` и минус активные `RRL_WAREHOUSE_TASK` по паллету;
- кандидат должен пройти проверку срока годности, если она задана клиентами волны;
- сортировка идет по FEFO: ближайший `EXPIRY_DATE`, затем `PRODUCED_DATE`, ячейка, паллет.

## 12.1. Клиентский Остаточный Срок Годности

Для части клиентов нужен более свежий товар.

Правило:

- для каждого клиента волны берется настройка `MIN_SHELF_LIFE_PERCENT` / `MIN_SHELF_LIFE_DAYS` из `RRL_CUSTOMER_PRODUCT_RULE`;
- если специального правила по артикулу нет, используется `RRL_CUSTOMER.DEFAULT_MIN_SHELF_LIFE_PERCENT` / `DEFAULT_MIN_SHELF_LIFE_DAYS`;
- для строки пополнения берется самый строгий порог среди клиентов волны;
- если настройки нет, фильтр свежести не применяется и выбирается первый подходящий паллет по FEFO.

Пример:

```text
Клиент A требует 70% остаточного срока.
Клиент B требует 50%.
Волна содержит обоих клиентов.
Для пополнения выбирается паллет, проходящий 70%.
```

Проверка процента:

```text
remaining_percent =
  (expiry_date - today) / (expiry_date - produced_date) * 100
```

Если процентный порог задан, паллет без `PRODUCED_DATE` или `EXPIRY_DATE` не считается подходящим.

Runtime load-сценарий `--shelf-life-scenario` создает контролируемые source pallets:

- stale pallet с остаточным сроком меньше 50%;
- middle pallet около 60%;
- fresh pallet около 80%.

В волне создаются клиенты с требованиями 70%, 50% и без настройки. При такой смеси строка пополнения должна сохранить строгий порог 70% и выбрать только fresh pallet.

## 12.2. Hard Reservation Источника

После выбора источника создается `RRL_STOCK_RESERVATION`:

```text
RESERVATION_KIND = HARD
RESERVATION_DOMAIN = WAVE
SOURCE_DOC_TYPE = PICK_WAVE
SOURCE_DOC_ID = PICK_WAVE_ID
SOURCE_LINE_ID = PICK_WAVE_REPLENISH_TASK_ID
UID_PALLET = выбранный паллет
CELL = ячейка-источник
QTY = зарезервированное количество
```

`RRL_WAREHOUSE_TASK` создается только после успешного выбора источника и создания hard reservation.

При успешном закрытии пополнения доменная синхронизация переводит reservation в `CONSUMED`. При отмене волны или release reservations активные source reservations переводятся в `RELEASED`.

## 13. Пополнение И Грузовая Зона

В этой модели не существует самостоятельного `SHIPMENT` как источника задач ричтрака.

Спуск паллета в грузовую зону тоже является задачей волны:

```text
TASK_SOURCE = WAVE
TASK_TYPE = PICKING_MOVE
SOURCE_DOC_TYPE = PICK_WAVE
SOURCE_DOC_ID = PICK_WAVE_ID
TO_CELL = грузовая зона
```

Если нужно сохранить ссылку на заказ отгрузки или производственный заказ, она хранится в строках волны или связях волны, но не заменяет `SOURCE_DOC_TYPE = PICK_WAVE`.

## 14. Ошибки

Типовые ошибки:

- нет pick face для артикула;
- не задан объем коробки;
- не задана емкость pick face;
- нет свободного паллета-источника;
- паллет-источник уже зарезервирован другой волной;
- Minimax-триггер сработал, но волна уже отменена;
- водитель частично выполнил `BOX`, но остаток не создан;
- целевая ячейка не вмещает рассчитанный объем.

Ошибки расчета пишутся в shortage/protocol волны.

Ошибки исполнения пишутся в `RRL_WAREHOUSE_TASK_SYNC`.

## 15. API MVP

Минимальные endpoints:

- `POST /api/picking/waves/{wave_id}/calculate`
- `POST /api/picking/waves/{wave_id}/launch`
- `GET /api/picking/waves/{wave_id}/replenishment-tasks`
- `POST /api/picking/waves/{wave_id}/replenishment/minimax-check`
- `POST /api/warehouse-tasks/{task_id}/complete`
- `GET /api/warehouse-tasks/domain-sync`

## 15.1. Операторский UI

Raw admin page:

```text
wiki-raw/wms_admin_ui_reference/wave-replenishment.html
```

Назначение:

- просмотр волн;
- просмотр строк `RRL_PICK_WAVE_REPLENISH_TASK`;
- KPI по `WAIT_MINIMAX`, `RELEASED`, `DONE`, `FAILED`;
- ручной запуск `POST /api/picking/waves/{wave_id}/replenishment/minimax-check`;
- просмотр pick-face;
- редактирование настроек артикула в pick-face: метод, режим, пороги, коробки в слое/паллете, объем коробки, частичный паллет.

Права:

- `pick_wave_view` для страницы;
- `pick_wave_launch` для Minimax check;
- `pick_topology_edit` для изменения правил pick-face.

`POST /api/picking/waves/{wave_id}/replenishment/minimax-check` пересчитывает свободный остаток pick face и выпускает `WAIT_MINIMAX` строки, если:

```text
pick_face_free_qty <= release_trigger_qty
replenish_qty > 0
```

После релиза строка становится `RELEASED`, получает `RELEASED_AT/RELEASED_BY`, а backend создает соответствующую `RRL_WAREHOUSE_TASK`.

## 16. Критерии Приемки

Модуль готов, если:

- волна создает доменные строки пополнения для дефицитных pick face;
- `IMMEDIATE` задачи сразу попадают водителю;
- `MINIMAX` задачи ждут порога и передаются водителю только после фактического снижения остатка;
- полный паллет закрывается только как полный паллет;
- полупаллет и добивка по объему работают как `BOX`;
- частичное `BOX` выполнение создает residual task;
- доменная строка пополнения становится `DONE` только после закрытия всех residual tasks;
- нет дублей `RRL_WAREHOUSE_TASK` по одной доменной строке;
- волна остается единственным управляющим документом;
- ошибки видны в диспетчерской sync.

## 17. Текущие Runtime-Проверки

Проверено 2026-05-18:

- mixed dispatcher/domain-sync load после изменения: `5` sync rows, все `SYNCED`, `0` duplicate sync keys, `0` invalid Oracle objects;
- dedicated Minimax wave load:

```text
python tests/load/wave/wave_replenishment_load_test.py --waves 1 --orders-per-wave 1 --concurrency 1 --execute-tasks --replenishment-method MINIMAX --cleanup --report tests/load/wave/minimax_report.json
```

Результат: `1` волна, `1` строка пополнения, до `minimax-check` статус `WAIT_MINIMAX` без warehouse task, после check выбран источник, создан hard reservation и warehouse task, выполнение довело доменную строку и sync до `DONE/SYNCED`, invalid objects `0`.

Проверено 2026-05-19:

```text
python tests\load\wave\wave_replenishment_load_test.py --waves 1 --orders-per-wave 3 --concurrency 1 --replenishment-method MINIMAX --auto-minimax-trigger --execute-tasks --cleanup --report tests/load/wave/minimax_auto_trigger_report.json
```

Результат: `CASE_PICK` fact автоматически выпустил `WAIT_MINIMAX` строку без ручного `minimax-check`; `1` active replenishment row, `1` warehouse task, `1` sync row, все `DONE/SYNCED`, duplicate warehouse tasks `0`, invalid objects `0`, cleanup `0`.

Проверка клиентской свежести:

```text
python tests\load\wave\wave_replenishment_load_test.py --waves 1 --orders-per-wave 3 --concurrency 1 --replenishment-method IMMEDIATE --shelf-life-scenario --execute-tasks --cleanup --report tests/load/wave/shelf_life_report.json
```

Результат: `1` волна, `3` клиента с правилами 70%, 50% и без настройки; выбран fresh source pallet, сохранен строгий `MIN_SHELF_LIFE_PERCENT = 70`, `1` warehouse replenishment task, final sync `DONE/SYNCED`, duplicate warehouse tasks `0`, invalid objects `0`, cleanup `0`.
