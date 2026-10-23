# RESULT C-0149 — T10: визиты двора, ворота, риски старшего смены (Claude)

Статус: **кандидат готов к ревью Codex; NOT_APPLIED** (native apply в среде Claude запрещён, не обходился). T10 целиком не объявляется закрытым — границы ниже.

## Исследование (что было)
- Реестра двора/визитов не было. Ворота рейса пишет legacy `services/transport_service.py`, факты этапов — `PATCH /api/admin/transport/operations/{id}/fact` (RRL_TT_OPERATION_PLAN_API.write_fact) без operation_id/версии/конфликтов. RRL_DELIVERY_ARRIVAL — приезд в магазин, не двор.
- Значит новый bounded домен визита поверх существующих рейса (RRL_TRANSPORT_TASK), ворот (RRL_TT_DOCK) и TRADECASE-привязки (RRL_TRADE_TRIP_LINK, RRL_TRADE_DOCUMENT TRIP). Складских количеств/резервов визит не трогает.
- Live READ ONLY (`scripts/permission_catalog_live.py` → `permission-catalog-live.json`): объектов RRL_YARD* нет; право `tradecase_view` есть в ролях, **`tradecase_yard_operate` не выдано ни одной роли** (права — свободные строки ролей, каталога в коде нет).

## Реализовано
### Native — `db/migrations/2026-10-22_yard_visit/` (additive, общие объекты не меняются)
- `001_schema.sql`: RRL_YARD_VISIT_SQ; RRL_YARD_VISIT (состояния EXPECTED → ARRIVED → AT_DOCK → WORKING → WORK_DONE → DEPARTED | CANCELLED, VERSION_NO, факты-времена с поясом; CHECK связывает состояние с его фактом); уникальные функциональные индексы: одни ворота / одна машина / один рейс — не больше одного активного визита на склад; RRL_YARD_VISIT_EVENT (OPERATION_ID PK, REQUEST_HASH, RESULT_JSON); **триггер RRL_YARD_VISIT_EVENT_APPEND** — история только дописывается.
- `002_api.sql` пакет RRL_YARD_VISIT_API:
  - `command`: порядок блокировок как у остальных TRADECASE-писателей (RRL_ACCESS_REV share → RRL_TRADE_SITE FOR UPDATE → строка визита) — все писатели склада сериализованы; затем `tradecase_yard_operate` (RRL_ACCESS_API.allowed — отключённый/удалённый RUSERS → 0); replay по operation_id: другой склад → YARD_OPERATION_CONFLICT; **owner-права текущего момента до любого раскрытия сохранённой операции**; другой hash → YARD_OPERATION_CONFLICT; иначе исходный ответ с `replayed:true`.
  - EXPECT (машина берётся из рейса), ARRIVE (**проверка занятости машины до UPDATE**), ASSIGN_DOCK/REASSIGN_DOCK (ворота: нет/неоднозначны/заблокированы/заняты — до UPDATE), START, FINISH, DEPART (освобождает ворота), CANCEL (до начала работы, причина обязательна). Версия визита обязательна (VERSION_CONFLICT). Уникальный индекс — последний страж гонки (YARD_DOCK_OR_VEHICLE_OCCUPIED).
  - Скрытый владелец: не видит даже чтением → тот же ответ, что для отсутствующего объекта (YARD_TRIP_REQUIRED / YARD_VISIT_NOT_FOUND); видит, но без записи → TRADE_OWNER_ACCESS_DENIED (403). В `visits` такие визиты пропускаются целиком (не считаются).
  - JSON_OBJECT_T.get_* только в PL/SQL-переменные, ни одного внутри SQL (ORA-40573) — проверяется тестом.
  - `visits(ware, actor, active)`: `tradecase_view`, ≤200 визитов, порядок «в работе → у ворот → закончили → на площадке → ожидаются», `observed_at` — часы сервера.
- 000_preflight / verify (INVALID 0, ошибки компиляции, 3 индекса, триггер) / rollback (отказ при наличии истории визитов) / rollback_verify / apply / manifest (`files_sha256` пересчитаны, `applied_by_claude:false`).

### Backend (`api/wms_api_server/app/`)
- `modules/resources/contracts_yard.py` (YardExpect/YardTransition с валидатором аргументов, YardPort, `wire()` — время до секунд с поясом), `infrastructure/yard_visits.py` (одна native-команда на запись; чтение READ ONLY; -20800…-20999 → 409/403 подтверждённый отказ; прочее → 503 YARD_RESULT_UNKNOWN), `api/yard_routes.py`: `GET/POST /api/tradecase/warehouses/{id}/yard/visits`, `POST …/visits/{visit}/transitions`; 503 → `retry_same_operation_id:true`.
- Регистрация: строки в `modules/resources/public.py` и **`app/case_resource_composition.py`** (место подключения не было названо в ACK K-0106 — сообщаю).
- Гант: `infrastructure/resource_timeline.py` — источник `yard` (право `tradecase_view`), активные визиты через owner-фильтрующий native `visits`; нет пакета (ORA-04043/06550) → источник `NOT_MAPPED`, прочие ошибки не глотаются. `timeline_projection.py` `yard()`: визит держит ворота от постановки, машину от приезда, окончание открыто до выезда (`fact_finish_at=null`, `fact_finish_status=OPEN`) → пересечение считается до «сейчас», неизвестная длительность ≠ свободно. Ожидаемый визит — точка плана; без плана — в очереди без времени. LOAD/DEPART остаются точками и визит не начинают.

