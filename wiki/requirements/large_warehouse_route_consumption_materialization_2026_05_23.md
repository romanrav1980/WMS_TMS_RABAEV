# Large Warehouse Route Consumption Materialization, 2026-05-23

## Статус

Sprint 2 после route-readiness добавил write-мост `published route cell -> pick face -> articul binding`.

Цель была не запускать wave вслепую, а создать явную операцию подготовки master-data: опубликованные `RRL_PICK_ROUTE_CELL` превращаются в `RRL_PICK_FACE`, а артикулы привязываются только явным входным mapping.

## Реализация

- Добавлен `POST /api/picking/warehouses/{ware_id}/route-consumption/materialize`.
- Endpoint требует `pick_topology_edit`.
- `ware_id=0` запрещен через `Path(gt=0)`.
- Request поддерживает:
  - `pick_route_id` как optional filter;
  - `create_missing_pick_faces`;
  - `bindings` по `pick_route_cell_id` и/или `cell_code`;
  - `dry_run`;
  - `limit`.
- Сервис создает `RRL_PICK_FACE` через `RRL_PICK_TOPOLOGY_API.upsert_pick_face`.
- Сервис назначает `RRL_PICK_FACE_ARTICUL` через `RRL_PICK_TOPOLOGY_API.assign_articul`, но только для явно переданных bindings.

## Evidence

На `WARE_ID=1`:

- первый materialize run: `route_cells_seen = 205`, `created_pick_faces = 205`, `existing_pick_faces = 0`, `assigned_articuls = 0`;
- readiness после первого run: `pick_face_count = 205`, `route_cells_without_pick_face_count = 0`, `storage_route_violation_count = 0`;
- повторный run: `created_pick_faces = 0`, `existing_pick_faces = 205`, `skipped_without_pick_face = 0`;
- binding dry-run по published `pick_route_cell_id`: `existing_pick_faces = 1`, `assigned_articuls = 1`, `dry_run = 1`;
- readiness после retry блокируется только `NO_CASE_PICK_ARTICUL_BINDINGS`.

## Вывод

Технический мост от опубликованного маршрута к pick-face master-data создан и проверен без дублей. Следующий sprint: загрузить или задать реальные SKU-to-pick-face bindings, после чего readiness должен стать `ready_for_wave_case_pick = true` и wave/case-pick сможет потреблять маршрутный порядок.
