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
| 28 | Диспетчер: Excel-экспорт списка рейсов | Диспетчер | 0.5 нед | 🟢 КК | ✅ `284c754` 2026-05-28 |
| 29 | Phase 2 полуавто: создать рейс из кластера (⚡ Рейс) | Диспетчер | 0.5 нед | 🟢 КК | ✅ `2f97815` 2026-05-28 |
| 30 | Live load bar — заполненность машины по паллетам | Диспетчер | 0.5 нед | 🟢 КК | ✅ `9436717` 2026-05-28 |
| 31 | ClusterSidebar — левая панель карточек районов | Диспетчер | 0.5 нед | 🟢 КК | ✅ `86d3a71` 2026-05-28 |
| 32 | Phase 2 ✅: предупреждение о перегрузе | Диспетчер | 0.5 нед | 🟢 КК | ✅ `286c0c7` 2026-05-28 |
| 33 | Режим «Кратко» в таблице маршрутов (§3.8.1) | Диспетчер | 0.5 нед | 🟢 КК | ✅ `b5b12d1` 2026-05-28 |
| 34 | Bugfix: cancel_task освобождает СТ перед удалением | Диспетчер | 0.25 нед | 🟢 КК | ✅ `73cd887` 2026-05-28 |
| 35 | Оптимизация: server-side raion filter в list_available_sts | Диспетчер | 0.25 нед | 🟢 КК | ✅ `c60c420` 2026-05-28 |
| 36 | Массовое снятие СТ с рейса (чекбоксы + «Снять выбранные») | Диспетчер | 0.25 нед | 🟢 КК | ✅ `7aa8b16` 2026-05-28 |
| 37 | «Выделить всё» в таблице СТ + авто-обновление данных (60 с) | Диспетчер | 0.25 нед | 🟢 КК | ✅ `a287a02` 2026-05-28 |
| 38 | «Копировать рейс» — клонировать реквизиты без СТ | Диспетчер | 0.25 нед | 🟢 КК | ✅ `ad2a56f` 2026-05-28 |
| 39 | Badge активных фильтров + кнопка «× Сбросить» | Диспетчер | 0.25 нед | 🟢 КК | ✅ `1a19f0d` 2026-05-28 |
| 40 | Сводка дня над таблицей рейсов (Рейсов · Паллет · Вес · Отгружено) | Диспетчер | 0.25 нед | 🟢 КК | ✅ `0fab5d7` 2026-05-28 |
| 41 | Фильтр рейсов по статусу (Все / Активен / Отгружен / Отменён) | Диспетчер | 0.25 нед | 🟢 КК | ✅ `04302e3` 2026-05-28 |
| 42 | Toast-уведомления об успешных операциях (создание, закрытие, назначение СТ) | Диспетчер | 0.25 нед | 🟢 КК | ✅ `abae320` 2026-05-28 |
| 43 | Сортировка таблицы рейсов по клику на заголовок колонки | Диспетчер | 0.25 нед | 🟢 КК | ✅ `86a8908` 2026-05-28 |
| 44 | Глобальный Escape: снятие выделения и закрытие диалогов | Диспетчер | 0.1 нед | 🟢 КК | ✅ `9f1c8a5` 2026-05-28 |
| 45 | Кнопка «#ID →» для перехода к рейсу из таблицы СТ | Диспетчер | 0.25 нед | 🟢 КК | ✅ `2476a00` 2026-05-28 |
| 46 | Кнопки ◄ ► быстрого переключения дня в тулбарах | Диспетчер | 0.1 нед | 🟢 КК | ✅ `123e8eb` 2026-05-28 |
| 47 | localStorage — сохранение даты, вкладки и режима просмотра | Диспетчер | 0.1 нед | 🟢 КК | ✅ `571643a` 2026-05-28 |
| 48 | Кнопка «Сегодня» для сброса даты фильтра | Диспетчер | 0.1 нед | 🟢 КК | ✅ `41deff6` 2026-05-28 |
| 49 | Компактный режим таблицы СТ (toggle «Компактно») | Диспетчер | 0.1 нед | 🟢 КК | ✅ `c7faca3` 2026-05-28 |
| 50 | Зелёная полоска для полностью собранных СТ (VERIFY_PERC=100%) | Диспетчер | 0.1 нед | 🟢 КК | ✅ `f3a7a42` 2026-05-28 |
| 51 | Закреплённая панель выделения (count · P · M · V + кнопки) | Диспетчер | 0.1 нед | 🟢 КК | ✅ `ad061e9` 2026-05-28 |
| 52 | Сортировка таблицы доступных СТ по клику на заголовок колонки | Диспетчер | 0.1 нед | 🟢 КК | ✅ `e19b892` 2026-05-28 |
| 53 | Сворачивание панели фильтров (collapse/expand + localStorage) | Диспетчер | 0.1 нед | 🟢 КК | ✅ `8db5812` 2026-05-28 |
| 54 | Кнопка «⬇ CSV» в sel-bar — экспорт выделенных СТ в файл | Диспетчер | 0.1 нед | 🟢 КК | ✅ `32cd67b` 2026-05-28 |
| 55 | Итоги по всем видимым СТ (П/кг/м³) в тулбаре таблицы | Диспетчер | 0.1 нед | 🟢 КК | ✅ `3e912d4` 2026-05-28 |
| 56 | Печать маршрутного листа (HTML-окно + window.print()) | Диспетчер | 0.1 нед | 🟢 КК | ✅ `c41a6e0` 2026-05-28 |
| 57 | Быстрое добавление СТ по номеру (quick-add row) | Диспетчер | 0.1 нед | 🟢 КК | ✅ `1d77f41` 2026-05-28 |
| 58 | Развернуть/свернуть все районы (кластерный режим) | Диспетчер | 0.1 нед | 🟢 КК | ✅ `6b8d913` 2026-05-28 |
| 59 | Быстрый поиск по маршрутам (ID, авто, водитель, регион, ТК) | Диспетчер | 0.1 нед | 🟢 КК | ✅ `c00a221` 2026-05-28 |
| 60 | Пагинация таблицы доступных СТ (100 строк/страница) | Диспетчер | 0.1 нед | 🟢 КК | ✅ `a25c8d4` 2026-05-28 |
| 61 | Быстрый фильтр по складу (warehouse selector) | Диспетчер | 0.1 нед | 🟢 КК | ✅ `971d128` 2026-05-28 |
| 62 | Прилипающий заголовок таблицы СТ (sticky thead) | Диспетчер | 0.1 нед | 🟢 КК | ✅ `97c2d32` 2026-05-28 |
| 63 | Значок «⚠ N не собрано» в тулбаре СТ | Диспетчер | 0.1 нед | 🟢 КК | ✅ `60d0842` 2026-05-28 |
| 64 | Клик по значку «не собрано» → выделить все несобранные | Диспетчер | 0.1 нед | 🟢 КК | ✅ `d29a250` 2026-05-28 |
| 65 | Синяя пилюля (выделено N) на вкладке «Заявки» | Диспетчер | 0.1 нед | 🟢 КК | ✅ `1498135` 2026-05-28 |
| 66 | VERIFY_PERC (VerifyBar) в таблице состава рейса (TaskStTableRow) | Диспетчер | 0.1 нед | 🟢 КК | ✅ `60dbc68` 2026-05-28 |
| 67 | Amber-подсветка несобранных строк в составе рейса (VERIFY_PERC < 100) | Диспетчер | 0.1 нед | 🟢 КК | ✅ `7ff119f` 2026-05-28 |
| 68 | Ctrl+Enter — добавить выделенные СТ в рейс (keyboard shortcut) | Диспетчер | 0.1 нед | 🟢 КК | ✅ `d3f3685` 2026-05-28 |
| 69 | Delete — снять выделенные СТ с рейса (keyboard shortcut) | Диспетчер | 0.1 нед | 🟢 КК | ✅ `326f499` 2026-05-28 |
| 70 | «Все» / «Нет» — тулбар выделения всех СТ рейса | Диспетчер | 0.1 нед | 🟢 КК | ✅ `340b52a` 2026-05-28 |
| **Итого** | | | **~30.6 нед** | | |

