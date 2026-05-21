# Финальное ТЗ: Модуль управления рейсами (Transport Management)

> AI-ассистент. Дата: 2026-05-21. Статус: финальная версия.
> Источники: Form1.cs, TRANSPORT.cs, VODITEL.cs, BillingTransport.cs,
> Oracle DDL (RRL_TRANSPORT_TASK, RRL_ADDR, RRL_TR_VEHICLE и др.),
> wiki/codex/transport_dispatch_assignment_tz.md (детальный разбор).

---

## Суть

Перенести управление транспортом из C# WinForms в FastAPI + React, добавить три уровня планирования: ручное → полу-автоматическое → полностью автоматическое. Oracle остаётся системой отсчёта, C# продолжает работать параллельно без изменений.

---

## Три уровня системы

```
Уровень 1 — РУЧНОЙ      Диспетчер сам выбирает СТ, назначает на рейс
Уровень 2 — ПОЛУАВТО    Авто-кластеризация, TSP-последовательность, цветовые подсказки
Уровень 3 — АВТО        Три независимых VRP-решателя, диспетчер выбирает лучший вариант
```

---

## Контекст существующей системы

**Единица назначения — СТ** (сборочное задание = все паллеты для одного адреса/заказа).
`RRL_TT_ADD_PALL(TT_ID, ST_NUMBER, user_id)` → обновляет `RRL_SBORKA_PALLETS.TRANSTASK_ID`.
После каждого назначения: `RRL_TT_REORDER_ADR(TT_ID)` → пересортировка по `RRL_ADDR.ORD`.

**Ключевые данные уже есть в Oracle:**
- `RRL_ADDR.SHIROTA / DOLGOTA` — координаты адресов (не используются сейчас)
- `RRL_TT_BILL_PRICE_KM` — тарификация по дистанции
- `RRL_TRANSPORT_TASK.HOURS / RANGE1` — плановые часы и км (не вычисляются)

---

## Модель данных — дополнения (миграции 044–045)

| Таблица | Что добавляется | Зачем |
|---------|----------------|-------|
| `RRL_TR_VEHICLE` | `WEIGHT_CAPACITY NUMBER`, `VOLUME_CAPACITY NUMBER` | Прогресс-бар по весу |
| `RRL_ADDR` | `SERVICE_MIN NUMBER(3) DEFAULT 15`, `DELIVERY_TIME_FROM/TO VARCHAR2(5)` | Временны́е окна |
| NEW `RRL_ADDR_DISTANCE_MATRIX` | `ADDR_FROM/TO, DIST_METERS, DURATION_SEC, CALC_DATE` | Кэш OSRM матрицы |
| NEW `RRL_TT_ROUTE_TEMPLATE` | `DOW, TRANSTYPE, ADDR_SIGNATURE, ADDR_LIST CLOB, TOTAL_KM, QUALITY_SCORE` | Шаблоны маршрутов |
| NEW `RRL_TT_RL_CORRECTIONS` | `ST_NUMBER, FROM/TO_TASK_IDX, ADDR_FROM/TO, DOW` | Обучение на правках диспетчера |
| NEW `RRL_TT_AUTO_PLAN_SESSION` | `PLAN_DATE, SOLVER_USED, RESULT_TASK_COUNT, TOTAL_KM, ACCEPTED_BY, EDITS_COUNT` | Аудит авто-планирования |

---

## Oracle-пакет RRL_TRANSPORT_API

```sql
PROCEDURE create_task(p_transtype, p_shipment_date, p_user_id, OUT p_task_id)
PROCEDURE update_task(p_task_id, p_vehicle_num, p_driver_id, p_dock, ...)
PROCEDURE assign_st_list(p_task_id, p_st_list SYS.ODCIVARCHAR2LIST, p_user_id, OUT p_warnings)
PROCEDURE unassign_st(p_task_id, p_st_number, p_user_id)
PROCEDURE reorder_by_sequence(p_task_id, p_st_ords SYS.ODCIVARCHAR2LIST)
PROCEDURE close_task(p_task_id, p_user_id)
PROCEDURE cancel_task(p_task_id, p_user_id)
FUNCTION  get_available_sts(p_date, p_unassigned_only, p_addr_mask, ...) RETURN SYS_REFCURSOR
```

Все существующие функции (`RRL_TRASPORT_TASK_ADD`, `RRL_TT_ADD_PALL` и т.д.)
вызываются **внутри пакета** — прямые вызовы из API запрещены.

---

## API (FastAPI router `transport`)

