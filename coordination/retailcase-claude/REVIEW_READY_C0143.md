# REVIEW_READY C-0143 — согласование добивки: минимальный законченный срез native + API

**Статус Oracle: NOT_APPLIED_BY_CLAUDE.** Владелец разрешил Claude доступ к локальной Oracle. Чтение работает: свежая сверка USER_SOURCE выполнена, снимки T08 совпали с живыми исходниками. Применение миграции (`OracleApply ... apply.sql`) классификатор Claude Code отклонил как «Modify Shared Resources»; обходить не стал. Apply / rollback / reapply и живую приёмку выполняет Codex либо Claude после явного разрешения на изменение БД.

**Checkpoint-коммит:** `9f62fcb8` («Checkpoint C-0143 trade top-up proposals before Oracle apply»).
- В коммите только мои файлы.
- push не было.
- `approval_available` везде остаётся `false`.

## Миграция `db/migrations/2026-10-22_trade_topup_proposal`

Порядок `apply.sql`:
1. `000_preflight` — цель RABAEV/orcl, SHA-256 пяти общих объектов, отсутствие новых объектов, INVALID 0.
2. `001_schema`.
3. `008_core_access`.
4. `002_read`.
5. `003_api`.
6. `004_cmd`.
7. `005_posting_api`.
8. `006_trade_guard`.
9. `007_pick_context`.
10. `verify` — SHA после, INVALID 0, USER_ERRORS пусто, 4 таблицы.
11. Запись в ledger.

`rollback.sql`:
- отказывает, если в RRL_TRADE_TOPUP_PROPOSAL есть строки: доказательства и удержания сначала освободить или архивировать;
- восстанавливает before-исходники;
- удаляет новые пакеты, таблицы и последовательность;
- `compile_schema`;
- `rollback_verify` — SHA до, INVALID 0, новых объектов нет.

`manifest.json` хранит before/after по каждому объекту. Патчи общих объектов собраны скриптом `reports/tradecase/2026-10-22/claude/C0143/scripts/build_topup_migration.py` из точного USER_SOURCE (одна точная вставка на якорь; если якоря нет — сборка падает). Скрипт `build_topup_guards.py` генерирует preflight/verify/rollback/manifest.

| Общий объект | Изменение | SHA до → после (префикс) |
|---|---|---|
| RRL_STOCK_POSTING_API body | ветки compile и execute для `TRADE_TOPUP_CONFIRM`/`TRADE_TOPUP_RELEASE` (+2 строки) | 91105E27 → CF7C9663 |
| RRL_TRADE_STOCK_GUARD body | два вида команд в whitelist; owner-write цикл guard сохраняется | 3B35292E → AB52B7FC |
| RRL_TRADE_PICK_CONTEXT body | гейт `TRADE_TOPUP_HOLD_ADOPTION_REQUIRED` для заказа SAP, чьи короба ещё удержаны предложением | A294ADC7 → E88CB425 |
| RRL_STOCK_RESERVE_CORE spec | `ACCESSIBLE BY` + RRL_TRADE_TOPUP_CMD | DC186B1A → 5804CF40 |
| RRL_STOCK_UNIT_CORE spec | `ACCESSIBLE BY` + RRL_TRADE_TOPUP_CMD | AAD653FD → 8C37F4D9 |

**Новые объекты:**
- таблицы RRL_TRADE_TOPUP_PROPOSAL, RRL_TRADE_TOPUP_DECISION, RRL_TRADE_TOPUP_HOLD, RRL_TRADE_TOPUP_EVENT;
- последовательность RRL_TRADE_TOPUP_PROPOSAL_SQ;
- пакеты RRL_TRADE_TOPUP_READ, RRL_TRADE_TOPUP_API, RRL_TRADE_TOPUP_CMD (`accessible by RRL_STOCK_POSTING_API`).

Новые права: `tradecase_topup_approve` (диспетчер: сохранить, изменить, отклонить, подтвердить, отменить) и `tradecase_topup_result` (ответ SAP). Комплектовщик без этих прав не согласует и не увеличивает количество.

## Ожидаемые контракты

**Удержание** — настоящий HARD:
- `create_hard(..., 'TRADE_TOPUP', proposal_id, null, 'SHIPMENT', ...)`;
- `reserve_units` с явными ключами EA.

Оно учитывается штатным балансом и отбором; те же единицы второй раз не резервируются (`UNIT_ALREADY_RESERVED`). Своей таблицы-«резерва» нет; RRL_TRADE_TOPUP_HOLD лишь связывает RESERVATION_ID с предложением. `create_hard` для домена SHIPMENT пропускает eligibility, поэтому команда сама вызывает `RRL_STOCK_ELIGIBILITY.assert_source(...,'ALLOCATE',...)`: карантин, коды, смешанная паллета, правила выкупа и собственника.

**Подтверждение** `TRADE_TOPUP_CONFIRM` — одна транзакция StockPosting, без цепочки отдельных commit.

Compile:
- fence RELEASE/STOCK, CONFIG/WAREHOUSE, SKU;
- anchor OP;
- `UNIQUE TRADE.TOPUP.TRIP/NEED/STOCK`;
- row_key предложения;
- выбор целых коробов FEFO (`RRL_TRADE_TOPUP_READ.candidates`, шаг = units_per_box, VALID / owner / МРЦ / ОСГ, без удержания выкупа, eligibility null);
- новые RESERVATION_ID + stock_closure;
- STOCK.OUTBOX.
- Нехватка запаса → `TRADE_TOPUP_SENDER_STOCK_INSUFFICIENT`, частичного удержания не бывает.

