# ТМС-2 — План внедрения по спринтам

**Проект:** ТМС-2 (Transport Management System 2) — полная замена C# WinForms транспортного модуля (tabPage6 / TRANSPORT.cs / BillingTransport.cs) на FastAPI + React.

Живой чеклист спринтов. После завершения: ставь ✅, пиши коммит-хэш и дату.

**ТЗ:** [transport_dispatch_tz.md](../requirements/transport_dispatch_tz.md) · [transport_billing_tz.md](../requirements/transport_billing_tz.md) · [transport_roadmap.md](transport_roadmap.md)

**Тестовые данные:** seed «Добра Цен» — `db/migrations/2026-05-23_dobrotseny_seed/` (046+047, применён в dev)

Команда: 3+ разработчика. Sprint = 1 неделя. Backend и frontend ведутся параллельно.

---

## Обзор всех спринтов

| # | Название | Блок | Оценка | Инструмент | Статус |
|---|---------|------|--------|-----------|--------|
| 1 | Таблица заявок и фильтры | Диспетчер | 1 нед | 🟢 КК | ✅ `672a47b` 2026-05-23 |
| 2 | Выделение СТ и создание рейса | Диспетчер | 1 нед | 🟢 КК | ✅ `fbdbec0` 2026-05-23 |
| 3 | Вкладка «Маршруты»: список и состав | Диспетчер | 1 нед | 🟢 КК | ✅ `906d876` 2026-05-23 |
| 4 | Редактирование и закрытие рейса | Диспетчер | 1 нед | 🟡 КК+КС | ✅ `a761a6a` 2026-05-26 |
| 5 | Прогресс сборки и требования ТС | Диспетчер | 1 нед | 🟢 КК | ✅ `00f64ed` 2026-05-26 |
| 6 | Тонкое редактирование и вкладка «Паллеты» | Диспетчер | 1 нед | 🟢 КК | ✅ `23c3fe6` 2026-05-26 |
| 7 | Карта заказов (OSM + маркеры) | MAP | 1 нед | 🟡 КК+КС | ✅ `3b19a91` 2026-05-26 |
| 8 | Матрица расстояний + VRP-оптимизатор | MAP | 1.5 нед | 🔴 КС | ✅ `7827b84` 2026-05-26 |
| 9 | Визуальный полигон, кластеры, шаблоны | MAP | 1 нед | 🟡 КК+КС | ✅ `7c284ec` 2026-05-26 |
| 10 | Аналитика плана и качество оптимизации | MAP | 1 нед | 🟢 КК | ✅ `bd08185` 2026-05-26 |
| 11 | Модель операций и нормативы (база ARM) | ARM | 1 нед | 🟡 КК+КС | ✅ `66d9c2b` 2026-05-27 |
| 12 | Диаграмма Ганта | ARM | 1.5 нед | 🔴 КС | ✅ `3c97fa6` 2026-05-27 |
| 13 | Умный подбор машины и конфликты | ARM | 1 нед | 🟡 КК+КС | ✅ `26e9278` 2026-05-27 |
| 14 | План-фактный анализ | ARM | 1 нед | 🟢 КК | ✅ `ab4b791` 2026-05-27 |
| 15 | Биллинг: создание счёта | Billing | 1 нед | 🟢 КК | ✅ `950c8e2` 2026-05-27 |
| 16 | Биллинг: закрытие и оплата | Billing | 1 нед | 🟢 КК | ✅ `5cbd227` 2026-05-27 |
| 17 | Биллинг: реестр счетов | Billing | 1 нед | 🟢 КК | ✅ `8b0bae7` 2026-05-27 |
| 18 | Биллинг: цена рейса | Billing | 0.5 нед | 🟢 КК | ✅ `bc0ddae` 2026-05-27 |
| 19 | Биллинг: привязка к существующему счёту | Billing | 0.5 нед | 🟢 КК | ✅ `6056aa9` 2026-05-27 |
| 20 | Биллинг: защита выставленного рейса | Billing | 0.5 нед | 🟢 КК | ✅ `47abd76` 2026-05-27 |
| 21 | Биллинг: права доступа (RBAC) | Billing | 0.5 нед | 🟢 КК | ✅ `f7e27ad` 2026-05-27 |
| 22 | Биллинг: справочник компаний + NUM_PLAT | Billing | 0.5 нед | 🟢 КК | ✅ `ef09a1c` 2026-05-27 |
| 23 | Биллинг: детальный просмотр счёта + экспорт CSV | Billing | 0.5 нед | 🟢 КК | ✅ `f4413b4` 2026-05-27 |
| 24 | VRP: Drag-and-drop перестановка СТ между маршрутами | MAP | 0.5 нед | 🟢 КК | ✅ `0c4ad0c` 2026-05-27 |
| 25 | Биллинг: снять рейс с биллинга | Billing | 0.5 нед | 🟢 КК | ✅ `7a3e833` 2026-05-27 |
| 26 | Биллинг: Excel-экспорт счёта | Billing | 0.5 нед | 🟢 КК | ✅ `5f6e110` 2026-05-27 |
| 27 | Биллинг: Excel-экспорт реестра счетов | Billing | 0.5 нед | 🟢 КК | ✅ `23682f3` 2026-05-28 |
| **Итого** | | | **~22 нед** | | |

**Легенда инструментов:**
- 🟢 **КК** — код-код ($20): весь спринт самостоятельно; задача типовая, паттерны в проекте есть
- 🟡 **КК+КС** — кодекс ($200) проектирует архитектуру → код-код ($20) реализует
- 🔴 **КС** — кодекс ($200) ведёт спринт: сложный алгоритм или нетипичный UI-компонент (Sprint 8: VRP, Sprint 12: Ганта)

**Инфраструктура OSRM/Valhalla** разворачивается в Docker Desktop (Windows, выделить ≥10 GB RAM) перед Sprint 8. При покупке сервера — перенести контейнеры без изменения кода.

---

## Блок I — Базовый Диспетчер

Цель блока: React-интерфейс полностью покрывает ежедневную работу диспетчера, заменяя C# WinForms.

---

### Sprint 1 — Таблица заявок и фильтры

**Инструмент:** 🟢 КК (код-код $20) — паттерн CRUD+таблица уже есть в проекте, всё типово

**Цель:** диспетчер видит полный список СТ как в C# — все 16 колонок, фильтры, цветовая подсветка.

**ТЗ:** §3.3, §3.4, §3.6, §5.4, §5.5

| Задача | Кто | Файл |
|--------|-----|------|
| Расширить `GET /available-sts`: добавить `RAION`, `TRANSPORT_TYPE`, `STOL`, `PRIM1`, `VERIFY_PERC`, `SUGAR`, `DATE_LOAD` | Backend | `transport_service.py` |
| Добавить query-параметры: `addr_mask`, `st_mask`, `st_mask_exclude`, `ware_ids`, `transport_type`, `assembled_only`, `not_assembled_only`, `max_weight_kg`, `max_volume_m3`, `date_to`, `articul` | Backend | `transport.py` |
| Расширить `AvailableSt` схему | Backend | `schemas.py` |
| Таблица СТ: 16 колонок согласно §3.3 | Frontend | `TransportDispatchPage.tsx` |
| Цветовая подсветка строк по WARE_ID (§3.4) | Frontend | `styles.css` |
| Панель фильтров (§3.6): все поля, дебаунс 300 мс | Frontend | `TransportDispatchPage.tsx` |

**Что видит диспетчер после спринта:**
Таблица СТ с полным набором данных: склад (цветная), паллеты, вес, объём, регион, адрес, ST-номер, рейс, район, тип ТС, гидроборт, стол, примечание, дата загрузки, сахар. Работают все фильтры: по дате, складу, адресу, СТ, типу ТС, весу/объёму.

**Коммит:** `672a47b` · **Дата:** 2026-05-23

---

### Sprint 2 — Выделение СТ и создание рейса

**Инструмент:** 🟢 КК (код-код $20) — стандартная логика выделения + диалог создания

**Цель:** диспетчер выбирает «Лысьва + Чусовой» двумя Shift-кликами, видит суммарную нагрузку и создаёт рейс.

**ТЗ:** §3.2, §3.5, §3.7

| Задача | Кто | Файл |
|--------|-----|------|
| Чекбокс выделения каждой строки | Frontend | `TransportDispatchPage.tsx` |
| Shift+Click — диапазон строк (§3.5) | Frontend | `TransportDispatchPage.tsx` |
| Клик по ячейке РАЙОН/РЕГИОН — выделить все СТ с тем же значением | Frontend | `TransportDispatchPage.tsx` |
| Строка итогов: `Палл / Вес / Объём` по выделенным, пересчёт без запроса | Frontend | `TransportDispatchPage.tsx` |
| Диалог «Создать маршрут»: выбор ТС, водителя, дока, даты отгрузки | Frontend | `TransportDispatchPage.tsx` |
| `POST /tasks` + цикл `POST /tasks/{id}/sts` для каждого выделенного СТ | Backend | `transport.py` |
| После создания: сбросить выделение, убрать назначенные СТ из таблицы | Frontend | `TransportDispatchPage.tsx` |

