# ТЗ: Модуль управления транспортом и отгрузкой

> Файл поддерживается AI-ассистентом. Дата: 2026-05-20.
> Основан на: анализе C# Form1.cs, TRANSPORT.cs, VODITEL.cs, BillingTransport.cs,
> Oracle функций (006_functions.sql) и таблиц существующей схемы RABAEV.

---

## 1. Контекст и цель

### Что есть сейчас

Управление транспортом реализовано **только в C# WinForms** (`Form1.cs`, `TRANSPORT.cs`, `VODITEL.cs`, `BillingTransport.cs`). Oracle хранит данные в таблицах `RRL_TRANSPORT_TASK`, `RRL_TR_VEHICLE`, `RRL_TR_VODITEL`, `RRL_SBORKA_PALLETS`, `RRL_TT_DOCK`, `RRL_TT_ZONES`. Бизнес-логика частично в Oracle-функциях, частично в C#.

### Проблема

Транспортный контур **изолирован от современного API-слоя**. Это означает:
- Диспетчер отгрузки работает только с C# desktop-клиентом
- Интеграция с wave-picking (который живёт в API) — только через прямые запросы к Oracle
- Нет мобильного интерфейса для водителя/экспедитора
- Нет аудит-трейла через `RRL_API_CALL_LOG`

### Цель модуля

Перенести управление транспортом в **FastAPI + React**, сохранив Oracle как систему отсчёта. Создать:
1. Oracle-пакет `RRL_TRANSPORT_API` как единственную точку записи
2. FastAPI роутер `transport`
3. React-страницу диспетчера отгрузки в admin frontend
4. TSD-страницу (HTML или React) для водителя/экспедитора

---

## 2. Существующая модель данных

### Ключевые таблицы (уже в Oracle)

```sql
RRL_TRANSPORT_TASK          -- рейс/задание на отгрузку
  ID                        -- PK
  CREATEDATE                -- дата создания
  TRANSPORT                 -- номер ТС (ссылка на RRL_TR_VEHICLE.NUM)
  TRANSTYPE                 -- тип транспорта (код)
  ROUTETYPE                 -- тип маршрута
  CONDITION                 -- статус рейса
  TRANSP_ZONE               -- транспортная зона
  WAVE                      -- дата волны (timestamp)
  SHIPMENT_DATE             -- дата отгрузки
  PLANNED_DELIVERY_DATE     -- плановая дата доставки
  VODITEL_ID                -- водитель (FK RRL_TR_VODITEL)
  DOCK                      -- номер дока
  PRICE                     -- стоимость рейса
  HOURS                     -- часы
  RANGE1                    -- дальность
  TEMP_REGION               -- регионы доставки (вычисляемое)
  TEMP_WEIGHT               -- вес (вычисляемое)
  PAY_ORDER_ID              -- ссылка на расчётный ордер
  SHIPMENT_TIME             -- время отгрузки (вычисляемое)
  DOCK_REZERV_TIME_FROM     -- резервация дока с
  DOCK_REZERV_TIME_TO       -- резервация дока до
  USER_ID                   -- создал
  PRIMECHANIE               -- примечание
  DELETED                   -- мягкое удаление

RRL_TR_VEHICLE              -- реестр транспортных средств
  ID                        -- PK
  NUM                       -- гос. номер
  TR_TYPE                   -- тип ТС (код)
  MARKA                     -- марка/модель
  REF_REJIM                 -- режим охлаждения
  WORKING_NOW               -- в работе (0/1)
  PALLETS                   -- ёмкость (паллет)
  BLOCKED                   -- заблокирован
  GIDROBORT                 -- наличие гидробортника (0/1)

RRL_TR_VODITEL              -- реестр водителей
  ID                        -- PK
  F, I, O                   -- ФИО
  DELETED                   -- мягкое удаление
  SOBSTVENNYY               -- собственный/наёмный
  TRANSPORT_NUM             -- закреплённое ТС
  PASSPORT                  -- паспорт
  DOVERENNOST_OT            -- доверенность от компании
  TEL                       -- телефон
  ADDR                      -- адрес
  (ext) INN                 -- ИНН (RRL_TR_VODITEL_EXT)
  (ext) TABEL_NUMBER        -- табельный номер

RRL_SBORKA_PALLETS          -- паллеты, приписанные к рейсу
  ID                        -- PK
  PALLET_UID                -- FK → RRL_PALLETS
  TRANSTASK_ID              -- FK → RRL_TRANSPORT_TASK (NULL = не назначен)
  ADDR                      -- адрес доставки
  KROSS_WEIGHT              -- вес кросс-докинг
  TRIAL_WEIGHT              -- фактический вес
  PROOVED                   -- проверен (0/1)
  ORD                       -- порядок загрузки
  WARE_ID                   -- склад
  STDATE                    -- дата стейджинга

RRL_TT_DOCK                 -- плановая загруженность доков
  DOCK                      -- номер дока
  WARE_ID                   -- склад
  ORD                       -- порядок
  COUNT_OF_PALLETS          -- кол-во паллет
  DOCK_IS_BLOCKED           -- блокировка

RRL_TT_ZONES                -- зоны погрузки
  ZONE                      -- код зоны
  SUB_ZONE                  -- подзона
  DOCK                      -- привязка к доку
  X, Y                      -- координаты

RRL_BILL_ORDERS             -- расчётные ордера (биллинг рейсов)
  ID                        -- PK
  NUM                       -- номер ордера
  COMPANY                   -- компания
  DATEOFORDER               -- дата ордера
  DATEFROM, DATETO          -- период
  CLOSED                    -- закрыт
  PAYED                     -- оплачен
  NUM_PLAT                  -- номер платежа

RRL_ADDR                    -- справочник адресов доставки
  ADDR                      -- код адреса
  ORD                       -- порядок объезда
  SHIPPING_TIME             -- время доставки (минуты от начала)
  STOL                      -- нужен ли гидробортник
```

