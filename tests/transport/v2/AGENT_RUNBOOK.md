# TMS-2 v2 — Runbook для агента-исполнителя

**Кому:** соседний агент (Claude Sonnet / Haiku)  
**Цель:** провести все тесты v2, исправить найденные ошибки, задокументировать результаты  
**Модель для рутины:** `claude-haiku-4-5` (дёшево и достаточно)  
**Модель для сложных исправлений:** `claude-sonnet-4-6`

---

## Шаг 0 — Установить зависимости (один раз)

```bash
pip install pytest-html playwright
python -m playwright install chromium
```

Проверить что всё поднято:

```bash
# API сервер
curl -s http://127.0.0.1:8088/api/admin/transport/available-sts?stdate=2099-01-01 | python -m json.tool

# Фронтенд
curl -s http://127.0.0.1:3000/?page=transport | findstr /i "TMS\|React\|html"
```

Если не запущено — запустить `serv.bat` и `front.bat` из корня проекта.

---

## Шаг 1 — Убедиться что seed-данные есть

```bash
cd c:\projects\TMS
python -m pytest tests/transport/v2/test_01_business_flow_e2e.py::TestStep01AvailableSTs::test_at_least_100_sts_on_seed_date -v
```

**Если PASSED** → идти дальше.  
**Если FAILED/SKIP** → применить seed-миграции:

```bash
# Найти скрипт применения миграций и запустить 046 + 047
python db/migrations/2026-05-23_dobrotseny_seed/run_seed.py
# или вручную через sqlplus / cx_Oracle
```

---

## Шаг 2 — Запуск тестов: порядок и команды

Запускать **строго по порядку**. Каждая следующая группа зависит от предыдущей.  
При ошибках — исправлять до перехода к следующей группе.

---

### Группа 1 — Data Fidelity (приоритет 🔴 критичный)

**Почему первая:** если данные из Oracle теряются в pipeline — все остальные тесты дадут ложные результаты.

```bash
python -m pytest tests/transport/v2/test_02_data_fidelity.py \
  -v --tb=short \
  --html=reports/01_data_fidelity.html --self-contained-html
```

**При провале любого теста:**
1. Читать сообщение об ошибке — оно указывает конкретное поле и где искать
2. Открыть `api/wms_api_server/app/services/transport_service.py`
3. Найти SQL-запрос (по имени метода из трейсбека)
4. Проверить три точки: `SELECT ... AS field` → `o.get("field")` → `Model(field=...)`
5. Исправить пропуск → повторить тест

**Скриншот после PASSED:** открыть `http://127.0.0.1:3000/?page=transport` → сделать скриншот таблицы СТ с заполненными колонками ZONE, VERIFY_PERC, TIME_FROM.

```bash
python tests/transport/v2/screenshot.py --page dispatcher --out reports/screenshots/01_data_fidelity_dispatcher.png
```

---

### Группа 2 — Сквозной бизнес-кейс (приоритет 🔴 критичный)

**Почему вторая:** подтверждает что весь бизнес-процесс работает end-to-end.

```bash
python -m pytest tests/transport/v2/test_01_business_flow_e2e.py \
  -v --tb=short \
  --html=reports/02_business_flow.html --self-contained-html
```

**При провале:**
- `TestStep02WarehouseFilter` → проверить параметр `ware_ids` в `list_available_sts()`
- `TestStep04to07TripCreation` → проверить Oracle-пакет `RRL_TRASPORT_TASK_ADD`
- `TestStep08to10TripClose` → проверить `TRANSPORT_TASK.can_print()` в Oracle
- `TestStep13to15Billing` → проверить `RRL_ADD_TT_2_BILLINGORDER`

**Скриншоты после PASSED:**

```bash
# 1. Таблица доступных СТ с назначенным рейсом
python tests/transport/v2/screenshot.py --page dispatcher --out reports/screenshots/02a_st_table.png

# 2. Таблица рейсов (маршруты)
python tests/transport/v2/screenshot.py --page routes --out reports/screenshots/02b_routes.png

# 3. Биллинг — реестр счетов
python tests/transport/v2/screenshot.py --page billing --out reports/screenshots/02c_billing.png
```

---

### Группа 3 — VRP Корректность (приоритет 🟠 высокий)

```bash
python -m pytest tests/transport/v2/test_03_vrp_solver_correctness.py \
  -v --tb=short \
  --html=reports/03_vrp_correctness.html --self-contained-html
```

**При провале `test_non_default_time_windows_present`:**

Это тот самый gap с ZONE_TIME_PLAN_IN/OUT. Искать в:
```
transport_service.py → get_planner_orders() → SQL SELECT
transport_service.py → solve_vrp() → VrpOrder(tw_from=o.get("TIME_FROM")...)
```

**При провале `test_route_pallets_within_vehicle_max`:**

Проверить `VrpVehicle.max_pallets` — возможно значение берётся не из того поля БД.

**Скриншот после PASSED:**

```bash
# Карта с маршрутами VRP
python tests/transport/v2/screenshot.py --page planner --out reports/screenshots/03_vrp_map.png
```

