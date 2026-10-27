# Версия получателя в торговом контексте отбора и рейса (C-0173)

Состояние: APPLIED. Авторский checkpoint18c47fbc, review/checkpoint root4961404c. Применение/откат/повторное применение прошли7/8/7, ошибок0; контроль исходников и неизменных спецификаций прошёл, INVALID0. Отчёты recipient-version-{apply,rollback,reapply}.json сохранены в runtime/test-evidence/tradecase/2026-10-27/T08/program-orders/.

Настоящая функция на C103вернула4для привязок1и4, nullдля99. После перезапуска8088 непринятое задание4109выполнено новой операцией после проверкиPLANNED/отсутствия прежней операции; старый запрос сохранён. Точный повтор новой операции дал тот же ответ и однуAPPLIED; товар11000/H6600/1100не изменился. recipient-version-physical-proof.json фиксирует результат; собственных записей slowSQL по этому вызову нет. Сохраняем индексный доступ к принятой истории без нового индекса/кэша.

- Комплект `db/migrations/2026-10-27_trade_recipient_version/`, MIGRATION_ID `2026-10-27-trade-recipient-version`.
- SHA:
  - тело RRL_TRADE_PICK_CONTEXT: до F7733DEB…405C, после 0938CD82…9DAD;
  - тело RRL_TRADE_TRANSPORT_CORE: до E5645184…DEA9, после 40D1EFA0…2F34;
  - новая функция RRL_TRADE_RECIPIENT_VERSION: 9974A571…0200;
  - неизменные зависимости — спецификации RRL_TRADE_PICK_CONTEXT, RRL_TRADE_TRANSPORT_CORE, RRL_TRADE_TOPUP_ADOPT, RRL_TRADE_STOCK_GUARD.
- Правило: строка заказа, привязанная к версии получателя N, может работать с более поздней версией только при совпадении принятых payload после исключения ровно topup_enabled и topup_horizon_days. Одинаковые повторные записи — один снимок; иначе, при отсутствии или неоднозначности истории — stale.
- Доказательства (свой набор без стока, 210069361/C103 только чтение):
  - `tests/tradecase/live_trade_recipient_version.py` → `runtime/test-evidence/tradecase/2026-10-27/C0173/recipient-version.json`;
  - выжимка `tests/fixtures/tradecase_recipient_version_20261027.json`;
  - проверка синтаксиса `reports/tradecase/2026-10-27/claude/C0173/parse-check.json`.