**Что видит диспетчер после спринта:**
Строка итогов обновляется мгновенно при каждом клике. Кнопка «Создать маршрут» становится активной при наличии выделенных СТ. После создания рейса назначенные СТ исчезают из таблицы (если включён фильтр «НЕ РАСПРЕДЕЛЁННЫЕ»).

**Коммит:** `fbdbec0` · **Дата:** 2026-05-23

---

### Sprint 3 — Вкладка «Маршруты»: список и состав

**Инструмент:** 🟢 КК (код-код $20) — split-view с двумя таблицами, знакомый паттерн

**Цель:** диспетчер видит все созданные рейсы и состав каждого.

**ТЗ:** §3.8

| Задача | Кто | Файл |
|--------|-----|------|
| Расширить `GET /tasks`: добавить `ПАЛЛЕТЫ`, `ОБЪЕМ`, `ТК`, `ЛОГИСТ`, `РЕГИОНЫ`, `READY_PERC` | Backend | `transport_service.py` |
| Расширить `GET /tasks/{id}/sts`: добавить `TIME_FROM`, `TIME_TO`, `ZONE`, `LOAD_TYPE` | Backend | `transport_service.py` |
| Вкладка «Маршруты»: верхняя таблица — 14 колонок (§3.8.1) | Frontend | `TransportDispatchPage.tsx` |
| Панель фильтров маршрутов: по ID, авто, компании, «до даты», «без оплат» (§3.8.1) | Frontend | `TransportDispatchPage.tsx` |
| Клик по рейсу → нижняя таблица состава — 12 колонок (§3.8.2) | Frontend | `TransportDispatchPage.tsx` |
| Поле примечания + кнопка «Сохранить примечание» → `PATCH /tasks/{id}` | Backend + Frontend | |

**Что видит диспетчер после спринта:**
Вкладка «Маршруты» показывает полную таблицу рейсов с машиной, водителем, доком, регионами, ценой. Клик на строку открывает состав: список СТ с адресом, паллетами, порядком, временными окнами, типом борта.

**Коммит:** `906d876` · **Дата:** 2026-05-23

---

### Sprint 4 — Редактирование и закрытие рейса

**Инструмент:** 🟡 КК+КС — КС проектирует поток Oracle-пакетов и обработку 422; КК реализует

**Цель:** полный цикл работы с рейсом — добавить СТ, снять СТ, изменить реквизиты, закрыть.

**ТЗ:** §3.8.2, §5.10, §5.11

| Задача | Кто | Файл |
|--------|-----|------|
| Кнопка «+Добавить в маршрут» со вкладки «Заявки» → `POST /tasks/{id}/sts` | Frontend | `TransportDispatchPage.tsx` |
| Кнопка «Удалить из маршрута» в составе рейса → `DELETE /tasks/{id}/sts/{st}` | Backend + Frontend | |
| Inline-dropdown `ТИПТС` в таблице рейсов → `PATCH /tasks/{id}` | Frontend | `TransportDispatchPage.tsx` |
| Редактирование реквизитов рейса: ТС, водитель, дёк, дата отгрузки | Frontend | `TransportDispatchPage.tsx` |
| `RRL_TT_SET_TRANSCOMMENT` при смене машины (§5.11) | Backend | `transport_service.py` |
| Закрытие рейса с проверкой `can_print` → 422 с текстом ошибки (§5.10) | Backend + Frontend | |
| Кнопка `Расформировать МАРШР` → `DELETE /tasks/{id}` с подтверждением | Backend + Frontend | |

**Что видит диспетчер после спринта:**
Полный жизненный цикл рейса: создан → отредактирован → закрыт. При попытке закрыть рейс без достаточной загрузки — понятное сообщение об ошибке. Смена машины автоматически обновляет комментарий через Oracle-функцию.

**Коммит:** `a761a6a` · **Дата:** 2026-05-26

**Тесты завершения:**
- Функциональные: `tests/transport/test_sprint4_functional.py` (pytest, 22 кейса)
- Нагрузочные: `tests/transport/transport_sprint4_load_test.py` (30 user, 60s, NFR §12)
- Юзабилити: `tests/transport/sprint4_usability_checklist.md` (37 пунктов)

---

### Sprint 5 — Прогресс сборки и требования ТС

**Инструмент:** 🟢 КК (код-код $20) — визуальные бейджи и прогресс-бары, чистый frontend

**Цель:** диспетчер видит готовность СТ к погрузке и соответствие ТС требованиям адреса — без перехода в другие экраны.

**ТЗ:** §5.2, §5.7

| Задача | Кто | Файл |
|--------|-----|------|
| Колонка `VERIFY_PERC` как прогресс-бар (🔴 < 50%, 🟡 < 100%, 🟢 = 100%) | Frontend | `TransportDispatchPage.tsx` |
| Колонка `TRANSPORT_TYPE` с бейджем типа ТС (реф / тент / 20т / 15т) | Frontend | `TransportDispatchPage.tsx` |
| Иконка гидроборта ♿ если `STOL = 1` | Frontend | `TransportDispatchPage.tsx` |
| `READY_PERC` как прогресс-бар в списке рейсов; параметр `include_readiness=true` (§5.7) | Backend + Frontend | |
| `TK_NAME` и бейдж «Свой» / «Наёмный» в списке рейсов (§5.7) | Backend + Frontend | |

**Что видит диспетчер после спринта:**
В каждой строке СТ — цветной бар готовности сборки. В строке рейса — бар с % собранных паллет и метка транспортной компании. Адреса, требующие спецтехнику, помечены иконками.

**Коммит:** `00f64ed` · **Дата:** 2026-05-26

**Тесты завершения:**
- Функциональные: `tests/transport/test_sprint5_functional.py` (pytest, поля API)
- Нагрузочные: `tests/transport/transport_sprint5_load_test.py` (40 users, 60s, NFR §12)
- Юзабилити: `tests/transport/sprint5_usability_checklist.md` (35 пунктов)

---

### Sprint 6 — Тонкое редактирование и вкладка «Паллеты»

**Инструмент:** 🟢 КК (код-код $20) — inline-поля и новая вкладка, типовой React-паттерн

**Цель:** диспетчер управляет порядком объезда и типом борта прямо в составе рейса.

**ТЗ:** §5.8, §5.9, вкладка «Паллеты заявки»

| Задача | Кто | Файл |
|--------|-----|------|
| `PATCH /tasks/{id}/sts/{st}/load-type` — изменение LOAD_TYPE (§5.8) | Backend | `transport.py` |
| `PATCH /tasks/{id}/sts/{st}/order` — изменение ORD (§5.9) | Backend | `transport.py` |
| Inline-dropdown `В ПРИЦЕП?` (—/П/Г) в составе рейса | Frontend | `TransportDispatchPage.tsx` |
| Inline-поле `ПОР` (числовое) в составе рейса | Frontend | `TransportDispatchPage.tsx` |
| Вкладка «Паллеты заявки»: детализация паллет по выбранному СТ | Frontend | `TransportDispatchPage.tsx` |

**Что видит диспетчер после спринта:**
В составе рейса можно изменить тип борта (прицеп/госборт) и порядок объезда кликом — без открытия отдельных форм. Вкладка «Паллеты заявки» показывает список паллет с артикулами.

**Статус:** ✅ Завершён  
**Коммит:** `23c3fe6` · **Дата:** 2026-05-26  
**Тесты:**  
- `tests/transport/test_sprint6_functional.py` — 10 pytest-кейсов (endpoint, fields, pallet count)  
- `tests/transport/sprint6_usability_checklist.md` — 25 юзабилити-проверок  
- `tests/transport/transport_sprint6_load_test.py` — 40 users, 60s, NFR p95 ≤ 200ms для `/sts/{st}/pallets`  
**Миграция:** `050_apply.sql` (no-op, схема без изменений)

---

## Блок II — Карта и VRP-Оптимизатор

Цель блока: диспетчер нажимает одну кнопку и получает оптимальный план рейсов на день.

---

### Sprint 7 — Карта заказов

**Инструмент:** 🟡 КК+КС — КС настраивает архитектуру новой страницы и Leaflet-слоёв; КК реализует компоненты и эндпоинты

**Цель:** все СТ на текущую дату — на карте OpenStreetMap. Диспетчер видит географию дня за секунды.

**ТЗ:** §11.5, §11.7, §11.10 (миграция 045)

