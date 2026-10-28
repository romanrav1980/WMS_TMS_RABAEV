# 2026-10-27 trade recipient version (C-0173) — APPLIED

Блокер: заказ привязан к получателю версии N (`RRL_TRADE_ORDER_LINK.RECIPIENT_VERSION`), а `RRL_TRADE_DOCUMENT` хранит только текущую версию. После любого нового сообщения получателя, в том числе только про настройку добивки, `RRL_TRADE_PICK_CONTEXT.enter_line` не находит документ версии N, и строка заказа становится `TRADE_ORDER_BINDING_STALE`. Так остановлен отбор O103 на 210069361. То же соединение есть в `RRL_TRADE_TRANSPORT_CORE.current_plan` (`TRADE_TRANSPORT_DEMAND_BINDING_STALE` перед LOAD/DEPART).

Изменение:
- Новая функция `RRL_TRADE_RECIPIENT_VERSION(p_ware,p_recipient,p_bound)`:
  - быстрый путь: текущая принятая версия равна привязанной;
  - иначе принятый payload привязанной версии из `RRL_TRADE_MESSAGE` (одинаковые повторные записи одного снимка — один снимок; записи с разным содержимым или с пустым payload — неоднозначность) сравнивается с текущим BODY_JSON через `JSON_EQUAL` после `JSON_MERGEPATCH(...,'{"topup_enabled":null,"topup_horizon_days":null}')`;
  - совпало — текущая версия, иначе null, то есть прежний stale.
- Тело `RRL_TRADE_PICK_CONTEXT`: оба чтения получателя (enter_line и check_source) по версии функции, которая хранится в контексте строки; `compatible` её сохраняет и восстанавливает.
- Тело `RRL_TRADE_TRANSPORT_CORE`: в current_plan соединение получателя по той же функции.
- LINK, прежние версии, проверки SKU, заказа, площадки и topup-confirm не меняются.

Порядок:
- `apply.sql`: preflight (цель, before SHA двух тел, 4 зависимости, включая спецификацию RRL_TRADE_TRANSPORT_CORE, функции нет, INVALID=0) → функция → два тела → verify → журнал.
- `rollback.sql`: только над точными after SHA (иначе `AFTER_SOURCE_DRIFT_REFUSED`) → оба тела «до» → удаление функции → rollback_verify. Откат возвращает строгую проверку точной версии; товар, резервы и проводки комплект не меняет.

Миграция применена в RABAEV/orcl. Повторная проверка 29.10 вызвала установленную RRL_TRADE_RECIPIENT_VERSION для изолированных версий получателя: изменение только topup_enabled или topup_horizon_days сохраняет доступ к строке заказа; изменение торгового условия возвращает обычный отказ устаревшей привязки. Внешний обмен не использовался.
