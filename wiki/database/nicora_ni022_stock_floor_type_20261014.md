# NI02.2: явный тип целой STOCK-паллеты
14.10.2026 /1207. Сервер установлен и подтверждён адресным dev-кейсом1206; UI подключён, браузерное сохранение ещё не проверено.

В текущем RRL_PALLETS нет нормативного PALLET_TYPE_ID для STOCK-носителя; существующие CASE.PALLET_TYPE_ID и HU tare booking не относятся к самостоятельной целой STOCK-паллете. HU_TYPE обозначает общий kind, а не EURO/AMERICAN норматив; тип по площади/SKU/названию не выводится.

Планируется одна additive metadata-таблица RRL_PALLET_FLOOR_TYPE: PK UID→существующая паллета, FKтип→существующий справочник, текущая версия, последний operation_id→Root и склад декларации. История остаётся в прежнем неизменяемом Root journal; отдельный журнал движений/дублирующий stock writer не создаётся.

Новая Root-команда PALLET_FLOOR_TYPE_CONFIRM, quantity effect0: current stock_posting_shipping/RUSERS/WARE, scan UID/SSCC и текущей ячейки, expected type version, действующий тип и основание. ROW20 stock/physical rows +metadata key в штатном порядке, CFG shared; независимые паллеты выполняются параллельно. Изменение типа не создаёт товар, резерв, tare asset/book или юридическую агрегацию. Повтор/конфликт/обязательный outbox — прежний Root.

LOAD STOCK читает подтверждённую metadata-версию, фиксирует ROOT_STOCK_TYPE proof, повторяет её проверку до qty effect. Metadata guard допускает insert/update только этой семьи под Root context/fence, delete запрещён. Нет новой колонки в RRL_PALLETS и массовой инвалидизации rowtype зависимостей. Captured live sources и checkpoint1201; apply/paired forward recovery/live проверка будут зафиксированы после реализации.

1202: private Root command and public scoped READ package prepared; one metadata table+existing Root journal, TYPEversion+scanCell/uid+explicit type/evidence, zero lines/units and unchanged stock/reserve, normal shared CFG/ROW20 fences. Root scope before cache, and current snapshot checked before write. StockPALLET schema untouched. LOAD type proof reads same metadata under same row lock. Native migration/application next; API/UI next.

1203: first CREATE rejected before any object change because legacy RRL_WARES.ID has no PK/UK. New table did not exist. Retained FK to pallet/type/Root; warehouse is checked by native scope count/current actor and stored as declared history, no new global WARES constraint/index. This is explicit legacy schema limitation, not an assumed FK.

1207: Root TYPE current1206v1/EU, trip33638 LOADED proof ROOT_STOCK_TYPE; exact cached type after load. USER_ERRORS empty. Current maintained source bundle rebuilt only. Report38/UI screenshot55; owner recipient-default/assembly-override rule: [[concepts/nicora_execution_delivery_rules]].
