# ТМС-2 — Roadmap: Транспортный Диспетчер

Дата: 2026-05-22.

## Текущее состояние

| Фаза | Статус | Коммит |
|------|--------|--------|
| Phase 1: Ручное назначение | ✅ Готово | `28d8b5d` |
| Phase 1 улучшения (9 пунктов) | ✅ Готово | `03311fa` |
| Phase 2: Полуавто | ⏳ Следующее | — |
| Phase 3: Авто-план (VRP) | ⏳ Планирование | — |
| Billing | ⏳ Отдельная фаза | — |

ТЗ: [transport_dispatch_tz.md](../requirements/transport_dispatch_tz.md) · [transport_billing_tz.md](../requirements/transport_billing_tz.md)

---

## Phase 2: Полуавто (~8 рабочих дней)

**Цель:** диспетчер видит карту с кластерами СТ по районам, выбирает кластер → рейс собирается с TSP-оптимизированным порядком объезда.

### Что реализовать

**Backend:**
- `GET /api/admin/transport/clusters?stdate=&ware_ids=` — группировка свободных СТ по `RRL_ADDR.RAION` + координаты `SHIROTA/DOLGOTA`; для каждого кластера: суммарный вес, паллеты, список СТ
- `POST /api/admin/transport/clusters/{raion}/create-task` — создать рейс из кластера одним запросом (вызов `RRL_TRASPORT_TASK_ADD` + цикл `RRL_TT_ADD_PALL` + `RRL_TT_REORDER_ADR`)
- Live-метрики: вес/объём/паллеты машины в реальном времени при добавлении СТ; предупреждение при превышении `MAX_PALLET_LOAD`

**DB:** `RRL_ADDR.RAION` и `RRL_ADDR.SHIROTA/DOLGOTA` уже есть. Новых таблиц не нужно.

**Frontend:**
- Левая панель: список кластеров (RAION) с суммарными метриками и цветовой маркировкой
- Кнопка «Создать рейс из кластера» — создаёт рейс и переходит к нему в правой панели
- В карточке рейса: live-метрики заполнения (weight bar, pallet bar относительно нормы машины)

**Оценка:** ~3 дня backend + ~5 дней frontend.

---

## Phase 3: Авто-план — VRP (~16 рабочих дней)

**Цель:** система сама предлагает оптимальное распределение всех свободных СТ по машинам на дату.

### Три решателя (запускаются параллельно, лучший результат побеждает)

| Решатель | Алгоритм | Скорость | Особенности |
|----------|----------|----------|-------------|
| Шаблонный | Jaccard similarity по историческим рейсам | < 50 мс | Нет внешних зависимостей |
| OR-Tools | LNS (Large Neighborhood Search) | ≤ 10 сек | Временны́е окна, ограничения вместимости |
| Attention Model | Трансформер (AM) | < 500 мс | Переобучение раз в месяц на истории |

### Технические зависимости

- **OSRM** — self-hosted Docker, данные OSM Russia. Матрица дорожных расстояний кэшируется в `RRL_ADDR_DISTANCE_MATRIX` (создать миграцией).
- **OR-Tools** — `pip install ortools`. Нет Oracle-зависимости.
- **Attention Model** — PyTorch inference. Веса модели хранятся в файловой системе сервера.

### Что реализовать

**DB миграция:** таблица `RRL_ADDR_DISTANCE_MATRIX (ADDR_FROM, ADDR_TO, DISTANCE_M, DURATION_S, UPDATED_AT)` + индексы.

**Backend:**
- `POST /api/admin/transport/vrp/solve` — входные данные: дата, список ТС, список свободных СТ; запускает 3 решателя в `asyncio.gather`, возвращает 3 плана + рекомендованный
- `POST /api/admin/transport/vrp/apply` — принять план: создать все рейсы одним запросом
- `GET /api/admin/transport/vrp/distance-matrix?stdate=` — получить/обновить матрицу дистанций через OSRM

**Frontend:**
- Новая вкладка «Авто-план» в TransportDispatchPage
- Три карточки решателей с метриками (общий пробег, загрузка, нарушения окон)
- Карта с маршрутами (Leaflet или SVG-схема)
- Кнопка «Принять план»

**Оценка:** ~6 дней backend + ~10 дней frontend (без OSRM setup).

---

## Billing (~8 рабочих дней)

Независима от Phase 2/3. ТЗ: [transport_billing_tz.md](../requirements/transport_billing_tz.md).

Ключевые объекты: `RRL_BILL_ORDERS`, `RRL_ADD_TT_2_BILLINGORDER`, `RRL_CLOSE_BILLINGORDER`, `RRL_PAY_BILLINGORDER`.

---

## Рекомендуемый порядок

```
Phase 2 (полуавто) → Billing (параллельно или после) → Phase 3 (VRP)
```

Phase 3 зависит от наличия OSRM и достаточной истории рейсов для обучения AM-модели. Можно начать с OR-Tools без OSRM (использовать евклидово расстояние по координатам `SHIROTA/DOLGOTA`), добавить OSRM позже.
