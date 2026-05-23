# Результат: Two-Camera Scale Acceptance — 2026-05-23

Статус: большой нагрузочно-функциональный прогон warehouse-map после исправления bulk save architecture.

## Контекст

Тест продолжает `large_warehouse_map_functional_testing_tz.md` и проверяет, что исправленный `projection/save-to-topology` выдерживает большой двухкамерный canvas без возврата к per-cell сохранению.

Сценарий запускался скриптом:

- `admin/wms_admin_frontend/runtime/test-evidence/warehouse-map-two-camera-scale-fixture.cjs`

Runtime evidence остается вне commit scope:

- `admin/wms_admin_frontend/runtime/test-evidence/warehouse-map-two-camera-scale-fixture-result.json`
- `admin/wms_admin_frontend/runtime/test-evidence/warehouse-map-two-camera-scale-fixture-report.md`
- `admin/wms_admin_frontend/runtime/test-evidence/warehouse-map-two-camera-scale-fixture-ui.png`

## Прогон

- `run_id = 20260522223805`
- `ware_id = 0`
- `draft_id = 180df8b4f7954e57a7d6d182a903893b`
- `canvas_id = 38`
- `topology_id = 31`
- `pick_route_id = 119`
- `camera_a_id = 53`
- `camera_b_id = 54`

## Масштаб

| Роль | Количество |
| --- | ---: |
| `PICK_FACE` | `1202` |
| `STORAGE` | `3000` |
| `TRANSPORT_STAGING` | `72` |
| `FILM_WRAP` | `40` |
| `GATE` | `8` |
| `AISLE` | `720` |
| `BLOCKED` | `13858` |

Итоговая Oracle projection:

- topology cells: `5042`;
- cell slots: `8`;
- pick slots: `4`;
- storage slots: `4`;
- route rows: `200`;
- storage/non-pick route rows: `0`;
- cameras: `2`;
- camera links: `1`.

Распределение topology cells по камерам:

```json
{
  "53": 2821,
  "54": 2221
}
```

## Фазовые Времена API

По `RRL_API_CALL_LOG` / admin API audit:

| Фаза | API | Time |
| --- | --- | ---: |
| Address pick faces | `pick-face-addresses/generate` | `302 ms` |
| Generate fractional pick slots | `small-pick-faces/generate` | `301 ms` |
| Generate fractional storage slots | `storage-slots/generate` | `273 ms` |
| Build route draft | `route/build` | `267 ms` |
| Validate draft | `validate` | `293 ms` |
| Save canvas DB | `save-to-db` | `1389 ms` |
| Save camera metadata | `metadata` | `288 ms` |
| Save topology projection | `projection/save-to-topology` | `2002 ms` |
| Save route DB | `route/save-to-db` | `1670 ms` |
| Publish Oracle | `publish-oracle` | `876 ms` |
| Reload warehouse state | `GET /warehouse-map/warehouses/0/state` | `2377 ms` |

Ключевой bottleneck, который ранее занимал сотни секунд, теперь уложился в `2002 ms` на `5042` cells.

## Проверки

Все проверки скрипта прошли:

- подготовлены роли масштаба `storage=3000`, `pick=1202`;
- назначены адреса pick-face уровня маршрута: `200`;
- созданы дробные slots: `pickSlots=4`, `storageSlots=4`;
- route draft построен только по pick cells: `rows=200`, `skippedNonPick=108`;
- draft validation вернул `valid=true`;
- созданы две камеры и одна связь камер;
- topology сохранена на масштабе: `cells=5042`, `slots=8`;
- route сохранен в Oracle: `rows=200`, Oracle validation `valid=true`;
- publish выполнен со статусом `PUBLISHED`;
- reload вернул опубликованные canvas/topology/route;
- reload подтвердил две камеры и одну связь;
- topology cells распределены по обеим камерам;
- route не содержит storage/non-pick rows.

## Вывод

Большой two-camera scale acceptance пройден. Исправление массового сохранения считается рабочим для текущего масштаба `5042` topology cells: операция `projection/save-to-topology` укладывается в целевой коридор около `2-3 секунд`.

Следующий риск остается архитектурным для существенно больших canvas: при росте до десятков тысяч persisted cells нужно переходить к Oracle-side bulk package/staging или JSON_TABLE/insert-select, сохраняя правило `никаких per-cell DB round-trip`.
