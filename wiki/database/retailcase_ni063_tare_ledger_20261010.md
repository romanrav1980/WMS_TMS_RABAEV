# NI06.3 — количественный баланс тары, 098
Миграция 2026-10-10-098-tare-quantity-ledger APPLIED в RABAEV. Новые таблицы BALANCE/OFFER/ACCEPT/JOURNAL под RRL_STOCK_POSTING_API; RRL_PALLET_TYPE/рейсы/машины/привязки магазинов и водителей переиспользованы. RRL_WARES.ID в legacy не имеет PK: новая FK на него не создаётся, точная единственность проверяется командой. Товарный P/H и вложенность HU не меняются.

## Действия
TARE_COUNT: только складской пересчёт, tare_adjust + текущая привязка к складу, observed целое0+, expected_version, причина/решение. История дельты сохраняется; прямой DML запрещён.
TARE_OFFER: отправитель, существующий рейс/машина/магазин, текущий источник/тип/состояние, скан машины. Баланс не меняется и количество не резервируется.
TARE_ACCEPT: другой действующий участник получателя, точное предложение, скан машины и фактическое количество≤предложение. Под теми же согласованными блокировками source минус/destination плюс + immutable accept/journal + обязательный общий outbox в одном commit. Непринятая часть остаётся у отправителя. Плановый возврат не доступен на складе.
Права tare_view/tare_adjust/tare_offer/tare_accept. Водитель — dedicated current binding; GLOBAL_ADMIN не заменяет подпись водителя. Магазин — existing receiver address binding. Store movements require departed original trip/store membership. Пересчёт не используется для исчезновения магазинного долга.

## Интерфейсы
API /api/inventory/tare/count|offer|accept, bounded balances200/offers100/context. Raw [АРМ](../../wiki-raw/wms_admin_ui_reference/tare-ledger.html): пересчёт/выдача/приёмка склада. React [inventory feature](../../admin/wms_admin_frontend/src/features/inventory/index.ts) подключён к прежней DriverMobilePage, выбор справочников/участников/фактических количеств. Подписи разных пользователей; пароль не сохраняется, исходная операция сохраняется до окончательного результата.

## Фактическое dev-подтверждение
Тип3 TROLLEY, owner9104: выдано6, магазин принял6, магазин вернул4, склад принял4. Итог warehouse4/store2/vehicle0, журнал5, товарных RRL_EVENTS0, Root replay/неизменяемость/подмена водительской подписи отказаны. Собственные store/driver users после кейса отключены.
Отдельная конкуренция: два предложения4+4 на остаток4, параллельные authenticated accepts — один200/4, один409; loser outbox0, остаток неотрицателен/общая тара6. Возврат победивших4 обратно складу восстановилwarehouse4/store2. Предложение проигравшего остаётся в истории без принятого количества.
Одноразовый [сценарий](../../scripts/ni063_tare_case.py); [конкуренция](../../scripts/ni063_tare_race.py). Повторный запуск исходного6 не разрешён: факты уже существуют.

## SQL/структура
V$SQL: ACCEPT insert2.893мс, balance MERGE2.499, journal1.854, sourceUPDATE1.497, primarykeybalance read0.121. Решение сохранить PK/holderindex/bounded queues; это dev-измерение, не заявленная промышленная мощность.
TypeScript --noEmit PASS. Общий architecture gate FAIL на прежних нарушениях supply_order/stock_command_routes/alternative_pick_faces/untyped helpers; новый feature помещён в зарегистрированный owner inventory, baseline не повышался. Независимое ревью и browser evidence остаются открыты.

## Следующее
Полный NI06.3 in_progress: сроки магазина/клиента, привязка долга к выдаче, повреждения/списание/претензии, пригодная тара в планировании и фактическая вместимость обратного участка. Предложения не являются резервом, финансовое решение/внешний ACK не возникают автоматически.
