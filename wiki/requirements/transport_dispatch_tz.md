# Техническое Задание: Модуль Транспортного Диспетчера

Статус: в разработке (Phase 1 реализована 2026-05-21).

Дата: 2026-05-22.

Связанные документы:

- [Биллинг транспорта](transport_billing_tz.md)
- [Oracle Change Protocol](../database/oracle_change_protocol.md)

---

## 1. Назначение

Модуль `Транспортный Диспетчер` обеспечивает полный цикл формирования и отгрузки рейсов:

- Просмотр сборочных заданий (СТ), готовых к погрузке.
- Формирование рейсов вручную: выбор СТ чекбоксами, группировка по машине/водителю/доку.
- Назначение транспортного средства, водителя, дока, времени отгрузки.
- Контроль минимальной загрузки машины перед закрытием.
- Мониторинг прогресса сборки внутри рейса.

Модуль является частью цепочки: **Wave Picking → Стейджинг → Транспортный Диспетчер → Отгрузка**.

Легаси-реализация существует в C# WinForms (tabPage6, TRANSPORT.cs). Новый модуль реализуется на FastAPI + React без изменения C# кода.

---

## 2. Ключевые Термины

- `СТ` — сборочное задание. Единица назначения в рейс.
- `Рейс` — транспортная задача (`RRL_TRANSPORT_TASK`). Один рейс = одна машина + один водитель + список СТ.
- `ТС` — транспортное средство (`RRL_TR_VEHICLE`).
- `ORD` — порядковый номер адреса в рейсе. Определяет последовательность объезда.
- `load_type` — способ погрузки: `Г` = государственный борт, `П` = прицеп, пусто = не указано.
- `ZONE_TIME_PLAN` — временно́е окно доставки: IN = начало, OUT = конец.
- `TT_READY_PERC` — процент паллет рейса, прошедших проверку/сборку.

---

## 3. Состояние Phase 1 (реализовано 2026-05-21)

### 3.1 Backend (`api/wms_api_server/app/`)

| Файл | Что реализовано |
|------|----------------|
| `routers/transport.py` | 13 эндпоинтов под `/api/admin/transport/` |
| `services/transport_service.py` | Полный CRUD рейса через Oracle-функции |
| `auth.py` | Права: `TRANSPORT_DISPATCH_VIEW`, `TRANSPORT_DISPATCH_EDIT`, `TRANSPORT_DISPATCH_CLOSE` |
| `schemas.py` | `TransportTaskCreateRequest`, `TransportTaskUpdateRequest`, `StAssignRequest` |
| `main.py` | Роутер зарегистрирован |

Используемые Oracle-функции: `RRL_TRASPORT_TASK_ADD`, `RRL_TT_ADD_PALL` (TT_ID=0 → снять), `RRL_TT_REORDER_ADR`.

### 3.2 DB (`db/migrations/2026-05-21_transport_dispatch_phase1/`)

- `042_apply.sql` — вьюха `RRL_V_AVAILABLE_STS`, индексы `IDX_SP_TRANSTASK`, `IDX_SP_STDATE`, `IDX_TT_SHIPDATE`.

### 3.3 Frontend (`admin/wms_admin_frontend/src/components/TransportDispatchPage.tsx`)

Двухпанельный диспетчерский борд:
- Левая панель: список рейсов (фильтр по дате) + список доступных СТ с чекбоксами.
- Правая панель: детали рейса, редакторы машина/водитель/дёк/время/примечание, состав рейса, кнопки закрыть/отменить.
- Demo-режим при недоступном API.

### 3.4 Действующие фильтры списка СТ (Phase 1)

| Параметр API | Описание |
|-------------|----------|
| `stdate` | Дата создания СТ |
| `unassigned_only` | Только не назначенные в рейс |
| `ware_id` | Один склад |

---

## 4. Улучшения Phase 1 (требуется реализация)

### 4.1 Дополнительные фильтры списка СТ

**Приоритет: высокий. Сложность: малая.**

Диспетчер не может эффективно работать без фильтрации по адресу и номеру СТ. Это основной инструмент ручного формирования рейса.

#### 4.1.1 Новые query-параметры эндпоинта `GET /api/admin/transport/available-sts`

