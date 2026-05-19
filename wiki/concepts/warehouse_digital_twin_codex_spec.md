# Спецификация для Codex: цифровой двойник склада с визуализацией операций, коллизий и потерь производительности

## 0. Цель документа

Нужно реализовать страницу цифрового двойника склада, которая визуально показывает не просто складскую схему, а **живую смену**: движение комплектовщиков, работу ричтраков/RTP, пополнение pick-face, сборку клиентских паллет, очереди, коллизии, причины задержек и влияние на производительность.

Цель UI — чтобы оператор мог нажать `play`, посмотреть “мультик” смены и за несколько минут понять:

- где идет нормальная комплектация;
- какие комплектовщики опережают план, какие отстают, какие стоят;
- какие задачи RTP/ричтраков просрочены;
- где пустой pick-face, низкий остаток, блокировка маршрута или затор;
- какие маршруты/волны/паллеты не закрываются и почему;
- сколько производительности теряется из-за каждой причины.

Визуальный результат должен быть близок к концепту: **enterprise dashboard + изометрический цифровой двойник склада + световые статусы + боковые панели причин**.

---

## 1. Главный визуальный референс

Референс-картинка для реализации:

```text
warehouse_digital_twin_dashboard_interface.png
```

Если файл приложен в рабочий контекст Codex, использовать его как визуальный ориентир. Не нужно вставлять его как статичную картинку в UI. Нужно **реализовать интерфейс нативно**: HTML/CSS/React + WebGL/Canvas/SVG, чтобы данные, статусы, маршруты и коллизии были интерактивными и анимируемыми.

Ключевые признаки референса:

- светлый современный dashboard;
- top bar с названием, статусом online, фильтрами смены/волны/зоны и временем;
- верхняя строка KPI-карточек;
- слева панель задач пополнения/RTP;
- по центру большая изометрическая карта склада с аллеями, стеллажами, паллетами, комплектовщиками, ричтраками, маршрутами и hotspot-ами;
- справа лента “Коллизии и причины”;
- снизу timeline/playback;
- поверх сцены — читаемые бейджи ресурсов, проценты скорости, статусы, callout-ы причин и прогресс маршрутов.

---

## 2. Рекомендуемый технологический стек

### 2.1. Предпочтительный frontend-стек

```text
React
TypeScript
Vite
Zustand или Redux Toolkit
TanStack Query
Tailwind / CSS Modules / SCSS
```

Назначение:

- `React` — dashboard-компоненты, панели, карточки, фильтры, timeline, overlays.
- `TypeScript` — строгие типы для layout, events, metrics, collisions, resources.
- `Vite` — быстрая сборка и dev server.
- `Zustand` — состояние проигрывания, выбранные слои, текущая минута, выбранный ресурс.
- `TanStack Query` — загрузка `layout.json`, `events.jsonl`, `metrics-by-minute.csv`, `collision-report.csv`.
- `Tailwind/CSS Modules/SCSS` — точная стилизация dashboard-а.

### 2.2. Предпочтительный 3D/2.5D стек

```text
Three.js
React Three Fiber
@react-three/drei
Blender → glTF/GLB assets
Orthographic Camera
InstancedMesh
```

Назначение:

- `Three.js` — WebGL-сцена склада.
- `React Three Fiber` — декларативная 3D-сцена как React-компоненты.
- `Drei` — helpers: camera controls, HTML overlays, sprites, helpers.
- `Orthographic Camera` — изометрический вид, как в операционном control tower, а не game camera.
- `InstancedMesh` — производительный рендер тысяч одинаковых объектов: стеллажи, коробки, паллеты, pick-face ячейки, маркеры.
- `glTF/GLB` — ассеты ричтрака, паллеты, коробки, ворот, тележки.

### 2.3. Fallback, если в проекте нельзя добавить React/Three

Если текущий репозиторий не поддерживает сборку frontend-зависимостей, реализовать первую версию как статическую страницу:

