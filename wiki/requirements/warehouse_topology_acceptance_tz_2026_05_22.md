# ТЗ От 22 Мая: Приемка Управления Топологией Склада

Статус: тактическое ТЗ к исполнению.

Дата: 2026-05-22.

Рабочий коридор: только topology admin, warehouse topology API, Oracle route invariants и visual evidence.

Связанная постановка:

- [Управление топологией склада и порядком обхода](warehouse_topology_pick_route_tz.md)
- [Правила подсказок и заглушек UI](../concepts/ui_interaction_rules.md)

## Цель

Довести модуль управления топологией склада и порядком обхода отбора до проверяемого состояния сдачи через техническую проверку и визуальное доказательство screenshots.

## Область Работ

Входит:

- React-страница `?page=topology` в `admin/wms_admin_frontend`;
- FastAPI endpoints `/api/admin/warehouse-topologies/*` и `/api/admin/pick-routes/*`;
- Oracle-данные `RRL_WAREHOUSE_TOPOLOGY`, `RRL_TOPOLOGY_CELL`, `RRL_PICK_ROUTE`, `RRL_PICK_ROUTE_CELL`, gate-distance слой;
- большая тестовая топология `LOAD-1500-2CH-60`;
- visual/evidence-проверки через Playwright screenshots.

Не входит:

- MES, wave picking, regulatory adapters, API replay/audit;
- digital twin simulation runner;
- новая ML/ABC-оптимизация layout;
- полноценная реализация split pick-face как новой БД-фичи;
- переработка общего дизайна админки вне topology page.

## Правила Постановки

- Топология склада является версионируемыми мастер-данными, а не ежедневным планом.
- `RRL_PICK_ROUTE_CELL` хранит линейный ранжированный список точек с `PICK_SEQUENCE`.
- `RRL_PICK_ROUTE_CELL` не является edge-table.
- UI-стрелки вычисляются из соседних строк активного маршрута.
- Для активного маршрута на `N` ячеек должно быть `N - 1` стрелок.
- Основной режим редактирования маршрута - `2D План`.
- Для topology на `1500` ЯО порядок обхода не должен исчезать из UI.

## Backend/API

Нужно завершить и проверить нормализацию адресов ЯО:

- `RRL_TOPOLOGY_CELL.CELL_CODE` должен иметь канонический формат по аллее, bay, level, side;
- `RRL_PICK_ROUTE_CELL.CELL_CODE` должен соответствовать связанному `RRL_TOPOLOGY_CELL.CELL_CODE`;
- endpoint `POST /api/admin/warehouse-topologies/{topology_id}/normalize-cell-codes` должен обновлять только безопасные неколлидирующие адреса, сохранять старый адрес в `LEGACY_CELL_CODE`, обновлять stale route cell codes, писать change log и возвращать счетчики;
- `build_pick_route()` должен строить маршрут после нормализации и не создавать дубли active route.

Валидация должна проверять:

- несколько active pick routes на одну topology;
- duplicate `PICK_SEQUENCE`;
- duplicate active physical cell membership;
- pick-face assignments на inactive/archived route rows;
- noncanonical pick-face cell codes;
- stale route cell codes.

## Oracle Route Invariants

Для активного маршрута topology должны выполняться инварианты:

- один active non-archived `PICK` route на topology;
- `PICK_SEQUENCE` уникален внутри active route;
- `TOPOLOGY_CELL_ID` уникален внутри active route;
- route rows ссылаются на active cells текущей topology;
- route rows сортируются по `PICK_SEQUENCE`;
- для `1500` route rows UI строит `1499` вычисленных переходов.

Проверка выполняется на локальной Oracle `RABAEV@127.0.0.1:1521/orcl`.

## Frontend

На странице `?page=topology` нужно обеспечить:

