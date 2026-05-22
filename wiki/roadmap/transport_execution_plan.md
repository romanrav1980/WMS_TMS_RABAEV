# Transport Execution Plan

Живой чеклист. После завершения sub-фазы: ставь ✅, пиши коммит-хэш и дату.

Roadmap с деталями: [transport_roadmap.md](transport_roadmap.md)
ТЗ: [transport_dispatch_tz.md](../requirements/transport_dispatch_tz.md) · [transport_billing_tz.md](../requirements/transport_billing_tz.md)

---

## Phase 2 — Полуавтоматическое распределение

### 2.1 — Кластеры на панели (~2 дня)
- [x] `GET /api/admin/transport/clusters` — группировка свободных СТ по RAION
- [x] `list_clusters()` в `transport_service.py` (группировка в Python поверх list_available_sts)
- [x] Переключатель «По СТ / По районам» в левой панели
- [x] Компонент `ClusterCard` с раскрываемым списком СТ и счётчиком выбранных

**Коммит:** `_______` · **Дата:** 2026-05-22

---

### 2.2 — Рейс из кластера (~2 дня)
- [ ] `POST /api/admin/transport/clusters/{raion}/create-task`
- [ ] Атомарная транзакция: ADD → цикл ADD_PALL → REORDER_ADR
- [ ] Модальное окно выбора машины/водителя на кнопке «Создать рейс»
- [ ] После создания: кластер исчезает, новый рейс выделяется в правой панели

**Коммит:** `_______` · **Дата:** ______

---

### 2.3 — Live-метрики машины (~2 дня)
- [ ] `MAX_WEIGHT` и `MAX_PALLET_LOAD` в ответе `GET /tasks/{id}` (из RRL_TR_VEHICLE)
- [ ] Компонент `CapacityBar` (вес / паллеты / объём)
- [ ] Автообновление баров при изменении состава рейса
- [ ] Предупреждение при >100% (красный цвет + текст)

**Коммит:** `_______` · **Дата:** ______

---

## Billing — Биллинг рейсов (независимо от Phase 3)

### B.1 — Создание счёта (~3 дня)
- [ ] `POST /api/admin/transport/tasks/{id}/billing/open`
- [ ] `GET  /api/admin/transport/tasks/{id}/billing`
- [ ] Oracle: `RRL_ADD_TT_2_BILLINGORDER(tt_id)`
- [ ] Кнопка «Выставить счёт» в карточке закрытого рейса
- [ ] Статусный тег `billed` на карточке рейса

**Коммит:** `_______` · **Дата:** ______

---

### B.2 — Закрытие и оплата (~3 дня)
- [ ] `POST /api/admin/transport/billing/{id}/close`
- [ ] `POST /api/admin/transport/billing/{id}/pay`
- [ ] Oracle: `RRL_CLOSE_BILLINGORDER`, `RRL_PAY_BILLINGORDER`
- [ ] Статусная машина `billed → closed → paid` с кнопками

**Коммит:** `_______` · **Дата:** ______

---

### B.3 — Реестр счетов (~2 дня)
- [ ] `GET /api/admin/transport/billing?date_from=&date_to=&status=`
- [ ] Отдельная вкладка «Биллинг» в TransportDispatchPage
- [ ] Таблица счетов, фильтр по периоду и статусу, итоговые суммы по TK
- [ ] Экспорт в Excel

**Коммит:** `_______` · **Дата:** ______

---

## Phase 3 — VRP Авто-план

### 3.1 — Матрица расстояний (~2 дня)
- [ ] Миграция `044_apply.sql`: таблица `RRL_ADDR_DISTANCE_MATRIX`
- [ ] `POST /api/admin/transport/distance-matrix/rebuild` (евклидово по SHIROTA/DOLGOTA)
- [ ] Haversine-функция в сервисе (OSRM подключается позже заменой одной функции)

**Коммит:** `_______` · **Дата:** ______

---

### 3.2 — OR-Tools решатель + apply (~4 дня)
- [ ] `pip install ortools` в requirements.txt
- [ ] `POST /api/admin/transport/vrp/solve` — LNS с вместимостью и временны́ми окнами
- [ ] `POST /api/admin/transport/vrp/apply` — атомарное создание всех рейсов плана
- [ ] Ограничения: `max_pallets`, `max_weight_kg`, `ZONE_TIME_PLAN_IN/OUT`

**Коммит:** `_______` · **Дата:** ______

---

### 3.3 — Шаблонный решатель (~2 дня)
- [ ] Jaccard similarity по последним 90 дням закрытых рейсов
- [ ] Ответ `{ "available": false }` если история < 30 рейсов
- [ ] Подключён к `/vrp/solve` как один из решателей

**Коммит:** `_______` · **Дата:** ______

---

### 3.4 — Авто-план UI (~5 дней)
- [ ] Вкладка «Авто-план» в TransportDispatchPage
- [ ] Компонент `SolverCard` × 3 (template / ortools / attention)
- [ ] Spinner с таймером во время расчёта
- [ ] `PlanPreviewList` — список предлагаемых рейсов с редактированием состава
- [ ] Кнопка «Создать все рейсы» → `/vrp/apply` → переход на вкладку «Рейсы»

**Коммит:** `_______` · **Дата:** ______

---

### 3.5 — Attention Model (~3 дня, после 6+ мес. истории)
- [ ] PyTorch inference, веса в файловой системе сервера
- [ ] `POST /api/admin/transport/vrp/retrain` — переобучение по истории
- [ ] Ответ `{ "available": false, "reason": "model_stale" }` если модель > 45 дней

**Коммит:** `_______` · **Дата:** ______

---

## Итог по фазам

| Фаза | Оценка | Статус |
|------|--------|--------|
| 2.1 Кластеры | 2 д | ✅ Готово |
| 2.2 Рейс из кластера | 2 д | ⬜ |
| 2.3 Live-метрики | 2 д | ⬜ |
| B.1 Создание счёта | 3 д | ⬜ |
| B.2 Закрытие/оплата | 3 д | ⬜ |
| B.3 Реестр счетов | 2 д | ⬜ |
| 3.1 Матрица расстояний | 2 д | ⬜ |
| 3.2 OR-Tools + apply | 4 д | ⬜ |
| 3.3 Шаблонный решатель | 2 д | ⬜ |
| 3.4 Авто-план UI | 5 д | ⬜ |
| 3.5 Attention Model | 3 д | ⬜ (нужна история) |
| **Итого без 3.5** | **27 д** | |