---

### Группа 4 — Биллинг (приоритет 🟠 высокий)

```bash
python -m pytest tests/transport/v2/test_04_billing_lifecycle.py \
  -v --tb=short \
  --html=reports/04_billing.html --self-contained-html
```

**При провале `test_cannot_bill_open_trip`:**

Проверить что в `billing/open` эндпоинте есть проверка статуса рейса.

**При провале `test_cannot_remove_st_from_billed_trip`:**

Проверить наличие проверки `PAY_ORDER_ID IS NOT NULL` перед удалением СТ.

**Скриншот после PASSED:**

```bash
python tests/transport/v2/screenshot.py --page billing --out reports/screenshots/04_billing_order.png
```

---

### Группа 5 — Fleet CRUD (приоритет 🟡 средний)

```bash
python -m pytest tests/transport/v2/test_05_fleet_crud.py \
  -v --tb=short \
  --html=reports/05_fleet_crud.html --self-contained-html
```

**При провале CRUD-тестов:**

Проверить `routers/transport.py` — наличие POST/PATCH/DELETE для `/vehicles` и `/drivers`.  
Проверить что Oracle-пакеты или прямые INSERT/UPDATE разрешены для этих таблиц.

**Скриншот после PASSED:**

```bash
python tests/transport/v2/screenshot.py --page fleet --out reports/screenshots/05_fleet.png
```

---

### Группа 6 — ARM / Гант (приоритет 🟡 средний)

```bash
python -m pytest tests/transport/v2/test_06_arm_gantt.py \
  -v --tb=short \
  --html=reports/06_arm_gantt.html --self-contained-html
```

**При провале операций:**

Проверить `plan-operations` эндпоинт и таблицу `RRL_TT_OPERATIONS`.

**Скриншот после PASSED:**

```bash
python tests/transport/v2/screenshot.py --page gantt --out reports/screenshots/06_gantt.png
```

---

### Группа 7 — Граничные случаи (приоритет 🟡 средний)

```bash
python -m pytest tests/transport/v2/test_07_edge_cases.py \
  -v --tb=short \
  --html=reports/07_edge_cases.html --self-contained-html
```

**При провале `test_assign_st_to_two_trips_fails`:**

Отсутствует блокировка на уровне Oracle или FastAPI. Добавить проверку `TRANSTASK_ID IS NULL` перед назначением.

---

### Группа 8 — Performance (приоритет 🟢 низкий, запускать последней)

```bash
python -m pytest tests/transport/v2/test_08_performance.py \
  -v --tb=short -s \
  --html=reports/08_performance.html --self-contained-html
```

**При провале SLA:**

Сообщение теста содержит конкретную рекомендацию. Типичные действия:

| Эндпоинт | Диагностика | Действие |
|---------|-------------|---------|
| `available-sts` > 500ms | `EXPLAIN PLAN` на основной SELECT | Индекс на `(STDATE, TRANSTASK_ID)` |
| `planner/orders` > 300ms | Проверить кол-во JOIN | Добавить `ROWNUM` лимит или индекс |
| `vrp/solve` > 20s | Профилировать `get_planner_orders` | Кэш матрицы расстояний |
| `plan-fact` 90д > 2s | `EXPLAIN PLAN` на агрегацию | Индекс на `TRANSPORT_TASK(STDATE)` |

---

## Шаг 3 — Утилита скриншотов

Создать файл `tests/transport/v2/screenshot.py`:

```python
"""
Утилита для скриншотов фронтенда TMS-2.
Используется агентом после успешного прохождения группы тестов.

Использование:
  python screenshot.py --page dispatcher --out reports/screenshots/01_dispatcher.png
  python screenshot.py --page planner    --out reports/screenshots/03_planner.png
  python screenshot.py --page gantt      --out reports/screenshots/06_gantt.png
  python screenshot.py --page billing    --out reports/screenshots/04_billing.png
  python screenshot.py --page fleet      --out reports/screenshots/05_fleet.png
"""
from __future__ import annotations
import argparse
import os
from pathlib import Path

FRONTEND_URL = os.environ.get("TMS_FRONTEND_URL", "http://127.0.0.1:3000")

PAGES = {
    "dispatcher": f"{FRONTEND_URL}/?page=transport",
    "routes":     f"{FRONTEND_URL}/?page=transport",
    "planner":    f"{FRONTEND_URL}/?page=planner",
    "gantt":      f"{FRONTEND_URL}/?page=gantt",
    "billing":    f"{FRONTEND_URL}/?page=transport",
    "fleet":      f"{FRONTEND_URL}/?page=fleet",
    "kpi":        f"{FRONTEND_URL}/?page=kpi",
}

WAIT_SELECTORS = {
    "dispatcher": ".dispatch-trips-table-wrap, table",
    "planner":    ".leaflet-container, canvas",
    "gantt":      ".gantt-svg, svg",
    "billing":    ".billing-orders-table, table",
    "fleet":      ".fleet-vehicles-table, table",
}


def take_screenshot(page_name: str, output_path: str, width: int = 1600, height: int = 900):
    from playwright.sync_api import sync_playwright

    url = PAGES.get(page_name, f"{FRONTEND_URL}")
    selector = WAIT_SELECTORS.get(page_name, "body")

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": width, "height": height})
        page.goto(url, timeout=30_000)
        try:
            page.wait_for_selector(selector, timeout=15_000)
        except Exception:
            pass  # fallback: screenshot anyway
        page.wait_for_timeout(2000)  # дать время на рендер данных
        page.screenshot(path=output_path, full_page=False)
        browser.close()

    print(f"Screenshot saved: {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--page", required=True, choices=list(PAGES.keys()))
    parser.add_argument("--out", required=True)
    parser.add_argument("--width", type=int, default=1600)
    parser.add_argument("--height", type=int, default=900)
    args = parser.parse_args()
    take_screenshot(args.page, args.out, args.width, args.height)
```

