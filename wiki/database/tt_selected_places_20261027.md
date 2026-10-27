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