- выбранная topology загружает именно свои cells, routes, gates и distances;
- route summary показывает реальное число active route cells;
- для `LOAD-1500-2CH-60` не должно быть `0 ячеек в последовательности`, если в Oracle есть active route rows;
- route layer показывает стрелки active route, а не все маршруты topology;
- стрелки не перехватывают клики по ячейкам;
- tooltip ЯО содержит паспорт ячейки и route row данные;
- deep zoom показывает короткий `bay-pick_sequence`;
- staging, gates, trucks и aisle labels не перекрывают рабочий слой маршрута;
- future/placeholder controls визуально отделены и имеют tooltip;
- интерактивные кнопки и переключатели имеют понятные `title`.

## Правило SNAKE От 2026-05-22

`SNAKE` не должен выглядеть как диагональный Z-переход между левой и правой стороной на каждом bay.

Для одной аллеи правильный `SNAKE`:

- сначала проходит одну сторону аллеи по bay-порядку;
- затем переходит на вторую сторону у торца;
- затем возвращается по второй стороне в обратном bay-порядке;
- стартовая ячейка первой стороны, например `01L`, должна входить в маршрут и получать `PICK_SEQUENCE`, а не оставаться визуально "бесхозной".

Frontend preview и backend `/api/admin/pick-routes/build` должны использовать одинаковую сортировку.

Результат анализа: после исправления `SNAKE` стал тем же маршрутом, что `U-образно`, поэтому как отдельный пользовательский вариант он удален. Backend принимает старое значение `SNAKE` только как legacy-алиас на `U_SHAPE`.

## Правило U/П От 2026-05-22

Варианты маршрута не должны называться `LINEAR` и не должны визуально выглядеть как русская `И` или английская `N`.

Пользовательские названия:

- `U-образно`;
- `П-образно`.

Правила:

- `U-образно`: вниз по одной стороне аллеи, перемычка снизу, вверх по другой стороне;
- `П-образно`: вверх по одной стороне аллеи, перемычка сверху, вниз по другой стороне;
- старое внутреннее значение `LINEAR` считается совместимым legacy-алиасом для `П-образно`, но не должно показываться пользователю как вариант;
- старое внутреннее значение `SNAKE` считается совместимым legacy-алиасом для `U-образно`, но не должно показываться пользователю как вариант.

Frontend preview и backend `/api/admin/pick-routes/build` должны использовать одинаковую сортировку для обоих вариантов.

## Правило Геометрии Паллетомест От 2026-05-22

Ячейки отбора на 2D-плане должны выглядеть как реальные паллетоместа в ряду, а не как отдельные квадратные иконки.

Правила:

- паллетоместо отображается как `1200 x 800`: длинная сторона `1200 мм` идет вдоль ряда, короткая сторона `800 мм` смотрит внутрь прохода;
- соседние паллетоместа одного ряда, например `01L` и `02L`, должны соприкасаться длинной стороной без зазора;
- соседние back-to-back ряды между соседними аллеями, например `01R` одной аллеи и `01L` следующей аллеи, должны соприкасаться без зазора;
- проход между левым и правым рядом паллетомест считается `3 м`;
- подпись ячейки можно писать внутри прямоугольника, но только на рабочем масштабе или малом участке;
- на общей карте большой topology подписи внутри ЯО скрываются, чтобы `1500` ячеек не превращались в текстовый шум.

Evidence:

- `admin/wms_admin_frontend/runtime/test-evidence/topology-2026-05-22-pallet-places-touching-clean-overview.png`.
- `admin/wms_admin_frontend/runtime/test-evidence/topology-2026-05-22-small-horizontal-pallet-geometry.png`.
- `admin/wms_admin_frontend/runtime/test-evidence/topology-2026-05-22-no-overlap-measured-grid.png`.

Geometry acceptance requires a numeric overlap check, not screenshot review only. For pick-face rectangles in a topology evidence run, `overlapCount` must be `0`.

## Visual Evidence

Минимальные сценарии VD-аудита:

1. Overview `100%`: видна структура склада, ЯО не превращаются в шум, ворота/staging/trucks не перекрыты крупными подписями, route summary показывает корректный count.
2. Route layer: active route виден, arrows count = route rows - 1, стрелки имеют направление, route tooltip содержит `pick_route_cell_id`.
3. Deep zoom: pick-face cells выглядят как читаемая сетка, есть compact labels `bay-pick_sequence`, подписи не перекрывают карту.
4. Interaction smoke: topology selector, layer checkboxes, zoom slider, click ЯО, `Рамка`, validate button, отсутствие React error boundary.

Evidence сохраняется в `runtime/test-evidence/` с понятными именами.

## Acceptance Criteria

Работа считается закрытой, если:

- `npm.cmd run build` проходит;
- API validation для большой topology возвращает `valid=true` либо явно объясняет remaining violations;
- для `LOAD-1500-2CH-60` active route отображается с фактическим количеством route rows, а не как `0`;
- если route rows = `1500`, UI показывает `1500` cells и `1499` arrows;
- Playwright smoke не ловит page errors;
- screenshots подтверждают overview, route layer и deep zoom;
- нет новых unrelated изменений вне рабочего коридора;
- wiki обновлена;
- если трогался русский текст, пройден `scripts/check-encoding.ps1`.

## Первый Диагностический Шаг

Начать нужно с диагностики:

- определить `TOPOLOGY_ID` для `LOAD-1500-2CH-60`;
- найти active route;
- посчитать active `RRL_PICK_ROUTE_CELL`;
- сравнить ответ `/api/admin/warehouse-topologies/{id}/map` с Oracle counts;
- выяснить, почему свежий screenshot показывает `CASE-Z-MAIN` и `0 ячеек в последовательности`.

## Диагностический Чекпоинт 2026-05-22

Первый прогон показал, что проблема была не в React-renderer-е: API сам возвращал для topology `2` маршрут `CASE-Z-MAIN` с `0` active route rows.

Факты диагностики:

- `LOAD-1500-2CH-60` имеет `TOPOLOGY_ID = 2`, `WARE_ID = 1`, статус `VALIDATED`;
- до восстановления `/api/admin/pick-routes?topology_id=2` возвращал active route `105 / CASE-Z-MAIN` с `cell_count = 0`;
- `/api/admin/warehouse-topologies/2/map` возвращал `1500` cells и `0` route_cells;
- validation возвращала `valid=true`, потому что в ней не было проверки active route без строк.

Первое исправление:

- маршрут `105 / CASE-Z-MAIN` восстановлен через `/api/admin/pick-routes/build`;
- API после восстановления возвращает `1500` route_cells, sequence range `1..1500`;
- validation дополнена проверкой `active_pick_routes_without_cells`, чтобы active route без rows больше не проходил как clean topology;
- `npm.cmd run build` прошел;
- `scripts/check-encoding.ps1` прошел.

Visual evidence:

- `admin/wms_admin_frontend/runtime/test-evidence/topology-2026-05-22-vd-loading-diagnostic.png` показывает topology page после восстановления: `1500` ЯО, `1500` в обходе, `CASE-Z-MAIN`, `1500 ячеек в последовательности`.

## Visual Fix: Зона Консолидации

Визуальная проверка выявила, что зона консолидации/накопления рисовалась выше ворот и наезжала на рабочую область ячеек отбора.

Исправление:

- SVG-план получил дополнительную нижнюю доковую полосу;
- dock layout приведен к физическому порядку сверху вниз: склад, зона накопления паллет, ворота, машина;
- staging-сетки ворот находятся между складом и воротами, без наезда на ЯО;
- данные Oracle/API не менялись, исправлен только renderer topology page.

Evidence:

- `admin/wms_admin_frontend/runtime/test-evidence/topology-2026-05-22-dock-order-fixed-gate-line.png` показывает порядок склад -> накопление -> ворота -> машина без перекрытия ЯО.
