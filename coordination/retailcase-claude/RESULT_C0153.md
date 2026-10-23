# RESULT C-0153 — штатное списание брака и native удержание T11 (Claude)

Статус: **кандидат готов, NOT_APPLIED, PL/SQL в моей среде не компилировался** (DDL запрещён). Checkpoint `7b076874`. T11 целиком не объявляется закрытым.

## Что сделано
### Списание (posting kind `TRADE_QUALITY_WRITE_OFF`, владелец — новый пакет `RRL_STOCK_QUALITY_WRITEOFF`)
По образцу действующего `STORE_RETURN_DISPOSE`, через существующий posting runner (журнал operation_id, RESULT_UNCERTAIN, exact retry, lock plan). **Одна транзакция runner'а:**
1. `assert_scope` до компиляции и после блокировок: `tradecase_quality_post` на складе дела + `assert_owner(...,1)` по каждому owner кодов; для kind runner берёт `RRL_ACCESS_REV` share до stock-блокировок (как остальные kind с проверкой прав).
2. `describe` (compile, execute и внутри consume): дело `WAITING_POSTING` той же версии, склад из запроса = склад дела; паллета одна строкой RRL_REMAINS в той же карантинной ячейке, той же STOCK_VERSION, **HARD_RESERVED_BASE=0**, без активной HU-связи (не в грузовом месте/погрузке); хеш состава = замороженный; ровно замороженные коды, той же UNIT_VERSION, AVAILABLE, без HARD_RESERVATION_ID, и ничего сверх; сумма = остаток; базовая единица по RRL_STOCK_UOM_CONVERSION.
3. Lock plan: OP, row_key дела, `stock_closure` (HU, SLOT, STOCK, резервы), UNIT rank 60 по каждому коду, UNIQUE outbox-якоря, регуляторные якоря.
4. `RRL_STOCK_EFFECT_CORE.consume(..., p_units=>коды, p_quality_case=>дело)` — уменьшение остатка и выдача кодов штатным ядром (журнал движения внутри consume).
5. Дело → `POSTED` (+POSTED_BY/AT/POST_OPERATION_ID, версия+1, `sql%rowcount=1`), удержание `RRL_QUALITY_HOLD` снимается (товара больше нет).
6. Маркированные коды (99.9% торговых): `RRL_REGULATORY_API.enqueue_stock_events('MARKED_GOODS_DISPOSED', ...)` — событие выбытия, `regulatory_status=PENDING`.
7. Исходящий документ `RRL_SAP_RECEIPT_OUTBOX` `TRADE_QUALITY_WRITTEN_OFF` с составом (артикул·owner·количество, коды); `external_sap_ack=false`. Ответ SAP/СКМ читается экраном из `ACKNOWLEDGED_AT` (PENDING / ACKNOWLEDGED / MISSING) — не выдумывается.
Любая ошибка — откат всей TX runner'ом (частичного эффекта нет). Python только отправляет команду (`POST …/exceptions/write-offs`).

### Native удержание (`RRL_TRADE_STOCK_GUARD.assert_command_stock`)
Вызывается dispatcher'ом в `execute_prepared` **после захвата STOCK-блокировок** для каждой паллеты (rank 50). Активное `RRL_QUALITY_HOLD(PALLET)` → `QUALITY_HOLD_ACTIVE` для любой команды, кроме `INVENTORY_COUNT`/`INVENTORY_REGISTER_LOT` и `TRADE_QUALITY_WRITE_OFF` именно того дела `WAITING_POSTING`, что держит паллету. Kind добавлен в список допустимых для торгового остатка (иначе был бы TRADE_ORDER_BINDING_REQUIRED).
**Покрытие путей:** при активном релизе триггеры `RRL_STOCK_REMAINS_GUARD`/`RRL_STOCK_UNIT_GUARD`/`RRL_PHYSICAL_VERSION_GUARD` требуют posting-контекст и удерживаемый STOCK-лок паллеты для любой записи RRL_REMAINS/RRL_WMS_RECEIPT_UNIT (`DIRECT_STOCK_WRITE_FORBIDDEN`) — значит любой writer остатка проходит `execute_prepared` с этой паллетой в rank 50, т.е. через guard (live READ ONLY, `C0153/scripts/write_paths_live.py`). Плюс товар в карантинной ячейке уже исключён из подбора/волн/отгрузки (C0152). Открытого обхода не нашёл; если где-то есть writer с выключенной enforcement (`RRL_STOCK_RELEASE.STATE='PREPARED'`), guard там не действует — это режим подготовки релиза, не рабочий.

