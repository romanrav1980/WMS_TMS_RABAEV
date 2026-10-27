# Выборочное снятие мест сборки с рейса (C-0176) — NOT_APPLIED

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

Root review rev1 добавляет явную перекомпиляцию двух зависимых тел при применении и откате. Исходник функции и нового пакета не изменён; frozen manifest обновлён с отметкой root-review-1. Reader теперь возвращает ST_WAREHOUSE_REQUIRED/409 для места без склада вместо TypeError/500. Native ещё не применён.

Root manifest: coordination/tradecase-20261019/reviews/C0176-root-manifest.json, SHA c9156b03fe39a012d63505f936875dcd3f0f3ec28601b96a1a3fd64fe1cc5932. После checkpoint выполнить apply/пустой rollback/reapply, только затем разрешить живые команды. UI rev1 с существующими helper, мобильным входом и справкой остаётся у Claude; его STUB не принят за живое действие.
