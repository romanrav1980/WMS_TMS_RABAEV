# TMS-2 v2 Test Suite — Handoff для следующего агента

**Проект:** `c:\projects\TMS`  
**Ветка:** `feature/transport-dispatch-phase1`  
**Дата передачи:** 2026-05-29  
**Модель для рутины:** `claude-haiku-4-5` (дёшево). Для сложных исправлений — `claude-sonnet-4-6`.

---

## Что уже сделано (не повторять)

### 1. Создан v2 тест-сьют: `tests/transport/v2/` — 136 тестов

| Файл | Тестов | Назначение |
|------|--------|-----------|
| `conftest.py` | — | Фикстуры, seed-константы, contract-поля, helpers |
| `test_01_business_flow_e2e.py` | 18 | Сквозной бизнес-кейс (15 шагов) |
| `test_02_data_fidelity.py` | 25 | Silent drop детектор + wave3 contract checks |
| `test_03_vrp_solver_correctness.py` | 19 | VRP: вместимость, TW, apply |
| `test_04_billing_lifecycle.py` | 14 | Биллинг: открытие → закрытие → оплата |
| `test_05_fleet_crud.py` | 12 | CRUD машин и водителей |
| `test_06_arm_gantt.py` | 17 | Операции ARM, Гант, план-факт |
| `test_07_edge_cases.py` | 16 | Граничные случаи, 404, конфликты |
| `test_08_performance.py` | 15 | SLA + contract check под нагрузкой |
| `screenshot.py` | — | Playwright утилита скриншотов |
| `AGENT_RUNBOOK.md` | — | Пошаговая инструкция запуска |

### 2. Исправления в коде

- **`serv.bat`**: добавлена строка `set "NLS_LANG=AMERICAN_AMERICA.AL32UTF8"` — фикс кодировки `?????????` в статусе рейса
- **`api/wms_api_server/app/db.py`**: добавлена поддержка thick mode через `WMS_ORACLE_THICK_MODE=1` (если NLS_LANG не поможет)

### 3. Найдены три бага (ещё НЕ закрыты)

Все три задокументированы в последнем чате. Твоя задача — подтвердить исправление и закрыть.

---

## Что нужно сделать (задачи по приоритету)

### Задача 1 — Проверить фикс кодировки `?????????` 🔴

**Симптом:** В диспетчере (`http://127.0.0.1:3000/?page=transport`) колонка "Статус" показывает `?????????` вместо "Открыт"/"Отгружен".

**Что уже сделано:** Добавлен `NLS_LANG=AMERICAN_AMERICA.AL32UTF8` в `serv.bat` + thick mode option в `db.py`.

**Что нужно:**
1. Перезапустить `serv.bat`
2. Открыть `http://127.0.0.1:3000/?page=transport`
3. Проверить колонку Статус — должна показывать кириллицу
4. Если всё ещё `?????????`:
   ```bat
   rem Добавить в serv.bat перед строкой WMS_ORACLE_USER:
   set "WMS_ORACLE_THICK_MODE=1"
   ```
   И перезапустить. Thick mode требует Oracle Instant Client на машине.
5. Если кириллица появилась → добавить тест в `test_02_data_fidelity.py`:
   ```python
   def test_task_condition_is_not_question_marks(self, session, plan_date):
       tasks = api_get(session, "/api/admin/transport/tasks", stdate=plan_date)
       for task in tasks[:5]:
           cond = task.get("condition") or task.get("CONDITION") or ""
           assert "?" not in cond or cond == "", \
               f"CONDITION='{cond}' — кириллица не декодируется, кодировочный баг"
   ```

### Задача 2 — Очистить тестовый мусор (31 пустой рейс) 🟠

**Симптом:** На дату 29.05.2026 в диспетчере висят 31 пустой рейс ("⚠ 31 пустых") — остатки от тестовых прогонов.

**Что нужно:**
```sql
-- Выполнить в Oracle SQL Developer / sqlplus
-- Отменить все пустые тестовые рейсы на 29.05.2026
UPDATE RABAEV.RRL_TRANSPORT_TASK
   SET DELETED = 1
 WHERE SHIPMENT_DATE = DATE '2026-05-29'
   AND (SELECT COUNT(*) FROM RABAEV.RRL_SBORKA_PALLETS SP
        WHERE SP.TRANSTASK_ID = RRL_TRANSPORT_TASK.ID
          AND SP.CONDITION <> 2) = 0
   AND CONDITION NOT IN ('Отгружен', 'Отменён');
COMMIT;
```

После этого: обновить страницу диспетчера → 0 пустых рейсов.

### Задача 3 — Запустить тесты по AGENT_RUNBOOK.md 🟠

**Порядок строго по AGENT_RUNBOOK.md:**

```bash
# Установить зависимости (один раз)
pip install pytest-html playwright
python -m playwright install chromium

# Папка для отчётов
mkdir reports\screenshots

# Запускать группами, исправлять ошибки между группами
# ВАЖНО: seed-дата = 2026-05-24 (НЕ 2026-05-29)
set TMS_PLAN_DATE=2026-05-24
```