| Задача | Кто | Файл |
|--------|-----|------|
| Миграция `045_apply.sql`: `LATITUDE`, `LONGITUDE`, `MAX_VEHICLE_TONS`, `UNLOAD_NORM_MIN`, `TW_STRICT` в `RRL_ADDR`; таблицы `RRL_ADDR_DISTANCE_MATRIX`, `RRL_PLANNER_PLANS` | DB | `045_apply.sql` |
| CLI-скрипт массового геокодирования через DaData.ru (§11.12.2) | Backend | `db/scripts/geocode_addresses.py` |
| `GET /planner/orders?date=` — список СТ с (lat, lon, ware_id, pallets, time_window, vehicle_type) | Backend | `transport.py` |
| `GET /routing/status` — активный провайдер, кол-во адресов без координат | Backend | `transport.py` |
| Новая страница `TransportPlannerPage` + роут `/transport/planner` | Frontend | `TransportPlannerPage.tsx` |
| Leaflet.js карта с OSM-тайлами: `npm install react-leaflet leaflet` | Frontend | `package.json` |
| Слой «Заказы»: маркеры СТ (цвет по WARE_ID, размер по паллетам) | Frontend | `TransportPlannerPage.tsx` |
| Слой «Временны́е окна»: иконка + цвет (жёсткое / мягкое) | Frontend | `TransportPlannerPage.tsx` |
| Слой «Тип ТС»: цветная рамка маркера (10т/15т/20т) | Frontend | `TransportPlannerPage.tsx` |
| Левая панель: фильтры по дате, складу, региону, типу ТС | Frontend | `TransportPlannerPage.tsx` |
| Клик на маркер → карточка СТ (адрес, паллеты, вес, временно́е окно) | Frontend | `TransportPlannerPage.tsx` |

**Что видит диспетчер после спринта:**
Новый раздел «Планировщик» в меню. Карта России с цветными значками заказов. Большой кружок = много паллет. Красная рамка = только 10-тонник. Значок ⏰ = жёсткое временно́е окно. Фильтр по складу убирает/показывает нужные точки.

**Статус:** ✅ Завершён  
**Коммит:** `3b19a91` · **Дата:** 2026-05-26  
**Тесты:**  
- `tests/transport/test_sprint7_functional.py` — 12 pytest-кейсов (planner/orders, routing/status)  
- `tests/transport/sprint7_usability_checklist.md` — 39 юзабилити-проверок  
- `tests/transport/transport_sprint7_load_test.py` — 30 users, 60s, NFR p95 ≤ 600ms для /planner/orders  
**Миграция:** `051_apply.sql` (MAX_VEHICLE_TONS, TW_STRICT, UNLOAD_NORM_MIN в RRL_ADDR; дистанционная матрица; seed-координаты ДЦ%)

---

### Sprint 8 — Матрица расстояний + VRP-оптимизатор

**Инструмент:** 🔴 КС (кодекс $200) — RoutingProvider ABC, OR-Tools CVRPTW, OSRM-интеграция; самый алгоритмически сложный спринт

**Цель:** одна кнопка → оптимальный набор рейсов на карте с учётом грузоподъёмности и временных окон.

**ТЗ:** §11.3–§11.8, §11.12.3

**Подготовка инфраструктуры (до начала спринта, ~2-3 часа):**
```bash
# В Docker Desktop: Settings → Resources → RAM ≥ 10 GB, CPUs ≥ 4
# Скачать карту России и подготовить OSRM (см. §11.12.3)
wget https://download.geofabrik.de/russia-latest.osm.pbf -P ./osrm-data/
# ... docker run osrm-extract, osrm-partition, osrm-customize
docker compose -f docker-compose.osrm.yml up -d
docker compose -f docker-compose.valhalla.yml up -d  # резерв
```

| Задача | Кто | Файл |
|--------|-----|------|
| `RoutingProvider` ABC + `HaversineProvider` + `OsrmProvider` + `ValhallaProvider` + `_fallback_chain()` (§11.12.3) | Backend | `services/routing.py` |
| `rebuild_matrix()` — пересчитать матрицу и сохранить в Oracle | Backend | `services/distance_matrix_service.py` |
| `POST /distance-matrix/rebuild?source=auto` | Backend | `transport.py` |
| `pip install ortools pyvrp scikit-learn` в requirements.txt | Backend | `requirements.txt` |
| `services/vrp_solver.py`: CVRPTW с ограничениями по грузоподъёмности, типу ТС, временны́м окнам, времени разгрузки | Backend | `services/vrp_solver.py` |
| `POST /planner/solve` — запуск OR-Tools, сохранение плана в `RRL_PLANNER_PLANS` | Backend | `transport.py` |
| `POST /planner/apply` — атомарное создание рейсов через Oracle-функции | Backend | `transport.py` |
| `GET /planner/metrics` — утилизация, пробег, нарушения окон, Score | Backend | `transport.py` |
| Кнопка «Авто-план» + spinner + таймер на карте | Frontend | `TransportPlannerPage.tsx` |
| Маршрутные полилинии на карте: цвет по машине, стрелки направления | Frontend | `TransportPlannerPage.tsx` |
| Правая панель: список рейсов плана (машина, паллеты, бар утилизации) | Frontend | `TransportPlannerPage.tsx` |
| Панель метрик: утилизация %, пробег км, нарушений окон, Score (§11.7.4) | Frontend | `TransportPlannerPage.tsx` |
| Кнопка «Применить план» с подтверждением | Frontend | `TransportPlannerPage.tsx` |
| Виджет статуса роутера: активный провайдер, дата пересчёта, кнопка «Пересчитать матрицу» | Frontend | `TransportPlannerPage.tsx` |

**Что видит диспетчер после спринта:**
Кнопка «Авто-план» → через 10–30 сек на карте появляются цветные маршруты (каждая машина — свой цвет). Справа: «Рейс 1: Е715ТТ — 14 паллет — 96% загрузки — 4ч20м». Внизу: «Утилизация парка: 84%, Общий пробег: 1 240 км, Нарушений окон: 2». Кнопка «Применить план» создаёт все рейсы в системе.

**Статус:** ✅ Завершён  
**Коммит:** `7827b84` · **Дата:** 2026-05-26  
**Тесты:**  
- `tests/transport/test_sprint8_functional.py` — 24 pytest-кейса (solve, metrics, apply, matrix)  
- `tests/transport/sprint8_usability_checklist.md` — 43 юзабилити-проверки  
- `tests/transport/transport_sprint8_load_test.py` — 3 users, 120s, NFR p95 solve≤60s, metrics≤500ms  
**Миграция:** `052_apply.sql` (APPLIED_AT, индексы на матрицу и планы)

---

### Sprint 9 — Визуальный полигон, кластеры, шаблоны

**Инструмент:** 🟡 КК+КС — КС проектирует DBSCAN-кластеризацию и Jaccard-matching; КК реализует leaflet-draw и drag-drop

**Цель:** диспетчер корректирует план вручную на карте; система предлагает исторические шаблоны для знакомых маршрутов.

**ТЗ:** §11.3 (подходы A, B, D), §11.9

| Задача | Кто | Файл |
|--------|-----|------|
| `npm install leaflet-draw` + инструмент рисования полигона (§11.7.3) | Frontend | `TransportPlannerPage.tsx` |
| Выделение маркеров СТ внутри полигона → кнопка «Создать рейс из выделенных» | Frontend | `TransportPlannerPage.tsx` |
| Слой кластеров по `RRL_ADDR.RAION`: подписанные полупрозрачные полигоны | Frontend | `TransportPlannerPage.tsx` |
| Клик на кластер → выделить все СТ кластера | Frontend | `TransportPlannerPage.tsx` |
| Drag & drop маркера СТ между маршрутами → пересчёт метрик без перезапуска solver | Frontend | `TransportPlannerPage.tsx` |
| `solver=cluster` в `/planner/solve`: DBSCAN-кластеризация + локальный VRP в каждом кластере | Backend | `services/vrp_solver.py` |
| `GET /planner/templates?date=` — Jaccard similarity ≥ 0.7 по истории 90 дней (§11.9) | Backend | `transport.py` |
| Правая панель: блок «Похожие маршруты из истории» с кнопкой «Применить шаблон» | Frontend | `TransportPlannerPage.tsx` |

**Что видит диспетчер после спринта:**
Можно нарисовать зону на карте и мгновенно получить рейс из точек внутри. Кластеры районов подсвечены — один клик выделяет весь район. Перетащить сложный адрес в другой маршрут — метрики пересчитываются без ожидания. В правой панели — «3 похожих маршрута из прошлого месяца».

**Статус:** ✅ Завершён  
**Коммит:** `7c284ec` · **Дата:** 2026-05-26  
**Тесты:**  
- `tests/transport/test_sprint9_functional.py` — 15 pytest-кейсов (cluster solver, templates, RAION)  
- `tests/transport/sprint9_usability_checklist.md` — 23 юзабилити-проверки  
**Примечание:** drag & drop между маршрутами (Jaccard-matching) включён; drag без перезапуска solver — в Sprint 10.

---

### Sprint 10 — Аналитика плана и оптимизация

**Инструмент:** 🟢 КК (код-код $20) — таблица истории, sparkline, слайдеры; стандартный React

**Цель:** руководство и диспетчер видят, насколько оптимизатор улучшает загрузку парка со временем.

**ТЗ:** §11.7.4, Sprint 13 (план-история)

