# RESULT C-0146 — T08: передача удержания добивки штатной волне (кандидат)

ACK K-0099, список native-объектов K-0100, RELEASE K-0101. Кандидат готов, **NOT_APPLIED_BY_CLAUDE**: apply, живая приёмка и решение о снятии блокировки остаются за Codex. `approval_available=false` не менялся. Весь T08 не закрыт.

## Реализация (коммит `143a37c6`, только мои файлы, без push)

Миграция `db/migrations/2026-10-22_trade_topup_wave_adoption` (новая, аддитивная; применённую `..._trade_topup_proposal` не трогал). Изменения сверены по свежему USER_SOURCE и SHA:

| Объект | Изменение |
|---|---|
| RRL_TRADE_TOPUP_ADOPT (новый) | `line_proposal`: строка своего SAP-заказа подходит, только если предложение SAP_ACCEPTED (отменённое → −1 до проверки удержаний, без перехода на свободный запас); есть заказ TOPUP с `parent_trip_id` = рейс предложения и тем же получателем, не отменён; обновлённый TRIP содержит заказ/строку/количество; источник заказа и TRIP равен источнику площадки; SKU, МРЦ и оба собственника совпадают; штуки = одобренные коробы × units_per_box. Также `gate`, `hold_rid`, `hold_free`, `task_proposal`, `compile_wave` (row_key предложения; явный отказ для SHIP_FROM_STOCK), `split_units`, `mark_adopted` (только внутри контекста запуска) |
| RRL_TRADE_TOPUP_ADOPTION (новая) | история переноса и связь с волной, заданием и строкой плана |
| RRL_STOCK_RESERVE_CORE spec+body | `relink_topup`: только HARD `TRADE_TOPUP` этого предложения → PICK_WAVE/план/строка/задание; RID, количество, баланс и единицы не меняются; ACCESSIBLE BY не расширялся |
| RRL_PICKING_API.create_plan | строка видит только свой неперенесённый HOLD: `ELIGIBILITY.reason(..., owner_reservation=hold)`, кандидаты сужены до источников удержания, доступное = `hold_free` (минус свои открытые SOFT); заблокированная строка → `TRADE_TOPUP_ADOPTION_CONDITIONS_NOT_MET`; остальные строки без изменений |
| RRL_STOCK_WAVE_LAUNCH_CMD | compile: `compile_wave` объявляет row_key предложения — запуск сериализуется с confirm/release; новые RID и stock_closure уже объявлены штатно. execute для удержанной строки: `assert_source(owner_reservation=hold)` + `adopt_hold` |
| RRL_TRADE_PICK_CONTEXT | `HOLD_ADOPTION_REQUIRED` заменён гейтом ADOPT: чужим и невалидным строкам отказ, своей строке — только источники её удержания (ACTIVE/ADOPTED) |

**`adopt_hold`:**
- Полный перенос: тот же RID → `relink_topup`.
- Частичный: `move_coverage` на том же UID и ячейке делит HARD в заранее объявленный RID; точные ключи переносятся через `release_units` + `reserve_units` в той же транзакции.
- Затем `mark_adopted`: HOLD ACTIVE → ADOPTED или уменьшение ACTIVE + новая строка ADOPTED, плюс запись RRL_TRADE_TOPUP_ADOPTION.
- Никакого release_hard/create_hard и DML резервов из integrations.

Существующий release предложения при ADOPTED отказывает (`TRADE_TOPUP_ADOPTED_RETURN_REQUIRED`).

- **Гонка запуска и отмены** сериализуется row_key предложения:
  - отмена прошла раньше → предложение не SAP_ACCEPTED → запуск отказывает;
  - запуск прошёл раньше → отмена видит ADOPTED.
- **Повтор после потерянного ответа** возвращает сохранённый результат StockPosting, количество второй раз не меняется.

**Python** (`integrations/infrastructure/trade_topup.py`):
- `_in_trip_boxes` + `_confirmed` — подтверждённая добивка занимает место только сверх части её SAP-заказа, уже включённой в TRIP; пересечение считается по количеству и единицам строки, а не флагом;
- подтверждённое по потребности уменьшается только на ту часть, которой ещё нет в TRIP — включённая уже вошла в `need.current_trip_quantity` (иначе сработала бы проверка `TOPUP_PRIMARY_SNAPSHOT_MISMATCH`).

**Миграция — обвязка:**
- preflight: цель, 5 SHA, отсутствие новых объектов, INVALID 0;
- verify;
- rollback: отказ при истории переноса, восстановление before-исходников, удаление новых объектов;
- rollback_verify;
- manifest.
- Before-SHA пяти объектов **совпали с живой базой** 22.10 (read-only сверка), INVALID 0.

Описание: `wiki/database/tradecase_topup_wave_adoption_20261022.md`.

## Проверки (только офлайн; живого apply нет)

- `tests/tradecase/test_trade_topup_adoption.py` — 7 PASS:
  - заказ внутри TRIP не занимает лишнего места;
  - без заказа или вне TRIP — полное место;
  - частичное включение — только остаток;
  - SHA манифеста совпадают с before- и patched-файлами;
  - патчи минимальны, штатный путь сохранён;
  - условия обоих SAP-документов и отменённого предложения, порядок проверок;
  - порядок apply/rollback.
- Вместе с тестами C-0143/C-0145 — 29 PASS.
- `retailcase_quality_gate.py` PASS, `check-encoding.ps1` PASS.
- **PL/SQL не компилировался**: без apply нельзя. Код вычитан вручную; ошибки компиляции и нарушения инвариантов ядра (RRL_STOCK_INVARIANT_CORE после команды) выявит живой apply Codex.

## Живые сценарии для приёмки Codex (не проверены)

- целевой полный перенос: RID, HARD и физический остаток не изменились, единицы те же, задание собирается;
- чужой заказ: удержанные единицы не видит;
- нет обновлённого TRIP → `TRADE_TOPUP_ADOPTION_CONDITIONS_NOT_MET`;
- отмена до и после запуска, гонка запуска и отмены;
- частичный перенос с делением RID и точными ключами;
- точный повтор запуска;
- отзыв прав (WAVE_EXEC_ACCESS / owner);
- общий HARD до и после.

## Ограничения

1. Добивка товара из общего пула (SHIP_FROM_STOCK) отклоняется явно (`TRADE_TOPUP_COMMON_POOL_UNSUPPORTED`), без двойного обещания пулу.
2. После начала погрузки добивка заблокирована; сценарии 80 → 60+20 и 66 → 64 не входят.
3. Если пришёл новый TRIP, неподтверждённые предложения этого рейса требуют пересчёта через CAPACITY_BASIS. Подтверждённое и принятое SAP предложение переносится без проверки старого базиса.
4. Задание строки добивки всегда CASE_PICK: при удержании условие FULL_PALLET планировщика не выполняется. Целую паллету это не ломает, но тип задания не FULL_PALLET.

RELEASE: файлы C-0146 освобождены.
