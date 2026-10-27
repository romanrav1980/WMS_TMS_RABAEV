# Единицы строки торгового заказа (C-0175) — первый этап

- Правило владельца — `wiki/requirements/nicora_order_units_20261027.md`.
- Первый этап: обработанная единица EA/BOX для TRADECASE ORDER. Весовой SKU с базой KG end-to-end и загрузка NI02 (StoreOrders) не закрыты.
- Контракт:
  - `TradeSku` + `processing_uom` (EA|BOX), `processing_step` (явный шаг в этой единице, не точность реестра), `round_to_processing_unit`;
  - `TradeOrderLine.uom` = EA, BOX, BLOCK, BLK, G, KG (BLOCK и BLK явно сопоставлены коду реестра BLK; исходный код сохраняется).
- Нормализация один раз при приёме документа: `domain/order_units.py` + `infrastructure/order_unit_registry.py` (RRL_STOCK_UOM_CONVERSION, последняя версия, неоднозначность — нет коэффициента), точная рациональная арифметика, всегда вниз до шага.
  - В строке: `quantity`/`uom` = обработанные; `normalization` — исходные количество и единица, база, обработанная база, разница, версии коэффициентов, версия SKU, шаг, флаг, статус и код ошибки.
  - Флаг выключен и единица отличается — строка загружена с `ORDER_UNIT_ROUNDING_NOT_ALLOWED` (даже при точном переводе 24 EA → 2 BOX).
  - Ответ ACCEPTED + `line_results` и `loaded_with_integration_error`.
  - Точный повтор отдаёт сохранённый запрос без повторной нормализации.
- Native NOT_APPLIED `db/migrations/2026-10-27_trade_order_units/`: нулевые и безкоэффициентные строки хранятся неисполнимыми, TRIP их не назначает, привязка пропускает.
- Доказательства: `tests/tradecase/live_order_units.py` (ASGI-приложение текущего кода + настоящий Oracle, свой склад), `runtime/test-evidence/tradecase/2026-10-27/C0175/order-units.json`, `tests/tradecase/test_order_units.py`.