**Легенда инструментов:**
- 🟢 **КК** — код-код ($20): весь спринт самостоятельно; задача типовая, паттерны в проекте есть
- 🟡 **КК+КС** — кодекс ($200) проектирует архитектуру → код-код ($20) реализует
- 🔴 **КС** — кодекс ($200) ведёт спринт: сложный алгоритм или нетипичный UI-компонент (Sprint 8: VRP, Sprint 12: Ганта)

**Инфраструктура OSRM/Valhalla** разворачивается в Docker Desktop (Windows, выделить ≥10 GB RAM) перед Sprint 8. При покупке сервера — перенести контейнеры без изменения кода.

---

## Hardening checkpoint — 2026-05-28

Область: ТМС-2, Sprint 1–20. Проверка идёт не по галочкам, а по рабочим API/DB/test paths.

- Block I / Sprint 1–6 fresh gate: добавлены прямые Sprint 1–3 tests и UI smoke Sprint 1–6; `pytest tests\transport\test_sprint1_functional.py ... tests\transport\test_sprint6_functional.py -q -ra --tb=short` -> `78 passed`; UI smoke Sprint 1–6 passed; Sprint 4–6 load NFR passed after connection pooling, set-based readiness, short caches, stable seed-date `2026-05-25`, and lightweight audit for high-frequency read-only transport GET endpoints.
- Блок I / Sprint 1–6: актуальный functional layer есть для Sprint 4–6; `pytest tests\transport\test_sprint4_functional.py tests\transport\test_sprint5_functional.py tests\transport\test_sprint6_functional.py -q -ra --tb=short` -> `40 passed, 14 skipped`.
- Блок II / Sprint 7–10: применены dev Oracle migrations `051_apply.sql` и `052_apply.sql`; `pytest tests\transport\test_sprint7_functional.py tests\transport\test_sprint8_functional.py tests\transport\test_sprint9_functional.py tests\transport\test_sprint10_functional.py -q -ra --tb=short` -> `54 passed, 7 skipped`.
- Блок III / Sprint 11–14: применена dev Oracle migration `053_apply.sql` с legacy-compatible правкой FK; `pytest tests\transport\test_sprint11_functional.py tests\transport\test_sprint12_functional.py tests\transport\test_sprint13_functional.py tests\transport\test_sprint14_functional.py -q -ra --tb=short` -> `54 passed, 1 skipped`.
- Блок IV / Sprint 15–20: применена dev Oracle migration `054_apply.sql` с legacy-compatible расширением `RRL_BILL_ORDERS.COMPANY`; `pytest tests\transport\test_sprint15_functional.py tests\transport\test_sprint16_functional.py tests\transport\test_sprint17_functional.py tests\transport\test_sprint18_functional.py tests\transport\test_sprint19_functional.py tests\transport\test_sprint20_functional.py -q -ra --tb=short` -> `62 passed`.
- Общий контроль Sprint 4–20: `pytest tests\transport\test_sprint4_functional.py ... tests\transport\test_sprint20_functional.py -q -ra --tb=short` -> `211 passed, 21 skipped` за 7:04.
- Исправлены обнаруженные дефекты: uppercase/lowercase contract для transport rows, лишний `user_id` bind в `PATCH /tasks/{id}`, закрытие пустого рейса, реальные колонки `RRL_TRANSPORT_TYPE`, паллетный запрос без несуществующего `SP.DELETED`, быстрый empty-date path для `available-sts`/planner orders, Sprint 8 `DISTANCE_KM/UPDATED_AT`, batch rebuild матрицы, `PAYLOAD` вместо `PLAN_JSON`, forecast без тяжёлой view.
- Для ARM/Ганта исправлены: alias `Газель -> 5` для legacy `TRANSTYPE`, Sprint 11 operations tables, Gantt на `RRL_TR_VEHICLE` вместо отсутствующей `RRL_TRANSPORTS`, авто-планирование операций для рейсов без цепочки, корректная агрегация рейсов без машины, `CONDITION AS STATUS`/`DELETED` в availability и plan-fact.
- Для биллинга исправлены: DML-функции Oracle вызываются из PL/SQL blocks, а не `SELECT FROM DUAL`; `RRL_ADD_TT_2_BILLINGORDER`/close/pay возвращают реальные ошибки; add/remove не выдают partial-success; `get_task()` возвращает `PAY_ORDER_ID`, поэтому billed-рейсы защищены от cancel/assign/unassign; Sprint 15/18/19/20 тестовые данные теперь используют реальные рейсы с ТК и рассчитанной ценой.
- Риск: skips связаны с отсутствием подходящих свободных СТ/истории в текущем seed на относительную дату теста; для финального приёмочного прогона нужен стабильный dated fixture вместо `date.today()+1`.
- Риск MAP/VRP: Sprint 8 route-detail assertions остаются skipped при текущем dev seed, потому что solver возвращает `solver_used=none` и 0 маршрутов на тестовые даты; нужен стабильный fixture с геокодированными СТ и активным ТС для полного apply-plan acceptance.

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
| Расширить `GET /available-sts`: добавить `RAION`, `TRANSPORT_TYPE`, `STOL`, `PRIM1`, `VERIFY_PERC`, `SUGAR` legacy-признак полнопалетной отборки, `DATE_LOAD` | Backend | `transport_service.py` |
| Добавить query-параметры: `addr_mask`, `st_mask`, `st_mask_exclude`, `ware_ids`, `transport_type`, `assembled_only`, `not_assembled_only`, `max_weight_kg`, `max_volume_m3`, `date_to`, `articul` | Backend | `transport.py` |
| Расширить `AvailableSt` схему | Backend | `schemas.py` |
| Таблица СТ: 16 колонок согласно §3.3 | Frontend | `TransportDispatchPage.tsx` |
| Цветовая подсветка строк по WARE_ID (§3.4) | Frontend | `styles.css` |
| Панель фильтров (§3.6): все поля, дебаунс 300 мс | Frontend | `TransportDispatchPage.tsx` |

**Что видит диспетчер после спринта:**
Таблица СТ с полным набором данных: склад (цветная), паллеты, вес, объём, регион, адрес, ST-номер, рейс, район, тип ТС, гидроборт, стол, примечание, дата загрузки, полнопалетная отборка. Работают все фильтры: по дате, складу, адресу, СТ, типу ТС, весу/объёму.

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

**Статус:** ✅ Завершён; 2026-05-28 hardening re-check passed
**Коммит:** `3b19a91` · **Дата:** 2026-05-26
**Тесты:**
- `tests/transport/test_sprint7_functional.py` — 14 pytest-кейсов (planner/orders, routing/status), `14 passed` on `2026-05-25` seed
- `tests/transport/sprint7_usability_checklist.md` — 39 юзабилити-проверок
- `tests/transport/transport_sprint7_load_test.py` — thread load, NFR p95 ≤ 600ms для `/planner/orders`; latest p95 `/planner/orders` 97.5 ms, `/routing/status` 35.8 ms
- `tests/ui/transport_sprint7_ui_smoke.cjs` — UI smoke карты, фильтра типа ТС, геокодинг-статуса, marker popup
**Hardening 2026-05-28:** `/planner/orders` переведён с тяжелого `RRL_V_AVAILABLE_STS` на прямую set-based выборку по `RRL_SBORKA_PALLETS`/`RRL_SBORKA_PALLET_ROWS`/`RRL_ADDR`; read-only MAP endpoints добавлены в lightweight audit; исправлен dev runtime crash Leaflet под React StrictMode.
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