### Существующие Oracle-функции (сохраняются)

| Функция | Назначение |
|---|---|
| `RRL_TRASPORT_TASK_ADD(transtype, date, user_id)` | Создать рейс |
| `RRL_TRASPORT_TASK_UPDATE2(...)` | Обновить рейс (ТС, водитель, дата, док) |
| `RRL_TT_ADD_PALL(tt_id, pallet_num)` | Привязать/отвязать паллет к рейсу |
| `RRL_TT_REORDER_ADR(tt_id)` | Пересортировать паллеты по адресам |
| `RRL_TT_PLAN_SHIPPPING_HOUR(tt_id)` | Вычислить время отгрузки |
| `RRL_TT_PLAN_DOCK(tt_id, time, ware_id)` | Зарезервировать док |
| `RRL_TT_SET_TRANSCOMMENT(tt_id)` | Проверить соответствие ТС адресам |
| `RRL_GET_TT_PRICE(tt_id)` | Рассчитать стоимость рейса |
| `RRL_TT_REGIONS(tt_id)` | Получить регионы доставки |
| `RRL_TT_PALLETS(tt_id)` | Количество паллет |
| `RRL_TT_WEIGHT(tt_id)` | Суммарный вес |
| `RRL_TT_VOLUME(tt_id)` | Суммарный объём |
| `ADD_RRL_TR_VEHICLE(...)` | Создать/обновить ТС |
| `ADD_RRL_VOD(...)` | Создать/обновить водителя |
| `RRL_BILL_ADD_TTBILL(...)` | Создать/обновить расчётный ордер |

---

## 3. Архитектурные решения

### 3.1 Oracle-пакет RRL_TRANSPORT_API

Создать новый PL/SQL-пакет по образцу `RRL_PICKING_API`, `RRL_WAREHOUSE_TASK_API`:

```
RRL_TRANSPORT_API
  .create_task(p_transtype, p_shipment_date, p_user_id)  → task_id
  .update_task(p_task_id, p_vehicle_num, p_driver_id, p_dock, p_date, ...)
  .assign_pallet(p_task_id, p_pallet_uid)
  .unassign_pallet(p_task_id, p_pallet_uid)
  .reorder_by_address(p_task_id)
  .plan_dock(p_task_id, p_ware_id)
  .close_task(p_task_id, p_user_id)      -- подтверждение отгрузки
  .cancel_task(p_task_id, p_user_id)
  .validate_vehicle(p_task_id)           -- проверка гидробортника и вместимости
```

Все существующие функции (`RRL_TRASPORT_TASK_ADD`, `RRL_TT_ADD_PALL` и т.д.) вызываются **изнутри пакета**, а не напрямую из API-сервера.

### 3.2 FastAPI роутер

Файл: `api/wms_api_server/app/routers/transport.py`  
Сервис: `api/wms_api_server/app/services/transport_service.py`

Маршруты строго через Oracle-пакет, без прямых INSERT/UPDATE в таблицы.

### 3.3 Интеграция с wave picking

Связь: `RRL_SBORKA_PALLETS.TRANSTASK_ID` → рейс.  
После завершения wave (статус `STAGED`/`READY_TO_SHIP`) паллеты становятся доступны для назначения на рейс. Диспетчер выбирает паллеты из списка "готовы к отгрузке".

### 3.4 Domain sync

Добавить домен `TRANSPORT / TASK_CLOSE / TRANSPORT_TASK` в `RRL_WAREHOUSE_TASK_SYNC` для синхронизации физического перемещения паллет от стейджинговой зоны до дока.

---

## 4. API контракт

### 4.1 Рейсы (Transport Tasks)

```
GET    /transport/tasks                    — список рейсов с фильтрами
POST   /transport/tasks                    — создать рейс
GET    /transport/tasks/{id}               — рейс с паллетами
PATCH  /transport/tasks/{id}               — обновить (ТС, водитель, дата, док)
POST   /transport/tasks/{id}/assign        — назначить паллет на рейс
DELETE /transport/tasks/{id}/assign/{uid}  — снять паллет с рейса
POST   /transport/tasks/{id}/reorder       — пересортировать паллеты по адресам
POST   /transport/tasks/{id}/plan-dock     — зарезервировать док
POST   /transport/tasks/{id}/validate      — проверить ТС (гидробортник, вместимость)
POST   /transport/tasks/{id}/close         — подтвердить отгрузку
POST   /transport/tasks/{id}/cancel        — отменить рейс
```

### 4.2 Транспортные средства

```
GET    /transport/vehicles                 — список ТС
POST   /transport/vehicles                 — добавить ТС
PATCH  /transport/vehicles/{id}            — обновить ТС
```

### 4.3 Водители

```
GET    /transport/drivers                  — список водителей
POST   /transport/drivers                  — добавить водителя
PATCH  /transport/drivers/{id}             — обновить водителя
```

### 4.4 Доки

```
GET    /transport/docks                    — список доков с занятостью
GET    /transport/docks/availability       — свободные слоты по времени
```

### 4.5 Паллеты к отгрузке

```
GET    /transport/pallets/ready            — паллеты готовые к отгрузке (без рейса)
GET    /transport/tasks/{id}/pallets       — паллеты рейса с порядком загрузки
```

### 4.6 Биллинг

```
GET    /transport/billing/orders           — расчётные ордера
POST   /transport/billing/orders           — создать ордер
POST   /transport/billing/orders/{id}/add-task    — добавить рейс
DELETE /transport/billing/orders/{id}/tasks/{tid} — убрать рейс
POST   /transport/billing/orders/{id}/close       — закрыть
POST   /transport/billing/orders/{id}/pay         — отметить оплаченным
```

### 4.7 Схемы данных (Pydantic)