| Задача | Кто | Файл |
|--------|-----|------|
| `GET /planner/history?date_from=&date_to=` — история применённых планов с Score | Backend | `transport.py` |
| Страница «История планов»: таблица с датой, Score, кол-вом рейсов, утилизацией | Frontend | `TransportPlannerPage.tsx` |
| График Score по дням (sparkline) | Frontend | `TransportPlannerPage.tsx` |
| Сравнение «Сегодня vs лучший за 30 дней» | Frontend | `TransportPlannerPage.tsx` |
| Слайдеры весов целевой функции α/β/γ в «Настройках оптимизации» (§11.5.3) | Frontend | `TransportPlannerPage.tsx` |
| Прогноз спроса: `GET /planner/demand-forecast?date=` — ожидаемое число СТ | Backend | `transport.py` |

**Что видит диспетчер после спринта:**
График «Утилизация парка» за последние 30 дней. Видно, что после внедрения оптимизатора средняя загрузка выросла с 71% до 86%. Настройки позволяют «жертвовать пробегом ради меньшего числа машин» и наоборот.

**Статус:** ✅ Завершён  
**Коммит:** `bd08185` · **Дата:** 2026-05-26  
**Тесты:**  
- `tests/transport/test_sprint10_functional.py` — 15 pytest-кейсов (history, forecast)  
- `tests/transport/sprint10_usability_checklist.md` — 24 юзабилити-проверки  

---

## Блок III — ARM: Транспорт как Ресурс

Цель блока: диспетчер видит загрузку каждой машины на день в виде диаграммы Ганта и получает умные подсказки по доступности.

---

### Sprint 11 — Модель операций и нормативы

**Инструмент:** 🟡 КК+КС — КС проектирует схему миграции 044 и алгоритм расчёта цепочки; КК реализует SQL и Python

**Цель:** заложить базу данных для Ганта — операции, нормативы, плановая цепочка.

**ТЗ:** §10.2–§10.4, §10.9 (критерии приёмки 1–3)

| Задача | Кто | Файл |
|--------|-----|------|
| Миграция `044_apply.sql`: `RRL_TRANSPORT_NORMS`, `RRL_TT_OPERATIONS` (§10.4) | DB | `044_apply.sql` |
| Seed нормативов: DOCK_ASSIGN=15, WAIT_LOAD=10, LOADING=3/палл, CLOSE_GATE=10, DOCUMENTS=10, DEPART=0, UNLOAD=3/палл, LOAD_RETURNS=15, DRIVE_BACK=0, RETURN_HANDOVER=20, CLEAN_RETURNS=20 | DB | `044_apply.sql` |
| `POST /tasks/{id}/plan-operations` — рассчитать и сохранить цепочку операций | Backend | `transport_service.py` |
| `PATCH /operations/{id}/fact` — зафиксировать `fact_start` / `fact_end` | Backend | `transport.py` |
| Автоматический вызов `plan-operations` при создании рейса | Backend | `transport_service.py` |
| Pydantic-схемы: `OperationPlan`, `OperationFactUpdate`, `VehicleGanttDay` | Backend | `schemas.py` |

**Что видит диспетчер после спринта:**
UI не меняется, но при создании каждого рейса в Oracle автоматически создаётся цепочка из 12 операций с плановыми временами. Фундамент для Ганта готов.

**Статус:** ✅ Завершён  
**Коммит:** `66d9c2b` · **Дата:** 2026-05-27  
**Тесты:**  
- `tests/transport/test_sprint11_functional.py` — 22 pytest-кейса (plan-operations, get-operations, patch-fact, gantt)  
- `tests/transport/sprint11_usability_checklist.md` — 25 юзабилити-проверок  
- `tests/transport/transport_sprint11_load_test.py` — 5 users, 60s, NFR p95 plan-ops≤500ms, ops≤200ms, fact≤200ms  
**Миграция:** `053_apply.sql` (RRL_TRANSPORT_NORMS + RRL_TT_OPERATIONS + 12 seed нормативов)

---

### Sprint 12 — Диаграмма Ганта

**Инструмент:** 🔴 КС (кодекс $200) — кастомный Ганта без UI-библиотек: 6 цветогрупп, REST-блоки, drag, live-линия; самый сложный frontend-спринт

**Цель:** диспетчер видит загрузку всех машин на день в виде цветной диаграммы Ганта с дискретными операциями.

**ТЗ:** §10.6, §10.9 (критерии 1–6)

| Задача | Кто | Файл |
|--------|-----|------|
| `GET /vehicles/gantt?date=` — все машины × цепочка операций за день | Backend | `transport.py` |
| Новая страница `TransportGanttPage` + роут `/transport/gantt` в сайдбаре | Frontend | `TransportGanttPage.tsx` |
| Компонент `GanttChart`: временна́я ось 06:00–22:00 × 30 мин, строки по машинам | Frontend | `TransportGanttPage.tsx` |
| Строка машины: иконка ТС + гос. номер + модель + аватар водителя + статус-бейдж (§10.6.2) | Frontend | `TransportGanttPage.tsx` |
| Блоки операций: 6 цветовых групп согласно §10.6.3; подпись внутри блока | Frontend | `TransportGanttPage.tsx` |
| Цветовая легенда под таблицей (§10.6.3) | Frontend | `TransportGanttPage.tsx` |
| Синяя линия «текущее время», обновление раз в минуту (§10.6.1) | Frontend | `TransportGanttPage.tsx` |
| Тултип hover: операция, план HH:MM–HH:MM, факт, дельта (§10.6.4) | Frontend | `TransportGanttPage.tsx` |
| Автоматические блоки `REST` (серые) при вождении > 2 ч (§10.3) | Frontend | `TransportGanttPage.tsx` |
| Сводная строка: Всего / В рейсе % / На базе % / Погрузка % / Отдых % / Нарушения ⚠ (§10.6.5) | Frontend | `TransportGanttPage.tsx` |
| Правые панели: «Ближайшие рейсы» + «Фактические отклонения» (§10.6.6) | Frontend | `TransportGanttPage.tsx` |
| Навигация: ◄► дата, «Сегодня», фильтр машин, переключатель День/Неделя (§10.6.1) | Frontend | `TransportGanttPage.tsx` |

**Что видит диспетчер после спринта:**
Новый раздел «Диаграмма Ганта» в меню. Каждая строка — одна машина с именем водителя и фото. На временно́й шкале — цветные блоки: синие (погрузка), зелёные (переезд), жёлтые (выгрузка), фиолетовые (возвраты), серые (перерывы). Синяя вертикальная линия — сейчас. Снизу: «В рейсе: 12 (52%), Погрузка: 3 (13%), Нарушений: 2 ⚠».

**Статус:** ✅ Завершён  
**Коммит:** `3c97fa6` · **Дата:** 2026-05-27  
**Тесты:**  
- `tests/transport/test_sprint12_functional.py` — 12 pytest-кейсов (gantt 200, fields, op-codes, chain, durations)  
- `tests/transport/sprint12_usability_checklist.md` — 46 юзабилити-проверок  
- `tests/transport/transport_sprint12_load_test.py` — 10 users, 60s, NFR gantt≤2s, ops≤200ms  

---

### Sprint 13 — Умный подбор машины и конфликты

**Инструмент:** 🟡 КК+КС — КС проектирует 6-факторную проверку доступности и логику конфликтов; КК реализует drag на Ганте и UI

**Цель:** при создании рейса система сразу показывает, какие машины свободны к нужному времени. Конфликты видны на Ганте.

**ТЗ:** §10.7, §10.9 (критерии 4–5, 10)

| Задача | Кто | Файл |
|--------|-----|------|
| `GET /vehicles/available?shipment_time=&pallets=` — 6 проверок доступности (§10.7) | Backend | `transport.py` |
| Интеграция в диалог создания рейса: колонка «Свободна с» | Frontend | `TransportDispatchPage.tsx` |
| Цветовая индикация 🟢/🟡/🔴 по доступности машины (§10.7) | Frontend | `TransportDispatchPage.tsx` |
| Сортировка машин: сначала зелёные | Frontend | `TransportDispatchPage.tsx` |
| Предупреждение при выборе красной машины | Frontend | `TransportDispatchPage.tsx` |
| Клик на блок Ганта → карточка рейса (§10.6.4) | Frontend | `TransportGanttPage.tsx` |
| Drag блока рейса по оси Ганта → сдвиг `SHIPMENT_DATE` через `PATCH /tasks/{id}` | Frontend + Backend | `TransportGanttPage.tsx` |
| Конфликт при перетаскивании → красный контур, сохранение заблокировано | Frontend | `TransportGanttPage.tsx` |
| Блок `DRIVER_CHANGE` на шкале машины (вставляется диспетчером) | Frontend | `TransportGanttPage.tsx` |

**Что видит диспетчер после спринта:**
В диалоге «Создать маршрут» у каждой машины написано «Свободна с 14:30» (зелёный), «Освободится в 16:10» (жёлтый) или «Занята, конфликт» (красный). Можно перетащить рейс на Ганте — он сдвигается, и если пересекается с другим — краснеет.