**Статус:** ✅ Завершён; 2026-05-28 hardening re-check passed
**Коммит:** `7827b84` · **Дата:** 2026-05-26
**Тесты:**
- `tests/transport/test_sprint8_functional.py` — 23 pytest-кейса (matrix rebuild, non-empty solve, metrics, apply contract), latest `23 passed`
- `tests/transport/sprint8_usability_checklist.md` — 43 юзабилити-проверки
- `tests/transport/transport_sprint8_load_test.py` — Windows-safe load gate; latest p95 metrics 360.7 ms, solve 647.5 ms, rebuild 414.6 ms
- `tests/ui/transport_sprint8_ui_smoke.cjs` — UI smoke автоплана, панели маршрутов и apply payload
**Hardening 2026-05-28:** тесты переведены на стабильный seed-date `2026-05-25`; default functional gate теперь требует непустой VRP-план, но не выполняет destructive apply на shared seed. Полный apply-flow оставлен как optional mutating gate через `TMS_RUN_MUTATING_VRP_APPLY=1`.
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

**Статус:** ✅ Завершён; 2026-05-28 hardening re-check passed with historical-template fixture risk
**Коммит:** `7c284ec` · **Дата:** 2026-05-26
**Тесты:**
- `tests/transport/test_sprint9_functional.py` — cluster solver/templates/RAION, latest `10 passed, 1 skipped` (skip: no historical template seed)
- `tests/transport/sprint9_usability_checklist.md` — 23 юзабилити-проверки
- `tests/transport/transport_sprint9_load_test.py` — Windows-safe load gate; latest p95 cluster solve 598.3 ms, templates 413.5 ms, orders 140.1 ms
- `tests/ui/transport_sprint9_ui_smoke.cjs` — UI smoke кластерного слоя, `solver=cluster`, шаблонов и template apply payload
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

**Статус:** ✅ Завершён; 2026-05-28 hardening re-check passed
**Коммит:** `bd08185` · **Дата:** 2026-05-26
**Тесты:**
- `tests/transport/test_sprint10_functional.py` — 15 pytest-кейсов (history, forecast), latest `15 passed`
- `tests/transport/sprint10_usability_checklist.md` — 24 юзабилити-проверки
- `tests/transport/transport_sprint10_load_test.py` — Windows-safe load gate; latest p95 history 471.5 ms, forecast 161.2 ms
- `tests/ui/transport_sprint10_ui_smoke.cjs` — UI smoke вкладки аналитики, history cards/table, forecast, objective weights
**Hardening 2026-05-28:** planner history/demand forecast/templates добавлены в lightweight audit; history/forecast получают короткий service-cache по параметрам.

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
**Hardening:** 2026-05-28 — доведено до рабочего состояния по API/UI/load/training.
**Тесты:**
- `tests/transport/test_sprint11_functional.py` — `20 passed` (plan-operations, get-operations, patch-fact, gantt)
- `tests/ui/transport_sprint11_ui_smoke.cjs` — passed: Гант, карточка рейса, контекстная отметка факта, план-факт вкладка
- `tests/transport/transport_sprint11_load_test.py` — passed: operations p95 160.8 ms, fact p95 219.5 ms, gantt p95 195.5 ms, plan-operations p95 175.7 ms
- `tests/transport/sprint11_usability_checklist.md` — 25 юзабилити-проверок
**Миграция:** `053_apply.sql` (RRL_TRANSPORT_NORMS + RRL_TT_OPERATIONS + 12 seed нормативов)
**Training pack:** [`../../wiki-raw/tms2_training/sprint11_arm_gantt_2026_05_28/index.html`](../../wiki-raw/tms2_training/sprint11_arm_gantt_2026_05_28/index.html)
**Performance fix:** `GET /vehicles/gantt` больше не делает N+1 и не мутирует данные на чтении; операции собираются set-based одним SQL, нормативы кешируются, `plan-operations` пишет цепочку пачкой в одной транзакции.

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
**Hardening:** 2026-05-28 — доведено до рабочего состояния по API/UI/load/training.
**Тесты:**
- `tests/transport/test_sprint12_functional.py` — `12 passed` (gantt 200, fields, op-codes, chain, durations)
- `tests/ui/transport_sprint12_ui_smoke.cjs` — passed: загрузка Ганта, легенда, сводка, hover tooltip, фильтр машин, дата-навигация, панель отклонений
- `tests/transport/transport_sprint12_load_test.py` — passed: gantt p95 158.0 ms, operations p95 86.0 ms
- `tests/transport/sprint12_usability_checklist.md` — 46 юзабилити-проверок
**Training pack:** [`../../wiki-raw/tms2_training/sprint12_gantt_dashboard_2026_05_28/index.html`](../../wiki-raw/tms2_training/sprint12_gantt_dashboard_2026_05_28/index.html)

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
**Hardening:** 2026-05-28 — доведено до рабочего состояния по API/UI/load/training.
**Тесты:**
- `tests/transport/test_sprint13_functional.py` — `16 passed` (available, plan-fact, vehicle filter without seed skip)
- `tests/ui/transport_sprint13_ui_smoke.cjs` — passed: диалог создания рейса, availability API, green/yellow/red машины, предупреждения конфликта
- `tests/transport/transport_sprint13_load_test.py` — passed: available p95 455.1 ms, plan-fact p95 651.1 ms, gantt p95 197.2 ms
- `tests/transport/sprint13_usability_checklist.md` — 24 юзабилити-проверки
**Training pack:** [`../../wiki-raw/tms2_training/sprint13_vehicle_availability_2026_05_28/index.html`](../../wiki-raw/tms2_training/sprint13_vehicle_availability_2026_05_28/index.html)
**Performance fix:** `GET /vehicles/available` получил короткий service-cache и lightweight audit; cache сбрасывается при пересчёте операций и фиксации факта.

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
**Hardening:** 2026-05-28 — доведено до рабочего состояния по API/UI/load/training.
**Тесты:**
- `tests/transport/test_sprint14_functional.py` — `7 passed` (plan-fact delta, rest_violations)
- `tests/ui/transport_sprint14_ui_smoke.cjs` — passed: вкладка «Аналитика», нарушения отдыха, бары отклонений, CSV export
- `tests/transport/transport_sprint14_load_test.py` — passed: plan-fact 1 day p95 420.1 ms, plan-fact 30 days p95 291.3 ms, gantt p95 125.5 ms
- `tests/transport/sprint14_usability_checklist.md` — 29 юзабилити-проверок
**Training pack:** [`../../wiki-raw/tms2_training/sprint14_plan_fact_2026_05_28/index.html`](../../wiki-raw/tms2_training/sprint14_plan_fact_2026_05_28/index.html)

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
**Hardening:** 2026-05-28 — доведено до рабочего состояния по API/UI/load/training.
**Тесты:**
- `tests/transport/test_sprint15_functional.py` — `12 passed` (create order, open billing, task billing, add task)
- `tests/ui/transport_sprint15_ui_smoke.cjs` — passed: закрытый рейс, диалог «Выставить счёт», создание счёта, тег счёта
- `tests/transport/transport_sprint15_load_test.py` — passed: list p95 283.0 ms, filtered list p95 85.0 ms, create p95 174.3 ms, task billing p95 189.4 ms
- `tests/transport/sprint15_usability_checklist.md` — 22 юзабилити-проверки
**Миграция:** `054_apply.sql` (SEQ_BILL_ORDERS + RRL_BILL_ORDERS идемпотентно)
**Training pack:** [`../../wiki-raw/tms2_training/sprint15_billing_open_2026_05_28/index.html`](../../wiki-raw/tms2_training/sprint15_billing_open_2026_05_28/index.html)
**Performance fix:** `GET /billing/orders` добавлен в lightweight audit; load runner допускает 404 для не привязанного рейса как корректный контракт `GET /tasks/{id}/billing`.

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
**Hardening:** 2026-05-28 — доведено до рабочего состояния по API/UI/load/training.
**Тесты:**
- `tests/transport/test_sprint16_functional.py` — `11 passed` (get order, close, pay, 404)
- `tests/ui/transport_sprint16_ui_smoke.cjs` — passed: выставлен → закрыт → оплачен в карточке рейса
- `tests/transport/transport_sprint16_load_test.py` — passed: get order p95 151.1 ms, close p95 86.3 ms, pay p95 75.1 ms
- `tests/transport/sprint16_usability_checklist.md` — 19 юзабилити-проверок
**Training pack:** [`../../wiki-raw/tms2_training/sprint16_billing_lifecycle_2026_05_28/index.html`](../../wiki-raw/tms2_training/sprint16_billing_lifecycle_2026_05_28/index.html)
**Performance fix:** read-only `GET /billing/orders/{id}` добавлен в lightweight audit; close/pay остаются полными audit mutations.

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
**Hardening:** 2026-05-28 — доведено до рабочего состояния по API/UI/load/training.
**Тесты:**
- `tests/transport/test_sprint17_functional.py` — `12 passed` (list, filters by date/company/status, totals)
- `tests/ui/transport_sprint17_ui_smoke.cjs` — passed: вкладка «Биллинг», фильтр компании, итоги, CSV export
- `tests/transport/transport_sprint17_load_test.py` — passed: list p95 112.2 ms, date filter p95 127.5 ms, company filter p95 146.5 ms, paid filter p95 64.4 ms
- `tests/transport/sprint17_usability_checklist.md` — 28 юзабилити-проверок (вкладка, фильтры, таблица, бейджи, итоги, CSV)
**Training pack:** [`../../wiki-raw/tms2_training/sprint17_billing_registry_2026_05_28/index.html`](../../wiki-raw/tms2_training/sprint17_billing_registry_2026_05_28/index.html)
**Исправлено ранее:** баг правой панели — вкладка «Биллинг» корректно скрывает `dispatch-right-panel`

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
**Hardening:** 2026-05-28 — доведено до рабочего состояния по API/UI/load/training.
**Тесты:**
- `tests/transport/test_sprint18_functional.py` — `11 passed` (recalculate, set price, remove from order, 404, 422)
- `tests/ui/transport_sprint18_ui_smoke.cjs` — passed: карточка рейса, пересчёт цены, ручное сохранение цены
- `tests/transport/transport_sprint18_load_test.py` — passed: set-price p95 205.3 ms, recalculate p95 92.8 ms, billing list p95 74.7 ms
- `tests/transport/sprint18_usability_checklist.md` — 15 юзабилити-проверок
**Training pack:** [`../../wiki-raw/tms2_training/sprint18_price_management_2026_05_28/index.html`](../../wiki-raw/tms2_training/sprint18_price_management_2026_05_28/index.html)

