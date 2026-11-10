# Выборочное снятие мест сборки с рейса (C-0176) — APPLIED

- Комплект `db/migrations/2026-10-27_tt_selected_places/` (README там же), MIGRATION_ID `2026-10-27-tt-selected-places`.
- SHA:
  - writer RRL_TT_ADD_PALL: до 4157F23B…A25A, после 7F464DEA…C37F;
  - новый RRL_TT_PLACE_REMOVAL_API: спецификация 182FED73…0CBF, тело 8508DF83…DA8E;
  - журнал RRL_TT_PLACE_REMOVAL_CMD;
  - неизменные зависимости: RRL_TT_MEMBERSHIP_CTX_API (спецификация и тело), тела RRL_TRANSPORT_PLAN_API и RRL_ST_DEFER_API, спецификация RRL_TRADE_STOCK_GUARD, триггер RRL_TT_MEMBERSHIP_WRITER_GUARD.
- API:
  - `GET /api/transport/trips/{trip}/sts/{st}/places` — места, флаги и `source_hash`;
  - `POST /api/transport/trips/{trip}/place-removals` с `{operation_id, st_number, member_ids[≤200], expected_source_hash, reason}`;
  - 403 и OPERATION_CONFLICT для команды — `outcome_confirmed=false`.
- UI: компонент `features/transport/TransportStPlaceRemoval.tsx` в панели «Паллеты СТ» диспетчера (обе вкладки).
- Товар, резерв, адреса, коды, получатель и заказ операция не меняет.


## Независимое ревью перед применением

Root review rev1 добавляет явную перекомпиляцию двух зависимых тел при применении и откате. Исходник функции и нового пакета не изменён; frozen manifest обновлён с отметкой root-review-1. Reader теперь возвращает ST_WAREHOUSE_REQUIRED/409 для места без склада вместо TypeError/500. At the time of this review native was not yet applied; see the live status below.

Root manifest: coordination/tradecase-20261019/reviews/C0176-root-manifest.json, SHA c9156b03fe39a012d63505f936875dcd3f0f3ec28601b96a1a3fd64fe1cc5932. После checkpoint выполнить apply/пустой rollback/reapply, только затем разрешить живые команды. UI rev1 с общими helper, мобильным отображением и справкой сдан; прежний STUB не считается живой приёмкой.

## Фактическое применение и повторная live-проверка — 27.10.2026

Предыдущий раздел «Независимое ревью перед применением» описывает состояние до установки. Текущий live ledger в RABAEV@orcl показывает MIGRATION_ID `2026-10-27-tt-selected-places` = APPLIED, 27.10.2026 04:04:26. Проверка выполнена read-only: соединение `RABAEV@orcl`; изменённые исходники имеют точные after SHA из манифеста; `RRL_TT_ADD_PALL`, `RRL_TT_PLACE_REMOVAL_API`, `RRL_TRANSPORT_PLAN_API`, `RRL_ST_DEFER_API` VALID; INVALID=0, USER_ERRORS=0. Оба endpoint присутствуют в работающем OpenAPI 8088.

Повторный прогон `python tests/tradecase/live_place_removal.py --after-kit` завершился PASS на собственном складе 241232574: 4 места одной сборки, сняты 2; точный повтор вернул ту же квитанцию; изменённое тело и устаревший снимок получили 409; две конкурирующие команды дали 200/409; конкурентный повтор — 2×200 и одна квитанция; актор без права получил 403. `tests/tradecase/test_place_removal.py`: 7 passed. Ранее Claude проверил экран 1440/390 и потерю ответа после commit: 7/7 (`RESULT_C0176.md`).

После очистки собственного QA-набора паллетных строк не осталось, доступ склада выключен, тестовый рейс удалён, товарный остаток не менялся. Неактивная строка тестового склада и 3 записи журнала снятия сохранены; записи журнала являются аудитом и запрещены к ручному удалению. Rollback теперь штатно откажет при непустом журнале.

Проверка `RRL_SQL_SLOW_LOG` за последние 20 минут не нашла записей с этими endpoint. Это отсутствие атрибутированных записей, а не доказательство отсутствия медленного SQL. Evidence: `runtime/test-evidence/tradecase/2026-10-27/C0176/PR27afc0154d5e.json`.
