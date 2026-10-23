# RESULT C-0152 — рабочее место исключений T11 (Claude)

Статус: **кандидат готов, native NOT_APPLIED**. Checkpoint `c4a2f0b8` (только мои файлы, без push). T11 не объявляется закрытым — открытые этапы ниже.

## Результат по операциям
| Операция сотрудника | Как сделано | Состояние |
|---|---|---|
| Поставить паллету в карантин / выпустить | Существующий native `MOVE_QUARANTINE` (целая паллета в/из ячейки `BLOCKED_FOR_REMAINS=1`, legacy право QUARANTINE_MOVE, owner write в RRL_TRADE_STOCK_GUARD) через существующий posting runner — новый маршрут `POST …/exceptions/quarantine-moves`; журнал/RESULT_UNCERTAIN/повтор те же | реализовано; живого выполнения нет |
| Товар в карантине заблокирован | Уже native: ячейки `BLOCKED_FOR_REMAINS` исключены из подбора, волн, сборки, отгрузки (RRL_STOCK_ELIGIBILITY, RRL_STOCK_WAVE_CMD, RRL_PICKING_API, RRL_STOCK_SHIPPING_CORE и др. — live READ ONLY `hold_shape_live.py`) | существующее |
| Выпуск при активном деле запрещён во всех путях | **Не native в этом пакете.** UI/маршрут проверяют `assert_release` до проведения (предпроверка, не блокировка). Точный кандидат для root: `reports/.../C0152/root_candidate_trade_stock_guard.md` (вставка в `RRL_TRADE_STOCK_GUARD.assert_command_stock` по активному `RRL_QUALITY_HOLD`, список точек применения) | кандидат root |
| Контролёр открывает дело и решает «брак»/«годен» | Новый `RRL_TRADE_QUALITY_CASE_API` (OPEN, DECIDE; право `tradecase_quality_control`). Дело только для паллеты в карантине, каждый код с собственником (fail closed). Удержание — **существующая** `RRL_QUALITY_HOLD` через `RRL_TRACEABILITY_API.create_quality_hold`, снимается при «годен». Решение принимается, только если ячейка, STOCK_VERSION и хеш кодового состава не изменились | реализовано; не применено |
| Руководство проводит списание | **Не проводится.** Штатного владельца списания товара нет (в RRL_STOCK_POSTING_API только TARE_WRITE_OFF). Руководство (`tradecase_quality_approve`) утверждает списание брака → `WAITING_POSTING`, `posting_status=WAITING_NATIVE_POSTING`; товар остаётся в карантине. Проведение (новый posting kind: списание замороженных кодов + исходящий документ в одной TX) — stock core, граница root. Ответ SAP/СКМ — ещё более поздний этап | бизнес-этап открыт |
| Пересчёт/расхождение | Существующие задания RRL_INVENTORY_TASK и API пересчёта; рабочее место показывает открытые и расходящиеся задания (право `stock_inventory_count`, иначе раздел «закрыт», не «пусто») и ведёт в складские задания. Новый пересчёт не создавал | чтение + навигация |

**Не второй ledger:** RRL_TRADE_QUALITY_CASE_UNIT хранит только ключи кодов и их версии; количество/артикул/собственник читаются из RRL_WMS_RECEIPT_UNIT/RRL_TRADE_STOCK_ATTR. Миграция не пишет RRL_REMAINS/RRL_WMS_RECEIPT_UNIT/RRL_PALLETS/RRL_TRADE_STOCK_ATTR (проверено тестом).

## Native — `db/migrations/2026-10-23_trade_quality_case/` (additive, общие объекты не меняются)
RRL_TRADE_QUALITY_CASE(+SQ, активное дело на паллету — уникально), _UNIT (коды, триггер FROZEN), _EVENT (append-only). Пакет: command (право до раскрытия площадки → lock ACCESS_REV/site → право снова → replay: склад, owner сейчас, автор+hash → квитанция с operation_id), overview (карантин, дела, расхождения; owner-фильтр до `fetch first`), case_detail, assert_release, visibility-функции. Скрытый owner → «не найдено». JSON get_* только в PL/SQL-переменные. preflight/verify/rollback(отказ при наличии дел)/rollback_verify/apply/manifest (sha256 по LF, before-SHA не нужен — заменяемых объектов нет). **PL/SQL не компилировался в моей среде** — ошибки покажет verify при apply.

## Backend / frontend
- `modules/inventory/{contracts_quality_case.py,infrastructure/quality_cases.py,api/quality_case_routes.py}`, экспорт в `modules/inventory/public.py`, `app/quality_case_composition.py` + 2 строки в `app/main.py` (после register_tradecase). `GET /api/tradecase/warehouses/{w}/exceptions`, `GET …/cases/{id}`, `POST …/cases`, `POST …/quarantine-moves`; 503 → `retry_same_operation_id`; чужая/неполная квитанция → 503 unknown.
- Рабочее место «Исключения» (`workspaces/exceptions/**`, роль в `WorkplaceHome.tsx`): разделы Карантин / Дела качества / Расхождения, состав (артикул·собственник·количество, коды), действия по состоянию, журнал команды в браузере (переживает 503/reload, повтор теми же байтами), подсказка у каждой кнопки. Справка `docs/help/authoring/exceptions.md`.

## Проверки: что исполнено где
- **Live Oracle READ ONLY** (`reports/.../C0152/scripts/*_live.py`): список posting kinds, объекты качества/инвентаризации, источник MOVE_QUARANTINE и trade guard, RRL_QUALITY_HOLD/traceability, кто читает BLOCKED_FOR_REMAINS. Найдено: **на торговых площадках нет ни одной карантинной ячейки** — живому сценарию root нужна ячейка в своей fixture. Замер эквивалентного SQL чтения (220793322, 215590763): холодный 37–102 мс, далее 1–3 мс; объём мал (0 паллет в карантине, крупнейшая паллета 110 кодов) — подтверждённого торможения нет.
- **Offline pytest:** `test_quality_case.py` 11 + соседние = **47 passed**.
- **UI fixtures:** `c0152_ui.cjs` **34/34** при 1440/390 (живые только GET, 0 записей, 0 JS-ошибок; готовность экрана 1,1–1,3 с): разделы/состав, выпуск недоступен при деле, title+help у кнопок, без горизонтального скролла, 503→сохранено→reload→чужая квитанция→повтор теми же байтами, 409 конфликт версии, утверждение = «ждёт проведения» без кнопок, коды, расхождения/закрытый раздел, поздний ответ, «не включено», 403 очищает.
- quality gate PASS (debt 72), encoding PASS, tsc PASS. HTTP через живой 8088 не проверялся (API без reload, root).

## Осталось (конкретно)
1. Root: apply миграции; выдать `tradecase_quality_control`/`tradecase_quality_approve` своим изолированным QA; карантинная ячейка на площадке; живой цикл карантин → дело → брак → утверждение и годен → выпуск, повтор/конфликт/отзыв, до/после количество/собственник/коды без изменения.
2. Root: native запрет по `RRL_QUALITY_HOLD` в RRL_TRADE_STOCK_GUARD (кандидат приложен).
3. Root/stock core: штатное проведение списания (posting kind + исходящий документ) — до него дела остаются `WAITING_POSTING`.
4. Ответ SAP/СКМ — внешний этап, недоступен.