---

### Sprint 39 — Badge активных фильтров + «× Сбросить»

**Инструмент:** 🟢 КК (код-код $20) — чисто фронтенд, derived state + reset function

**Цель:** диспетчер сразу видит, сколько фильтров активно, и может сбросить все одним кликом — без ручного обхода каждого поля.

| Задача | Кто | Файл |
|--------|-----|------|
| `activeFilterCount` computed — считает все отклонения от дефолтов | Frontend | `TransportDispatchPage.tsx` |
| `handleResetFilters()` — сбрасывает все 11 filter state-переменных | Frontend | `TransportDispatchPage.tsx` |
| `dispatch-fp-header-row`: строка «Фильтры» + badge + кнопка | Frontend | `TransportDispatchPage.tsx` |
| `.dispatch-fp-header-row`, `.dispatch-fp-badge`, `.dispatch-fp-reset-btn` | Frontend | `styles.css` |

**Статус:** ✅ Завершён
**Коммит:** `1a19f0d` · **Дата:** 2026-05-28
**Тесты:**
- `tests/transport/test_sprint39_functional.py` — 24 pytest-кейса (каждый фильтр по отдельности, all-active=11, reset=0, badge/btn visibility)
- `tests/transport/sprint39_usability_checklist.md` — 19 юзабилити-проверок
- `tests/transport/transport_sprint39_load_test.py` — 5 users, 60s, NFR /available-sts c разными фильтрами p95 ≤ 400ms

---

### Sprint 43 — Сортировка таблицы рейсов по колонкам

**Инструмент:** 🟢 КК (код-код $20) — чисто фронтенд, derived state + Array.sort

**Цель:** диспетчер кликает на заголовок колонки → таблица рейсов сортируется; повторный клик меняет направление. NULL-значения всегда в конце.

| Задача | Кто | Файл |
|--------|-----|------|
| `tasksSortField` / `tasksSortDir` state + `toggleTasksSort()` | Frontend | `TransportDispatchPage.tsx` |
| `sortedTasks` computed array (spread + sort) | Frontend | `TransportDispatchPage.tsx` |
| Заголовки `dispatch-sortable-th` с hover + стрелкой ▲/▼ | Frontend | `TransportDispatchPage.tsx` |
| `grid-cancelled` на отменённых рейсах в tasks-tab | Frontend | `TransportDispatchPage.tsx` |
| `.dispatch-sortable-th` | Frontend | `styles.css` |

**Статус:** ✅ Завершён
**Коммит:** `86a8908` · **Дата:** 2026-05-28
**Тесты:**
- `tests/transport/test_sprint43_functional.py` — 13 pytest-кейсов (asc/desc, null-last, stable, all fields)
- `tests/transport/sprint43_usability_checklist.md` — 16 юзабилити-проверок
- `tests/transport/transport_sprint43_load_test.py` — 7 users, 60s, NFR p95 ≤ 700ms

---

### Sprint 42 — Toast-уведомления об успешных операциях

**Инструмент:** 🟢 КК (код-код $20) — чисто фронтенд, state + setTimeout

**Цель:** после создания/закрытия/отмены рейса и назначения/снятия СТ диспетчер видит зелёный toast вместо тишины; он исчезает через 3 с или закрывается кликом.

| Задача | Кто | Файл |
|--------|-----|------|
| `toastMsg` state + `showToast()` helper с auto-dismiss 3 с | Frontend | `TransportDispatchPage.tsx` |
| `showToast` вызовы в: create, createFromCluster, close, cancel, assign, bulkUnassign, copy | Frontend | `TransportDispatchPage.tsx` |
| Toast JSX — фиксированная позиция bottom-right | Frontend | `TransportDispatchPage.tsx` |
| `.dispatch-toast` + `@keyframes toast-in` | Frontend | `styles.css` |