```text
warehouse-simulation.html
warehouse-simulation.css
warehouse-simulation.js
```

Fallback-вариант:

```text
Vanilla TypeScript/JavaScript
Canvas 2D или SVG
CSS overlays
requestAnimationFrame replay engine
```

Важно: fallback может быть 2.5D/top-down, но должен сохранить тот же визуальный язык: статусы, коллизии, задачи, timeline, overlays, карточки причин.

### 2.4. Графики и KPI

```text
Apache ECharts
```

Использовать для:

- производительности по минутам;
- SLA пополнения;
- utilization комплектовщиков и ричтраков;
- lost minutes by collision type;
- route/wave completion.

Для timeline лучше сделать кастомный компонент, потому что он управляет replay engine.

### 2.5. Backend/API, если нужен live или integrated режим

```text
Python
FastAPI
Pydantic
WebSocket
PostgreSQL
ClickHouse
Redis
S3 / MinIO
```

Назначение:

- `FastAPI` — API для layout/events/metrics/collisions.
- `Pydantic` — валидация моделей данных.
- `WebSocket` — live-события склада.
- `PostgreSQL` — справочники, layout, волны, задания.
- `ClickHouse` — большой event stream и поминутные метрики.
- `Redis` — live-state и pub/sub.
- `S3/MinIO` — evidence, screenshots, HTML-артефакты.

### 2.6. Evidence и скриншоты

```text
Playwright
pytest
visual regression screenshots
```

Playwright должен делать обязательные screenshots состояния склада:

```text
T00_initial_layout.png
T01_wave_01_launched.png
T02_first_replenishment.png
T03_peak_congestion.png
T04_mid_shift.png
T05_reachtruck_queue.png
T06_dock_queue.png
T07_last_wave_launched.png
T08_shift_finish.png
```

---

## 3. Обязательные файлы и точки входа

Сохранить совместимость с текущим ТЗ. Страница “мультика” должна существовать по путям:

```text
wiki-raw/wms_admin_ui_reference/warehouse-simulation.html
wiki-raw/wms_admin_ui_reference/warehouse-simulation.js
wiki-raw/wms_admin_ui_reference/warehouse-simulation.css
```

Если внедряется React/Vite-приложение, эти файлы могут быть shell/entrypoint-ами, которые подключают bundle. Например:

```text
wiki-raw/wms_admin_ui_reference/warehouse-simulation.html
src/warehouse-digital-twin/main.tsx
src/warehouse-digital-twin/App.tsx
src/warehouse-digital-twin/components/*
src/warehouse-digital-twin/scene/*
src/warehouse-digital-twin/replay/*
src/warehouse-digital-twin/types/*
```

Runner/evidence ожидается в структуре:

```text
runtime/test-evidence/warehouse-minute-simulation/<run-id>/
  report.json
  report.md
  timeline.csv
  events.jsonl
  layout.json
  generated-orders.json
  generated-stock.json
  metrics-by-minute.csv
  collision-report.csv
  evidence-presentation.html
  warehouse-animation.html
  screenshots/
```

---

## 4. Информационная архитектура страницы

### 4.1. Top bar

Содержит:

- логотип/иконку куба;
- заголовок `Цифровой двойник склада`;
- зеленый badge `Онлайн`;
- фильтр смены: `Смена: 1 (08:00–20:00)`;
- фильтр волны: `Волна: WAVE-SIM-03` или `Все волны`;
- фильтр зоны: `Все зоны`;
- текущее время replay: `09:42:17`;
- иконки поиска, уведомлений, пользователя.

### 4.2. KPI row

Карточки сверху:

```text
Производительность        112% к плану
Обработано единиц         18 432 / 20 000
Активные комплектовщики   24 / 32 или 10 / 10 для simulation
SLA пополнения            84%
Просроченные задачи       27
Коллизии                  7 критические
Средняя скорость          1,21 м/с
```