| Параметр | Тип | Oracle-условие |
|----------|-----|---------------|
| `addr_mask` | str | `(P.ADDR LIKE '%:mask%' OR A.REGION LIKE '%:mask%')` |
| `st_mask` | str | `UPPER(P.ST_NUMBER) LIKE UPPER('%:mask%')` |
| `ware_ids` | list[int] | `P.WARE_ID IN (:ids)` — заменяет одиночный `ware_id` |
| `assembled_only` | bool | `HAVING MAX(RRL_ST_VERYFY_PERC(P.ST_NUMBER)) > 0` |
| `max_weight_kg` | float | `HAVING ROUND(SUM(R.ORDER_WEIGHT),0) < :max_weight` |
| `max_volume_m3` | float | `HAVING ROUND(SUM(R.TARESIZE*R.PACK_COUNT)/1000000,2) < :max_vol` |

#### 4.1.2 Изменения в `transport_service.py`

Метод `list_available_sts()` — добавить параметры и соответствующие SQL-условия в `WHERE` и `HAVING` clause запроса к `RRL_V_AVAILABLE_STS` (или прямо к `RRL_SBORKA_PALLETS`).

`assembled_only` требует добавления подзапроса или `HAVING`, т.к. `RRL_ST_VERYFY_PERC` — функция. Альтернатива: добавить колонку `VERIFY_PERC` в вьюху и фильтровать по ней.

#### 4.1.3 Изменения в `042_apply.sql` / новая миграция

Обновить `RRL_V_AVAILABLE_STS` — добавить:

```sql
RABAEV.RRL_ST_VERYFY_PERC(P.ST_NUMBER)  AS VERIFY_PERC,
P.NAPR                                   AS NAPR
```

Столбец `VERIFY_PERC` в `GROUP BY` не нужен — вычислять через `MAX()` после `GROUP BY`:

```sql
MAX(RABAEV.RRL_ST_VERYFY_PERC(P.ST_NUMBER)) AS VERIFY_PERC
```

Миграция: `db/migrations/2026-05-22_transport_dispatch_improvements/043_apply.sql`.

#### 4.1.4 Изменения во фронтенде

В `TransportDispatchPage.tsx`:
- Добавить поля фильтра: текстовое поле «Адрес/регион», текстовое поле «СТ», чекбокс «Только собранные», мультиселект складов.
- Передавать параметры в запрос к API при изменении.
- Дебаунс 300 мс на текстовые поля.

---

### 4.2 Временны́е окна доставки в составе рейса

**Приоритет: высокий. Сложность: малая.**

Без временны́х окон диспетчер не видит, к какому времени нужно доставить каждый СТ. Это критично для планирования порядка объезда.

#### 4.2.1 Изменения в `transport_service.py`

Метод `get_task_sts()` — добавить в SELECT:

```sql
SP.ZONE_TIME_PLAN_IN   AS TIME_FROM,
SP.ZONE_TIME_PLAN_OUT  AS TIME_TO,
SP.ZONE               AS ZONE,
SP.LOAD_TYPE          AS LOAD_TYPE
```

#### 4.2.2 Изменения в схемах `schemas.py`

`TaskSt` (если используется Pydantic-схема) — добавить поля `time_from`, `time_to`, `zone`, `load_type`.

#### 4.2.3 Изменения во фронтенде

В типе `TaskSt` добавить `TIME_FROM`, `TIME_TO`, `ZONE`, `LOAD_TYPE`.

В таблице состава рейса добавить колонки:

| Колонка | Отображение |
|---------|------------|
| ZONE | текст |
| TIME_FROM / TIME_TO | `09:00 – 12:00` или прочерк |
| LOAD_TYPE | бейдж: `П` = прицеп (синий), `Г` = гос (серый) |

---

### 4.3 Район и процент проверки в списке доступных СТ

**Приоритет: высокий. Сложность: малая.**

#### 4.3.1 Текущее состояние

`RAION` уже присутствует в `RRL_V_AVAILABLE_STS`, но не возвращается фронту.
`VERIFY_PERC` отсутствует в вьюхе (добавляется в п. 4.1.3).

#### 4.3.2 Изменения

