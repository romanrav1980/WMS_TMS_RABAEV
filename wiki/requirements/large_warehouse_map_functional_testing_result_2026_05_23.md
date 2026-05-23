# Итог функционального тестирования карты большого склада от 2026-05-23

Статус: функциональный аудит выполнен через Playwright по ТЗ [large_warehouse_map_functional_testing_tz.md](large_warehouse_map_functional_testing_tz.md).

Проверенный экран: `?page=warehouse-map`.

Evidence runtime:

- `admin/wms_admin_frontend/runtime/test-evidence/warehouse-map-functional-audit-report.md`
- `admin/wms_admin_frontend/runtime/test-evidence/functional-01-open-warehouse.png`
- `admin/wms_admin_frontend/runtime/test-evidence/functional-02-templates.png`
- `admin/wms_admin_frontend/runtime/test-evidence/functional-03-addresses.png`
- `admin/wms_admin_frontend/runtime/test-evidence/functional-04-validation-route.png`
- `admin/wms_admin_frontend/runtime/test-evidence/functional-05-final.png`

## Результат

Итог последнего прогона:

- `PASS`: 19
- `PARTIAL`: 0
- `FAIL`: 0

Проверены:

- открытие экрана и выбор реального склада Oracle;
- Excel ribbon и быстрые действия левой панели;
- шаблоны layout: регулярный склад, проходы, ворота/накопление;
- выделение области canvas;
- назначение ролей, очистка, undo/redo;
- format painter copy/paste;
- сохранение draft;
- назначение адресов отбора с визуальным отображением адресов на canvas;
- context menu tree: редактирование, шаблоны, отбор, хранение, проверка;
- route patterns через context menu;
- projection preview и validation;
- Save canvas DB;
- инструкция модуля.

## Исправленные Дефекты По Ходу Тестирования

1. `Назначить адреса` раньше меняло данные/статус, но canvas продолжал рисовать технические координаты вида `aisle.slot`.
   Исправлено: после успешной адресации карта хранит визуальные адресные labels и рисует их внутри соответствующих ячеек при достаточном zoom.

2. После построения route draft выделение сбрасывалось через `applyApiDraft(reloaded)`, поэтому повторное построение `Z`, `u-образно` или `П-образно` требовало заново выделять область.
   Исправлено: `buildRouteFromSelection` восстанавливает рабочее выделение и активную ячейку после reload draft.

## Заключение О Достаточности

Текущий набор функций достаточен для управления canvas склада в режиме черновика:

- склад можно выбрать;
- карту можно нарисовать ролями и шаблонами;
- массовые операции, выделение, format painter и undo/redo работают;
- адресация отбора теперь подтверждается и данными, и визуально;
- route можно строить и проверять;
- canvas можно сохранить в Oracle.

Ограничение приемки: полный end-to-end publish/reload опубликованного склада требует отдельного контролируемого Oracle-сценария, чтобы не портить рабочие склады. В текущем UI-аудите проверен `Save canvas DB`, но полный publish должен выполняться на отдельном тестовом складе/fixture с заранее согласованной очисткой.

## Следующее ТЗ На Оптимизацию

Следующий UX-спринт стоит посвятить не добавлению новых кнопок, а снижению когнитивной нагрузки:

- динамический topbar: склад, canvas, камера, route rows, publish state;
- рабочие вкладки левой панели: `Склад`, `Рисование`, `Формат`, `Маршрут`, `Публикация`, `Проверка`;
- command palette для поиска команды;
- отдельные мастера `Создать камеру`, `Ворота + накопление`, `Аллеи отбора/хранения`;
- автоматизированный smoke для help/tooltip/disabled-state подписей.
