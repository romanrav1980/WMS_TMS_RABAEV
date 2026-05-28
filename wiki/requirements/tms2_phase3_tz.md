# ТМС-2 — Техническое Задание: Фаза 3 (Спринты 96–119)

**Проект:** ТМС-2  
**Статус:** В разработке  
**Дата:** 2026-05-29  
**Предыдущий этап:** Спринты 1–95 завершены (dispatch, MAP/VRP, ARM/Ганта, биллинг, UX-надстройки)

Связанные документы:
- [transport_dispatch_tz.md](transport_dispatch_tz.md)
- [transport_billing_tz.md](transport_billing_tz.md)
- [transport_execution_plan.md](../../roadmap/transport_execution_plan.md)

---

## 16. WebSocket `/ws/dispatch` — Реальное время (Sprint 96)

### 16.1 Назначение

Синхронизация состояния между несколькими диспетчерами в реальном времени. Когда диспетчер А создаёт рейс, диспетчер Б видит его немедленно без перезагрузки страницы.

### 16.2 Протокол событий

Сервер рассылает JSON-сообщения всем подключённым клиентам после успешного завершения мутации:

| Тип события | Когда | Payload |
|-------------|-------|---------|
| `task_created` | После `POST /tasks` | `{task_id, shipment_date}` |
| `task_updated` | После `PATCH /tasks/{id}` | `{task_id}` |
| `task_closed` | После `POST /tasks/{id}/close` | `{task_id}` |
| `task_cancelled` | После `POST /tasks/{id}/cancel` | `{task_id}` |
| `sts_assigned` | После `POST /tasks/{id}/sts` | `{task_id, st_numbers}` |
| `st_unassigned` | После `DELETE /tasks/{id}/sts/{st}` | `{task_id, st_number}` |
| `sts_bulk_unassigned` | После массового снятия СТ | `{task_id, count}` |
| `ping` | Каждые 30 сек от сервера | `{}` |

Формат сообщения:
```json
{"type": "task_created", "payload": {"task_id": 4501, "shipment_date": "2026-05-30"}}
```

### 16.3 Эндпоинт

```
WS /api/admin/transport/ws/dispatch
```

Аутентификация: query-параметры `?u=username&p=password`. Если `admin_auth_enabled=False` — аутентификация не требуется (debug-режим).

### 16.4 Поведение клиента

| Событие | Действие |
|---------|---------|
| `task_created` / `task_updated` / `task_closed` / `task_cancelled` | Рефетч `GET /tasks` |
| `sts_assigned` / `st_unassigned` / `sts_bulk_unassigned` | Рефетч `GET /available-sts` + если выбранный рейс затронут — рефетч `GET /tasks/{id}/sts` |
| `ping` | Не обрабатывается (keep-alive) |
| Разрыв соединения | Reconnect: 1s → 2s → 4s → 8s → 16s → max 30s |
| Успешное переподключение | Сброс задержки до 1s, немедленный рефетч tasks + available-sts |

### 16.5 UI индикатор

Строка в хедере страницы: `● WS` (зелёный = подключён, жёлтый = переподключение, красный = ошибка).

### 16.6 Oracle-зависимости

Новых Oracle-объектов не требуется.

---

## 17. Справочники флота: Транспортные средства (Sprint 97)

### 17.1 Назначение

CRUD-управление списком транспортных средств через веб-интерфейс, без прямого доступа к Oracle.

### 17.2 Oracle-объекты (миграция 055)

```sql
-- Последовательность для новых ID
CREATE SEQUENCE RABAEV.SEQ_TR_VEHICLE START WITH 10000 INCREMENT BY 1 NOCACHE;

-- Функция создания ТС
CREATE OR REPLACE FUNCTION RABAEV.RRL_TR_VEHICLE_ADD(
    p_num_plat        VARCHAR2,
    p_transtype_id    NUMBER,
    p_max_weight_kg   NUMBER DEFAULT 10000,
    p_max_pallets     NUMBER DEFAULT 20,
    p_sobstvennyy     NUMBER DEFAULT 1,
    p_doverennost_ot  VARCHAR2 DEFAULT NULL
) RETURN NUMBER;

-- Процедура обновления ТС
CREATE OR REPLACE PROCEDURE RABAEV.RRL_TR_VEHICLE_UPDATE(
    p_id              NUMBER,
    p_num_plat        VARCHAR2,
    p_transtype_id    NUMBER,
    p_max_weight_kg   NUMBER,
    p_max_pallets     NUMBER,
    p_sobstvennyy     NUMBER,
    p_doverennost_ot  VARCHAR2
);

-- Мягкое удаление
CREATE OR REPLACE PROCEDURE RABAEV.RRL_TR_VEHICLE_DEL(p_id NUMBER);
```