В `list_available_sts()` — добавить в SELECT: `RAION`, `VERIFY_PERC`.

В типе `AvailableSt` — добавить `RAION: string | null`, `VERIFY_PERC: number | null`.

В таблице доступных СТ — добавить колонки:

| Колонка | Отображение |
|---------|------------|
| RAION | текст |
| VERIFY_PERC | прогресс-бар или число `85%`. Цвет: красный < 50%, жёлтый 50–99%, зелёный 100% |

---

### 4.4 Проверка минимальной загрузки при закрытии рейса

**Приоритет: высокий. Сложность: малая.**

#### 4.4.1 Бизнес-правило

Нельзя закрыть (отгрузить) рейс, если количество паллет меньше `MIN_PALLET_LOAD` для данного типа ТС. Исключение: у пользователя есть право `SEND_EMPTY_TRUCK`.

Oracle-функция: `TRANSPORT_TASK.can_print(tt_id INT, user_id VARCHAR2) → VARCHAR2`.
Возвращает `'ok'` если всё в порядке, иначе — текст ошибки.

#### 4.4.2 Изменения в `transport_service.py`

Метод `close_task()` — перед UPDATE вызвать `can_print`:

```python
result = self.gateway.call_varchar_function(
    "TRANSPORT_TASK.can_print",
    {"tt_id": task_id, "user_id1": user_id},
)
if result != "ok":
    raise HTTPException(status_code=422, detail=result)
```

#### 4.4.3 Изменения в `auth.py`

Добавить право `SEND_EMPTY_TRUCK`. Передавать `user_id` в `can_print` — Oracle сама проверит право через `RRL_HAS_WRIGHT`.

#### 4.4.4 Изменения во фронтенде

При получении 422 от `POST /tasks/{id}/close` — показать toast с текстом ошибки из `detail`.

---

### 4.5 Прогресс готовности рейса

**Приоритет: средний. Сложность: малая.**

#### 4.5.1 Бизнес-правило

В списке рейсов отображать, какой процент паллет уже собран и проверен.

Oracle-функции:
- `TRANSPORT_TASK.TT_READY_PERC(tt_id)` → `NUMBER` (0..1)
- `TRANSPORT_TASK.TT_UNREADY_COUNT(tt_id)` → `NUMBER`

#### 4.5.2 Изменения в `transport_service.py`

В `list_tasks()` добавить в SELECT:

```sql
ROUND(TRANSPORT_TASK.TT_READY_PERC(TT.ID) * 100, 0)  AS READY_PERC,
TRANSPORT_TASK.TT_UNREADY_COUNT(TT.ID)                AS UNREADY_COUNT
```

Внимание: функции вызываются на каждую строку — при большом количестве рейсов это нагрузка. Добавить фильтр `include_readiness: bool = False` в параметры запроса и вычислять только когда явно запрошено.

#### 4.5.3 Изменения во фронтенде

В `TransportTask` добавить `READY_PERC: number | null`, `UNREADY_COUNT: number | null`.

В карточке рейса добавить индикатор:
- `100%` → зелёная галочка «Собран»
- `> 0%` → прогресс-бар `X%`
- `0%` → красный индикатор «Не собран»

---

### 4.6 Редактирование load_type (в прицеп / гос. борт)

**Приоритет: средний. Сложность: средняя.**

#### 4.6.1 Бизнес-правило

Для каждого СТ в составе рейса диспетчер может указать способ погрузки:
- `П` — грузить в прицеп
- `Г` — государственный борт
- пусто — стандартная погрузка

Поле хранится в `RRL_SBORKA_PALLETS.LOAD_TYPE`.

#### 4.6.2 Новый эндпоинт

```
PATCH /api/admin/transport/tasks/{task_id}/sts/{st_number}/load-type
Body: { "load_type": "П" | "Г" | "" }
```

В `transport_service.py` добавить метод `set_st_load_type(task_id, st_number, load_type, user_id)`:

```python
self.gateway.execute(
    """
    UPDATE RABAEV.RRL_SBORKA_PALLETS
       SET LOAD_TYPE = :load_type
     WHERE ST_NUMBER  = :st_number
       AND TRANSTASK_ID = :task_id
       AND (DELETED IS NULL OR DELETED <> 1)
    """,
    {"load_type": load_type, "st_number": st_number, "task_id": task_id},
)
```