Запуск каждой группы:
```bash
# Группа 1 — Data Fidelity (приоритет: ПЕРВАЯ)
pytest tests/transport/v2/test_02_data_fidelity.py -v --tb=short --html=reports/01_data_fidelity.html --self-contained-html

# Группа 2 — E2E бизнес-кейс
pytest tests/transport/v2/test_01_business_flow_e2e.py -v --tb=short --html=reports/02_business_flow.html --self-contained-html

# ... и так далее по AGENT_RUNBOOK.md
```

**После каждой прошедшей группы — скриншот:**
```bash
python tests/transport/v2/screenshot.py --page dispatcher --out reports/screenshots/01_dispatcher.png
python tests/transport/v2/screenshot.py --page planner --out reports/screenshots/02_planner.png
```

### Задача 4 — Исправить падающие тесты 🟡

При падении теста:
1. Прочитать assert message — он указывает конкретное поле и место
2. Открыть `api/wms_api_server/app/services/transport_service.py`
3. Найти маппинг: SQL `AS FIELD` → `o.get("FIELD")` → `Model(field=...)`
4. Исправить минимальным патчем
5. Повторить только упавший тест: `pytest -k "test_name" -v`
6. Когда зелёный — повторить всю группу

### Задача 5 — Итоговый коммит 🟢

После того как ВСЕ группы зелёные:

```bash
cd c:\projects\TMS
git add tests/transport/v2/ api/wms_api_server/app/db.py serv.bat
git commit -m "Add TMS-2 v2 test suite (136 tests) + Oracle charset fix"
```

---

## Ключевые факты для понимания контекста

### Архитектура
- API: FastAPI + python-oracledb → Oracle 11g схема RABAEV, порт 8088
- Frontend: React 19 + Vite, роутинг через `?page=`, порт 3000
- Seed: миграции 046 + 047 создали 77 магазинов, 15 машин, ~385 СТ

### Ключевые URL
| Страница | URL |
|---------|-----|
| Диспетчер | http://127.0.0.1:3000/?page=transport |
| VRP-планировщик | http://127.0.0.1:3000/?page=planner |
| Гант | http://127.0.0.1:3000/?page=gantt |
| Флот | http://127.0.0.1:3000/?page=fleet |
| API docs | http://127.0.0.1:8088/docs |

### Seed-данные
- **СТ на 2026-05-24**: ~308 штук (основная дата для тестов)
- **СТ на 2026-05-25**: ~77 штук (1/5 от общего)
- **Seed машины**: ID 9201–9215
- **Seed склады**: ID 9201, 9202, 9203
- Устанавливать `TMS_PLAN_DATE=2026-05-24` при запуске тестов

### Oracle кодировка
- Стандартная кодировка старых русских Oracle: `CL8MSWIN1251`
- Если `?????????` в статусах — выполни запрос:
  ```sql
  SELECT VALUE FROM NLS_DATABASE_PARAMETERS WHERE PARAMETER='NLS_CHARACTERSET';
  ```
- Если `CL8MSWIN1251` → нужен `WMS_ORACLE_THICK_MODE=1` в `serv.bat`
- Если `AL32UTF8` → уже должно работать после `NLS_LANG`

### Почему v2 тесты важны
v1 тесты проверяли только HTTP 200. Из-за этого пропустили gap: `ZONE_TIME_PLAN_IN/OUT` выбирался в SQL, но не прокидывался в `VrpOrder.tw_from/tw_to`. VRP работал на дефолтных окнах `(0, 1080)`. v2 ловит такое через `test_vrp_stops_not_all_default_tw`.

### Правила кода
- Все мутации Oracle — только через пакеты `RRL_*` (прямой INSERT/UPDATE запрещён кроме `RRL_TT_OPERATIONS` и `RRL_PLANNER_PLANS`)
- CSS — только в `admin/wms_admin_frontend/src/styles.css`
- Pydantic — только в `schemas.py`
- `.cs` файлы — только через PowerShell + `GetEncoding(1251)`, не через Edit/Write

---

## Файлы которые НЕ трогать
- `WindowsApplication2/` — C# WinForms легаси, работает параллельно
- Oracle пакеты `RRL_TRASPORT_TASK_ADD`, `RRL_TT_ADD_PALL`, `RRL_TT_REORDER_ADR`, `RRL_TT_SET_TRANSCOMMENT`, `TRANSPORT_TASK` — не менять

---

## Готовность к завершению

Когда все задачи выполнены, убедись что:
- [ ] Статус рейсов показывает кириллицу (не `?????????`)
- [ ] 31 пустой рейс убран
- [ ] 136 тестов запущены, все PASSED или объяснены SKIP
- [ ] HTML отчёты созданы в `reports/`
- [ ] Скриншоты созданы в `reports/screenshots/`
- [ ] git commit сделан