### Гонка дела с перемещением
Команды дела (OPEN/DECIDE/APPROVE) после ACCESS_REV/site берут **тот же dbms_lock паллеты**, что runner (`resource_lock_id(50,resource_key('STOCK',uid))`, release on commit), **до** чтения остатка/кодов; занято 5 с → `QUALITY_STOCK_LOCK_BUSY` (повтор тем же operation_id). Удержание создаётся под этим локом, guard проверяет его под тем же локом. Замечание root по `cell_visible` исправлено: код без owner скрывает ячейку (fail closed).

### Экран исключений
«Провести списание» → подтверждение → `TRADE_QUALITY_WRITE_OFF` тем же журналом команды (503/reload/exact retry, только своя квитанция). `WAITING_POSTING` = «утверждено, ещё не проведено»; `POSTED` = «Списано со склада» + отдельно «ответ SAP/СКМ ожидается/подтверждён». Тексты отказов native (изменился состав, резерв, грузовое место, удержание). Справка `exceptions.md` обновлена.

## Миграция `db/migrations/2026-10-23_trade_quality_posting/`
Порядок: preflight (fresh before-SHA 7 объектов: EFFECT_CORE spec/body, POSTING_API body, TRADE_STOCK_GUARD body, REGULATORY_STOCK_OUTBOX body — live; RRL_TRADE_QUALITY_CASE_API spec/body — **установленная root версия C0152, прочитана live, байт-в-байт = исходнику C0152**) → ALTER дела (POSTED, колонки, ограничения, индексы) → case API → EFFECT_CORE spec → writeoff → EFFECT_CORE body → regulatory → guard → dispatcher → verify. Изменения общих объектов минимальны: dispatcher — ровно 5 строк с kind (проверено тестом), EFFECT_CORE — параметр/accessible by/ветка, guard — блок удержания + kind в списке, regulatory — одна ветка. rollback: отказ при POSTED/операциях kind; restore общих владельцев из before-копий до drop пакета, затем C0152-версия дела и колонки; rollback_verify сверяет SHA всех 7 объектов с before. manifest c files_sha256.
**Recovery своих тестовых данных (root):** непроведённые дела — штатно: OPEN → «годен» (снимает удержание) → выпуск MOVE_QUARANTINE; DEFECT/WAITING_POSTING отмены не имеют (не изобретал) — тестовую fixture держать на отдельной паллете или провести списание; проведённое списание — реальный факт, восстановление только новой штатной приёмкой, не откатом.

## Проверки
- **Live READ ONLY:** источники и SHA, triggers/write guard, posting kinds, regulatory outbox, MARK_STATE (PENDING 746 / VALID 2303 / REJECTED 1), индекс `RRL_QUALITY_HOLD_I1(ENTITY_TYPE,ENTITY_ID,HOLD_STATUS)` — проверка удержания в guard ~1,5 мс; запросы describe на крупнейшей торговой паллете (1000 кодов) 2–8 мс; describe выполняется 3 раза за проводку.
- **pytest:** `test_quality_posting.py` 11 + `test_quality_case.py` 11 + соседние = 35/58 PASS. `tests/retailcase/test_mes_stock_command_replay.py` 5 FAIL — **предсуществующие**: те же 5 падают при откате моей строки в contracts_stock.py.
- **UI fixtures:** `C0153/scripts/c0153_ui.cjs` **42/42** при 1440/390 (проведение: тело case_id+version, 503→повтор теми же байтами, отказ изменённого состава; POSTED с отдельным внешним статусом; весь прежний сценарий C0152). Живые только GET.
- gate PASS (debt 72), encoding PASS, tsc PASS.

## Ограничения / осталось
1. Root: apply после ревью (PL/SQL не компилировался у меня); живая приёмка в своей fixture: карантинная ячейка, права `tradecase_quality_control/approve/post`, цикл до POSTED с проверкой до/после остатка, кодов, outbox, regulatory; параллельно OPEN vs MOVE_QUARANTINE (лок), отказ HU/резерва, отзыв owner/склада, exact retry/changed request.
2. Возможна взаимная блокировка «дело (site→STOCK) vs TRADE_TOPUP_CONFIRM (STOCK→site)» на одной площадке: разрешается таймаутом 5 с у команды дела (`QUALITY_STOCK_LOCK_BUSY`, повтор), без зависания.
3. Отмены DEFECT/WAITING_POSTING нет — в BP11 не описана, не добавлял.
4. Ответы SAP/СКМ и ЧЗ — внешние этапы, остаются PENDING до реального подтверждения.