Для model-only сценария с 10 комплектовщиками и 5 ричтраками KPI должны вычисляться из `metrics-by-minute.csv` и текущего состояния replay.

### 4.3. Left panel: задачи пополнения / RTP

Панель `Задачи пополнения (RTP)`:

- вкладки `Просроченные` и `Все`;
- список задач по приоритету;
- для каждой задачи:
  - elapsed/overdue time;
  - адрес pick-face;
  - причина: `Пик-лицо пусто`, `Низкий остаток`, `Ждет динамическую ячейку`, `Minimax wait`;
  - SKU;
  - остаток `0 / 48 шт` или `12 / 96 шт`;
  - зона/стеллаж;
  - warning icon;
  - мини-иконка паллеты/короба.

Внизу карточка RTP/ричтрака:

```text
RTP-01 · Владимир
Загрузка: 78%
Очередь: 8 задач
```

Для симуляции использовать ресурсы `RT01..RT05`.

### 4.4. Central scene: цифровой двойник склада

Главная область — большая изометрическая сцена склада.

Обязательно показать:

- 25 аллей `A01..A25`;
- стеллажи вдоль аллей;
- pick-face ячейки на уровне `L1`;
- зоны хранения `L2..L6` визуально как верхние уровни/резерв;
- ворота `G01..G25`;
- зона фронтального транспорта у ворот;
- зона отгрузки;
- комплектовщики `P01..P10`;
- ричтраки `RT01..RT05`;
- клиентские паллеты;
- паллеты пополнения;
- маршруты комплектовки и ричтраков;
- heatmap очередей и задержек;
- hotspot-ы коллизий.

### 4.5. Right panel: коллизии и причины

Панель `Коллизии и причины`:

Список событий:

```text
Пик-лицо пусто
A01-S023-L1
Задержка: 28 мин
Влияет на: P02, P07
Потеря: ~120 ед./час

Затор в проходе
A03, сегмент 30–40 м
3 комплектовщика ожидают проход
Влияет на: P04, P05, P08
Потеря: ~80 ед./час

Блокировка маршрута
RT03 выполняет опускание паллеты
P06 ждет безопасный доступ
Потеря: ~95 ед./час
```

Список должен быть синхронизирован с текущей минутой replay.

### 4.6. Bottom timeline

Timeline смены `08:00–20:00`:

- play/pause;
- скорость `x1`, `x5`, `x10`, `x60`;
- scrubber времени;
- цветные event markers:
  - зеленые — нормальные этапы;
  - желтые — риск/задержка;
  - красные — критическая коллизия;
  - серые — ожидание;
- кнопка `Сейчас` / `Live`, если есть live mode.

---

## 5. Визуальный язык статусов

| Цвет | Значение | Использование |
|---|---|---|
| Зеленый | Норма / выше плана | ресурс идет по плану, SLA в норме, маршрут без риска |
| Синий | Активное движение | motion trail, маршрут, перемещение ресурса |
| Желтый/оранжевый | Риск / задержка | низкий остаток, замедление, очередь, перегруз сегмента |
| Красный | Коллизия / критическая проблема | пустой pick-face, стоп, блокировка маршрута, SLA breach |
| Серый | Ожидание / idle | ресурс стоит, ждет пополнение, нет задачи, очередь |

### 5.1. Комплектовщик

Каждый комплектовщик должен иметь:

```text
ID: P01..P10
badge с процентом скорости/плана
status ring
motion trail
мини-иконку человека/тележки
```

Примеры статусов:

```text
P07 132%    зеленый, опережает план
P02 98%     зеленый/синий, в норме
P04 74%     желтый, замедлен
P03 стоп    красный, не выполняет задачу
P06 ожид.   серый, ждет пополнение
```

### 5.2. Ричтрак/RTP

Ричтрак должен иметь:

```text
ID: RT01..RT05
очередь задач
текущую задачу
статус загрузки
route trail
зону блокировки при операции опускания паллеты
```