### 17.3 API эндпоинты

| Метод | URL | Описание |
|-------|-----|---------|
| `GET` | `/api/admin/transport/vehicles` | Список ТС (с deleted=false) |
| `POST` | `/api/admin/transport/vehicles` | Создать ТС |
| `PATCH` | `/api/admin/transport/vehicles/{id}` | Обновить ТС |
| `DELETE` | `/api/admin/transport/vehicles/{id}` | Удалить ТС (soft delete) |

Права: `TRANSPORT_FLEET_EDIT` (новое) для POST/PATCH/DELETE; `TRANSPORT_DISPATCH_VIEW` для GET.

### 17.4 Схема данных

| Поле | Тип | Описание |
|------|-----|---------|
| `id` | int | PK |
| `num_plat` | str | Гос. номер |
| `transtype_id` | int | FK на `RRL_TRANSPORT_TYPE` |
| `transtype_name` | str | Название типа (join) |
| `max_weight_kg` | int | Грузоподъёмность, кг |
| `max_pallets` | int | Вместимость, паллет |
| `sobstvennyy` | bool | Собственный (true) / Наёмный (false) |
| `doverennost_ot` | str? | Транспортная компания |

### 17.5 UI — Страница `FleetManagementPage`

Новая страница `/fleet` в сайдбаре под «Транспорт». Две вкладки: **Транспортные средства** (Sprint 97) и **Водители** (Sprint 98).

Вкладка «ТС»:
- Таблица с колонками: Гос. номер, Тип, Грузоподъёмность, Паллет, Компания, Собственный
- Кнопки «+ Добавить», «✏ Редактировать», «✕ Удалить» (с подтверждением)
- Диалог добавления/редактирования: форма с полями из §17.4
- Dropdown типа ТС из `GET /types`

### 17.6 Права

Новое право `transport_fleet_edit` — добавить в константы `auth.py`.

---

## 18. Справочники флота: Водители (Sprint 98)

### 18.1 Назначение

CRUD-управление списком водителей через веб-интерфейс.

### 18.2 Oracle-объекты (миграция 056)

```sql
CREATE SEQUENCE RABAEV.SEQ_TR_VODITEL START WITH 10000 INCREMENT BY 1 NOCACHE;

CREATE OR REPLACE FUNCTION RABAEV.RRL_TR_VODITEL_ADD(
    p_name       VARCHAR2,
    p_phone      VARCHAR2 DEFAULT NULL,
    p_license    VARCHAR2 DEFAULT NULL,
    p_company    VARCHAR2 DEFAULT NULL
) RETURN NUMBER;

CREATE OR REPLACE PROCEDURE RABAEV.RRL_TR_VODITEL_UPDATE(
    p_id         NUMBER,
    p_name       VARCHAR2,
    p_phone      VARCHAR2,
    p_license    VARCHAR2,
    p_company    VARCHAR2
);

CREATE OR REPLACE PROCEDURE RABAEV.RRL_TR_VODITEL_DEL(p_id NUMBER);
```

### 18.3 API эндпоинты

| Метод | URL | Описание |
|-------|-----|---------|
| `GET` | `/api/admin/transport/drivers` | Список водителей |
| `POST` | `/api/admin/transport/drivers` | Создать водителя |
| `PATCH` | `/api/admin/transport/drivers/{id}` | Обновить водителя |
| `DELETE` | `/api/admin/transport/drivers/{id}` | Удалить водителя (soft delete) |

### 18.4 Схема данных `RRL_TR_VODITEL`