```python
class TransportTaskCreate(BaseModel):
    transtype: str
    shipment_date: date

class TransportTaskUpdate(BaseModel):
    vehicle_num: str | None
    driver_id: int | None
    dock: str | None
    shipment_date: date | None
    planned_delivery_date: date | None
    primechanie: str | None

class TransportTaskDetail(BaseModel):
    id: int
    condition: str
    transtype: str
    vehicle: VehicleInfo | None
    driver: DriverInfo | None
    shipment_date: date
    shipment_time: datetime | None
    dock: str | None
    dock_from: datetime | None
    dock_to: datetime | None
    pallets_count: int
    weight: float
    volume: float
    regions: str
    price: float | None
    pallets: list[PalletAssignment]
```

---

## 5. Бизнес-логика

### 5.1 Жизненный цикл рейса

```
CREATED → [назначение ТС, водителя, паллет] → PLANNED →
[резервация дока] → DOCK_RESERVED →
[диспетчер подтверждает загрузку] → LOADING →
[завершена погрузка, закрыт рейс] → DISPATCHED
```

Отмена возможна из любого статуса кроме `DISPATCHED`.

### 5.2 Проверка ТС

При назначении транспортного средства система проверяет:
- Хватает ли вместимость (`RRL_TR_VEHICLE.PALLETS >= count(палет в рейсе)`)
- Если хотя бы один адрес доставки требует гидробортник (`RRL_ADDR.STOL = 1`), то `RRL_TR_VEHICLE.GIDROBORT = 1`
- ТС не заблокировано (`BLOCKED = 0`)

### 5.3 Планирование времени отгрузки

Автоматически вычисляется как максимум из:
- Дат стейджинга паллет (`RRL_SBORKA_PALLETS.STDATE`)
- Планового времени доставки по адресам (`RRL_ADDR.SHIPPING_TIME`)

### 5.4 Резервация дока

Алгоритм (из `RRL_TT_PLAN_DOCK`):
1. Находит пустой док в указанном складе
2. Итерирует с шагом 30 минут если док занят (макс 10 итераций)
3. Резервирует зоны погрузки (`RRL_TT_ZONE_FIND_EMPTY_DOCK` → `RRL_TT_PLAN_PALL_ZONES`)
4. Записывает `DOCK_REZERV_TIME_FROM/TO`

### 5.5 Автоматический расчёт стоимости

Вызывается при каждом изменении состава рейса. Учитывает:
- Базовую цену по типу маршрута и ТС (`RRL_TRANSPORT_PRICE`)
- Дальность доставки (`RANGE1`)
- Почасовую ставку если применимо

### 5.6 Кросс-докинг

Рейсы с `REMOTE_TT_ID` — входящий кросс-докинг. Паллеты поступают с внешнего рейса, проверяются весы, затем паллеты освобождаются (`TRANSTASK_ID = NULL`) для переназначения на исходящий рейс.

---

## 6. UI/UX

### 6.1 Страница диспетчера отгрузки (React Admin)

**Компонент:** `admin/wms_admin_frontend/src/components/Transport/`

**Левая панель — рейсы на дату:**
- Фильтр по дате отгрузки
- Таблица рейсов: время отгрузки, ТС, водитель, паллет/кг/м³, регионы, док, статус
- Кнопки: Создать рейс, Отменить, Закрыть (отгружен)
- Строка рейса expandable: список паллет с адресами и порядком загрузки

**Правая панель — паллеты готовы к отгрузке:**
- Фильтр: дата, адрес, клиент
- Таблица: UID паллеты, артикул, кол-во, вес, адрес, клиент, дата волны
- Drag-and-drop или checkbox-назначение на рейс

**Нижняя панель — доки:**
- Временная шкала занятости доков (текущий день)
- Визуализация резерваций

### 6.2 TSD страница для водителя (HTML или React)

**URL:** `/transport/driver-tsd` или `wiki-raw/wms_admin_ui_reference/transport-driver-tsd.html`

**Функции:**
- Список рейсов водителя на сегодня
- Для каждого рейса: список паллет в порядке загрузки (ORD)
- Сканирование ШК паллеты → подтверждение загрузки (`PROOVED = 1`)
- Статус погрузки: x/n паллет загружено
- Кнопка "Рейс отправлен" → закрытие рейса

### 6.3 Страница администрирования ТС и водителей

