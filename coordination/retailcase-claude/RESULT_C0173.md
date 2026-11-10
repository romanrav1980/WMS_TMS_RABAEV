# C-0173 — блокер версии получателя (приоритет) и состояние 640/20

## 1. Блокер версии получателя — исправление подготовлено (NOT_APPLIED)
- Факт:
  - `RRL_TRADE_DOCUMENT` хранит одну текущую версию (PK WARE_ID, ENTITY_TYPE, EXTERNAL_ID);
  - O103 привязан к C103 v1, а документ сейчас v4 (только topup_enabled менялся в v2/v3/v4);
  - `RRL_TRADE_PICK_CONTEXT.enter_line` соединяет точную версию → `TRADE_ORDER_BINDING_STALE`; то же в `RRL_TRADE_TRANSPORT_CORE.current_plan`, стр. 67 (до LOAD/DEPART).
- Комплект `db/migrations/2026-10-27_trade_recipient_version/` (README там же):
  - новая функция `RRL_TRADE_RECIPIENT_VERSION`;
  - два тела используют её вместо точного соединения;
  - быстрый путь равной версии без чтения истории;
  - исключены ровно topup_enabled и topup_horizon_days;
  - одинаковые повторные записи — один снимок, разное содержимое, запись с пустым payload или нет истории — stale.
  - LINK и прежние версии не трогаются, topup-confirm остаётся строгим.
- Live SHA:
  - до: RRL_TRADE_PICK_CONTEXT F7733DEB…405C, RRL_TRADE_TRANSPORT_CORE E5645184…DEA9;
  - после: 0938CD82…9DAD / 40D1EFA0…2F34, функция 9974A571…0200 (полные — в manifest.json).
- Проверки:
  - `tests/tradecase/live_trade_recipient_version.py`: свой новый склад без стока; документы и привязка через API; READ ONLY сравнение точной копии live-предиката enter_line и кандидата (функция исполнена как локальная копия в READ ONLY транзакции):

    | версия получателя | live | кандидат |
    |---|---|---|
    | v1 (привязка) | VALID | VALID |
    | v2 только topup_enabled | STALE | VALID |
    | v3 только настройки добивки | STALE | VALID |
    | v4 min_osg_days 50→60 | STALE | STALE |
    | v5 собственники +BLC | STALE | STALE |
    | v6 выкуп IN_TRANSIT | STALE | STALE |
    | v7 active=false | STALE | STALE |
    | v8 как v1, кроме добивки | STALE | VALID |

  - повтор v1 под новым event_id дал 2 принятые записи одного снимка — совместимость сохраняется; отсутствующая история (версия 99) — null;
  - 210069361/C103, только чтение: live STALE, кандидат возвращает v4;
  - `parse-check.json`: тело PICK_CONTEXT скомпилировано анонимным блоком с функцией как локальной подпрограммой; в TRANSPORT_CORE только ожидаемый PLS-00231 (локальная функция в SQL), синтаксических ошибок нет;
  - `tests/tradecase/test_trade_recipient_version.py` 3/3 на обезличенной выжимке `tests/fixtures/tradecase_recipient_version_20261027.json` и файлах комплекта.
- Ограничения:
  - живого положительного отбора до apply нет: после apply root продолжает свой набор (отбор O103) и проверяет LOAD/DEPART;
  - стоимость: один индексный доступ к RRL_TRADE_MESSAGE только при несовпадении версии, по числу строк рейса в current_plan (≤200);
  - мои пустые склады без стока: 213677092 и 226374487 (прерванные запуски), 213212993, 211009664 и 223491197 (полные прогоны, последний — на финальной функции); актор setup выведен в каждом.

## 2. 640/20 — не выполнено в этом запросе (по приоритету Codex)
- Исследование: штатный остаток тому же получателю — путь T07 (bulk_remainder: непогруженное место ждёт следующий рейс). Новый контракт для 40/20 не нужен.
- Гипотеза двойного учёта: после adoption предложение SAP_ACCEPTED, удержания ADOPTED. `_confirmed` считает extra = approved − в рейсе по TRIP, поэтому при O104 40 из 60 остаются 20 фиктивных коробов. Не подтверждена фактом, дефектом не объявляю.
- Подготовлен, но не запускался: `tests/tradecase/live_topup_trip_reduction.py` (малый набор 6+3→8; фазы receive/main_orders/topup/pick). Фазы уменьшения рейса и погрузки ещё не написаны.

## Текст для wiki (обновляет Codex)
«27.10 C-0173: строка заказа, привязанная к версии получателя N, после изменения только настройки добивки больше не будет stale (комплект NOT_APPLIED 2026-10-27_trade_recipient_version: функция RRL_TRADE_RECIPIENT_VERSION, тела RRL_TRADE_PICK_CONTEXT и RRL_TRADE_TRANSPORT_CORE). Любое коммерческое изменение, inactive, отсутствие или неоднозначность истории — stale как раньше. Проверено на своём наборе READ ONLY; применение и продолжение отбора O103 — root.»

- Локальный коммит 18c47fbc (без push). Комплект frozen: manifest.json фиксирует SHA всех файлов.