### Данные
```
GET  /transport/tasks?date=                    # рейсы + метрики (km, h, cost)
GET  /transport/pallets/available?date=&...    # СТ с координатами и временны́ми окнами
GET  /transport/planning/summary?date=          # итоги дня: СТ, палл, машины, покрытие
GET  /transport/docks/schedule?date=            # Gantt доков
```

### Назначение
```
POST   /transport/tasks                        # создать рейс (+ сразу назначить st_numbers)
PATCH  /transport/tasks/{id}                   # обновить (ТС, водитель, дата, дока)
POST   /transport/tasks/{id}/assign            # { "st_numbers": [...] }
DELETE /transport/tasks/{id}/st/{st_number}    # снять СТ
POST   /transport/tasks/{id}/close             # подтвердить отгрузку
POST   /transport/tasks/{id}/cancel
```

### Оптимизация (уровень 2)
```
POST   /transport/tasks/{id}/optimize-sequence        # TSP по координатам, preview
POST   /transport/tasks/{id}/optimize-sequence/confirm
GET    /transport/pallets/nearby?task_id=&radius_km=  # СТ-соседи для рейса
GET    /transport/tasks/{id}/manifest                 # PDF-манифест водителя
```

### Авто-план (уровень 3)
```
POST   /transport/planning/auto-plan           # { date, solver_priority, ortools_time_limit_sec }
                                               # возвращает до 3 вариантов, НЕ создаёт рейсы
POST   /transport/planning/accept              # { session_id, variant, edits } → создать в Oracle
GET    /transport/planning/templates?dow=&transtype=
DELETE /transport/planning/templates/{id}
POST   /transport/planning/osrm-sync           # фоновая пересинхронизация матрицы
```

### Справочники
```
GET/POST/PATCH /transport/vehicles
GET/POST/PATCH /transport/drivers
GET            /transport/billing/orders
POST           /transport/billing/orders/{id}/close
```

---

## Три VRP-решателя (уровень 3)

### Решатель 1 — Шаблонное планирование (< 50 мс)
- Накапливает исторические маршруты как шаблоны по `(day_of_week, transtype)`
- Jaccard similarity по множеству адресов; если > 0.85 → предлагает шаблон
- Корректирует объёмы под сегодняшние факты
- Обучается на правках диспетчера (`RRL_TT_RL_CORRECTIONS`): 3 одинаковых правки → обновляет шаблон
- **Работает с первой недели**, становится лучше каждый месяц

### Решатель 2 — OR-Tools VRP (≤ 10 сек)
- Google OR-Tools (LNS + guided local search)
- Входные данные: матрица `RRL_ADDR_DISTANCE_MATRIX` (OSRM), вместимость, временны́е окна
- Seed: Clarke-Wright Savings Algorithm (~100 мс, O(N² log N))
- Качество: ~1–3% от оптимума при 10-секундном лимите
- Единственный, кто **полностью учитывает временны́е окна**

### Решатель 3 — Attention Model (нейросеть, < 500 мс на CPU)
- Трансформер (Kool et al., ICLR 2019), policy gradient REINFORCE
- Обучается на синтетических (100k экземпляров) + исторических данных
- Переобучается ежемесячно в фоне на одобренных диспетчером рейсах
- Качество: ~3–5% от оптимума для N ≤ 100
- **Быстрее OR-Tools**, но не учитывает временны́е окна

### Оркестрация
```
Запрос auto-plan →
  1. Jaccard-поиск шаблона (< 50 мс)
     ├─ similarity > 0.85 → Шаблон как вариант 1
     └─ нет
  2. Attention Model + OR-Tools запускаются параллельно
  3. Применить RL-коррекции к каждому варианту
  → Вернуть лучшие 2–3 варианта диспетчеру
```

### OSRM — геоданные
```
Источник:    OpenStreetMap, выгрузка России (Geofabrik)
Деплой:      Docker self-hosted, preprocessing 1 раз
Table API:   матрица 50×50 за < 100 мс
Route API:   геометрия маршрута → polyline на карте
Обновление:  ночной cron, воркер vrp_matrix_worker.py
```

---

## Жизненный цикл рейса

```
CREATED → PLANNED → DOCK_RESERVED → LOADING → DISPATCHED
                                              ↑
                                         водитель сканирует
                                         паллеты через TSD
```

Отмена возможна из любого статуса кроме `DISPATCHED`.

---

## UI-экраны (React Admin)

### Режим Планирования
- Статистика дня: СТ / паллеты / машины / покрытие
- Карта адресов (Leaflet + OSM, точки окрашены по районам)
- Панель авто-плана: 2–3 варианта с таблицей сравнения (км / часы / стоимость / учёт окон)
- Выбор варианта → редактирование → «Принять»