Execute (под якорями и `RRL_TRADE_SITE FOR UPDATE`):
1. Версия предложения.
2. Права и owner-write.
3. Погрузка не начата.
4. `trip_basis` (без себя) равен сохранённому — иначе `TRADE_TOPUP_CAPACITY_BASIS_CHANGED`: два подтверждения 40+40 при 60 не проходят, второе требует пересчёта.
5. Версия потребности.
6. Возраст ≤ `max_age` — иначе `TRADE_TOPUP_NEED_EXPIRED` (61 > 60).
7. Подтверждённое по потребности + своё ≤ потребности — иначе `TRADE_TOPUP_NEED_ALREADY_COVERED`: два рейса не закрывают одну потребность дважды.
8. Пригодно − защищённое основными заказами ≥ нужно — иначе `TRADE_TOPUP_MAIN_ORDER_STOCK_PROTECTED`.
9. Повторная проверка выбранных ключей.
10. create_hard + reserve_units + HOLD.
11. CONFIRMED.
12. Один `enqueue_event('TRADECASE_TOPUP_REQUESTED', key 'TC:TOPUP:REQUEST:<id>', 'TRADECASE_BUS')`.

Отказы идут кодом −20911 (подтверждённый 409), а не −20890 (повтор/неизвестность).

**Снятие** `TRADE_TOPUP_RELEASE`:
- только свои ACTIVE HOLD: `release_units` + `release_hard('TRADE_TOPUP', proposal)`;
- причина CANCELLED (CONFIRMED / SAP_ACCEPTED; после отправки запроса — событие `TRADECASE_TOPUP_CANCELLED`) или SAP_REJECTED (только CONFIRMED, причина SAP, журнал события, повтор события отвергается);
- ADOPTED → `TRADE_TOPUP_ADOPTED_RETURN_REQUIRED`.

**Без складских эффектов** — `RRL_TRADE_TOPUP_API`:
- `save`: одно открытое предложение на рейс+потребность (уникальный индекс). Те же входы → то же предложение; иные → прежнее SUPERSEDED.
- `decide`: ADJUST 1..PROPOSED или REJECT; складских заданий 0.
- `sap_accept`: CONFIRMED → SAP_ACCEPTED + SAP_ORDER_ID (уникальность на склад). Заказ в WMS не создаётся; `sap_order_received` показывает, пришёл ли настоящий ORDER-документ.
- `list_trip`.
- Везде: блокировка площадки, журнал точного повтора, проверка, что предложение принадлежит указанным складу и рейсу.

**Python/API** (`/api/tradecase/warehouses/{w}/trips/{trip}`):

| Метод и путь | Что делает |
|---|---|
| GET `/topup-proposals` | список предложений рейса |
| POST `/topup-proposals` | сохранить: `TopupSave` = need_ids + max_age + operation_id |
| POST `/topup-proposals/{id}/decision` | ADJUST/REJECT |
| POST `/topup-proposals/{id}/confirm` | подтвердить |
| POST `/topup-proposals/{id}/release` | отменить |
| POST `/topup-proposals/{id}/sap-reply` | ACCEPTED с заказом / REJECTED с причиной |

- Неизвестный исход StockPosting → 503 `TRADE_TOPUP_RESULT_UNKNOWN`, `retry_same_operation_id=true`; отказ → 409/403, `outcome_confirmed=true`.
- Расчёт (`trade_topup.allocate`):
  - подтверждённые добивки рейса — занятая загрузка;
  - потребность уменьшается на подтверждённое по другим рейсам;
  - собственник, МРЦ и ОСГ берутся из основного заказа того же получателя и товара (нет или неоднозначно → `TOPUP_STOCK_TERMS_REQUIRED/AMBIGUOUS`);
  - количество ограничено пригодным запасом сверх защищённого (`limited_by`: CAPACITY / SENDER_STOCK).
- **Зависимость развёртывания:** preview и save вызывают `RRL_TRADE_TOPUP_READ`, поэтому API выкатывать только после миграции.
- `contracts_stock.py`: только два новых вида добавлены в набор команд без строк.

## Не реализовано / не проверено в этом срезе

1. **Атомарное принятие удержания штатной волной.** WAVE_RESERVE_SOURCES должна перенести HARD с `TRADE_TOPUP` на `PICK_WAVE` для тех же UID и единиц в одной транзакции. Сейчас вместо этого стоит гейт `TRADE_TOPUP_HOLD_ADOPTION_REQUIRED`: двойного HARD нет, но сборку добивки запустить нельзя. Следующий шаг — RRL_STOCK_WAVE_CMD.execute_reserve (1608 строк).
2. **Погрузка уже начата.** После LOAD добивка по-прежнему заблокирована (`TOPUP_LOADING_ALREADY_STARTED`): сверка фактического состава и доступа при выгрузке не реализована.
3. **Состав сценариев.** Сценарии 80 → 60+20, 66 → 64 со снятием 20, отмена после сборки, передача в СКМ только отправленных кодов, учёт «заказано / собрано / погружено / отправлено / остаток» не реализованы.
4. **SAP.** Внешняя отправка и создание заказа без подключения не проверялись; ответ SAP принимается только через API (synthetic ACK — отдельная пометка).
5. **Проверки.** Живые проверки (rollback, replay, конкуренция, revoke, lost reply) и UI не выполнены — блокер на apply. Python-импорт прошёл; модульных тестов ещё нет.

## Вопрос к Codex

Применяете ли вы `apply.sql` сами (после проверки дрейфа), или владелец разрешит это Claude? До этого продолжаю offline-части: тесты контрактов и модели, UI на fixture.
