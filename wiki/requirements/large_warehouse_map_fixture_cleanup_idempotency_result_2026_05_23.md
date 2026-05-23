# Результат: Fixture Cleanup & Idempotent Publish — 2026-05-23

Статус: реализован первый слой повторяемой приемки warehouse-map fixture.

## Цель

После большого two-camera scale acceptance нужно было убрать два риска:

- fixture-прогоны засоряют тестовый склад активными `FX-/TC-` canvas/topology/route;
- повторный клиентский retry после timeout или сетевого обрыва может создать дубли topology/route.

## Реализовано

### Archive Canvas API

Добавлен endpoint:

- `POST /api/admin/warehouse-map/canvases/{canvas_id}/archive`

Архивация canvas выполняется без физического удаления evidence:

- `RRL_WAREHOUSE_MAP_CANVAS.STATUS = ARCHIVED`, `ACTIVE = 0`;
- активные камеры canvas переводятся в `ARCHIVED`, `ACTIVE = 0`;
- активные camera links, passages и objects деактивируются;
- связанная topology переводится в `ARCHIVED`;
- активные pick routes связанной topology переводятся в `ARCHIVED`, `ACTIVE = 0`.

### Idempotent Retry

Добавлена защита повторов без новой миграции БД:

- `save-to-db` повторно использует активный canvas с тем же `canvas_code`;
- `projection/save-to-topology` при повторе с тем же `topology_code` возвращает существующую topology и counts, не создает новую;
- `route/save-to-db` при повторе с тем же active pick route на topology возвращает существующий route и validation, не создает новую route;
- `publish-oracle` остается повторяемым через существующую Oracle-процедуру publish/update.

Это закрывает основной риск timeout/retry: повтор запроса больше не обязан создавать новую topology/route.

### Fixture Cleanup Tool

Добавлен скрипт:

- `tests/load/warehouse_map/warehouse_map_fixture_cleanup.cjs`

По умолчанию он:

- берет активные canvas тестового склада `WARE_ID=0`;
- выбирает только canvas с кодами `FX-*` и `TC-*`;
- оставляет `WMS_FIXTURE_KEEP_LATEST=1` самый свежий active fixture;
- остальные архивирует через API.

## Проверка

### Cleanup До Повторного Большого Прогона

Первый cleanup:

- active fixture до cleanup: `5`;
- оставлен canvas: `38`;
- заархивированы canvas: `37`, `36`, `35`, `34`.

### Повторный Two-Camera Scale Acceptance

После cleanup повторно запущен большой сценарий:

- `run_id = 20260522231007`;
- `draft_id = df901a734b94412ca79de530747f6642`;
- `canvas_id = 39`;
- `topology_id = 34`;
- `pick_route_id = 121`;
- cameras: `55`, `56`;
- camera links: `1`.

Масштаб:

- storage cells: `3000`;
- pick cells: `1202`;
- topology cells: `5042`;
- cell slots: `8`;
- route rows: `200`;
- storage/non-pick route rows: `0`.

Все checks большого fixture прошли.

### Idempotency Retry

Повторный HTTP retry на опубликованном draft:

```json
{
  "topology_id": 34,
  "topology_idempotent": true,
  "topology_cells": 5042,
  "route_id": 121,
  "route_idempotent": true,
  "route_rows": 200,
  "route_valid": true
}
```

### Cleanup После Повторного Прогона

Второй cleanup:

- active fixture до cleanup: `2`;
- оставлен canvas: `39`;
- заархивирован canvas: `38`.

Финальная проверка active state:

- active fixture: `TC-CANVAS-20260522231007`;
- selected canvas: `39`;
- selected topology: `34`;
- topology cells: `5042`;
- slots: `8`;
- routes: `1`;
- route rows: `200`.

## Вывод

Спринт `Fixture Cleanup & Idempotent Publish` закрыт. Большой fixture теперь можно повторять без накопления активного мусора в тестовом складе, а retry ключевых операций `save canvas / save topology / save route / publish` не должен создавать дубли при использовании стабильных codes.

Следующий слой для production-grade идемпотентности: добавить явный `idempotency_key/request_id` в Oracle schema/API для canvas publish chain, чтобы повтор определялся не только кодом объекта, но и бизнес-идентификатором запроса.