---

## Шаг 4 — Итоговый прогон: всё сразу с общим HTML-отчётом

После того как все группы прошли по отдельности:

```bash
python -m pytest tests/transport/v2/ \
  -v --tb=short \
  --html=reports/FULL_REPORT.html --self-contained-html \
  --ignore=tests/transport/v2/test_08_performance.py

# Performance отдельно (медленно):
python -m pytest tests/transport/v2/test_08_performance.py \
  -v --tb=short -s \
  --html=reports/FULL_PERFORMANCE.html --self-contained-html
```

---

## Шаг 5 — Структура отчётов

После прохождения у тебя должна быть следующая структура:

```
tests/transport/v2/reports/
├── 01_data_fidelity.html
├── 02_business_flow.html
├── 03_vrp_correctness.html
├── 04_billing.html
├── 05_fleet_crud.html
├── 06_arm_gantt.html
├── 07_edge_cases.html
├── 08_performance.html
├── FULL_REPORT.html
├── FULL_PERFORMANCE.html
└── screenshots/
    ├── 01_data_fidelity_dispatcher.png
    ├── 02a_st_table.png
    ├── 02b_routes.png
    ├── 02c_billing.png
    ├── 03_vrp_map.png
    ├── 04_billing_order.png
    ├── 05_fleet.png
    └── 06_gantt.png
```

---

## Шаг 6 — Правила исправления кода

### Что можно исправлять самостоятельно
- Пропущенное поле в `o.get("FIELD")` маппинге
- Отсутствующий AS alias в SQL SELECT
- Неправильный ключ словаря (регистр, опечатка)
- Отсутствующая проверка статуса перед мутацией

### Что требует согласования с пользователем
- Изменение схемы Oracle (новая таблица, новый столбец)
- Изменение Oracle-пакетов (`RRL_*`)
- Изменение контракта API (новые обязательные поля в ответе)
- Удаление или переименование эндпоинтов

### Алгоритм при ошибке

```
1. Прочитать assert message — там указано ПОЛЕ и МЕСТО
2. grep по полю в transport_service.py
3. Найти три точки: SQL → dict → model
4. Исправить минимальным патчем
5. Повторить только упавший тест: pytest -k "test_name" -v
6. После green — повторить всю группу
```

---

## Шаг 7 — Что делать с медленными Oracle запросами

Если performance тест падает — запустить диагностику:

```python
# Добавить временно в transport_service.py перед проблемным запросом:
import time
t0 = time.perf_counter()
cursor.execute(sql, params)
rows = cursor.fetchall()
elapsed = (time.perf_counter() - t0) * 1000
if elapsed > 300:
    import logging
    logging.warning(f"SLOW QUERY {elapsed:.0f}ms: {sql[:120]}")
```

Затем запросить у DBA `EXPLAIN PLAN FOR <sql>` и добавить индекс:

```sql
-- Типичные индексы для TMS
CREATE INDEX IDX_ST_DATE_TT ON RRL_V_AVAILABLE_STS_BASE (STDATE, TRANSTASK_ID);
CREATE INDEX IDX_TT_STDATE   ON TRANSPORT_TASK (STDATE, CONDITION);
```

После добавления индекса — повторить performance тест.

---

## Чеклист завершения

- [ ] Установлены `pytest-html` и `playwright`
- [ ] Seed-данные есть (≥100 СТ на ближайшую дату)
- [ ] Группа 1 (Data Fidelity): все PASSED + HTML + скриншот
- [ ] Группа 2 (E2E Flow): все PASSED + HTML + 3 скриншота
- [ ] Группа 3 (VRP): все PASSED + HTML + скриншот
- [ ] Группа 4 (Billing): все PASSED + HTML + скриншот
- [ ] Группа 5 (Fleet): все PASSED + HTML + скриншот
- [ ] Группа 6 (ARM/Gantt): все PASSED + HTML + скриншот
- [ ] Группа 7 (Edge Cases): все PASSED + HTML
- [ ] Группа 8 (Performance): все PASSED + HTML
- [ ] `FULL_REPORT.html` сформирован
- [ ] Все найденные ошибки исправлены и зафиксированы в git commit