Право: `TRANSPORT_DISPATCH_EDIT`.

#### 4.6.3 Изменения во фронтенде

В таблице состава рейса сделать колонку `LOAD_TYPE` редактируемой: select с тремя вариантами (`—`, `П`, `Г`). При изменении — PATCH-запрос, оптимистичное обновление.

---

### 4.7 Ручная перестановка порядка СТ в рейсе

**Приоритет: средний. Сложность: средняя.**

#### 4.7.1 Бизнес-правило

После автоматической сортировки по `RRL_TT_REORDER_ADR` диспетчер может вручную скорректировать порядок объезда адресов. Поле `ORD` в `RRL_SBORKA_PALLETS` задаёт последовательность.

#### 4.7.2 Новый эндпоинт

```
PATCH /api/admin/transport/tasks/{task_id}/sts/{st_number}/order
Body: { "ord": 5 }
```

В `transport_service.py` добавить `set_st_order(task_id, st_number, ord, user_id)`:

```python
self.gateway.execute(
    """
    UPDATE RABAEV.RRL_SBORKA_PALLETS
       SET ORD = :ord
     WHERE ST_NUMBER   = :st_number
       AND TRANSTASK_ID = :task_id
       AND (DELETED IS NULL OR DELETED <> 1)
    """,
    {"ord": ord, "st_number": st_number, "task_id": task_id},
)
```

Право: `TRANSPORT_DISPATCH_EDIT`.

#### 4.7.3 Изменения во фронтенде

Два варианта UX:
- **Простой**: редактируемое числовое поле `ORD` в строке таблицы. При изменении — PATCH.
- **Удобный**: drag-and-drop строк в таблице состава рейса с пересчётом `ORD` по позиции. При drop — батч PATCH по всем затронутым строкам.

Рекомендуется вариант «простой» для Phase 1, drag-and-drop — как улучшение.

---

### 4.8 Транспортная компания (ТК) в списке рейсов

**Приоритет: низкий. Сложность: малая.**

#### 4.8.1 Источник данных

`RRL_TR_VODITEL.DOVERENNOST_OT` — компания, выдавшая доверенность водителю (= транспортная компания для наёмных водителей).

В Oracle также есть функция `RABAEV.RRL_TT_VODITEL_COMPANY(voditel_id)` — обёртка над тем же полем.

#### 4.8.2 Изменения в `list_tasks()`

В SELECT добавить:

```sql
V.DOVERENNOST_OT AS TK_NAME,
V.SOBSTVENNYY    AS IS_OWN_DRIVER
```

#### 4.8.3 Изменения во фронтенде

В `TransportTask` добавить `TK_NAME: string | null`, `IS_OWN_DRIVER: number | null`.

В карточке рейса: показывать ТК рядом с водителем. Собственные водители (`IS_OWN_DRIVER = 1`) — метка «Свой», наёмные — название ТК.

---

### 4.9 Вызов RRL_TT_SET_TRANSCOMMENT при смене машины

**Приоритет: низкий. Сложность: малая.**

#### 4.9.1 Бизнес-правило

При назначении машины на рейс Oracle-процедура `RRL_TT_SET_TRANSCOMMENT(TRANS, TTID1)` проверяет параметры ТС (лопата, гидроборт) и записывает комментарий в рейс. В C# вызывалась до `RRL_TRASPORT_TASK_UPDATE2`.

#### 4.9.2 Изменения в `transport_service.py`

В методе `update_task()`, если меняется `transport` (поле машины):

```python
if req.transport is not None:
    self.gateway.call_varchar_function(
        "RABAEV.RRL_TT_SET_TRANSCOMMENT",
        {"TRANS": req.transport, "TTID1": task_id},
    )
```

Вызов — до основного UPDATE.

---

## 5. Oracle-объекты, которые должны существовать

Перед деплоем улучшений проверить наличие (все созданы миграцией `042_apply.sql` или ранее):