### Режим Назначения (основной рабочий экран)
- Левая панель: карточки рейсов (прогресс-бар палл+вес, км, стоимость, дока)
- Правая панель: таблица СТ с чекбоксами, цвета по районам, live-итог P/M/V
- Нижний грид: состав рейса, drag-and-drop порядка, кнопка ✕
- Кнопки: «+ Создать рейс», «→ Добавить в рейс», «⚡ Оптим. маршрут»

### Дополнительные экраны
- Gantt доков (вкладка внутри режима Назначения)
- Манифест водителя (PDF: порядок загрузки = обратный порядку объезда)
- TSD водителя: список рейсов → сканирование паллет → закрыть рейс
- CRUD транспортных средств и водителей

---

## React — структура компонентов

```
src/components/Transport/
  DispatchBoard.tsx          — root layout, переключатель режимов
  planning/
    PlanningModeView.tsx     — режим Планирования
    PlanningMap.tsx          — Leaflet-карта адресов
    AutoPlanPanel.tsx        — варианты авто-плана + таблица сравнения
    AutoPlanDraftCard.tsx    — карточка одного варианта
  assignment/
    AssignmentModeView.tsx   — три панели
    TransportTaskCard.tsx    — карточка рейса (прогресс-бары, метрики)
    AvailableOrdersTable.tsx — СТ с чекбоксами, цвета, live-итог
    TaskPalletsTable.tsx     — состав рейса, drag-and-drop
    DockScheduleGantt.tsx    — Gantt доков
  shared/
    AssignmentSummaryBar.tsx — строка P=... M=... V=...
    AssignmentWarnings.tsx   — inline предупреждения
    ManifestView.tsx         — манифест PDF/print
  hooks/
    useDispatchBoard.ts
    useAutoPlan.ts           — вызов /auto-plan, polling статуса
    useRouteMetrics.ts       — Haversine на клиенте (live-метрики)
    useCapacityWarnings.ts
    useDockSchedule.ts
```

---

## Воркеры

```
vrp_matrix_worker.py         — ночная пересинхронизация OSRM-матрицы
attention_train_worker.py    — ежемесячное переобучение нейросети
template_cleanup_worker.py   — удаление устаревших шаблонов
```

---

## Критерии приёмки (сводные)

### Уровень 1 (ручной)
- [ ] Рейсы и СТ загружаются на выбранную дату
- [ ] Чекбокс + «Создать рейс» / «Добавить в рейс» работают
- [ ] Снятие СТ с рейса
- [ ] C# WinForms видит всё без изменений

### Уровень 2 (полу-авто)
- [ ] Цветовая индикация районов в таблице и на карте совпадают
- [ ] «⚡ Оптим. маршрут» предлагает TSP-порядок, диспетчер подтверждает
- [ ] Прогресс-бар обновляется при каждом изменении состава
- [ ] Манифест: порядок загрузки = обратный доставке

### Уровень 3 (авто)
- [ ] `/auto-plan` возвращает ≥ 2 варианта за < 15 сек (50 СТ)
- [ ] Шаблон с similarity > 0.85 появляется как вариант 1 (< 50 мс)
- [ ] OR-Tools не нарушает вместимость ТС
- [ ] «Принять» создаёт рейсы в Oracle, сессия в аудите
- [ ] После 3 правок диспетчера шаблон обновляется

### Load-test (evidence-driven)
- [ ] Smoke: создать рейс → 5 СТ → оптим. → манифест
- [ ] Load: авто-план 50 СТ + 8 машин → черновики < 15 сек
- [ ] Артефакты: `report.json`, `report.md`, скриншоты всех 3 режимов

---

## Оценка трудоёмкости

| Этап | Содержание | Дней |
|------|-----------|------|
| **0** | Oracle: миграции 044–045, пакет RRL_TRANSPORT_API | 3 |
| **1** | FastAPI: базовые CRUD + назначение + манифест | 3 |
| **2** | React: уровень 1 (ручной) — полный рабочий стол | 5 |
| **3** | React: уровень 2 — карта, TSP, метрики, Gantt | 5 |
| **4** | OSRM Docker + матрица + Clarke-Wright | 2 |
| **5** | OR-Tools VRP + шаблонный движок | 4 |
| **6** | Attention Model + воркеры | 5 |
| **7** | React: уровень 3 — панель авто-плана | 3 |
| **8** | Load-tests + evidence | 2 |
| **Итого** | | **~32 рабочих дня** |

**Минимальная рабочая версия (этапы 0–3):** ~16 дней — полный ручной + полу-авто стол.
**Полная версия с авто-планом:** ~32 дня.
