# Publish/Reload Fixture — результат приемки 2026-05-23

## Назначение

Спринт `Publish/Reload Fixture` проверяет полный цикл публикации карты склада на изолированном тестовом складе, без использования рабочего `WARE_1`.

Критерий приемки:

- создать изолированный draft карты на `WARE_ID = 0`;
- назначить роли физическим ячейкам: отбор, хранение, ворота, транспортное накопление, проходы, зона на пленку;
- создать дробный pick slot и дробный storage slot;
- назначить адреса отбора;
- построить маршрут только по ячейкам отбора;
- выполнить `Save canvas DB -> Save topology DB -> Save route DB -> Publish Oracle`;
- перечитать склад через `GET /api/admin/warehouse-map/warehouses/{ware_id}/state`;
- доказать, что reload вернул опубликованные `canvas/topology/route`, а маршрут не содержит storage/non-pick строк.

## Evidence

Runtime evidence находится вне коммита и может быть очищен позже:

- `admin/wms_admin_frontend/runtime/test-evidence/warehouse-map-publish-reload-fixture-report.md`;
- `admin/wms_admin_frontend/runtime/test-evidence/warehouse-map-publish-reload-fixture-result.json`;
- `admin/wms_admin_frontend/runtime/test-evidence/warehouse-map-publish-reload-fixture-ui.png`.

Проверенный fixture:

- `WARE_ID = 0`;
- `draft_id = 7ec9da99c09c467290726eb78f44aa0b`;
- `canvas_id = 35`, `canvas_code = FX-CANVAS-20260522212946`;
- `topology_id = 19`, `topology_code = FX-TOPO-20260522212946`;
- `pick_route_id = 117`, `route_code = FX-PICK-20260522212946`.

## Результат

Все acceptance checks прошли:

- `19 / 19 PASS`;
- `route_row_count = 144`;
- `topology_cell_count = 1078`;
- `cell_slots = 4`;
- `pick_slots = 2`;
- `storage_slots = 2`;
- `route_rows_excluded_storage_slots = 0`.

Oracle publish validation:

```json
{
  "valid": true,
  "error_count": 0,
  "route_row_count": 144,
  "storage_slot_route_rows": 0,
  "non_pick_cell_route_rows": 0
}
```

Oracle publish statuses:

```json
{
  "canvas_status": "PUBLISHED",
  "topology_status": "PUBLISHED",
  "route_status": "PUBLISHED",
  "route_row_count": 144
}
```

Reload через warehouse state подтвердил:

- `canvas=35/PUBLISHED`;
- `topology=19/PUBLISHED`;
- `route=117/PUBLISHED`;
- `route_rows=144`;
- `route_rows_excluded_storage_slots=0`.

## Важная проверка и решение

Первый локальный прогон был остановлен validation на ошибке `pick_face_address_points_to_non_pick_face`: адрес был назначен на физическую ячейку, которую затем сделали дробной. Для приемочного fixture адресуемый участок и дробная pick-ячейка разведены. Это полезное ограничение для будущей модели: либо адрес должен ссылаться на физическую pick-face до дробления, либо адресация дробных pick slots должна стать отдельной явной операцией.

Уточнение от 2026-05-23: физическое место может быть родителем дробного отбора, но `pick-face address` не должен указывать на `FRACTIONAL_PICK_FACE`. Для дробного отбора адресуются дочерние `PICK_FACE_SLOT` через маску дробления; полноразмерный pick-face address остается только для физической роли `PICK_FACE`.

## Вывод

Спринт `Publish/Reload Fixture` закрыт: публикация склада на изолированном тестовом складе проходит полный цикл и подтверждается API-инвариантами Oracle, reload через warehouse state и UI screenshot.

## Геограмма Ганта

| Спринт | Статус | Evidence |
| --- | --- | --- |
| Excel Actions 1-3 | Done | Ribbon/context menu parity, функциональный audit |
| Functional Testing Audit | Done | 19/19 UI/API checks |
| Publish/Reload Fixture | Done | 19/19 publish/reload checks, UI screenshot |
| Следующий спринт | Ready | UX/fixture cleanup или масштабная приемка на 2 камеры |