**Статус:** ✅ Завершён  
**Коммит:** `26e9278` · **Дата:** 2026-05-27  
**Тесты:**  
- `tests/transport/test_sprint13_functional.py` — 15 pytest-кейсов (available, plan-fact)  
- `tests/transport/sprint13_usability_checklist.md` — 24 юзабилити-проверки  
- `tests/transport/transport_sprint13_load_test.py` — 8 users, 60s, NFR available≤500ms, plan-fact≤1s  

---

### Sprint 14 — План-фактный анализ

**Инструмент:** 🟢 КК (код-код $20) — аналитическая таблица, цветовые бары отклонений, Excel-экспорт

**Цель:** диспетчер фиксирует фактические времена; руководство видит систематические отклонения и нарушения режимов.

**ТЗ:** §10.8, §10.9 (критерии 7–9)

| Задача | Кто | Файл |
|--------|-----|------|
| `GET /plan-fact?date_from=&date_to=&vehicle=` — сводный отчёт по операциям (§10.8) | Backend | `transport.py` |
| Модальное окно «Отметить факт»: клик правой кнопкой на блок Ганта | Frontend | `TransportGanttPage.tsx` |
| Вкладка «Аналитика» в `TransportGanttPage` | Frontend | `TransportGanttPage.tsx` |
| Таблица: операция / план / факт / дельта; бары отклонений 🟢≤15 / 🟡≤60 / 🔴>60 мин | Frontend | `TransportGanttPage.tsx` |
| Счётчик нарушений норм отдыха `rest_violations` в строке рейса | Frontend | `TransportGanttPage.tsx` |
| Модальное окно «Нарушения режимов → Подробнее» (§10.6.7) | Frontend | `TransportGanttPage.tsx` |
| Экспорт в Excel | Frontend | `TransportGanttPage.tsx` |

**Что видит диспетчер после спринта:**
Вкладка «Аналитика» показывает: «Погрузка: план 45 мин, факт 67 мин, +22 мин 🔴» для каждой операции. Руководство видит паттерн — погрузка стабильно опаздывает → нужно скорректировать норматив или процесс. 2 нарушения режима отдыха водителей — с деталями по каждому.

**Статус:** ✅ Завершён  
**Коммит:** `ab4b791` · **Дата:** 2026-05-27  
**Тесты:**  
- `tests/transport/test_sprint14_functional.py` — 7 pytest-кейсов (plan-fact delta, rest_violations)  
- `tests/transport/sprint14_usability_checklist.md` — 29 юзабилити-проверок  
- `tests/transport/transport_sprint14_load_test.py` — 10 users, 60s, NFR p95 plan-fact(1d)≤500ms, plan-fact(30d)≤2000ms  

---

## Блок IV — Биллинг

Цель блока: закрытый рейс становится счётом для транспортной компании.

---

### Sprint 15 — Создание счёта

**Инструмент:** 🟢 КК (код-код $20) — один Oracle-пакет, кнопка, тег billed; минимальный объём

**Цель:** диспетчер выставляет счёт по закрытому рейсу одной кнопкой.

**ТЗ:** [transport_billing_tz.md](../requirements/transport_billing_tz.md), B.1

| Задача | Кто | Файл |
|--------|-----|------|
| `POST /tasks/{id}/billing/open` → Oracle `RRL_ADD_TT_2_BILLINGORDER` | Backend | `transport.py` |
| `GET /tasks/{id}/billing` — данные счёта | Backend | `transport.py` |
| Кнопка «Выставить счёт» в карточке закрытого рейса | Frontend | `TransportDispatchPage.tsx` |
| Статусный тег `billed` на карточке рейса | Frontend | `TransportDispatchPage.tsx` |
| Pydantic-схемы: `BillingOrder`, `BillingOrderCreate` | Backend | `schemas.py` |

**Что видит диспетчер после спринта:**
На закрытом рейсе появляется кнопка «Выставить счёт». После нажатия — рейс получает метку `billed` и больше не доступен для редактирования.

**Статус:** ✅ Завершён  
**Коммит:** `950c8e2` · **Дата:** 2026-05-27  
**Тесты:**  
- `tests/transport/test_sprint15_functional.py` — 9 pytest-кейсов (create order, open billing, task billing)  
- `tests/transport/sprint15_usability_checklist.md` — 22 юзабилити-проверки  
- `tests/transport/transport_sprint15_load_test.py` — 8 users, 60s, NFR p95 list≤300ms, create≤500ms  
**Миграция:** `054_apply.sql` (SEQ_BILL_ORDERS + RRL_BILL_ORDERS идемпотентно)

---

### Sprint 16 — Закрытие и оплата счёта

**Инструмент:** 🟢 КК (код-код $20) — два Oracle-пакета, статусная машина из 3 состояний

**Цель:** статусная машина счёта — выставлен → закрыт → оплачен.

**ТЗ:** B.2

| Задача | Кто | Файл |
|--------|-----|------|
| `POST /billing/{id}/close` → Oracle `RRL_CLOSE_BILLINGORDER` | Backend | `transport.py` |
| `POST /billing/{id}/pay` → Oracle `RRL_PAY_BILLINGORDER` | Backend | `transport.py` |
| Кнопки «Закрыть счёт» и «Отметить оплаченным» в карточке | Frontend | `TransportDispatchPage.tsx` |
| Статусная машина `billed → closed → paid` с цветными бейджами | Frontend | `TransportDispatchPage.tsx` |

**Что видит диспетчер после спринта:**
Счёт проходит путь: 🟡 Выставлен → 🔵 Закрыт → 🟢 Оплачен. Каждый переход — кнопка с подтверждением.

**Статус:** ✅ Завершён  
**Коммит:** `5cbd227` · **Дата:** 2026-05-27  
**Тесты:**  
- `tests/transport/test_sprint16_functional.py` — 9 pytest-кейсов (get order, close, pay, 404)  
- `tests/transport/sprint16_usability_checklist.md` — 19 юзабилити-проверок  
- `tests/transport/transport_sprint16_load_test.py` — 5 users, 60s, NFR p95 get≤300ms, close/pay≤500ms  

---

### Sprint 17 — Реестр счетов

**Инструмент:** 🟢 КК (код-код $20) — таблица с фильтрами, итоги по ТК, Excel-экспорт

**Цель:** бухгалтерия видит все счета за период с итогами по ТК и может выгрузить в Excel.

**ТЗ:** B.3

| Задача | Кто | Файл |
|--------|-----|------|
| `GET /billing?date_from=&date_to=&status=&tk=` | Backend | `transport.py` |
| Вкладка «Биллинг» в `TransportDispatchPage` | Frontend | `TransportDispatchPage.tsx` |
| Таблица счетов: дата, рейс, ТК, сумма, статус | Frontend | `TransportDispatchPage.tsx` |
| Фильтры: период, статус, транспортная компания | Frontend | `TransportDispatchPage.tsx` |
| Итоговые суммы по ТК внизу таблицы | Frontend | `TransportDispatchPage.tsx` |
| Экспорт в Excel | Frontend | `TransportDispatchPage.tsx` |

**Что видит диспетчер после спринта:**
Вкладка «Биллинг» — таблица всех счетов с фильтрами. Внизу: «ООО Ромашка: 127 450 ₽ за май». Кнопка «Скачать CSV».

**Статус:** ✅ Завершён  
**Коммит:** `8b0bae7` · **Дата:** 2026-05-27  
**Тесты:**  
- `tests/transport/test_sprint17_functional.py` — 13 pytest-кейсов (list, filters by date/company/status, totals)  
- `tests/transport/sprint17_usability_checklist.md` — 28 юзабилити-проверок (вкладка, фильтры, таблица, бейджи, итоги, CSV)  
- `tests/transport/transport_sprint17_load_test.py` — 8 users, 60s, NFR p95 list≤300ms  
**Исправлено:** баг правой панели — вкладка «Биллинг» корректно скрывает `dispatch-right-panel`

---

### Sprint 18 — Цена рейса

**Инструмент:** 🟢 КК (код-код $20) — два эндпоинта + секция в карточке рейса

**Цель:** диспетчер пересчитывает стоимость рейса через Oracle и может скорректировать её вручную. Можно отвязать рейс от биллинг-заказа.

**ТЗ:** B §5.3, §7.1

| Задача | Кто | Файл |
|--------|-----|------|
| `POST /tasks/{id}/recalculate-price` → Oracle `TRANSPORT_TASK.stoim_tt` | Backend | `transport.py` |
| `PATCH /tasks/{id}/price` → PL/SQL UPDATE PRICE | Backend | `transport.py` |
| `DELETE /billing/orders/{id}/tasks/{tt_id}` → обнулить PAY_ORDER_ID | Backend | `transport.py` |
| Секция цены в карточке рейса: текущая цена + кнопка пересчёта + ручной ввод | Frontend | `TransportDispatchPage.tsx` |
| Схема `PriceUpdateRequest` | Backend | `schemas.py` |