| Поле | Тип | Описание |
|------|-----|---------|
| `id` | int | PK |
| `name` | str | ФИО водителя |
| `phone` | str? | Телефон |
| `license_number` | str? | Номер водительского удостоверения |
| `company` | str? | ТК (если наёмный) |

### 18.5 UI — вкладка «Водители» в `FleetManagementPage`

- Таблица: ФИО, Телефон, Удостоверение, Компания
- Диалог добавления/редактирования

---

## 19. Управление пользователями и правами (Спринты 99–100)

### 19.1 Назначение

Администратор назначает права доступа группам пользователей через веб-интерфейс без прямого доступа к Oracle.

### 19.2 Модель данных (существующая)

**Таблица `RUSERS`:**

| Колонка | Описание |
|---------|---------|
| `ID` | Логин |
| `NAME` | Отображаемое имя |
| `USER_GROUP` | Группа прав |
| `PASS` | Пароль (plaintext в legacy Oracle) |
| `PRAVO_ADMIN_LOGIN` | 1 = может войти в admin |
| `DELETED` | Мягкое удаление |

**Таблица `RIGHTS`:**

| Колонка | Описание |
|---------|---------|
| `USER_GROUP` | Группа |
| `RIGHT1` | Код права |

### 19.3 Sprint 99 — Просмотр пользователей и прав

**API:**
```
GET /api/admin/users          — список пользователей (без паролей)
GET /api/admin/users/groups   — список групп с правами
GET /api/admin/users/rights   — полный справочник прав
```

**UI — `UserManagementPage`** (`/admin/users`):
- Список пользователей: логин, имя, группа, статус (активен/удалён)
- Список групп с раскрываемым перечнем прав
- Кнопка «Скопировать группу» — создать группу с теми же правами

**Права:** `RIGHTS_ADMIN_VIEW_PERMISSION` (уже есть в auth.py).

### 19.4 Sprint 100 — Редактирование прав RBAC

**API:**
```
POST   /api/admin/users/groups          — создать группу
POST   /api/admin/users/groups/{group}/rights        — добавить право к группе
DELETE /api/admin/users/groups/{group}/rights/{right} — удалить право из группы
POST   /api/admin/users                — создать пользователя
PATCH  /api/admin/users/{login}        — изменить группу / PRAVO_ADMIN_LOGIN
DELETE /api/admin/users/{login}        — мягкое удаление (DELETED=1)
PATCH  /api/admin/users/{login}/password — сменить пароль
```

**Oracle-объекты (миграция 057):**
```sql
-- Изменение группы пользователя (UPDATE RUSERS SET USER_GROUP)
CREATE OR REPLACE PROCEDURE RABAEV.RRL_USER_SET_GROUP(p_login VARCHAR2, p_group VARCHAR2);
-- Добавить право
CREATE OR REPLACE PROCEDURE RABAEV.RRL_RIGHT_ADD(p_group VARCHAR2, p_right VARCHAR2);
-- Удалить право
CREATE OR REPLACE PROCEDURE RABAEV.RRL_RIGHT_DEL(p_group VARCHAR2, p_right VARCHAR2);
-- Создать пользователя
CREATE OR REPLACE FUNCTION RABAEV.RRL_USER_ADD(p_login VARCHAR2, p_name VARCHAR2, p_pass VARCHAR2, p_group VARCHAR2) RETURN NUMBER;
-- Удалить пользователя
CREATE OR REPLACE PROCEDURE RABAEV.RRL_USER_DEL(p_login VARCHAR2);
-- Сменить пароль
CREATE OR REPLACE PROCEDURE RABAEV.RRL_USER_SET_PASS(p_login VARCHAR2, p_new_pass VARCHAR2);
```

**UI — `UserManagementPage` вкладка «Права»:**
- Выбор группы → список прав с чекбоксами
- Создать группу (модальный диалог)
- Создать/редактировать/удалить пользователя

**Права:** `RIGHTS_ADMIN_EDIT_PERMISSION` (уже есть в auth.py).

---

## 20. SSE VRP: отмена и таймаут (Sprint 101)

### 20.1 Назначение

Диспетчер может отменить запущенный VRP-оптимизатор кнопкой «Отмена», не дожидаясь 60-секундного таймаута.