Простые CRUD-страницы через API, встраиваются в admin frontend.

---

## 7. Интеграция с существующей системой

### 7.1 С wave picking

Триггер: при переходе паллеты в статус `STAGED` (загружена в зону отгрузки)  
→ в `RRL_SBORKA_PALLETS` создаётся запись (если не существует)  
→ паллет появляется в списке "готовы к отгрузке" в API `/transport/pallets/ready`

### 7.2 С warehouse tasks

При подтверждении загрузки паллеты (водитель сканирует):
→ создаётся `RRL_WAREHOUSE_TASK` типа `LOADING_MOVE` (док → рейс)
→ домен: `TRANSPORT / LOADING_MOVE / TRANSPORT_TASK`
→ синхронизируется через `RRL_WAREHOUSE_TASK_SYNC`

### 7.3 С API audit

Все мутирующие операции через API → логируются в `RRL_API_CALL_LOG` через `ApiAuditMiddleware`.

### 7.4 Совместимость с C# клиентом

- Oracle-таблицы не меняются, только **добавляется** пакет `RRL_TRANSPORT_API`
- C# продолжает работать как раньше, вызывая те же функции напрямую
- API-сервер использует тот же пакет
- Миграция диспетчеров на React admin — постепенная, без принудительного отключения C#

---

## 8. Миграции Oracle

### Миграция 041 — transport_api_package

```sql
-- Создаёт пакет RRL_TRANSPORT_API
-- Обёртывает существующие функции
-- Добавляет статусную машину CONDITION
-- Добавляет индексы для API-запросов
```

### Миграция 042 — transport_warehouse_task_sync

```sql
-- Добавляет домен TRANSPORT в RRL_WAREHOUSE_TASK_SYNC
-- Обработчик: TRANSPORT / LOADING_MOVE / TRANSPORT_TASK
```

### Миграция 043 — transport_ready_pallets_view

```sql
-- View RRL_V_PALLETS_READY_TO_SHIP
-- JOIN RRL_SBORKA_PALLETS + RRL_PALLETS + RRL_PICK_WAVE
-- WHERE TRANSTASK_ID IS NULL AND wave status IN ('STAGED', 'READY')
```

---

## 9. Критерии приёмки

### Функциональные

- [ ] Создать рейс через API → появляется в dataGridView17 (C# не ломается)
- [ ] Назначить 10+ паллет на рейс, пересортировать по адресам
- [ ] Зарезервировать док → время отгрузки вычисляется автоматически
- [ ] Проверка гидробортника работает корректно
- [ ] Водитель сканирует паллеты через TSD → прогресс загрузки обновляется
- [ ] Закрыть рейс → паллеты уходят из списка "готовы к отгрузке"
- [ ] Расчётный ордер: добавить рейсы, закрыть, отметить оплаченным

### Интеграционные

- [ ] Паллеты из завершённых wave-волн видны в `/transport/pallets/ready`
- [ ] Закрытие рейса создаёт запись в `RRL_WAREHOUSE_TASK` (тип LOADING_MOVE)
- [ ] Все мутации видны в `RRL_API_CALL_LOG`

### Load-тест (evidence-driven)

- [ ] Smoke: создать рейс → назначить паллеты → закрыть → все статусы корректны
- [ ] Load: 5 рейсов в день, 50 паллет каждый, 3 дока — нет конфликтов резервации
- [ ] Артефакты: `report.json`, `report.md`, скриншоты ARM-страницы, TSD-страницы

---

## 10. Оценка трудоёмкости

| Компонент | Размер |
|---|---|
| Oracle-пакет RRL_TRANSPORT_API + миграции | M (2–3 дня) |
| FastAPI роутер + сервис | M (2 дня) |
| React admin страница диспетчера | L (4–5 дней) |
| TSD страница для водителя | S (1 день) |
| CRUD ТС и водителей | S (1 день) |
| Интеграция с warehouse tasks | M (2 дня) |
| Load-тест + evidence артефакты | S (1 день) |
| **Итого** | **~14 рабочих дней** |