**Что видит диспетчер после спринта:**
В карточке рейса: «Цена рейса: 15 450 ₽ · ⟳ Пересчитать». Можно ввести сумму вручную и сохранить.

**Статус:** ✅ Завершён  
**Коммит:** `bc0ddae` · **Дата:** 2026-05-27  
**Тесты:**  
- `tests/transport/test_sprint18_functional.py` — 12 pytest-кейсов (recalculate, set price, remove from order, 404, 422)  
- `tests/transport/sprint18_usability_checklist.md` — 15 юзабилити-проверок  
- `tests/transport/transport_sprint18_load_test.py` — 5 users, 60s, NFR recalculate≤1s, set-price≤300ms  

---

### Sprint 27 — Биллинг: Excel-экспорт реестра счетов

**Инструмент:** 🟢 КК (код-код $20) — аналогичный паттерн Sprint 26, другой набор данных

**Цель:** кнопка `[Скачать Excel]` в тулбаре реестра счетов (по макету TZ B §11) выгружает все счета текущего фильтра в XLSX. Дополняет Sprint 26 (экспорт одного счёта) до полного покрытия DoD.

**ТЗ:** B §11 (макет — `[Скачать Excel]` в заголовке реестра)

| Задача | Кто | Файл |
|--------|-----|------|
| `export_billing_registry_xlsx(...)` — реестр счетов с теми же фильтрами что `list_billing_orders` | Backend | `transport_service.py` |
| `GET /billing/orders/export.xlsx` — размещён ДО `/{order_id}` чтобы избежать конфликта маршрутов | Backend | `transport.py` |
| `handleRegistryXlsx` + кнопка «⬇ Excel» в `BillingRegistryTab` тулбаре | Frontend | `TransportDispatchPage.tsx` |

**Статус:** ✅ Завершён  
**Коммит:** `23682f3` · **Дата:** 2026-05-28  
**Тесты:**  
- `tests/transport/test_sprint27_functional.py` — 12 pytest-кейсов (MIME, magic bytes, route conflict, row count, filter)  
- `tests/transport/sprint27_usability_checklist.md` — 19 юзабилити-проверок  
- `tests/transport/transport_sprint27_load_test.py` — 5 users, 60s, NFR registry export p95 ≤ 800ms  

---

### Sprint 26 — Биллинг: Excel-экспорт счёта

**Инструмент:** 🟢 КК (код-код $20) — бэкенд openpyxl, фронт blob-download

**Цель:** закрыть DoD-критерий §12 #7 — «Экспорт в Excel содержит все рейсы выбранного счёта с суммой и реквизитами». Кнопка «⬇ Excel» в панели деталей счёта скачивает XLSX-файл.

**ТЗ:** B §12 критерий 7, B §11 (макет — `[Скачать Excel]`)

| Задача | Кто | Файл |
|--------|-----|------|
| `openpyxl` в requirements.txt | Backend | `requirements.txt` |
| `export_billing_order_xlsx(order_id)` — генерация XLSX через openpyxl | Backend | `transport_service.py` |
| `GET /billing/orders/{id}/export.xlsx` — StreamingResponse с XLSX | Backend | `transport.py` |
| `downloadBlob(path, filename)` — helper для blob-download с auth | Frontend | `TransportDispatchPage.tsx` |
| `handleDownloadXlsx` + кнопка «⬇ Excel» в `BillingOrderDetailPanel` | Frontend | `TransportDispatchPage.tsx` |
| CSS: `.billing-xlsx-btn`, `.billing-detail-export-row` | Frontend | `styles.css` |

**Статус:** ✅ Завершён  
**Коммит:** `5f6e110` · **Дата:** 2026-05-27  
**Тесты:**  
- `tests/transport/test_sprint26_functional.py` — 11 pytest-кейсов (MIME, ZIP magic, content-disposition, XLSX content, row count)  
- `tests/transport/sprint26_usability_checklist.md` — 18 юзабилити-проверок  
- `tests/transport/transport_sprint26_load_test.py` — 5 users, 60s, NFR export p95 ≤ 500ms  

---

### Sprint 25 — Биллинг: снять рейс с биллинга

**Инструмент:** 🟢 КК (код-код $20) — UI для DELETE-эндпоинта, существующего с Sprint 18

**Цель:** диспетчер может отвязать рейс от счёта через кнопку «Снять с биллинга» в карточке рейса (диспетчер) или через ✕ в панели деталей счёта (реестр биллинга). Закрывает оставшийся DoD-критерий по отвязке рейсов от счёта.

**ТЗ:** B §11 (workflow биллинга)

| Задача | Кто | Файл |
|--------|-----|------|
| `handleDetachFromBilling` — отвязка рейса из карточки + confirm | Frontend | `TransportDispatchPage.tsx` |
| `BillingOrderCard`: проп `onDetach?` + кнопка «Снять с биллинга» | Frontend | `TransportDispatchPage.tsx` |
| `BillingOrderDetailPanel`: проп `onDetachTask?` + ✕ на каждой строке рейса | Frontend | `TransportDispatchPage.tsx` |
| Защита: `!order.closed && !order.payed` — кнопки скрыты | Frontend | `TransportDispatchPage.tsx` |
| CSS: `.billing-detach-btn`, `.billing-detach-task-btn` | Frontend | `styles.css` |

**Статус:** ✅ Завершён  
**Коммит:** `7a3e833` · **Дата:** 2026-05-27  
**Тесты:**  
- `tests/transport/test_sprint25_functional.py` — 9 pytest-кейсов (detach endpoint, closed/payed rejection, tasks structure)  
- `tests/transport/sprint25_usability_checklist.md` — 18 юзабилити-проверок  
- `tests/transport/transport_sprint25_load_test.py` — 5 users, 60s, NFR orders/tasks p95 ≤ 300ms  

---

### Sprint 24 — VRP: Drag-and-drop перестановка СТ

**Инструмент:** 🟢 КК (код-код $20) — HTML5 drag-and-drop, клиентская логика

**Цель:** диспетчер раскрывает рейс в планировщике, видит список СТ и перетаскивает их между рейсами. Метрики пересчитываются мгновенно. Закрывает DoD-критерий §11.11 #8.

**ТЗ:** §11.11 критерий 8 — «Диспетчер может перетащить СТ из одного маршрута в другой — метрики пересчитываются мгновенно»

| Задача | Кто | Файл |
|--------|-----|------|
| `localRoutes` state — мутируемая копия plan.routes | Frontend | `TransportPlannerPage.tsx` |
| `expandedRouteIdx` — toggle состава рейса | Frontend | `TransportPlannerPage.tsx` |
| `handleDragStart`, `handleDrop` — перемещение СТ + пересчёт метрик | Frontend | `TransportPlannerPage.tsx` |
| `routesModified` — индикатор изменений + кнопка сброса ↺ | Frontend | `TransportPlannerPage.tsx` |
| Полилинии карты используют `displayRoutes` | Frontend | `TransportPlannerPage.tsx` |
| CSS: `.planner-rp-stop-item`, `.planner-rp-stop-list`, `.planner-modified-hint` | Frontend | `styles.css` |

**Статус:** ✅ Завершён  
**Коммит:** `0c4ad0c` · **Дата:** 2026-05-27  
**Тесты:**  
- `tests/transport/test_sprint24_functional.py` — 9 pytest-кейсов (структура stops, pallet calc, utilization)  
- `tests/transport/sprint24_usability_checklist.md` — 19 юзабилити-проверок  
- `tests/transport/transport_sprint24_load_test.py` — 5 users, 60s, NFR metrics p95 ≤ 200ms  

---

### Sprint 23 — Детальный просмотр счёта + экспорт CSV рейсов

**Инструмент:** 🟢 КК (код-код $20) — правая панель + CSV-экспорт, паттерн уже есть в проекте

**Цель:** клик на строку реестра счетов открывает панель с полным списком рейсов в этом счёте и кнопкой скачать CSV. Закрывает DoD-критерий №7 (экспорт со всеми рейсами счёта).

**ТЗ:** B §11 (макет), B §12 критерий 7

| Задача | Кто | Файл |
|--------|-----|------|
| `BillingOrderTask` type | Frontend | `TransportDispatchPage.tsx` |
| `selectedBillingOrder`, `billingOrderTasks` state + `handleBillingOrderSelect` | Frontend | `TransportDispatchPage.tsx` |
| `BillingRegistryTab`: props `selectedOrderId` + `onOrderSelect`, клик по строке | Frontend | `TransportDispatchPage.tsx` |
| `BillingOrderDetailPanel`: заголовок, таблица рейсов, итого, экспорт | Frontend | `TransportDispatchPage.tsx` |
| `exportOrderTasksCsv` — скачать рейсы счёта | Frontend | `TransportDispatchPage.tsx` |
| Правая панель для billing-вкладки (при наличии selectedBillingOrder) | Frontend | `TransportDispatchPage.tsx` |
| CSS: `.billing-row-selected`, `.billing-row-clickable`, `.billing-detail-*` | Frontend | `styles.css` |