### 20.2 Изменения в `/planner/solve`

```
POST /api/admin/transport/planner/solve → возвращает {job_id, stream_url}
DELETE /api/admin/transport/planner/solve/{job_id} — отменить задачу
GET /api/admin/transport/planner/solve/{job_id}/stream — SSE-стрим прогресса
```

Каждое SSE событие:
```
data: {"type": "progress", "step": "clustering", "pct": 10}
data: {"type": "progress", "step": "solving",    "pct": 45}
data: {"type": "done",     "plan_id": 123,        "score": 84.5}
data: {"type": "error",    "detail": "timeout_60s"}
data: {"type": "cancelled"}
```

Таймаут: 60 сек. По истечении — событие `error/timeout_60s`, задача завершается.

### 20.3 Backend

- Хранить активные задачи: `{job_id → asyncio.Task}` в словаре в памяти
- `DELETE /solve/{job_id}` — вызывает `task.cancel()`, отправляет `{"type":"cancelled"}` в SSE
- `job_id` генерируется при старте: `uuid4()`

### 20.4 Frontend

- Кнопка «Отмена» рядом со спиннером во время solve
- При нажатии: `DELETE /planner/solve/{job_id}`, spinner скрывается, toast «Оптимизация отменена»

---

## 21. Виртуализация таблицы СТ (Sprint 102)

### 21.1 Текущее состояние

Sprint 60 реализовал пагинацию 100 строк/страницу. При 2000+ СТ это требует листать страницы.

### 21.2 Требование (§12.2, §14.4 TZ)

Заменить пагинацию на виртуализацию через `@tanstack/react-virtual`. Все 2000 строк загружены в память, DOM рендерит только ~25 видимых строк + overscan 10.

```
npm install @tanstack/react-virtual
```

Настройки:
```tsx
const rowVirtualizer = useVirtualizer({
  count: filteredSts.length,
  getScrollElement: () => tableContainerRef.current,
  estimateSize: () => 36,
  overscan: 10,
});
```

Таблица: `<tbody>` с отступами `paddingTop/paddingBottom` для имитации скролла.

NFR: 2000 строк → рендер ≤ 300 мс (§12.2).

---

## 22. Мобильный интерфейс водителя (Спринты 103–105)

### 22.1 Назначение

Водитель видит свои рейсы на день, отмечает факт выполнения операций через мобильный браузер. Работает без установки приложения (PWA).

### 22.2 Sprint 103 — Страница «Мои рейсы»

**Новый роут** `/driver` — отдельная страница, не требует прав диспетчера.

**Аутентификация водителя:** по `driver_id` — передаётся как query-параметр в ссылке (`/driver?id=9201`) или через QR-код на путевом листе.

**API:**
```
GET /api/driver/trips?driver_id=&date=   — рейсы водителя на дату
GET /api/driver/trips/{task_id}/ops       — операции рейса
```

**UI:**
- Карточка рейса: номер рейса, дата, список СТ с адресами
- Список операций с плановым временем и статусом
- Адаптивная верстка (mobile-first, шрифт 16px+)

### 22.3 Sprint 104 — Отметка факта операций

```
POST /api/driver/ops/{op_id}/start  — начать операцию (fact_start = now)
POST /api/driver/ops/{op_id}/done   — завершить операцию (fact_end = now)
```

UI: кнопки «Начать» / «Готово» на каждой операции. Автоматически записывает timestamp.

### 22.4 Sprint 105 — Офлайн-режим (PWA)

- `manifest.json` + `service-worker.js` — кэширование страницы водителя
- При потере сети: операции сохраняются в `IndexedDB`
- При восстановлении: синхронизация с сервером через `Background Sync API`

---

## 23. Уведомления (Спринты 106–107)

### 23.1 Sprint 106 — Browser Push (Web Push API)

Диспетчер подписывается на уведомления через браузер. Сервер отправляет push-уведомления через VAPID.

**Триггеры:**
| Событие | Уведомление |
|---------|------------|
| VRP-план готов | «Авто-план на {дату} готов: {N} рейсов, утилизация {X}%» |
| Рейс собран на 100% | «Рейс #{id}: все СТ собраны, готов к закрытию» |
| Нарушение норм отдыха | «Водитель {ФИО}: превышение нормы вождения» |