Примеры:

```text
RT01 · queue 8 · загрузка 78%
RT03 · опускает паллету · блокирует A04-S017-L1
RT05 · в пути к G12
```

### 5.3. Pick-face и остатки

Pick-face ячейки должны иметь три состояния:

```text
normal       остаток достаточный
low          низкий остаток, риск
empty        пусто, комплектовщик не может закрыть строку
```

Визуально:

- `normal` — нейтральный/легкий зеленый marker;
- `low` — желтый halo;
- `empty` — красный hotspot и callout.

### 5.4. Коллизии

Каждая коллизия должна иметь:

```text
type
severity
start_time
end_time или active
location
affected_resources
affected_wave/client/route/SKU
root_cause
lost_minutes
productivity_loss_estimate
```

Визуально:

- красный/желтый hotspot на карте;
- callout прямо над местом проблемы;
- дублирование в right panel;
- marker на timeline;
- влияние на route progress / KPI.

---

## 6. Типы коллизий, которые нужно визуализировать

| Код | Визуальный смысл | Пример callout-а |
|---|---|---|
| `PICK_FACE_QUEUE` | очередь к ячейке отбора | `Очередь к A01-S023-L1 · 3 комплектовщика` |
| `AISLE_CONGESTION` | перегруз прохода | `Затор в проходе A03 · скорость снижена` |
| `REACHTRUCK_BLOCK` | блокировка ричтраком | `RT03 блокирует зону отбора` |
| `DYNAMIC_CELL_SHORTAGE` | нет свободной динамической ячейки | `Нет динамической ячейки под SKU-33211` |
| `MINIMAX_WAIT` | ожидание Minimax | `Пополнение ждет порога Minimax` |
| `REACH_RESOURCE_SHORTAGE` | нехватка ричтраков | `Очередь RTP: 8 задач` |
| `PICKER_RESOURCE_SHORTAGE` | нехватка комплектовщиков | `Паллет больше, чем свободных комплектовщиков` |
| `DOCK_QUEUE` | очередь на ворота | `G07 заняты, клиент ждет отгрузку` |
| `SHIPMENT_RATE_LIMIT` | ограничение скорости отгрузки | `15 паллет/час: клиент ждет слот` |

---

## 7. Данные и контракты

### 7.1. Layout

`layout.json` должен описывать физическую модель склада.

Минимальный TypeScript-контракт:

```ts
export type WarehouseLayout = {
  warehouseId: string;
  shiftStart: string; // "08:00"
  shiftEnd: string;   // "20:00"
  aisles: Aisle[];
  gates: Gate[];
  zones: WarehouseZone[];
  pickFaces: PickFace[];
  storageLocations: StorageLocation[];
  coordinateSystem: {
    origin: "front_transport_zone";
    aisleLengthM: number;       // 90
    aisleSpacingM: number;      // 4
    slotSpacingM: number;       // 1.5
  };
};

export type Aisle = {
  id: string;       // A01..A25
  index: number;
  x: number;
  y: number;
  lengthM: number;
  slots: number;    // 60
};

export type Gate = {
  id: string;       // G01..G25
  aisleId: string;
  x: number;
  y: number;
};

export type PickFace = {
  locationId: string; // A01-S001-L1
  aisleId: string;
  slot: number;
  level: "L1";
  sku?: string;
  capacityCases: number;
  initialCases: number;
  x: number;
  y: number;
};
```

### 7.2. Events

`events.jsonl` — поток событий. Каждая строка — JSON.

Минимальный контракт:

```ts
export type WarehouseEvent = {
  ts: string; // ISO or "HH:mm:ss"
  minute: number;
  type:
    | "WAVE_STARTED"
    | "PICKER_MOVED"
    | "PICK_STARTED"
    | "PICK_COMPLETED"
    | "PICKER_WAIT_STARTED"
    | "PICKER_WAIT_ENDED"
    | "REPLENISHMENT_TASK_CREATED"
    | "REPLENISHMENT_STARTED"
    | "REPLENISHMENT_COMPLETED"
    | "REACHTRUCK_MOVED"
    | "PALLET_MOVED"
    | "ROUTE_PROGRESS"
    | "COLLISION_STARTED"
    | "COLLISION_ENDED"
    | "CLIENT_READY"
    | "SHIPMENT_STARTED"
    | "SHIPMENT_COMPLETED";
  resourceId?: string;
  taskId?: string;
  waveId?: string;
  clientId?: string;
  routeId?: string;
  palletId?: string;
  sku?: string;
  from?: WarehousePoint;
  to?: WarehousePoint;
  locationId?: string;
  payload?: Record<string, unknown>;
};

export type WarehousePoint = {
  x: number;
  y: number;
  z?: number;
  aisleId?: string;
  locationId?: string;
};
```

### 7.3. Metrics

`metrics-by-minute.csv` или JSON-аналог.

Ключевые поля:

```text
minute
time
active_pickers
active_reachtrucks
picker_utilization
reachtruck_utilization
picker_wait_minutes
replenishment_wait_minutes
reachtruck_queue_depth
collision_count
lost_minutes_total
units_processed
units_per_hour
sla_delay_minutes
```

### 7.4. Collision report

```ts
export type Collision = {
  id: string;
  type: CollisionType;
  severity: "info" | "warning" | "critical";
  startMinute: number;
  endMinute?: number;
  active: boolean;
  locationId?: string;
  aisleId?: string;
  segmentM?: [number, number];
  affectedResources: string[];
  waveId?: string;
  clientId?: string;
  routeId?: string;
  sku?: string;
  rootCause: string;
  lostMinutes: number;
  productivityLossPerHour?: number;
};
```

---

## 8. Scene engine: как строить склад

### 8.1. Камера

Использовать orthographic/isometric view:

```text
camera.position = [80, 90, 80]
camera.lookAt(center)
projection = orthographic
```

Камера должна позволять:

- pan;
- zoom;
- reset view;
- optional rotate only within safe range или вообще без rotate, чтобы сохранить читаемость.

### 8.2. Генерация геометрии

Не моделировать 25 аллей вручную. Генерировать из `layout.json`:

```text
for each aisle:
  draw floor lane
  draw rack rows left/right or center
  draw slots S001..S060
  draw pick-face indicators L1
  draw storage levels L2..L6 as stacked boxes/racks
  draw aisle label
```

Геометрия:

- floor planes;
- rack beams;
- pallet/box instances;
- gate docks;
- columns;
- transport zone;
- shipping zone.

### 8.3. Instancing

Использовать instanced rendering для:

```text
boxes
pallets
rack posts
rack beams
pick-face markers
slot markers
warning halos
```

Это критично для производительности.

### 8.4. HTML overlays поверх 3D

Текстовые подписи не делать тяжелым 3D-text. Делать HTML/CSS overlay:

```text
3D position → project(camera) → screen x/y → CSS transform
```

Overlay-элементы:

- `P07 132%`;
- `P03 стоп`;
- `RT01 queue 8`;
- `Пик-лицо пусто A01-S023-L1`;
- `Затор в проходе`;
- `Ждет паллету P-55321`;
- route progress widget.

---

## 9. Replay engine

### 9.1. Назначение

Replay engine превращает `events.jsonl` в состояние склада на выбранную минуту.

Он должен поддерживать:

- play/pause;
- playback speed `x1/x5/x10/x60`;
- scrubber;
- jump to event;
- filtering by wave/client/resource/SKU/collision type;
- live-like mode, если данные поступают по WebSocket.

### 9.2. State model