### Frontend (`admin/wms_admin_frontend/src/features/platform/workspaces/`)
- `shift/YardPanel.tsx`, `shift/yardModel.ts`, `shift/yardCommands.ts`; процесс «Двор и ворота» в `ShiftSupervisorDesk.tsx` (`key={wh}`), подсказки в `shift/help.ts`.
  - Группы состояний, текущая машина/рейс/ворота (назначенные или план рейса), очередь на ворота по времени приезда, опоздание/ожидание по `observed_at` сервера, «Нет данных» (машина, план приезда, плановые ворота), «Конфликт» (плановые ворота заняты другим визитом), «В Ганте».
  - Журнал команды: тело с operation_id сохраняется в localStorage до отправки, переживает 503/reload, повтор — те же байты; снимается только подтверждённым ответом/отказом; пока не прояснено — новые действия заблокированы. Повреждённая запись не перезаписывается.
  - 401/403/404 чтения очищают список (useApiRead), поздний ответ прежнего чтения игнорируется (abort).
- `resources/timelineAdapter.ts` (YARD_VISIT, источник «Двор (визиты)», NOT_MAPPED → «источник не подключён»), `resources/ResourceCard.tsx` (состояния визита, источник).
- Help: `docs/help/authoring/shift-supervisor.md` (раздел «Двор и ворота», уточнено «что отправляется отсюда»), `resource-gantt.md` (раздел «Визиты двора»).

## Проверено
- `tests/tradecase/test_yard_visit.py` 11 + `tests/retailcase/test_resource_timeline.py` = **34 passed** (`PYTHONPATH=api/wms_api_server`): точные аргументы переходов, формат времени, отказ/неизвестный исход, один native вызов, роуты 503/409/422, проекция ворот/машины с открытым концом, конфликт второго пользователя ворот при открытом визите, LOAD — точка, NOT_MAPPED до миграции; статически: JSON вне SQL, права/owner до replay, append-only, проверка машины до UPDATE.
- UI `reports/.../C0149/scripts/c0149_ui.cjs` на dev :3021, **26/26 PASS** при 1440 и 390 (`c0149-ui.json`, скриншоты `yard-*.png`, `gantt-*.png`): группы/очередь/опоздание/конфликт/нехватка; у каждой кнопки title+help id; без горизонтального скролла; 503 → команда сохранена, блокирует новые, переживает reload, повтор теми же байтами и тем же operation_id; 409 VERSION_CONFLICT снимает команду с причиной; отмена требует причину; «В Ганте» выделяет полосу визита, карточка показывает состояние и открытое окончание; поздний ответ игнорируется; 403 очищает список. Живые только GET (и read-only POST shift-overview); не-GET вне /yard/ — 0.
- **Живой API 8088 (без миграции) отдаёт источник `yard` = NOT_MAPPED** — Гант не падает до apply.
- Время: рендер панели после ответа 6–10 мс; живой `/api/resources/timeline` 432–806 мс (4 выборки, вкл. NOT_MAPPED-попытку yard). Живых замеров SQL визитов нет — объекты не применены.
- `retailcase_quality_gate.py` PASS (Architecture PASS, debt_items 72 — не вырос), `check-encoding.ps1` PASS, tsc PASS.

## Не подтверждено / план живой проверки для Codex (после apply)
1. Выдать `tradecase_yard_operate` ролью своему изолированному QA на тестовый склад (без реактивации старых QA). Без этого управлять двором сможет только GLOBAL_ADMIN.
2. Свой рейс-фикстура TRIP с ordered owners; EXPECT → ARRIVE → ASSIGN_DOCK → START → FINISH → DEPART; затем CANCEL на втором визите; до/после — RRL_REMAINS/резервы склада не меняются.
3. Два параллельных ASSIGN_DOCK на одни ворота (две сессии): один AT_DOCK, второй YARD_DOCK_OCCUPIED/OR_VEHICLE_OCCUPIED; то же ARRIVE двух визитов одной машины.
4. Двойной exact retry (тот же operation_id/байты → `replayed:true`, одно событие), changed request (тот же id, другое тело → YARD_OPERATION_CONFLICT), устаревшая версия → VERSION_CONFLICT, неверное состояние → YARD_STATE_CONFLICT.
5. Отзыв склада (роль) и owner-гранта между командой и повтором: replay → 403/YARD_VISIT_NOT_FOUND, исходный ответ не возвращается; удалённый RUSERS → 403.
6. UPDATE/DELETE RRL_YARD_VISIT_EVENT → YARD_EVENT_APPEND_ONLY. Убрать свои визиты штатно: CANCEL/DEPART (история остаётся; rollback откажет при наличии истории — по замыслу).
7. Замер `visits` при 200 визитах: owner-проверка на визит (разбор TRIP BODY_JSON) — при росте выше сотен визитов нужен set-based вариант.

## Ограничения / границы
- Гант показывает только **активные** визиты (уехавшие видны точками LOAD/DEPART); история визитов в окне — отдельная доработка при необходимости.
- Уникальность машины — в пределах склада (блокировка сайта сериализует один склад); межскладская не проверяется.
- Визиты INBOUND в API предусмотрены, UI создаёт только OUTBOUND по рейсу. Нормативов простоя/опоздания нет — показываются минуты, без порогов.
- Не тронуто: существующая роль «Двор и ворота» (`workspaces/RoleDesks.tsx` YardDesk, не моя) по-прежнему пишет «нет журнала прибытия машин» — после apply владельцу стоит заменить текст/подключить панель.
- integrations/trade_route*/trade_topup*/receiving_marks, stock core/wave/guard, picking, fixtures — не трогал.