**Backend:**
```
POST /api/admin/notifications/subscribe   — сохранить push-подписку
DELETE /api/admin/notifications/subscribe — отписаться
```

**Хранение:** таблица `RRL_PUSH_SUBSCRIPTIONS (USER_ID, ENDPOINT, AUTH, P256DH, CREATED_AT)` — миграция 058.

**Библиотека:** `pip install pywebpush`

### 23.2 Sprint 107 — Email-уведомления

**Триггеры (расширение §23.1):** + суточный отчёт в 18:00, + счёт к оплате создан.

**Конфигурация:** `.env` параметры `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASS`, `SMTP_FROM`.

**API:**
```
GET  /api/admin/notifications/settings      — настройки уведомлений пользователя
POST /api/admin/notifications/settings      — сохранить
POST /api/admin/notifications/test-email    — отправить тестовое письмо
```

**Хранение:** `RRL_NOTIFICATION_SETTINGS (USER_ID, EMAIL, EVENTS_JSON, ENABLED)` — миграция 059.

---

## 24. KPI Дашборд для руководства (Спринты 108–109)

### 24.1 Sprint 108 — Операционные KPI

Новая страница `/transport/kpi`. Только read-only.

**Метрики и виджеты:**
| Виджет | Описание |
|--------|---------|
| Утилизация парка (линия) | % загрузки за последние 30 дней. Источник: `RRL_PLANNER_PLANS` + `RRL_TRANSPORT_TASK` |
| Рейсов за день (бар) | Сравнение план/факт по дням |
| Среднее паллет на рейс | Тренд по неделям |
| % своевременных доставок | Из plan-fact: `delta_min ≤ 30` |
| Топ-10 регионов по объёму | Паллет за месяц по REGION |

**API:**
```
GET /api/admin/transport/kpi/fleet?date_from=&date_to=    — утилизация по дням
GET /api/admin/transport/kpi/summary?date_from=&date_to=  — сводка
GET /api/admin/transport/kpi/regions?date=                — топ регионов
```

**Графики:** `npm install recharts` — легковесная SVG-библиотека.

### 24.2 Sprint 109 — Финансовые KPI (Биллинг)

| Виджет | Описание |
|--------|---------|
| Расходы на ТК (бар) | Сумма счетов по компаниям за период |
| Оплачено / Не оплачено | Круговая диаграмма |
| Динамика цены рейса | Среднее за месяц, тренд |
| Топ-5 ТК по расходам | Таблица с долями |

**API:**
```
GET /api/admin/transport/kpi/billing?date_from=&date_to=  — финансовая сводка
GET /api/admin/transport/kpi/billing/by-company?date_from=&date_to=
```

---

## 25. GPS: позиции машин в реальном времени (Спринты 110–111)

### 25.1 Источник координат

Интеграция с GPS-трекером через HTTP POST или TCP. Трекеры присылают JSON:
```json
{"vehicle_id": 9201, "lat": 58.0105, "lon": 56.2502, "speed_kmh": 65, "ts": 1717000000}
```

**Эндпоинт приёма:**
```
POST /api/gps/track  — принять координату (без auth, защищён IP-whitelist через nginx)
```

### 25.2 Oracle-объекты (миграция 060)

```sql
CREATE TABLE RABAEV.RRL_VEHICLE_GPS (
    ID          NUMBER(15) PRIMARY KEY,
    VEHICLE_ID  NUMBER(10) NOT NULL,
    LAT         NUMBER(10,7),
    LON         NUMBER(10,7),
    SPEED_KMH   NUMBER(5),
    TS          DATE NOT NULL,
    CREATED_AT  DATE DEFAULT SYSDATE
);
-- Только последняя позиция на машину:
CREATE TABLE RABAEV.RRL_VEHICLE_GPS_LAST (
    VEHICLE_ID  NUMBER(10) PRIMARY KEY,
    LAT         NUMBER(10,7),
    LON         NUMBER(10,7),
    SPEED_KMH   NUMBER(5),
    TS          DATE
);
```

### 25.3 Sprint 110 — Backend GPS