```ts
export type ReplayState = {
  currentMinute: number;
  currentTimeLabel: string;
  playing: boolean;
  speed: 1 | 5 | 10 | 60;
  selectedWaveId?: string;
  selectedClientId?: string;
  selectedSku?: string;
  selectedResourceId?: string;
  enabledLayers: EnabledLayers;
  resources: Record<string, ResourceState>;
  pallets: Record<string, PalletState>;
  tasks: Record<string, TaskState>;
  activeCollisions: Collision[];
  routeProgress: Record<string, RouteProgress>;
  metrics: MinuteMetrics;
};
```

### 9.3. Interpolation

Для movement-events:

```text
position at Tn → position at Tn+1
```

Использовать интерполяцию, чтобы ресурсы двигались плавно между минутами. Если нет точной позиции, использовать последнее известное состояние.

### 9.4. Event markers

Timeline должен показывать markers:

- старт волны;
- начало/конец коллизии;
- пик очереди ричтраков;
- момент пустого pick-face;
- готовность клиента;
- начало/конец отгрузки;
- окончание смены.

---

## 10. Interaction model

### 10.1. Click по комплектовщику

Показать карточку:

```text
P07
Статус: комплектация
Скорость: 132% к плану
Текущая задача: PICK-000931
Волна: WAVE-SIM-03
Клиент: C014
Паллета: CP-014-03
SKU: SKU-88421
Маршрут: R-104
Плановое время: 09:35
Фактическое время: 09:42
Потерянные минуты: 7
Причина задержки: ожидание пополнения A01-S023-L1
```

### 10.2. Click по ричтраку/RTP

Показать:

```text
RT03 / водитель RTD03
Статус: опускание паллеты
Текущая задача: REPL-00231
Очередь: 8 задач
Источник: A14-S044-L4
Назначение: A01-S023-L1
SKU: SKU-88421
Просрочка: 28 мин
Влияет на: P02, P07, route R-104
```

### 10.3. Click по коллизии

Показать:

```text
Коллизия: PICK_FACE_QUEUE
Severity: critical
Адрес: A01-S023-L1
Начало: 09:14
Длительность: 28 мин
Root cause: несвоевременное пополнение pick-face
Affected resources: P02, P07
Affected route: R-104
Productivity loss: ~120 ед./час
```

### 10.4. Click по маршруту/волне

Подсветить:

- все связанные паллеты;
- всех комплектовщиков;
- все задачи ричтраков;
- все коллизии;
- прогресс `40% / 60% / 90% / blocked`.

---

## 11. Layers / фильтры

Слои:

```text
Комплектовщики
Ричтраки/RTP
Пополнение
Коробочная сборка
Моно-паллеты
Отгрузка
Коллизии
Heatmap
Маршруты
Pick-face остатки
```

Фильтры:

```text
Волна
Клиент
SKU
Ресурс
Тип события
Тип коллизии
Severity
```

Layer toggles должны влиять и на сцену, и на панели/карточки.

---

## 12. KPI formulas / поведение

### 12.1. Производительность

```text
productivity_percent = actual_units_processed / planned_units_processed * 100
```

### 12.2. SLA пополнения

```text
replenishment_sla = completed_replenishment_tasks_on_time / completed_replenishment_tasks * 100
```

### 12.3. Средняя скорость комплектовщиков

```text
avg_picker_speed = average(resource.distance_moved / active_move_time)
```

### 12.4. Потери производительности

```text
lost_minutes_total = sum(active_collisions.lost_minutes)
productivity_loss_estimate = lost_minutes * baseline_units_per_minute
```

### 12.5. Route progress

```text
route_progress = picked_lines_or_units / planned_lines_or_units
```

Если маршрут ждет паллету или pick-face пустой, показывать:

```text
R-104 · Заблокирован · Ждет паллету P-55321
```

---

## 13. Acceptance criteria

### 13.1. Визуальные критерии

