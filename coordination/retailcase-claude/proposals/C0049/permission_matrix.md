# Матрица прав: роли, области, разделение обязанностей

Полная таблица «роль → права R/X/A/M → область → состояние рабочего места» сгенерирована из каталога: [generated/permission_mapping.md](generated/permission_mapping.md). Ниже — правила, по которым она составлена, и решения, которые нужно принять до подключения.

## 1. Что сохраняется без изменений

- `RUSERS.USER_GROUP` + `RIGHTS(USER_GROUP, RIGHT1)` — текущие права пользователей. Новые назначения их не отнимают.
- `GLOBAL_ADMIN` — особый режим `{"*"}` в Python и в `RRL_HAS_WRIGHT`.
- `RRL_HAS_WRIGHT(user, right)` — прежняя семантика для legacy и для Oracle-проверок (`cost_access`, приёмка магазина, возвраты).
- 29 legacy-прав desktop/ТСД (`komplect`, `check_weight`, `load_st`, `view_vesov` и др.) остаются в группах и не проверяются новым API.

Плоский список permissions остаётся совместимостью, но не доказывает scoped-доступ. Решение о доступе с областью принимает сервер/Oracle по активному назначению (AK02/AK03, Codex).

## 2. Состояние прав в каталоге

| Статус | Сколько упоминаний | Что значит для внедрения |
|---|---|---|
| API, выдано группам | 164 | Можно включать в роли сразу после AK02 |
| API, сейчас ни у одной группы | 12 | Работает только у GLOBAL_ADMIN. Сюда входят `warehouse_receipt_confirm`, `warehouse_receipt_reconcile`, `sap_supply_view`, `transport_dispatch_close`, `transport_fleet_edit`, `stock_receipt_reverse`. Без роли приёмка SAP и закрытие рейса требуют администратора |
| legacy RIGHTS | 29 | Только для desktop/ТСД; в новых ролях — для совместимости legacy-групп |
| Новое | 10 | `stock_adjust_approve`, `cell_availability_edit`, `network_kpi_view`, `store_region_view`, `carrier_manage`, `yard_gate_manage` и права модуля доступа/знаний из ACCESS_KNOWLEDGE_API_V1. Без серверной команды право ничего не даёт |

## 3. Области

Виды совпадают с enum `scope_kinds` в `GET /api/access/catalog` (C-0060).

| Область | Определение | Есть сейчас |
|---|---|---|
| WAREHOUSE | отдельный склад | `RUSERS.WARE_ID` и `require_warehouse` в части SQL; объекты в `/api/access/objects?kind=WAREHOUSE` |
| DC | распределительный центр — объект верхнего уровня, может содержать склады (`parent_kind/parent_id`) | `/api/access/objects?kind=DC` |
| ZONE | подсклад/участок склада | объект доступа; в исполнении — зоны квалификаций ресурсов |
| STORE | магазин | объект доступа; в существующих экранах акт магазина привязан к рейсу и приёмщику |
| REGION | регион магазинов | объект доступа |
| CARRIER | перевозчик | объект доступа; модуля перевозчиков нет |
| ORG_BRANCH | организационная ветвь, `scope_id = ВИД:КОД`; снимок использует `access_revision` из `/me` (C-0057) | API |
| GROUP | именованная группа объектов одного вида; актуальный состав или снимок версии | API (`/api/access/groups`, предпросмотр влияния) |
| SELF | свои объекты по серверной привязке | водитель: driver-bindings + `/api/driver/*`; комплектовщик: задание за собой |
| NETWORK | вся сеть | назначение; GLOBAL_ADMIN — особый режим |
| PLATFORM | системные полномочия платформы, отдельно от данных сети | API |

Права проверяются вместе с областью конкретного назначения (native, Codex). Сетевое чтение одной роли не расширяет складское исполнение другой.

## 4. Разделение обязанностей

Проверка внутри одной роли недостаточна. Правила двух видов.

**Человек** — совокупность всех активных назначений пользователя. Правило ниже — предложение для утверждения владельцем, не действующий запрет. Мандат назначающего (нельзя выдать больше своих прав, области и срока) уже проверяет сервер; GLOBAL_ADMIN сохраняет особый режим.