- `POST /api/gps/track` — вставить в `RRL_VEHICLE_GPS` и UPSERT в `RRL_VEHICLE_GPS_LAST`
- `GET /api/admin/transport/vehicles/positions` — текущие позиции всех машин
- `GET /api/admin/transport/vehicles/{id}/track?date=` — трек машины за день

### 25.4 Sprint 111 — Карта Live

На `TransportPlannerPage` и `TransportGanttPage`:
- Слой «Автопарк»: иконка грузовика на текущей позиции (из `GET /vehicles/positions`)
- Цвет иконки совпадает с статусом из Ганта (в рейсе = зелёный, на базе = синий)
- Hover: скорость, время последнего обновления, гос. номер
- Автообновление каждые 30 сек через polling (или через WebSocket из Sprint 96)

---

## 26. Тарифная сетка (Sprint 112)

### 26.1 Назначение

Управление тарифами для расчёта цены рейса. Сейчас цена вычисляется Oracle-функцией `stoim_tt` — логика внутри Oracle-пакета непрозрачна. Нужен интерфейс для просмотра и редактирования тарифов.

### 26.2 Предположение о структуре тарифов

Oracle-пакет `TRANSPORT_TASK.stoim_tt` использует некую таблицу тарифов (предположительно `RRL_TT_PRICE` или аналог). Sprint 112:
1. Reverse-engineer: выяснить реальную таблицу тарифов (`DESCRIBE`-анализ)
2. Добавить read-only просмотр тарифов
3. Добавить Oracle-процедуры для редактирования

### 26.3 API

```
GET  /api/admin/transport/tariffs?region=&transport_type=  — список тарифов
POST /api/admin/transport/tariffs                          — создать тариф
PATCH /api/admin/transport/tariffs/{id}                   — обновить тариф
```

**Права:** `BILLING_CREATE_PRICE_PERMISSION` (уже есть).

---

## 27. Интеграция с 1С (Sprint 113)

### 27.1 Назначение

Выгрузка закрытых биллинг-заказов в 1С:Предприятие для бухгалтерского учёта. Формат: XML или JSON в 1С-совместимом формате.

### 27.2 API

```
GET /api/admin/transport/billing/orders/{id}/export/1c   — выгрузить счёт в формате 1С XML
GET /api/admin/transport/billing/orders/export/1c?date_from=&date_to=&status=closed — реестр
```

### 27.3 Формат выгрузки (1С CommerceML / XML)

```xml
<КоммерческаяИнформация Версия="2.09">
  <Документ>
    <Ид>{order_id}</Ид>
    <Номер>{num}</Номер>
    <Дата>{date}</Дата>
    <Контрагент>{company}</Контрагент>
    <Сумма>{total}</Сумма>
    <Табличная>
      <Строка><Рейс>{tt_id}</Рейс><Сумма>{price}</Сумма></Строка>
    </Табличная>
  </Документ>
</КоммерческаяИнформация>
```

### 27.4 UI

Кнопка «⬇ 1С» рядом с «⬇ Excel» в `BillingOrderDetailPanel`.

---

## 28. Архивирование и партиционирование (Sprint 114)

### 28.1 Назначение

Через год эксплуатации `RRL_TRANSPORT_TASK` и `RRL_SBORKA_PALLETS` накопят >100K строк. Нужны инструменты архивирования.

### 28.2 Архивирование рейсов

Скрипт `db/scripts/archive_old_tasks.sql`:
```sql
-- Перенос рейсов старше 2 лет в архив
INSERT INTO RABAEV.RRL_TRANSPORT_TASK_ARCH
SELECT * FROM RABAEV.RRL_TRANSPORT_TASK WHERE SHIPMENT_DATE < ADD_MONTHS(SYSDATE, -24);
DELETE FROM RABAEV.RRL_TRANSPORT_TASK WHERE SHIPMENT_DATE < ADD_MONTHS(SYSDATE, -24);
```

### 28.3 Миграция 061

```sql
-- Архивная таблица (зеркало основной без ограничений FK)
CREATE TABLE RABAEV.RRL_TRANSPORT_TASK_ARCH AS SELECT * FROM RABAEV.RRL_TRANSPORT_TASK WHERE 1=0;

-- Административный эндпоинт запуска архивирования
```