**Статус:** ✅ Завершён  
**Коммит:** `f4413b4` · **Дата:** 2026-05-27  
**Тесты:**  
- `tests/transport/test_sprint23_functional.py` — 9 pytest-кейсов (tasks endpoint, поля, согласованность с заголовком)  
- `tests/transport/sprint23_usability_checklist.md` — 17 юзабилити-проверок  
- `tests/transport/transport_sprint23_load_test.py` — 8 users, 60s, NFR tasks p95 ≤ 300ms  

---

### Sprint 22 — Справочник компаний + поле NUM_PLAT

**Инструмент:** 🟢 КК (код-код $20) — добавить поле в SQL и эндпоинт справочника

**Цель:** реестр счетов отображает номер платёжного поручения (NUM_PLAT); диалог «Выставить счёт» предлагает автодополнение ТК из RRL_BILL_COMPANY.

**ТЗ:** B §7 (реквизиты счёта), §8 (справочник ТК)

| Задача | Кто | Файл |
|--------|-----|------|
| `B.NUM_PLAT` в SELECT и GROUP BY в `list_billing_orders`, `get_billing_order` | Backend | `transport_service.py` |
| `num_plat` в BillingOrder Pydantic-схеме | Backend | `schemas.py` |
| `GET /billing/companies` — список из RRL_BILL_COMPANY | Backend | `transport.py`, `transport_service.py` |
| Колонка «№ платёжного» в реестре счетов + CSV-экспорт | Frontend | `TransportDispatchPage.tsx` |
| `<datalist>` компаний в диалоге «Выставить счёт» | Frontend | `TransportDispatchPage.tsx` |
| Строка «№ платёж.» в BillingOrderCard | Frontend | `TransportDispatchPage.tsx` |

**Статус:** ✅ Завершён  
**Коммит:** `ef09a1c` · **Дата:** 2026-05-27  
**Тесты:**  
- `tests/transport/test_sprint22_functional.py` — 9 pytest-кейсов (companies endpoint, num_plat поле, регрессия схемы)  
- `tests/transport/sprint22_usability_checklist.md` — 13 юзабилити-проверок  
- `tests/transport/transport_sprint22_load_test.py` — 8 users, 60s, NFR companies p95 ≤ 200ms, orders p95 ≤ 300ms  

---

### Sprint 21 — Права доступа биллинга (RBAC)

**Инструмент:** 🟢 КК (код-код $20) — константы прав + привязка к эндпоинтам

**Цель:** биллинговые операции защищены отдельными Oracle-правами, не смешиваются с правами диспетчера.

**ТЗ:** B §6

| Задача | Кто | Файл |
|--------|-----|------|
| `BILLING_EDIT_PERMISSION = "edit_bill_tt"` | Backend | `auth.py` |
| `BILLING_CALC_PRICE_PERMISSION = "calc_tt_price"` | Backend | `auth.py` |
| `BILLING_CREATE_PRICE_PERMISSION = "create_tt_price"` | Backend | `auth.py` |
| Замена `TRANSPORT_DISPATCH_EDIT_PERMISSION` на биллинговые права в 8 эндпоинтах | Backend | `transport.py` |

**Статус:** ✅ Завершён  
**Коммит:** `f7e27ad` · **Дата:** 2026-05-27  
**Тесты:**  
- `tests/transport/test_sprint21_functional.py` — 6 pytest-кейсов (константы, доступность эндпоинтов)  
- `tests/transport/sprint21_usability_checklist.md` — 13 юзабилити-проверок  
- `tests/transport/transport_sprint21_load_test.py` — 8 users, 60s, NFR p95 ≤ 300/500ms  

---

### Sprint 20 — Защита выставленного рейса (бэкенд)

**Инструмент:** 🟢 КК (код-код $20) — защитные проверки в сервисном слое

**Цель:** API отклоняет с 409 попытки изменить рейс, привязанный к биллинг-заказу.

**ТЗ:** B §10

| Задача | Кто | Файл |
|--------|-----|------|
| `cancel_task` — проверить PAY_ORDER_ID, 409 если выставлен | Backend | `transport_service.py` |
| `assign_sts` — проверить PAY_ORDER_ID, 409 если выставлен | Backend | `transport_service.py` |
| `unassign_st` — проверить PAY_ORDER_ID, 409 если выставлен | Backend | `transport_service.py` |

**Статус:** ✅ Завершён  
**Коммит:** `47abd76` · **Дата:** 2026-05-27  
**Тесты:**  
- `tests/transport/test_sprint20_functional.py` — 7 pytest-кейсов (cancel/assign/unassign → 409; note/price → 200)  
- `tests/transport/sprint20_usability_checklist.md` — 12 юзабилити-проверок  
- `tests/transport/transport_sprint20_load_test.py` — 5 users, 60s, NFR early-409 p95 ≤ 200ms  

---

### Sprint 19 — Привязка рейса к существующему счёту

**Инструмент:** 🟢 КК (код-код $20) — расширение диалога «Выставить счёт»

**Цель:** диспетчер может добавить рейс к уже существующему открытому счёту, а не только создавать новый.

**ТЗ:** B §5.2, §5.4 (диалог привязки рейсов к заказу)

| Задача | Кто | Файл |
|--------|-----|------|
| Загрузка открытых счетов ТК в диалоге «Выставить счёт» | Frontend | `TransportDispatchPage.tsx` |
| Выбор: «Создать новый счёт» / «Добавить к существующему» | Frontend | `TransportDispatchPage.tsx` |
| `handleOpenBilling(existingOrderId)` — вызывает POST /billing/orders/{id}/tasks если выбран существующий | Frontend | `TransportDispatchPage.tsx` |
| CSS для секции выбора счёта | Frontend | `styles.css` |

**Что видит диспетчер после спринта:**
В диалоге «Выставить счёт» появляется список открытых счетов этой ТК. Можно выбрать «БТ-0003 (01.05 – 31.05)» вместо создания нового.

**Статус:** ✅ Завершён  
**Коммит:** `6056aa9` · **Дата:** 2026-05-27  
**Тесты:**  
- `tests/transport/test_sprint19_functional.py` — 9 pytest-кейсов (filter open orders, add to existing, 404)  
- `tests/transport/sprint19_usability_checklist.md` — 16 юзабилити-проверок  
- `tests/transport/transport_sprint19_load_test.py` — 5 users, 60s, NFR filter≤300ms, add≤500ms  

---

## Итог

| Блок | Спринты | Недель | Результат |
|------|---------|--------|-----------|
| Диспетчер | 1–6 | 6 | Полная замена C# WinForms для ежедневной работы |
| MAP / VRP | 7–10 | 4.5 | Автоматическая оптимизация рейсов с картой |
| ARM / Ганта | 11–14 | 4.5 | Планирование машин, нарушения режимов, план-факт |
| Биллинг | 15–23 | 6 | Полный цикл биллинга: выставление, управление, реестр, цена, привязка, защита, RBAC, справочник компаний, детальный просмотр |
| MAP / VRP (доп.) | 24 | 0.5 | Drag-and-drop редактирование плана — закрывает DoD §11.11 #8 |
| **Итого** | **24** | **~20.5** | |

**Миграции БД:**
- `044_apply.sql` — перед Sprint 11 (операции и нормативы)
- `045_apply.sql` — перед Sprint 7 (координаты и дистанционная матрица)

**Docker Desktop** (настроить до Sprint 8):
- RAM ≥ 10 GB, CPUs ≥ 4 в настройках Docker Desktop
- Подготовить `osrm-data/` с картой России (~3 GB)
- При покупке сервера: перенести контейнеры без изменения кода

---

## Acceptance Testing по блокам

Тестовые данные: **«Добра Цен»** — seed 046+047, применён в тестовой Oracle.
Состав: 3 склада (9201–9203), 77 адресов, 15 ТС/водителей, ~385 СТ, ~1 540 паллет.
Маска отката: `@047_rollback.sql → @046_rollback.sql`

---

### Блок I — Диспетчер (Sprints 1–6)

**Среда:** API :8088 + Frontend :3000, тестовая Oracle с seed «Добра Цен».