| Объект | Тип | Статус |
|--------|-----|--------|
| `RABAEV.RRL_TRANSPORT_TASK` | TABLE | существует |
| `RABAEV.RRL_SBORKA_PALLETS` | TABLE | существует |
| `RABAEV.RRL_TR_VEHICLE` | TABLE | существует |
| `RABAEV.RRL_TR_VODITEL` | TABLE | существует |
| `RABAEV.RRL_TRANSPORT_TYPE` | TABLE | существует |
| `RABAEV.RRL_ADDR` | TABLE | существует |
| `RABAEV.RRL_V_AVAILABLE_STS` | VIEW | создана в 042 |
| `RABAEV.RRL_TRASPORT_TASK_ADD` | FUNCTION | существует |
| `RABAEV.RRL_TT_ADD_PALL` | FUNCTION | существует |
| `RABAEV.RRL_TT_REORDER_ADR` | FUNCTION | существует |
| `RABAEV.RRL_TT_SET_TRANSCOMMENT` | PROCEDURE | существует |
| `TRANSPORT_TASK.can_print` | FUNCTION (пакет) | существует |
| `TRANSPORT_TASK.TT_READY_PERC` | FUNCTION (пакет) | существует |
| `TRANSPORT_TASK.TT_UNREADY_COUNT` | FUNCTION (пакет) | существует |
| `RABAEV.RRL_ST_VERYFY_PERC` | FUNCTION | существует |

---

## 6. Новые права доступа

Добавить в `auth.py`:

| Право | Кому |
|-------|------|
| `SEND_EMPTY_TRUCK` | Старший диспетчер, логист |

Существующие права (Phase 1): `TRANSPORT_DISPATCH_VIEW`, `TRANSPORT_DISPATCH_EDIT`, `TRANSPORT_DISPATCH_CLOSE`.

---

## 7. Миграция БД

### 043_apply.sql (новая)

Содержание:
1. Заменить `RRL_V_AVAILABLE_STS` (`CREATE OR REPLACE`) — добавить `VERIFY_PERC`, `NAPR`.
2. Добавить комментарий к колонкам вьюхи.
3. Проверить индекс `IDX_SP_NAPR` на `RRL_SBORKA_PALLETS(NAPR)` при необходимости.

### 043_rollback.sql

Восстановить `RRL_V_AVAILABLE_STS` в состояние из `042_apply.sql`.

---

## 8. Порядок Реализации

| Шаг | Что делать | Приоритет |
|-----|-----------|-----------|
| 1 | Миграция 043: обновить вьюху | 🔴 |
| 2 | Backend: фильтры `addr_mask`, `st_mask`, `assembled_only`, `max_weight_kg`, `max_volume_m3`, `ware_ids` | 🔴 |
| 3 | Backend: `get_task_sts()` — добавить `TIME_FROM/TO`, `ZONE`, `LOAD_TYPE` | 🔴 |
| 4 | Backend: `list_available_sts()` — добавить `RAION`, `VERIFY_PERC` | 🔴 |
| 5 | Backend: `close_task()` — вызов `can_print` | 🔴 |
| 6 | Frontend: новые колонки в составе рейса | 🔴 |
| 7 | Frontend: панель фильтров СТ | 🔴 |
| 8 | Backend: `list_tasks()` — `TK_NAME`, `IS_OWN_DRIVER`, `READY_PERC` | 🟠 |
| 9 | Frontend: прогресс готовности рейса | 🟠 |
| 10 | Backend + Frontend: `load_type` редактирование | 🟠 |
| 11 | Backend + Frontend: ручная перестановка `ORD` | 🟠 |
| 12 | Backend: `RRL_TT_SET_TRANSCOMMENT` при смене машины | 🟡 |
| 13 | Frontend: ТК в карточке рейса | 🟡 |

---

## 9. Связь с биллингом

Функциональность расчёта цены рейса (`PRICE`), платёжных заказов (`RRL_BILL_ORDERS`) и привязки рейсов к биллинг-заказам вынесена в отдельное ТЗ: [transport_billing_tz.md](transport_billing_tz.md).

Поле `PRICE` в `RRL_TRANSPORT_TASK` заполняется автоматически при вызове `RRL_TT_REORDER_ADR` и уже отображается в Phase 1.