### 28.4 API

```
POST /api/admin/transport/maintenance/archive?older_than_months=24  — запустить архивирование
GET  /api/admin/transport/maintenance/stats  — размеры таблиц
```

**Права:** `RIGHTS_ADMIN_EDIT_PERMISSION`.

---

## 29. Attention Model — PyTorch VRP (Спринты 115–117)

### 29.1 Назначение

Дополнить OR-Tools нейросетевым решателем на основе Attention Model (трансформер). При повторяющемся геопрофиле спроса AM работает быстрее OR-Tools (<500 мс vs 5-30 сек).

### 29.2 Sprint 115 — Сбор данных и обучение

- Экспорт исторических рейсов в обучающий датасет: `{координаты, паллеты, время_окна} → {маршрут}`
- Скрипт `scripts/am_train.py` — обучение модели
- Сохранение весов в `models/am_vrp.pt`

### 29.3 Sprint 116 — Инференс API

```
POST /api/admin/transport/planner/solve
Body: {..., "solver": "attention_model"}
→ результат за <500 мс
```

### 29.4 Sprint 117 — UI интеграция

Третья карточка решателя в `TransportPlannerPage`: «AI-план (<500 мс)» рядом с OR-Tools и шаблонным.

**Требование к обучению:** минимум 1000 исторических рейсов.

---

## 30. Geofencing и авто-отметка операций (Спринты 118–119)

### 30.1 Назначение

При въезде машины в геозону магазина — автоматически фиксировать `fact_start` для операции `UNLOAD`. При выезде — `fact_end`.

### 30.2 Sprint 118 — Геозоны

**Миграция 062:**
```sql
ALTER TABLE RABAEV.RRL_ADDR ADD (
    GEO_FENCE_RADIUS_M  NUMBER(5) DEFAULT 200  -- радиус геозоны в метрах
);
```

**Логика:** в GPS-обработчике (`POST /api/gps/track`) проверять расстояние до адресов активных рейсов машины. При входе/выходе — триггерить отметку факта.

### 30.3 Sprint 119 — Авто-отметка факта

При срабатывании геозоны (Sprint 118):
```python
if entered_geofence(vehicle_id, addr_id):
    auto_mark_operation_start(vehicle_id, "UNLOAD", addr_id)
elif exited_geofence(vehicle_id, addr_id):
    auto_mark_operation_done(vehicle_id, "UNLOAD", addr_id)
```

**UI:** в Ганте, рядом с фактическим временем — иконка «📡 GPS» если факт проставлен автоматически.

---

## 31. Нефункциональные требования

| Требование | Значение |
|-----------|---------|
| WebSocket клиентов одновременно | ≤ 10 (3–5 диспетчеров + 5 запасных) |
| Push-уведомления | ≤ 5 сек задержки от события |
| KPI дашборд | запросы ≤ 3 сек (агрегация за 30 дней) |
| GPS track | ≤ 100 мс ответ на POST /gps/track |
| Mobile PWA offline | полная работа без сети ≥ 8 ч |
| 1С экспорт | файл ≤ 2 сек при 100 рейсах в счёте |

---

## 32. Миграции БД (сводная таблица)

| № | Спринт | Содержание |
|---|--------|-----------|
| 055 | 97 | SEQ_TR_VEHICLE + RRL_TR_VEHICLE_ADD/UPDATE/DEL |
| 056 | 98 | SEQ_TR_VODITEL + RRL_TR_VODITEL_ADD/UPDATE/DEL |
| 057 | 100 | RRL_USER_ADD/DEL/SET_GROUP/SET_PASS + RRL_RIGHT_ADD/DEL |
| 058 | 106 | RRL_PUSH_SUBSCRIPTIONS |
| 059 | 107 | RRL_NOTIFICATION_SETTINGS |
| 060 | 110 | RRL_VEHICLE_GPS + RRL_VEHICLE_GPS_LAST |
| 061 | 114 | RRL_TRANSPORT_TASK_ARCH |
| 062 | 118 | RRL_ADDR.GEO_FENCE_RADIUS_M |