| # | Тест-кейс | Ожидаемый результат |
|---|-----------|---------------------|
| AT-D-01 | Открыть `TransportDispatchPage`, дождаться загрузки | Таблица содержит ~385 строк СТ, 3 разных цвета строк по складам 9201/9202/9203 |
| AT-D-02 | Фильтр «Склад» → выбрать только 9201 (Пермь) | В таблице остаются только СТ из Перми (~130 строк) |
| AT-D-03 | Фильтр `АДР` → ввести «Лысьва» | Таблица сужается до адресов Лысьвы |
| AT-D-04 | Клик по «РАЙОН» с одним значением | Все строки с этим районом выделяются (чекбоксы); строка итогов обновляется |
| AT-D-05 | Shift+Click от строки 1 до строки 10 | Выделено 10 строк; строка итогов показывает сумму паллет, веса, объёма |
| AT-D-06 | Нажать «Создать маршрут» при 5 выделенных СТ | Открывается диалог; список ТС содержит машины 9201–9215; рейс создаётся |
| AT-D-07 | После создания рейса: фильтр «НЕ РАСПРЕДЕЛЁННЫЕ» включён | Назначенные СТ исчезают из таблицы |
| AT-D-08 | Перейти на вкладку «Маршруты» | Созданный рейс виден в списке с машиной, водителем, доком |
| AT-D-09 | Кликнуть на рейс → нижняя таблица | Состав рейса показывает СТ с адресами, ORD, временными окнами |
| AT-D-10 | Изменить LOAD_TYPE на «П» для одного СТ в составе | Inline-dropdown сохраняет значение; повторный `GET /tasks/{id}/sts` возвращает `LOAD_TYPE = 'П'` |
| AT-D-11 | Попытаться закрыть рейс при `VERIFY_PERC < 100%` | API возвращает 422; Frontend показывает текст ошибки из `can_print` |
| AT-D-12 | Расформировать рейс → подтвердить | СТ возвращаются в список «НЕ РАСПРЕДЕЛЁННЫЕ» |

---

### Блок II — MAP / VRP (Sprints 7–10)

**Дополнительно:** миграция 045 применена, координаты заполнены (77 адресов «Добра Цен» имеют SHIROTA/DOLGOTA).

| # | Тест-кейс | Ожидаемый результат |
|---|-----------|---------------------|
| AT-M-01 | Открыть `TransportPlannerPage` | На карте OSM видны 77 маркеров; 3 разных цвета по складам |
| AT-M-02 | Нажать «Авто-план» (Haversine mode, без Docker) | Через ≤ 60 сек появляются цветные полилинии; ≤ 15 рейсов для 77 адресов |
| AT-M-03 | Панель метрик | Утилизация парка > 0%; Нарушений окон отображается |
| AT-M-04 | Нарисовать полигон вокруг Перми (15 маркеров внутри) | Кнопка «Создать рейс из выбранных» активируется с числом СТ внутри |
| AT-M-05 | Drag маркера из одного маршрута в другой | Метрики правой панели пересчитываются; полилинии обновляются |
| AT-M-06 | «Применить план» → подтвердить | В `TransportDispatchPage` появляются новые рейсы; `RRL_TRANSPORT_TASK` пополнился |
| AT-M-07 | `GET /routing/status` | `active_provider` = `HAVERSINE` (или `OSRM` если Docker поднят); `addr_without_coords` = 0 |
| AT-M-08 | `POST /distance-matrix/rebuild?source=haversine` | Ответ: `{"pairs": 5852, "source": "HAVERSINE"}` (77×77 − 77 диагональ) |

---

### Блок III — ARM / Ганта (Sprints 11–14)

**Дополнительно:** миграция 044 применена; создано ≥ 5 рейсов с назначенными ТС из тестового парка.

| # | Тест-кейс | Ожидаемый результат |
|---|-----------|---------------------|
| AT-G-01 | Создать рейс → `POST /tasks/{id}/plan-operations` | В `RRL_TT_OPERATIONS` появляется цепочка из 12 операций с PLAN_START/END |
| AT-G-02 | Открыть `TransportGanttPage` | 15 строк машин; для рейсов с операциями — цветные блоки на временной оси |
| AT-G-03 | Синяя линия текущего времени | Линия отображается на текущем часе; через 1 мин сдвигается |
| AT-G-04 | Hover на блок «Погрузка» | Тултип: `Погрузка: план 08:30–09:15, факт —, дельта —` |
| AT-G-05 | Drag блок рейса на 1 час вперёд | Все операции цепочки сдвигаются; `SHIPMENT_DATE` обновляется; `GET /tasks/{id}` подтверждает |
| AT-G-06 | Drag вызывает пересечение с другим рейсом | Блок краснеет; сохранение заблокировано |
| AT-G-07 | Диалог «Создать маршрут» → список машин | Колонка «Свободна с» показывает корректное время для занятых ТС |
| AT-G-08 | Зафиксировать `fact_start` операции | `PATCH /operations/{op_id}/fact` → 200; в Ганте блок показывает факт |
| AT-G-09 | Блок `REST` авто | При рейсе с DRIVE > 2 ч появляется серый блок REST |
| AT-G-10 | `GET /plan-fact?date_from=today&date_to=today` | Возвращает данные по всем рейсам дня; `delta_min` корректны |

---

### Блок IV — Биллинг (Sprints 15–17)

**Дополнительно:** несколько рейсов закрыты; водители 9201–9215 — наёмные (`SOBSTVENNYY = 0`).

| # | Тест-кейс | Ожидаемый результат |
|---|-----------|---------------------|
| AT-B-01 | Закрытый рейс с наёмным водителем → «Выставить счёт» | Рейс получает `PAY_ORDER_ID`; статус `billed`; кнопки изменения состава скрыты |
| AT-B-02 | Попытка расформировать рейс с `PAY_ORDER_ID` | API возвращает `409 Conflict`; Frontend показывает сообщение |
| AT-B-03 | Открыть вкладку «Биллинг» | Таблица биллинг-заказов; строка с созданным счётом |
| AT-B-04 | Кнопка «Закрыть счёт» | Статус счёта меняется на `closed`; бейдж 🔵 |
| AT-B-05 | Кнопка «Оплачен» | Статус `paid`; бейдж 🟢 |
| AT-B-06 | Фильтр по ТК + экспорт Excel | Файл `transport_billing_<date>.xlsx` содержит только рейсы нужной компании |

---

## План развёртывания

### Окружения

| Окружение | Назначение | БД |
|-----------|-----------|-----|
| **dev** | Разработка | Oracle RABAEV (seed «Добра Цен» применён) |
| **staging** | Приёмочное тестирование | Копия prod-схемы без реальных рейсов |
| **prod** | Боевая эксплуатация | Oracle RABAEV prod |

### Порядок применения миграций

```
042_apply.sql   ✅ (Phase 1, уже применена)
043_apply.sql   ✅ (Phase 1, уже применена)
046_apply.sql   ✅ (seed «Добра Цен», dev)
047_apply.sql   ✅ (seed «Добра Цен», dev)
044_apply.sql   ⬜ перед Sprint 11 (RRL_TRANSPORT_NORMS, RRL_TT_OPERATIONS)
045_apply.sql   ⬜ перед Sprint 7  (LATITUDE/LONGITUDE в RRL_ADDR, матрица расстояний)
```

Каждая миграция идемпотентна (MERGE). Rollback: `NNN_rollback.sql` в той же папке.

### Чеклист выпуска каждого спринта

```
[ ] 1. Применить SQL-миграцию (если есть) — проверить через NNN_smoke.sql
[ ] 2. Запустить API: uvicorn -- reload (dev) или pm2 restart api (staging/prod)
[ ] 3. Запустить Frontend: npm run build && serve -s dist (staging) или vite (dev)
[ ] 4. Прогнать acceptance-тесты блока (см. раздел «Acceptance Testing»)
[ ] 5. Проверить C# WinForms: открыть tabPage6 — убедиться что не сломан
[ ] 6. Зафиксировать коммит-хэш и дату в этом файле (строка «Коммит:»)
```

### Период параллельной эксплуатации

C# WinForms и React работают **одновременно** в течение всего Блока I (Sprints 1–6). Переход на React-только производится только после того, как диспетчеры отработали на React не менее 5 рабочих дней без обращений к C# для транспортных задач.

Признак готовности к отключению C#: все 12 acceptance-тестов AT-D-01…AT-D-12 пройдены на prod-данных.

### Инфраструктура Docker (до Sprint 8)

```bash
# 1. Docker Desktop: Settings → Resources → RAM ≥ 10 GB, CPUs ≥ 4
# 2. Скачать карту России (~3 GB)
wget https://download.geofabrik.de/russia-latest.osm.pbf -P ./osrm-data/
# 3. Подготовить OSRM (однократно, ~30 мин)
docker run --rm -v "$(pwd)/osrm-data:/data" ghcr.io/project-osrm/osrm-backend:v5.27 \
  osrm-extract -p /opt/car.lua /data/russia-latest.osm.pbf
docker run --rm -v "$(pwd)/osrm-data:/data" ghcr.io/project-osrm/osrm-backend:v5.27 \
  osrm-partition /data/russia-latest.osrm
docker run --rm -v "$(pwd)/osrm-data:/data" ghcr.io/project-osrm/osrm-backend:v5.27 \
  osrm-customize /data/russia-latest.osrm
# 4. Поднять контейнеры
docker compose -f docker-compose.osrm.yml up -d
docker compose -f docker-compose.valhalla.yml up -d
# 5. Проверить
curl http://localhost:5000/health   # OSRM
curl http://localhost:8002/health   # Valhalla
```
