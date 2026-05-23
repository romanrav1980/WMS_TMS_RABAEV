# Large Warehouse Route Binding Loader, 2026-05-23

## Статус

После materialize bridge следующий blocker для wave/case-pick: нет реальных SKU-to-pick-face bindings. Их нельзя угадывать из карты, потому что это бизнес master-data.

Sprint 3 добавляет безопасный runner для загрузки явных bindings из файла.

## Реализация

- Добавлен `tests/load/warehouse_map/warehouse_route_binding_loader.cjs`.
- Поддерживаются `.json` и `.csv`.
- По умолчанию runner работает в `--dry-run`.
- Для записи нужен явный `--apply`.
- Для локальной проверки файла без API есть `--validate-only`.
- Для экспорта кандидатов из текущих остатков есть `--discover-from-stock --out <csv>`.
- `ware_id` должен быть положительным и ненулевым.
- Runner вызывает `POST /api/picking/warehouses/{ware_id}/route-consumption/materialize`.

## Формат

CSV:

```text
cell_code,articul,priority,min_qty,max_qty,case_pick_enabled,active
A1-001-L1,SKU-001,100,,,1,1
```

JSON:

```json
[
  {"cell_code": "A1-001-L1", "articul": "SKU-001"}
]
```

## Следующий шаг

## Evidence

- PR #4 merged into `feature/transport-dispatch-phase1`.
- API restarted from `C:\projects\TMS_warehouse_next`.
- `GET /api/picking/warehouses/1/route-consumption-readiness` returns `pick_face_count = 205`, `route_cells_without_pick_face_count = 0`, `storage_route_violation_count = 0`, and only `NO_CASE_PICK_ARTICUL_BINDINGS` remains.
- HTTP dry-run with `route_bindings_sample.csv` succeeds against the live API: `route_cells_seen = 1`, `existing_pick_faces = 1`, `created_pick_faces = 0`, `assigned_articuls = 0`, `dry_run = 1`.
- Stock discovery mode checked `205` materialized pick faces on `WARE_ID=1` and produced `0` candidate bindings from `RRL_REMAINS` / `RRL_PALLETS`; no `--apply` was run.

## Следующий шаг

Подставить реальные `cell_code` / `pick_route_cell_id` и `articul` из бизнес master-data или загрузить stock в нужные pick-face cells, выполнить `--dry-run`, затем `--apply`, после чего проверить `route-consumption-readiness`. Цель следующего checkpoint: `ready_for_wave_case_pick = true`.