**Статус:** ✅ Завершён
**Коммит:** `abae320` · **Дата:** 2026-05-28
**Тесты:**
- `tests/transport/test_sprint42_functional.py` — 13 pytest-кейсов (все форматы сообщений)
- `tests/transport/sprint42_usability_checklist.md` — 15 юзабилити-проверок
- `tests/transport/transport_sprint42_load_test.py` — 5 users, 60s, NFR POST /tasks p95 ≤ 600ms

---

### Sprint 41 — Фильтр рейсов по статусу в таблице маршрутов

**Инструмент:** 🟢 КК (код-код $20) — чисто фронтенд, derived state

**Цель:** диспетчер быстро фильтрует рейсы по статусу кнопками «Все / Активен / Отгружен / Отменён» с счётчиками; фильтрация клиентская.

| Задача | Кто | Файл |
|--------|-----|------|
| `routeCondFilter` state + `filteredRouteTasks` computed | Frontend | `TransportDispatchPage.tsx` |
| `routeCondCounts` — подсчёт по каждому статусу | Frontend | `TransportDispatchPage.tsx` |
| Кнопки `.dispatch-cond-filter-btn` в тулбаре вкладки «Маршруты» | Frontend | `TransportDispatchPage.tsx` |
| `grid-cancelled` на отменённых рейсах | Frontend | `TransportDispatchPage.tsx` |
| `.dispatch-cond-filter`, `.dispatch-cond-filter-btn`, `.dispatch-cond-filter-cnt` | Frontend | `styles.css` |

**Статус:** ✅ Завершён
**Коммит:** `04302e3` · **Дата:** 2026-05-28
**Тесты:**
- `tests/transport/test_sprint41_functional.py` — 14 pytest-кейсов (all/active/closed/cancelled, counts, edge cases)
- `tests/transport/sprint41_usability_checklist.md` — 17 юзабилити-проверок
- `tests/transport/transport_sprint41_load_test.py` — 6 users, 60s, NFR p95 ≤ 700ms

---

### Sprint 40 — Сводка дня над таблицей рейсов

**Инструмент:** 🟢 КК (код-код $20) — чисто фронтенд, derived values

**Цель:** диспетчер видит быструю сводку «Рейсов · Паллет · Вес кг · Отгружено X/N» над таблицей рейсов без дополнительных API-запросов.

| Задача | Кто | Файл |
|--------|-----|------|
| `dayTotalTasks`, `dayTotalPallets`, `dayTotalWeight`, `dayClosedTasks` computed | Frontend | `TransportDispatchPage.tsx` |
| `.dispatch-day-summary` strip JSX (голубоватый фон, разделители «·») | Frontend | `TransportDispatchPage.tsx` |
| `.dispatch-day-summary`, `.dispatch-ds-*` CSS-классы | Frontend | `styles.css` |

**Статус:** ✅ Завершён
**Коммит:** `0fab5d7` · **Дата:** 2026-05-28
**Тесты:**
- `tests/transport/test_sprint40_functional.py` — 11 pytest-кейсов (empty, single, mixed, null weight/pallets, large dataset)
- `tests/transport/sprint40_usability_checklist.md` — 13 юзабилити-проверок
- `tests/transport/transport_sprint40_load_test.py` — 5 users, 60s, NFR p95 ≤ 800ms

---

### Sprint 38 — «Копировать рейс»

**Инструмент:** 🟢 КК (код-код $20) — фронтенд + вызов существующих эндпоинтов

**Цель:** диспетчер может скопировать рейс одной кнопкой — создаётся новый рейс с теми же реквизитами (машина, водитель, дата, тип ТС, время, докст.) но без СТ. Полезно для ежедневных повторяющихся маршрутов.

| Задача | Кто | Файл |
|--------|-----|------|
| `handleCopyTask()` — POST /tasks + PATCH если есть реквизиты, navigate to new task | Frontend | `TransportDispatchPage.tsx` |
| «📋 Копировать» button в `dispatch-trip-title-row` (tasks tab + routes tab) | Frontend | `TransportDispatchPage.tsx` |
| `.dispatch-copy-task-btn` | Frontend | `styles.css` |

**Статус:** ✅ Завершён
**Коммит:** `ad2a56f` · **Дата:** 2026-05-28
**Тесты:**
- `tests/transport/test_sprint38_functional.py` — 14 pytest-кейсов (inherit fields, no STs, no price, no pay_order, tab switch, multiple copies)
- `tests/transport/sprint38_usability_checklist.md` — 17 юзабилити-проверок
- `tests/transport/transport_sprint38_load_test.py` — 5 users, 60s, NFR POST/tasks p95 ≤ 500ms

---

### Sprint 37 — «Выделить всё» + авто-обновление данных

**Инструмент:** 🟢 КК (код-код $20) — чисто фронтенд, state + setInterval

**Цель:** две UX-улучшения:
1. Чекбокс «Выделить всё» в шапке таблицы доступных СТ (flat-режим) — один клик выделяет/снимает все видимые СТ.
2. Авто-обновление: каждые 60 секунд страница автоматически перезагружает данные (СТ, рейсы, кластеры), пока диалоги закрыты и нет активного редактирования.

| Задача | Кто | Файл |
|--------|-----|------|
| `autoRefresh` state + `lastRefreshAt` timestamp | Frontend | `TransportDispatchPage.tsx` |
| `useEffect` с `setInterval(60_000)`: reload STs/tasks/clusters, guard против loading/dialog/editMode | Frontend | `TransportDispatchPage.tsx` |
| «Авто» checkbox + время последнего обновления в ST toolbar | Frontend | `TransportDispatchPage.tsx` |
| Header `<th>` select-all checkbox (flat mode only): toggle all/none | Frontend | `TransportDispatchPage.tsx` |
| `.dispatch-autorefresh-toggle`, `.dispatch-last-refresh` | Frontend | `styles.css` |

**Статус:** ✅ Завершён
**Коммит:** `a287a02` · **Дата:** 2026-05-28
**Тесты:**
- `tests/transport/test_sprint37_functional.py` — 18 pytest-кейсов (select-all toggle, partial→all, auto-refresh guards, enable/disable)
- `tests/transport/sprint37_usability_checklist.md` — 20 юзабилити-проверок
- `tests/transport/transport_sprint37_load_test.py` — 10 users, 90s polling, NFR /available-sts p95 ≤ 400ms под concurrent auto-refresh

---

### Sprint 36 — Массовое снятие СТ с рейса

**Инструмент:** 🟢 КК (код-код $20) — чисто фронтенд, чекбоксы + bulk bar

**Цель:** диспетчер может снять несколько СТ с рейса одним кликом через мультиселект, не нажимая ✕ на каждой строке по отдельности.

| Задача | Кто | Файл |
|--------|-----|------|
| `selectedTripStNums: Set<string>` state + сброс при смене рейса | Frontend | `TransportDispatchPage.tsx` |
| `handleBulkUnassign()` — параллельные DELETE через `Promise.all` | Frontend | `TransportDispatchPage.tsx` |
| Чекбокс-колонка (width 22) в шапке таблицы состава рейса | Frontend | `TransportDispatchPage.tsx` |
| `TaskStTableRow`: props `checked?` + `onToggleCheck?` + ячейка с `<input type="checkbox">` | Frontend | `TransportDispatchPage.tsx` |
| Amber bulk bar сверху таблицы: «N СТ выбрано» + «Снять выбранные» + «Отмена» | Frontend | `TransportDispatchPage.tsx` |
| Guard: bar и чекбоксы скрыты для «Отгружен» и `PAY_ORDER_ID` | Frontend | `TransportDispatchPage.tsx` |
| `.dispatch-trip-bulk-bar`, `.dispatch-bulk-unassign-btn` | Frontend | `styles.css` |