| Нельзя иметь вместе | Почему | Обеспечено сейчас |
|---|---|---|
| `stock_inventory_count` + `stock_adjust_approve` на одном складе | пересчитавший не утверждает расхождение | GAP: утверждения нет |

**Объект** — автор конкретного документа не делает следующий шаг по нему. Проверяется на сервере по автору, а не по названию права:

| Объект | Автор | Следующий шаг | Сейчас |
|---|---|---|---|
| Недостача комплектации | `…/lines/{id}/short` (created_by) | `/case-pick/shorts/{id}/approve` | GAP: запрета совпадения нет |
| Дополнительный расход | `/logistics-expenses/report` (`edit_bill_tt`) | `/decide` LOGIST (`expense_logist_approve`), FINANCE (`expense_finance_approve`) | **Обеспечено native** (C-0066): автор ≠ решающий, LOGIST ≠ FINANCE, в т. ч. для GLOBAL_ADMIN |
| Приёмка SAP | `…/pallets` (`warehouse_receipt_confirm`) | сторно (`stock_receipt_reverse`) | GAP |
| Акт магазина | `/store-receipts/confirm` | `/case-work/{id}/loss` | GAP |
| Недостача тары | `/tare/loss-report` | `/tare/loss-decide` | **Обеспечено native** (C-0065): `TARE_INDEPENDENT_LOSS_DECISION_REQUIRED` |
| Возврат магазина | приём водителем | `/store-returns/{id}/approve` | GAP |

Согласование расходов переведено на узкие права `expense_logist_approve` / `expense_finance_approve` по фактическому складу расхода, без права менять ставки (C-0066). Legacy `calc_tt_price`/`create_tt_price` сохраняются как прежний источник доступа; согласующему `create_tt_price` (ставки) не выдаётся.

## 5. Legacy-группы: соответствие без переназначения

| Группа | Пользователей | Ближайшая роль каталога | Различия |
|---|---|---|---|
| SBORSHIK | 401 | Комплектовщик | Прав в RIGHTS нет — работают через legacy ТСД; новой роли нужен `case_pick_execute` |
| SHTABELER | 71 | Водитель ричтрака | То же; нужен `warehouse_task_execute` |
| KLADOVSHIK | 51 | Старший контроля / контролёр | `komplect`, `create_vycherk` шире контроля |
| STOCK_MANAGER | 46 | Контролёр остатков | `internal_move`, `change_articul` — исполнение, не контроль |
| VESOV | 46 | Контролёр веса | `op_delete`, `create_fake_pal` — опасные legacy-права, оставить только в legacy |
| STOPPER | 21 | Грузчик / старший экспедиции | `divide_st` — решение диспетчера |
| REVIZOR | 15 | Инвентаризатор | нет `stock_inventory_count` |
| ST_PRIEMO_SD | 15 | Старший приёмки | нет прав API приёмки (они ни у кого) |
| ST_SMEN | 10 | Начальник смены | нет прав волн/заданий API |
| LOGIST | 10 | Руководитель планирования / маршрутный планировщик | `edit_bill_tt`, `create_tt_price` — финансовые права внутри логистов |

Перевод только по утверждённому mapping, с отчётом до/после и откатом (AK08). Автоматически никто не переназначается.

## 6. Подтверждённые проблемы авторизации — в первый этап

Проверено по `main.py` (`include_router` без зависимостей, у `FastAPI()` нет глобальных `dependencies`) и по самим маршрутам:

1. **Без аутентификации:** `routers/production.py` — `/api/production-batches/*`, `/api/raw-batches*`, `/api/aggregations/*`, `/api/mercury-operations*`, `/api/regulatory/*`, `/api/crpt-codes/status`, включая POST/PATCH. Это реальный обход, не отсутствие локального декоратора.
2. **`POST /api/gps/track`** — отдельный сценарий учётной записи устройства. Административный логин не подходит, нужен токен устройства (C-0051).
3. **Чтение под правом изменения:** часть GET тары и возвратов под `warehouse_settings_edit` — аудитор и наблюдающие роли их не получат.
4. **Изменение под правом просмотра:**
   - `POST /api/admin/notifications/broadcast|settings` — под `transport_dispatch_view`;
   - `POST /api/finance/logistics-expenses/decide` — на маршруте `transport_dispatch_view`, настоящая проверка в Oracle.

   Второй случай корректен, если Oracle-проверка обязательна: зафиксировать это в контракте.
