# RESULT C-0150 — исправление блокеров yard (C-0149) перед Oracle apply (Claude)

Статус: **кандидат исправлен, NOT_APPLIED**. Checkpoint `4d9bbed0` (только мои файлы, без push). Полный T10 не объявляется закрытым.

## Блокеры → изменение → доказательство
| # | Блокер | Изменение | Доказательство |
|---|---|---|---|
| 1 | owner через native ORDER_LINK/LINE (несвязанный заказ = пустой цикл) | `require_owners`: каждая строка TRIP `orders[]{order_id,line_id}` → ровно один `source_owner_id` в последней ACCEPTED версии ORDER `lines[]`. Нет TRIP/строк/ORDER/строки/owner, или owner неоднозначен — fail closed. Не видит → «не найдено»; только просмотр → TRADE_OWNER_ACCESS_DENIED на запись | offline static test; формы TRIP/ORDER — live READ ONLY (`C0150/scripts/document_shapes_live.py`) |
| 2 | cached replay без ACTOR; deleted user | порядок: право склада → lock ACCESS_REV/site → право ещё раз → склад операции → owner сейчас → `e.ACTOR=p_actor` и hash → квитанция; иначе YARD_OPERATION_CONFLICT. Deleted RUSERS: `RRL_ACCESS_API.allowed` вызывает `alive()` (DELETED) первым, GLOBAL_ADMIN тоже через `is_admin` с DELETED — дубль не добавлен | static test; источник — live READ ONLY (`rusers_columns_live.py`, `C0149/scripts/guard_source_live.py`) |
| 3 | ARRIVE с VEHICLE=NULL, INBOUND без trip | `bind_vehicle`: при ARRIVE заново RRL_TRADE_TRIP_LINK → RRL_TRANSPORT_TASK.TRANSPORT; нет привязки → YARD_TRIP_BINDING_REQUIRED, нет машины → YARD_VEHICLE_REQUIRED. INBOUND → YARD_INBOUND_UNSUPPORTED. CHECK: после приезда машина обязательна | static test |
| 4 | VEHICLE_UK по складу | индекс глобальный по `VEHICLE` активных состояний; CHECK `VEHICLE=upper(trim(VEHICLE))`, запись нормализуется; предпроверка глобальная, отказ YARD_VEHICLE_OCCUPIED без склада/рейса; гонка складов A/B → индекс → YARD_DOCK_OR_VEHICLE_OCCUPIED | static test; живые A/B/регистр — план для Codex |
| 5 | квитанция без operation_id | `card(v,p_op)` кладёт operation_id в каждую новую квитанцию (хранится в RESULT_JSON, replay возвращает её же). Python-адаптер: чужой/пустой operation_id → 503 YARD_RESULT_UNKNOWN. UI-журнал снимает команду только при совпадении operation_id и визита | pytest (чужой/пустой); UI: чужая квитанция оставляет команду, повтор — те же байты |
| 6 | старый Гант до apply | история читается через `history`; ORA-942/4043/6550 → источник `yard` NOT_MAPPED, остальные источники читаются; панель: «учёт двора не включён… это не „ворота свободны“» (YARD_NOT_AVAILABLE) | pytest (3 кода + прочие ошибки не глотаются); UI; live 8088 до apply ранее отдавал NOT_MAPPED (C0149) |
| 7 | FETCH FIRST до owner-фильтра | `trip_visible()` (public, без исключений) в WHERE до `fetch first 200` (visits) и `fetch first 501` (history, >500 → YARD_HISTORY_BOUND_NARROW_WINDOW, считаются только видимые) | static test. Сценарий «200 скрытых + видимый» — **не исполнен** (нужен Oracle) |
| 8 | Гант: одна точка начала, только активные | `history(ware,actor,from,to)` (окно ≤7 сут, owner-фильтр) + EVENT_AT/VEHICLE в журнале. Проекция: YARD_VISIT = машина ARRIVE→DEPART/CANCEL; YARD_DOCK:{visit}:{n} = каждые ворота от назначения до смены/выезда/отмены; закрытые остаются в окне; открытый конец — только до момента чтения; EXPECTED — точка плана | pytest на синтетике: ARRIVE10:00/DOCK A10:30/REASSIGN B11:00/DEPART12:00 → машина 10–12, A 10:30–11, B 11–12; отмена освобождает; конфликт второго пользователя ворот; UI: закрытый интервал старых ворот и открытый — новых |

## Живое / офлайн
- Живое только READ ONLY: формы TRIP/ORDER (ключи, без значений), столбцы RUSERS и `alive/is_admin/RRL_HAS_WRIGHT`, каталог прав (`tradecase_yard_operate` не выдано ни одной роли).
- Офлайн: pytest **42 passed** (`test_yard_visit.py`, `test_resource_timeline.py`, `test_trade_route_points.py`); UI `C0150/scripts/c0150_ui.cjs` **34/34** при 1440/390 (fixture /yard/** и события двора в живом timeline; живые только GET); quality gate PASS (debt 72), encoding PASS, tsc PASS.
- Native **не компилировался** (DDL в моей среде запрещён): ошибки PL/SQL возможны и покажет verify при apply.

## Файлы
`db/migrations/2026-10-22_yard_visit/{001_schema,002_api,000_preflight,verify,rollback_verify,manifest}` (sha256 по LF-копии, `revision: C-0150`, триггер в new_objects); `modules/resources/infrastructure/{yard_visits,resource_timeline,timeline_projection}.py`; frontend `shift/{YardPanel.tsx,yardModel.ts,yardCommands.ts}`, `resources/{timelineAdapter.ts,ResourceCard.tsx}`; help shift-supervisor/resource-gantt; `tests/tradecase/test_yard_visit.py`; `wiki/database/tradecase_yard_visit_20261022.md` (кандидат, в wiki/index не вносил); `reports/.../C0150/**`.

## План живой проверки Codex после apply
1. Роль с `tradecase_yard_operate` своему изолированному QA. 2. Несвязанный внешний ORDER в TRIP: без owner — не видит/не пишет; только просмотр — не пишет; operate — может; отзыв — скрывает. 3. Replay тем же operation_id/телом другим пользователем → 409; удалённый пользователь → 403. 4. ARRIVE без привязки/машины → отказ. 5. Одна машина (`" a1 "`/`"A1"`) на складах A и B параллельно → один ARRIVED. 6. Два параллельных ASSIGN_DOCK на одни ворота. 7. 200 визитов скрытого owner + 1 видимый → видимый в visits/history. 8. История: REASSIGN/DEPART в Ганте; UPDATE/DELETE журнала → YARD_EVENT_APPEND_ONLY; до/после — stock без изменений.

## Ограничения
Межскладская гонка решается уникальным индексом (общий отказ, без деталей). Входящие визиты не поддерживаются. Нормативов опоздания нет.