**Статус:** ✅ Завершён
**Коммит:** `7aa8b16` · **Дата:** 2026-05-28
**Тесты:**
- `tests/transport/test_sprint36_functional.py` — 13 pytest-кейсов (toggle, guard conditions, bulk unassign, clear on task switch)
- `tests/transport/sprint36_usability_checklist.md` — 18 юзабилити-проверок
- `tests/transport/transport_sprint36_load_test.py` — 5 users, 60s, NFR single DELETE p95 ≤ 300ms, bulk burst p95 ≤ 800ms

---

### Sprint 35 — Оптимизация: server-side raion filter

**Инструмент:** 🟢 КК (код-код $20) — бэкенд, одно условие в SQL

**Цель:** `create_task_from_cluster` раньше делал 2 операции: fetch всех свободных СТ → Python-фильтрация по RAION. Теперь Oracle фильтрует в SQL одним запросом. NFR создания рейса из кластера снижен с 1500ms до 1200ms.

| Задача | Кто | Файл |
|--------|-----|------|
| Параметр `raion` в `list_available_sts()` | Backend | `transport_service.py` |
| `«(без района)» → RAION IS NULL`, иначе `RAION = :raion` | Backend | `transport_service.py` |
| `create_task_from_cluster` передаёт `raion=raion` (убрана Python-фильтрация) | Backend | `transport_service.py` |
| `raion` в `GET /available-sts` endpoint | Backend | `transport.py` |

**Статус:** ✅ Завершён
**Коммит:** `c60c420` · **Дата:** 2026-05-28
**Тесты:**
- `tests/transport/test_sprint35_functional.py` — 9 pytest-кейсов (SQL условия, без района IS NULL, с spецсимволами, integ)
- `tests/transport/sprint35_usability_checklist.md` — 14 проверок
- `tests/transport/transport_sprint35_load_test.py` — 5 users, 60s, NFR filtered p95 ≤ 200ms

---

### Sprint 34 — Bugfix: cancel_task освобождает СТ перед удалением

**Инструмент:** 🟢 КК (код-код $20) — бэкенд, одна функция

**Проблема:** `cancel_task` ставил `DELETED=1` без снятия СТ с рейса. После отмены СТ оставались с `TRANSTASK_ID` удалённого рейса и не появлялись в доступных для нового рейса.

**Исправление:** перед `UPDATE DELETED=1` — цикл `RRL_TT_ADD_PALL(TT_ID=0)` для каждого СТ из `get_task_sts()`.

| Задача | Кто | Файл |
|--------|-----|------|
| `cancel_task`: добавить цикл unassign перед DELETE | Backend | `transport_service.py` |

**Статус:** ✅ Завершён
**Коммит:** `73cd887` · **Дата:** 2026-05-28
**Тесты:**
- `tests/transport/test_sprint34_functional.py` — 6 pytest-кейсов (пустой рейс, N СТ, порядок операций, 409, большой рейс)
- `tests/transport/sprint34_usability_checklist.md` — 12 проверок
- `tests/transport/transport_sprint34_load_test.py` — 2 users, 30s, NFR cancel p95 ≤ 500ms

---

### Sprint 33 — Режим «Кратко» в таблице маршрутов

**Инструмент:** 🟢 КК (код-код $20) — условный рендер колонок, минимальный JS

**Цель:** §3.8.1 ТЗ — чекбокс «КРАТКО» в тулбаре таблицы маршрутов. Скрывает 6 второстепенных колонок (Объём, Тип, Цена, ТК, Логист, 💰), оставляя 9 эссенциальных.

| Задача | Кто | Файл |
|--------|-----|------|
| `routeBriefMode` state | Frontend | `TransportDispatchPage.tsx` |
| «Кратко» checkbox в тулбаре | Frontend | `TransportDispatchPage.tsx` |
| Условный рендер 6 колонок через `{!routeBriefMode && …}` | Frontend | `TransportDispatchPage.tsx` |
| `.routes-brief-toggle`, `.routes-brief.dispatch-grid td/th` | Frontend | `styles.css` |

**Статус:** ✅ Завершён
**Коммит:** `b5b12d1` · **Дата:** 2026-05-28
**Тесты:**
- `tests/transport/test_sprint33_functional.py` — 12 pytest-кейсов (видимость колонок в обоих режимах)
- `tests/transport/sprint33_usability_checklist.md` — 16 проверок
- `tests/transport/transport_sprint33_load_test.py` — 5 users, 60s, NFR GET /tasks p95 ≤ 300ms

---

### Sprint 32 — Phase 2 ✅: предупреждение о перегрузе

**Инструмент:** 🟢 КК (код-код $20) — чисто фронтенд, one-liner condition

**Цель:** замкнуть Phase 2 — «предупреждение при превышении MAX_PALLET_LOAD». Красный баннер появляется под load bar когда в рейсе больше паллет, чем допускает машина.

| Задача | Кто | Файл |
|--------|-----|------|
| Overload banner `{tripP > selectedVehicle.PALLETS && <div className="dispatch-overload-warn">…}` | Frontend | `TransportDispatchPage.tsx` |
| В обоих панелях: tasks tab + routes tab | Frontend | `TransportDispatchPage.tsx` |
| `.dispatch-overload-warn` | Frontend | `styles.css` |

**Статус:** ✅ Завершён
**Коммит:** `286c0c7` · **Дата:** 2026-05-28
**Hardening:** 2026-05-28 — добавлен UI smoke и обучающий HTML pack для overload banner; Locust-only load script заменён на Windows-safe runner.
**Тесты:**
- `tests/transport/test_sprint32_functional.py` — 11 pytest-кейсов (границы, формат сообщения, интеграция с LoadBar) → `11 passed`
- `tests/ui/transport_sprint32_ui_smoke.cjs` — UI smoke: перегруженный рейс показывает 100% load bar и красный warning
- `tests/ui/transport_sprint32_training_capture.cjs` → `wiki-raw/tms2_training/sprint32_overload_warning_2026_05_28/index.html`
- `tests/transport/sprint32_usability_checklist.md` — 17 проверок + Phase 2 чеклист
- `tests/transport/transport_sprint32_load_test.py` — Windows-safe load gate; p95 task 186.3 ms, task STs 160.6 ms, vehicles 75.7 ms

**Phase 2 «Полуавто» теперь полностью закрыта.**

---

### Sprint 31 — ClusterSidebar — левая панель карточек районов

**Инструмент:** 🟢 КК (код-код $20) — чисто фронтенд, повторяет логику ClusterGroup

**Цель:** дать диспетчеру быстрый обзор всех районов в виде карточек в левой панели вместо прокрутки таблицы. Кликабельные карточки синхронизированы с раскрытыми кластерами в таблице.

| Задача | Кто | Файл |
|--------|-----|------|
| `ClusterSidebar` компонент — список карточек, итоговая строка | Frontend | `TransportDispatchPage.tsx` |
| Рендер в `dispatch-workspace` перед `dispatch-center` (только `viewMode===clusters && activeTab===tasks`) | Frontend | `TransportDispatchPage.tsx` |
| `.cluster-sidebar`, `.cluster-card`, `.cluster-card-active`, `.cluster-card-create-btn` | Frontend | `styles.css` |