- Страница выглядит как premium logistics control tower.
- Центральная сцена занимает основную часть экрана.
- Есть изометрический склад с 25 аллеями, воротами и зонами.
- Видны комплектовщики и ричтраки.
- Видны speed/status badges ресурсов.
- Видны маршруты и motion trails.
- Видны hotspot-ы коллизий.
- Видны причины задержек прямо на карте.
- Есть left panel задач RTP.
- Есть right panel коллизий и причин.
- Есть top KPI row.
- Есть bottom playback timeline.

### 13.2. Функциональные критерии

- Страница читает `layout.json` и `events.jsonl`.
- Страница читает `metrics-by-minute.csv` и `collision-report.csv`, если они есть.
- Replay работает по минутам `08:00–20:00`.
- Play/pause/speed/scrubber работают.
- При выборе момента времени обновляются сцена, KPI, задачи и коллизии.
- Click по ресурсу/паллету/коллизии открывает detail card.
- Layer toggles работают.
- Timeline показывает markers критических событий.
- Страница не падает, если часть optional данных отсутствует; использует graceful fallback.

### 13.3. Производительность

- Сцена не тормозит на layout 25 аллей × 60 слотов × 6 уровней.
- Одинаковые объекты рендерятся через instancing или другой оптимизированный подход.
- Большой `events.jsonl` парсится без блокировки UI, желательно через Web Worker или chunked parsing.
- UI остается отзывчивым при проигрывании `x60`.

### 13.4. Evidence

- Есть screenshots ключевых моментов через Playwright.
- `warehouse-animation.html` или `warehouse-simulation.html` может быть открыт из evidence-папки.
- Итоговый `report.md` содержит ссылки на визуализацию и screenshots.

---

## 14. Рекомендуемый порядок реализации

1. Проинспектировать текущую структуру проекта и понять, есть ли React/Vite frontend.
2. Сохранить обязательные entrypoint-файлы `warehouse-simulation.html/js/css`.
3. Добавить типы данных для layout/events/metrics/collisions.
4. Реализовать loader данных из evidence-папки.
5. Реализовать replay store и timeline.
6. Построить базовую сцену склада из `layout.json`.
7. Добавить ресурсы: комплектовщики и ричтраки.
8. Добавить movement trails и status badges.
9. Добавить pick-face состояния и replenishment tasks.
10. Добавить collision hotspots и right panel.
11. Добавить left panel RTP tasks.
12. Добавить KPI row и route progress widget.
13. Добавить click interactions.
14. Добавить layer filters.
15. Добавить Playwright screenshots.
16. Добавить tests для replay reducer/parser.
17. Сверить визуал с reference image и довести CSS/позиционирование.

---

## 15. Что нельзя делать

- Не вставлять референс-картинку как единственную “визуализацию”. UI должен быть интерактивным.
- Не хардкодить только один красивый скрин без связи с данными.
- Не рисовать каждую коробку отдельным тяжелым DOM-элементом.
- Не делать русский текст в 3D, если он становится нечитаемым. Использовать HTML overlays.
- Не делать только top-down схему, если доступен 3D/WebGL стек. Приоритет — изометрический digital twin.
- Не ломать существующие evidence-пути и runner-артефакты.
- Не использовать CDN/внешнюю сеть, если проект предполагает offline/repo-contained сборку.

---

## 16. Краткое резюме для Codex

Нужно сделать интерактивный dashboard цифрового двойника склада, визуально похожий на `warehouse_digital_twin_dashboard_interface.png`. Основной эффект достигается через:

```text
React + TypeScript dashboard
Three.js / React Three Fiber isometric scene
Orthographic camera
Instanced warehouse geometry
HTML/CSS overlays for readable Russian labels
Replay engine over events.jsonl
KPI/cards from metrics-by-minute.csv
Collision feed from collision-report.csv
Timeline playback from 08:00 to 20:00
Playwright screenshots for evidence
```

Страница должна не просто показывать, что происходит, а объяснять **почему падает производительность**: пустой pick-face, несвоевременное пополнение, очередь RTP, затор в проходе, ожидание Minimax, блокировка маршрута, очередь на ворота.
