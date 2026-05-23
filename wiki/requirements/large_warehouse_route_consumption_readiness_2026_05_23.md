# Large Warehouse Route Consumption Readiness, 2026-05-23

## Статус

После merge релиза карты склада стратегический план перешел к следующему слою: published warehouse state должен стать входом для wave picking, replenishment/tasks, TSD route flow и digital twin.

Первый маленький Sprint 1 выполнен как read-only readiness API, а не как изменение запуска волн. Причина: существующий wave/case-pick уже умеет сортировать задачи по `PICK_SEQUENCE` и хранить `PICK_FACE_ID` / `PICK_ROUTE_CELL_ID`, но опубликованная карта склада пока создает маршрутные ячейки, а не артикульные pick-face bindings.

## Реализация

- Добавлен `GET /api/picking/warehouses/{ware_id}/route-consumption-readiness`.
- Endpoint требует `pick_topology_view`.
- `ware_id=0` запрещен через `Path(gt=0)`.
- Сервис проверяет опубликованные topology rows, active/published pick routes, route cells, storage-slot violations внутри pick route, наличие `RRL_PICK_FACE`, и наличие активных `RRL_PICK_FACE_ARTICUL` для case-pick.

## Evidence

Прямой service-call на `WARE_ID=1`:

- `published_topology_count = 6`
- `active_pick_route_count = 8`
- `published_pick_route_count = 6`
- `route_cell_count = 205`
- `storage_route_violation_count = 0`
- `pick_face_count = 0`
- `route_cells_without_pick_face_count = 205`
- `case_pick_articul_binding_count = 0`
- `ready_for_wave_case_pick = false`
- blockers: `NO_PICK_FACE_BINDINGS`, `NO_CASE_PICK_ARTICUL_BINDINGS`

## Вывод

Опубликованная карта уже дает безопасный маршрут без storage-slot попаданий, но wave/case-pick еще не может потреблять его автоматически для артикулов. Следующий sprint должен создать мост `published route cell -> pick face -> articul binding`.