**Статус:** ✅ Завершён
**Коммит:** `86d3a71` · **Дата:** 2026-05-28
**Hardening:** 2026-05-28 — functional tests переведены на реальный import path; добавлен UI smoke для левой панели районов и обучающий HTML pack. Locust-only load script заменён на Windows-safe runner; load gate использует `shipment_date`, а не broad `date_to`.
**Тесты:**
- `tests/transport/test_sprint31_functional.py` — 6 кейсов (агрегация, сортировка, поля кластера) → `6 passed`
- `tests/ui/transport_sprint31_ui_smoke.cjs` — UI smoke: режим «По районам», sidebar totals, active card, dialog «Рейс»
- `tests/ui/transport_sprint31_training_capture.cjs` → `wiki-raw/tms2_training/sprint31_cluster_sidebar_2026_05_28/index.html`
- `tests/transport/sprint31_usability_checklist.md` — 20 проверок
- `tests/transport/transport_sprint31_load_test.py` — Windows-safe load gate; p95 clusters 200.5 ms, tasks 247.8 ms

---

### Sprint 30 — Live load bar

**Инструмент:** 🟢 КК (код-код $20) — чисто фронтенд, логика простая

**Цель:** показать диспетчеру степень заполнения машины прямо в панели рейса, не выходя из UI. Цветовая индикация: зелёный (<85%), жёлтый (85–99%), красный (≥100%).

| Задача | Кто | Файл |
|--------|-----|------|
| `LoadBar` компонент — progress track с цветом | Frontend | `TransportDispatchPage.tsx` |
| Рендер в панели рейса: `selectedVehicle.PALLETS && tripP > 0` | Frontend | `TransportDispatchPage.tsx` |
| `.load-bar-row`, `.load-bar-track`, `.load-bar-fill`, `.load-bar-text` | Frontend | `styles.css` |

**Статус:** ✅ Завершён
**Коммит:** `9436717` · **Дата:** 2026-05-28
**Hardening:** 2026-05-28 — functional tests переведены на реальный import path; UI smoke покрывает отображение LoadBar 9/10 пал (90%).
**Тесты:**
- `tests/transport/test_sprint30_functional.py` — 11 кейсов (пороги, clamping, regression clusters)
- `tests/ui/transport_sprint30_ui_smoke.cjs` — UI smoke: выбрать рейс, увидеть live load bar
- `tests/ui/transport_sprint30_training_capture.cjs` → `wiki-raw/tms2_training/sprint30_load_bar_2026_05_28/index.html`
- `tests/transport/sprint30_usability_checklist.md` — 17 проверок
- `tests/transport/transport_sprint30_load_test.py` — Windows-safe load gate; p95: task detail 215.3 ms, task STs 149.6 ms, clusters 37.1 ms

---

### Sprint 29 — Phase 2 полуавто: создать рейс из кластера (⚡ Рейс)

**Инструмент:** 🟢 КК (код-код $20)

**Цель:** одна кнопка «⚡ Рейс» в заголовке каждого кластера (режим «Кластеры») открывает мини-диалог и создаёт рейс из всех свободных СТ района одним запросом. Закрывает Phase 2 полуавто (roadmap §2).

**ТЗ:** Phase 2 Полуавто — roadmap [transport_roadmap.md](transport_roadmap.md)

| Задача | Кто | Файл |
|--------|-----|------|
| `ClusterCreateTaskRequest` — Pydantic-схема | Backend | `schemas.py` |
| `create_task_from_cluster(raion, req, user_id)` — фильтрует СТ по RAION, создаёт рейс, назначает | Backend | `transport_service.py` |
| `POST /clusters/{raion}/create-task` | Backend | `transport.py` |
| `clusterCreateRaion`, `clusterCreateLoading` — state | Frontend | `TransportDispatchPage.tsx` |
| `handleCreateFromCluster(params)` — вызов API, reload, select | Frontend | `TransportDispatchPage.tsx` |
| `ClusterQuickCreateDialog` — диалог с summary, vehicle avail check | Frontend | `TransportDispatchPage.tsx` |
| `onCreateTask?` prop + «⚡ Рейс» button в `ClusterGroup` header | Frontend | `TransportDispatchPage.tsx` |
| `.cluster-create-task-btn`, `.cluster-dialog-summary`, `.cluster-dialog-date` | Frontend | `styles.css` |

**Статус:** ✅ Завершён
**Коммит:** `2f97815` · **Дата:** 2026-05-28
**Hardening:** 2026-05-28 — тесты переведены на реальный import path; проверяется server-side `raion` filter, clusters добавлен в lightweight audit; UI smoke покрывает диалог создания рейса из района.
**Тесты:**
- `tests/transport/test_sprint29_functional.py` — 8 pytest-кейсов (404 когда нет СТ, создание, update_task при vehicle, фильтрация, null RAION, schema defaults)
- `tests/ui/transport_sprint29_ui_smoke.cjs` — UI smoke: режим «По районам» → «Рейс» → создание и выбор нового рейса
- `tests/ui/transport_sprint29_training_capture.cjs` → `wiki-raw/tms2_training/sprint29_cluster_create_task_2026_05_28/index.html`
- `tests/transport/sprint29_usability_checklist.md` — 20 юзабилити-проверок
- `tests/transport/transport_sprint29_load_test.py` — Windows-safe load gate; p95: clusters 41.3 ms, safe empty create 110.7 ms

---

### Sprint 28 — Диспетчер: Excel-экспорт списка рейсов

**Инструмент:** 🟢 КК (код-код $20) — аналогичный паттерн Sprints 26-27, другой источник данных

**Цель:** закрыть ТЗ §3 — кнопка «В Excel» во вкладке «Маршруты». Скачивает XLSX со всеми рейсами текущего фильтра (дата, авто, компания, «без оплат»).

**ТЗ:** §3 «В Excel» (кнопка в тулбаре таблицы маршрутов)

| Задача | Кто | Файл |
|--------|-----|------|
| `export_tasks_xlsx(...)` — XLSX-список рейсов, те же фильтры что `list_tasks` | Backend | `transport_service.py` |
| `GET /tasks/export.xlsx` — размещён ДО `/{task_id}` | Backend | `transport.py` |
| `handleRoutesXlsx` + кнопка «⬇ Excel» в тулбаре вкладки «Маршруты» | Frontend | `TransportDispatchPage.tsx` |
| `.routes-xlsx-btn` | Frontend | `styles.css` |

