# TMS-2 — v2 Test Suite

## Почему v2?

v1 тесты (sprint N load tests) проверяли **HTTP 200 и latency**. Они пропустили gap:
- `ZONE_TIME_PLAN_IN/OUT` выбирался в SQL, но не прокидывался в `VrpOrder.tw_from/tw_to`
- VRP работал на дефолтных окнах `(0, 1080)` вместо реальных
- Тест `saw_time_window = True` мог проходить через fallback-эвристику, не через Oracle

**v2 принцип:** каждый тест проверяет **данные**, а не только статус ответа.

---

## Структура

```
tests/transport/v2/
├── conftest.py                     # Фикстуры, seed-константы, helpers
├── test_01_business_flow_e2e.py    # Сквозной бизнес-кейс (15 шагов)
├── test_02_data_fidelity.py        # Данные из Oracle не теряются в pipeline
├── test_03_vrp_solver_correctness.py # VRP: вместимость, TW, машины, apply
├── test_04_billing_lifecycle.py    # Биллинг: создание → закрытие → оплата
├── test_05_fleet_crud.py           # CRUD ТС и водителей
├── test_06_arm_gantt.py            # Операции, Гант, план-факт
├── test_07_edge_cases.py           # Граничные случаи и обработка ошибок
└── test_08_performance.py          # SLA + Oracle query performance
```

---

## Запуск

### Предусловия

1. API сервер запущен на порту 8088 (`serv.bat`)
2. Seed-миграции применены: `046_apply.sql` + `047_apply.sql` (Добра Цен)
3. Python 3.11+, pytest, requests

```bash
pip install pytest requests
```

### Запуск всего v2 набора

```bash
cd c:\projects\TMS
pytest tests/transport/v2/ -v --tb=short
```

### Запуск отдельного файла

```bash
pytest tests/transport/v2/test_02_data_fidelity.py -v
```

### Запуск с явным URL / авторизацией

```bash
set TMS_API_BASE_URL=http://192.168.1.100:8088
set TMS_AUTH=dispatcher:password123
pytest tests/transport/v2/ -v
```

### Запуск только performance-тестов

```bash
pytest tests/transport/v2/test_08_performance.py -v -s
```

---

## Сквозной бизнес-кейс (test_01)

| Шаг | Описание | Что проверяется |
|-----|---------|-----------------|
| 1 | Таблица СТ | Поля заполнены, данные из Oracle |
| 2 | Фильтр по складу | Сужает результат, фильтр работает корректно |
| 3 | Кластеры | Группировка по районам, сумма паллет совпадает |
| 4 | Создать рейс | TT_ID получен |
| 5 | Назначить СТ | Итоги П/кг в рейсе = сумме по СТ |
| 6 | Рейс в списке | Поля корректны |
| 7 | Назначить машину | Номер сохранился в рейсе |
| 8 | can_print | 200 или 422 с деталью |
| 9 | Закрыть рейс | |
| 10 | СТ ушли из пула | unassigned_only=true не возвращает их |
| 11 | Планировать операции | Цепочка ≥2 операций |
| 12 | Гант | Машина отображается |
| 13 | Создать счёт | order_id получен |
| 14 | Счёт содержит рейс | TT_ID в списке задач счёта |
| 15 | Закрыть и оплатить | closed=1, payed=1 |

---

## Data Fidelity тесты (test_02)

Ключевая группа — детектирует "silent drop" полей:

| Тест | Что ищет |
|------|---------|
| `test_time_from_is_not_all_zero` | TIME_FROM из ZONE_TIME_PLAN_IN не пустой |
| `test_verify_perc_is_not_all_null` | VERIFY_PERC прокидывается из Oracle |
| `test_planner_orders_tw_matches_available_sts` | Один и тот же СТ — одинаковые TW в двух эндпоинтах |
| `test_vrp_stops_not_all_default_tw` | **Главный тест**: хотя бы один stop с non-default TW |
| `test_vrp_tw_from_matches_planner_orders` | tw_from в VRP-stop = конвертация TIME_FROM в минуты |
| `test_vrp_tw_strict_flag_propagated` | TW_STRICT из Oracle появляется в VRP |

---

## VRP корректность (test_03)

| Тест | Инвариант |
|------|---------|
| `test_route_pallets_within_vehicle_max` | total_pallets ≤ max_pallets |
| `test_route_weight_within_vehicle_max` | total_kg ≤ max_tons × 1000 |
| `test_non_default_time_windows_present` | Не все TW = (0, 1080) |
| `test_all_route_vehicles_are_from_fleet` | Нет фантомных machine_id |
| `test_apply_creates_tasks` | apply() создаёт N рейсов = N маршрутов |

---

## Производительность — SLA пороги (test_08)

| Эндпоинт | p95 SLA | Примечание |
|---------|---------|-----------|
| GET /available-sts | 500 ms | Тяжёлый JOIN |
| GET /tasks | 300 ms | |
| GET /planner/orders | 300 ms | |
| GET /clusters | 200 ms | GROUP BY |
| POST /planner/solve | 20 s RTT | time_limit=15s |
| POST /distance-matrix/rebuild | 60 s | haversine |
| GET /plan-fact (90 дней) | 2 000 ms | Агрегация |
| GET /vehicles/gantt | 500 ms | JOIN operations |

При превышении SLA тест выводит конкретную рекомендацию (индекс, HINT, ограничение выборки).

---

## Если тест упал

### "Данные из Oracle не прокидываются"
Проверить: SQL SELECT → dict-ключ → маппинг в конструктор модели.
Паттерн поиска: `o.get("FIELD_NAME")` в `transport_service.py`.

### "can_print не прошёл — skip"
Seed-данных недостаточно для прохождения проверки минимальной загрузки.
Добавить больше СТ в seed или уменьшить порог can_print в тестовом окружении.

### "Нет seed-СТ в ближайшие 7 дней"
Повторно применить миграцию `db/migrations/2026-05-23_dobrotseny_seed/`.
СТ в seed имеют даты +1/+2 дня от момента применения.

### Performance тест падает на p95
1. Запустить `EXPLAIN PLAN FOR <запрос>` в Oracle SQL Developer
2. Проверить Full Table Scan на больших таблицах
3. Добавить индекс или ROWNUM/pagination hint
4. Пересмотреть JOIN порядок
