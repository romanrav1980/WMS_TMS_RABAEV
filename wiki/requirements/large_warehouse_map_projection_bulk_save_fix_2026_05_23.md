# Projection Bulk Save Architecture Fix — 2026-05-23

## Проблема

Сохранение `projection/save-to-topology` для двухкамерного fixture на `5042` topology cells занимало неприемлемое время:

- первый прогон: `761720 ms`;
- повторный retry: `766722 ms`;
- клиентский Node fetch обрывался примерно на 5-й минуте, а сервер продолжал работу;
- повтор после timeout создавал новую topology, то есть операция была не только медленной, но и опасной для дублей.

## Причина

Основная причина была в API/DB gateway, а не в данных склада:

- `OracleGateway.execute_many()` назывался bulk-операцией, но фактически выполнял `cursor.execute(...)` в Python-цикле для каждой строки;
- `save_projection_to_topology()` получал `RRL_TOPOLOGY_CELL_SQ.nextval` отдельно для каждой physical cell;
- на `5042` cells это давало тысячи round-trip к Oracle перед фактическим insert.

## Исправление

Внесено минимальное архитектурное исправление без расширения контекста UI:

- `OracleGateway.execute_many()` группирует statements по SQL и вызывает настоящий `cursor.executemany(sql, rows)`;
- `save_projection_to_topology()` получает блок `RRL_TOPOLOGY_CELL_SQ.nextval` одним запросом через `connect by level <= :count`;
- topology cells сохраняются через один bulk group вместо тысяч отдельных execute;
- projection header, topology-cell ids, topology cells, slots и связь canvas с topology сохраняются в одной Oracle-транзакции;
- сохранена поддержка `draft_metadata.camera_regions`, чтобы topology cells распределялись по двум камерам.

## Evidence

Проверка выполнена на существующем two-camera draft:

- `draft_id = 0276161812484df69fceffd9c9018e6c`;
- `canvas_id = 37`;
- `topology_id = 24`;
- `pick_route_id = 118`;
- камеры: `51`, `52`;
- camera link: `1`;
- topology cells: `5042`;
- slots: `8`;
- route rows: `200`.

Замеры после исправления:

| Операция | Результат |
| --- | ---: |
| Save topology projection, первый bulk-fix | `3936 ms` |
| Save topology projection, одна bulk-транзакция | `2737 ms` |
| Save route DB | `1683 ms` |
| Publish Oracle | `1183 ms` |
| Reload warehouse state | `4470 ms` |

Малое нагрузочное тестирование того же endpoint после исправления:

| Run | Topology ID | Cells | Slots | Time |
| ---: | ---: | ---: | ---: | ---: |
| 1 | `26` | `5042` | `8` | `2251 ms` |
| 2 | `27` | `5042` | `8` | `2656 ms` |
| 3 | `28` | `5042` | `8` | `2524 ms` |
| 4 | `29` | `5042` | `8` | `2625 ms` |
| 5 | `30` | `5042` | `8` | `2310 ms` |

Итог малого load test:

- успешных сохранений: `5/5`;
- минимум: `2251 ms`;
- максимум: `2656 ms`;
- среднее: `2473 ms`;
- все прогоны уложились в `3 секунды`;
- reload после серии подтвердил: canvas `37` указывает на topology `30`, topology cells `5042`, slots `8`, cameras `2`, camera links `1`.

Reload подтвердил:

```json
{
  "canvas_id": 37,
  "canvas_status": "PUBLISHED",
  "topology_id": 24,
  "topology_status": "PUBLISHED",
  "cameras": 2,
  "camera_links": 1,
  "topology_cells": 5042,
  "cell_slots": 8,
  "routes": 1,
  "route_rows": 200,
  "route_rows_excluded_storage_slots": 0,
  "camera_cell_counts": {
    "51": 2821,
    "52": 2221
  }
}
```

## Остаточный риск

`2737 ms` попадает в целевой пользовательский коридор `2-3 секунды` для текущего fixture на `5042` cells. Остаточный риск остается для существенно больших projection saves, поэтому принято архитектурное правило:

- массовое сохранение не должно умножать DB/API-операции на количество cells;
- для thousands-scale операций допустимы только `O(1)` HTTP-вызовы и малое число DB round-trip на фазу;
- запрещен per-cell `execute`, per-cell `nextval`, per-cell commit и retry без идемпотентности;
- если измерение выходит за адекватный лимит, сначала меняется bulk-архитектура, а не увеличивается timeout.

Следующий слой оптимизации, если понадобится стабильно уходить ниже `2 секунд` или работать с десятками тысяч cells:

- убрать Python-подготовку больших row dict там, где возможно;
- перенести projection в Oracle package через JSON/staging + `insert select` или PL/SQL `FORALL`;
- сделать idempotency по `draft_id + topology_code/request_id`, чтобы timeout/retry не создавал дубли.

## Решение По Адресации Дробного Отбора

Физическое место может быть родителем дробного отбора, но `pick-face address` не должен указывать на `FRACTIONAL_PICK_FACE`.

Для дробного отбора адресуются дочерние `PICK_FACE_SLOT` через маску дробления. Полноразмерный pick-face address остается только для физической роли `PICK_FACE`.