**Статус:** ✅ Завершён
**Коммит:** `284c754` · **Дата:** 2026-05-28
**Hardening:** 2026-05-28 — export списка рейсов больше не падает без `openpyxl`, использует stdlib XLSX fallback; UI download покрыт smoke.
**Тесты:**
- `tests/transport/test_sprint28_functional.py` — `9 passed, 4 skipped` (MIME, magic, route conflict, filters; content checks skipped без openpyxl на test runner)
- `tests/ui/transport_sprint28_ui_smoke.cjs` — UI smoke: скачать Excel списка рейсов
- `tests/ui/transport_sprint28_training_capture.cjs` → `wiki-raw/tms2_training/sprint28_tasks_xlsx_2026_05_28/index.html`
- `tests/transport/sprint28_usability_checklist.md` — 17 юзабилити-проверок
- `tests/transport/transport_sprint28_load_test.py` — Windows-safe load gate; p95: tasks 153.2 ms, dated tasks export 308.6 ms

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
**Hardening:** 2026-05-28 — registry export больше не падает без `openpyxl`, использует stdlib XLSX fallback; UI download покрыт smoke.
**Тесты:**
- `tests/transport/test_sprint27_functional.py` — `8 passed, 5 skipped` (MIME, magic bytes, route conflict, filters; content checks skipped без openpyxl на test runner)
- `tests/ui/transport_sprint27_ui_smoke.cjs` — UI smoke: скачать Excel реестра
- `tests/ui/transport_sprint27_training_capture.cjs` → `wiki-raw/tms2_training/sprint27_billing_registry_xlsx_2026_05_28/index.html`
- `tests/transport/sprint27_usability_checklist.md` — 19 юзабилити-проверок
- `tests/transport/transport_sprint27_load_test.py` — Windows-safe load gate; p95: orders 137.7 ms, registry export 139.1 ms, order export 95.0 ms

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
**Hardening:** 2026-05-28 — export endpoint больше не падает без `openpyxl`: проверка счёта отдаёт 404 до генерации, XLSX fallback строится на стандартном `zipfile`; UI download покрыт smoke.
**Тесты:**
- `tests/transport/test_sprint26_functional.py` — `7 passed, 4 skipped` (content checks skipped без openpyxl на test runner; endpoint XLSX/ZIP/MIME проверен)
- `tests/ui/transport_sprint26_ui_smoke.cjs` — UI smoke: открыть детали счёта и скачать Excel
- `tests/ui/transport_sprint26_training_capture.cjs` → `wiki-raw/tms2_training/sprint26_billing_order_xlsx_2026_05_28/index.html`
- `tests/transport/sprint26_usability_checklist.md` — 18 юзабилити-проверок
- `tests/transport/transport_sprint26_load_test.py` — Windows-safe load gate; p95: orders 138.2 ms, order tasks 57.9 ms, export 75.5 ms

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
**Hardening:** 2026-05-28 — backend теперь запрещает отвязку от оплаченного счёта; UI smoke покрывает снятие из карточки рейса и из панели деталей счёта.
**Тесты:**
- `tests/transport/test_sprint25_functional.py` — 10 pytest-кейсов; `7 passed, 3 skipped` на dev seed без задач в закрытом/оплаченном счёте
- `tests/ui/transport_sprint25_ui_smoke.cjs` — UI smoke: отвязка из карточки рейса и из деталей счёта
- `tests/ui/transport_sprint25_training_capture.cjs` → `wiki-raw/tms2_training/sprint25_detach_billing_2026_05_28/index.html`
- `tests/transport/sprint25_usability_checklist.md` — 18 юзабилити-проверок
- `tests/transport/transport_sprint25_load_test.py` — Windows-safe load gate; p95: orders 278.9 ms, order tasks 105.9 ms, companies 41.4 ms

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
**Hardening:** 2026-05-28 — добавлен UI smoke на drag-and-drop СТ между рейсами, индикатор ручной правки, сброс и отсутствие backend apply до явной команды; planner metrics переведен в lightweight audit.
**Тесты:**
- `tests/transport/test_sprint24_functional.py` — 9 pytest-кейсов (структура stops, pallet calc, utilization)
- `tests/ui/transport_sprint24_ui_smoke.cjs` — UI smoke: drag ST между рейсами, пересчёт количества адресов, reset, без apply-вызова
- `tests/ui/transport_sprint24_training_capture.cjs` → `wiki-raw/tms2_training/sprint24_vrp_drag_drop_2026_05_28/index.html`
- `tests/transport/sprint24_usability_checklist.md` — 19 юзабилити-проверок
- `tests/transport/transport_sprint24_load_test.py` — Windows-safe load gate; p95: metrics 37.0 ms, history 36.9 ms, routing status 31.9 ms

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
**Hardening:** 2026-05-28 — `GET /billing/orders/{id}/tasks` теперь возвращает 404 для неизвестного счёта; UI проверяет открытие панели, итог и CSV.
**Тесты:**
- `tests/transport/test_sprint23_functional.py` — 9 pytest-кейсов (tasks endpoint, поля, согласованность с заголовком)
- `tests/ui/transport_sprint23_ui_smoke.cjs` — UI smoke: открыть счёт, увидеть рейсы/итог, скачать CSV
- `tests/ui/transport_sprint23_training_capture.cjs` → `wiki-raw/tms2_training/sprint23_billing_order_detail_2026_05_28/index.html`
- `tests/transport/sprint23_usability_checklist.md` — 17 юзабилити-проверок
- `tests/transport/transport_sprint23_load_test.py` — Windows-safe load gate; p95: orders 227.5 ms, order tasks 123.6 ms, companies 38.8 ms

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
**Hardening:** 2026-05-28 — справочник компаний переведен в lightweight audit + reference-cache; UI проверяет `NUM_PLAT` в реестре/деталях и datalist компаний.
**Тесты:**
- `tests/transport/test_sprint22_functional.py` — 10 pytest-кейсов (companies endpoint, num_plat поле, регрессия схемы)
- `tests/ui/transport_sprint22_ui_smoke.cjs` — UI smoke: `NUM_PLAT` в реестре/деталях, datalist компаний в диалоге счёта
- `tests/ui/transport_sprint22_training_capture.cjs` → `wiki-raw/tms2_training/sprint22_company_directory_num_plat_2026_05_28/index.html`
- `tests/transport/sprint22_usability_checklist.md` — 13 юзабилити-проверок
- `tests/transport/transport_sprint22_load_test.py` — Windows-safe load gate; p95: companies 189.5 ms, orders 164.9 ms, filtered orders 86.5 ms

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
**Hardening:** 2026-05-28 — проверен полный контур RBAC: backend permissions, UI error visibility, load gate, training pack.
**Тесты:**
- `tests/transport/test_sprint21_functional.py` — 9 pytest-кейсов (константы, доступность эндпоинтов)
- `tests/ui/transport_sprint21_ui_smoke.cjs` — UI smoke: 403 от price/recalculate показывается пользователю и не считается успехом
- `tests/ui/transport_sprint21_training_capture.cjs` → `wiki-raw/tms2_training/sprint21_billing_rbac_2026_05_28/index.html`
- `tests/transport/sprint21_usability_checklist.md` — 13 юзабилити-проверок
- `tests/transport/transport_sprint21_load_test.py` — Windows-safe load gate; p95: list 76.9 ms, filtered list 60.7 ms, create 159.8 ms, recalc 185.6 ms, manual price 167.9 ms

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
**Hardening:** 2026-05-28 — доведено до рабочего состояния по API/UI/load/training.
**Тесты:**
- `tests/transport/test_sprint20_functional.py` — `7 passed` (cancel/assign/unassign → 409; note/price → 200)
- `tests/ui/transport_sprint20_ui_smoke.cjs` — passed: billed badge, disabled cancel, billing card
- `tests/transport/transport_sprint20_load_test.py` — passed: billed cancel p95 192.3 ms, billed assign p95 156.3 ms, allowed price p95 174.3 ms
- `tests/transport/sprint20_usability_checklist.md` — 12 юзабилити-проверок
**Training pack:** [`../../wiki-raw/tms2_training/sprint20_billed_task_protection_2026_05_28/index.html`](../../wiki-raw/tms2_training/sprint20_billed_task_protection_2026_05_28/index.html)

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
**Hardening:** 2026-05-28 — доведено до рабочего состояния по API/UI/load/training.
**Тесты:**
- `tests/transport/test_sprint19_functional.py` — `9 passed` (filter open orders, add to existing, 404)
- `tests/ui/transport_sprint19_ui_smoke.cjs` — passed: выбор открытого счета ТК в диалоге и добавление рейса
- `tests/transport/transport_sprint19_load_test.py` — passed: open-order filter p95 121.1 ms, order tasks p95 48.2 ms, add task p95 89.0 ms
- `tests/transport/sprint19_usability_checklist.md` — 16 юзабилити-проверок
**Training pack:** [`../../wiki-raw/tms2_training/sprint19_link_existing_billing_2026_05_28/index.html`](../../wiki-raw/tms2_training/sprint19_link_existing_billing_2026_05_28/index.html)

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
