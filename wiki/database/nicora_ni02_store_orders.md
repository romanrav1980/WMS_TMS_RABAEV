# NI02 — исходные заказы SAP в RABAEV

## SAP → существующая СТ, изменение 009

Подключён операторский маршрут подготовки: existing ORDERS.CREATE_ORDER/ADD_ORDER_ROW → RRL_SBORKA_PALLETS_ADD2/ROWS_ADD4 → existing RRL_CUSTOMER_ORDER_FULFILLMENT → прежнее назначение TMS. Общее количество укладки равно source demand; округление ORDERS не должно изменять его. Истинные legacy логопараметры обязательны. Факт stock не создаётся. Паллета имеет внутренний OP_SAP_* identifier, не выдуманный SSCC.

Миграция **2026-10-07-009-ni02-legacy-st-adapter**: PREPARATION_HASH/JSON/PREPARED_AT в существующей source metadata; в существующем fulfillment enum добавлен PLANNED, FACT_QTY/WEIGHT=0 до факта сборки. CO.LEGACY_ORDER_ID — действующая ссылка. Другой order–trip реестр не создаётся. SQL/rollback/verify: db/migrations/2026-10-07_ni02_legacy_st. Накопленные подготовки блокируют rollback.

009 применена: 3 statements, 0 errors. В live metadata подтверждены три поля и ENABLED RRL_CUST_ORDER_FULF_CHK1 с PLANNED. Бизнес-DML/примерный SAP-заказ не запускались; rollback не выполнялся. Существующее назначение оставлено на RRL_SBORKA_PALLETS.TRANSTASK_ID.

Live PALL_SPLITTER.split_ufa/split_vegetables — return 0 в compatibility script 2026-05-11; не выдаются за автоматическое деление. Восстановление полноценной версии отдельно от адаптера. Перевод PLANNED fulfillment в фактический picking/shipping — часть стыка складских заданий; legacy sync не обновляет уже существующую плановую строку и должен быть адресно дополнен при этом переходе.

7 октября 2026 года. Добавочное изменение 008 в существующей ORCL/orcl, RABAEV. [SQL/rollback/verify](../../db/migrations/2026-10-07_ni02_store_orders/), migration ID **2026-10-07-008-ni02-store-orders**. Перед установкой сохраняется source checkpoint в runtime/ni02; статус установки фиксируется в runbook/log.

Владелец данных — fulfillment. Одна транзакция StoreOrders.receive сохраняет существующие RRL_CUSTOMER_ORDER/ROW, immutable исходную потребность/сроки и raw/message/result. Остатки, резервы, волны, рейсы и марки этим импортом не изменяются. Используются существующие RRL_CUSTOMER_ORDER_SQ/ROW_SQ и RRL_CUSTOMER_STORE_MAP; магазины/товары не создаются из неполного сообщения заказа.

| Объект | Контракт |
|---|---|
| RRL_SAP_STORE_CALENDAR | PK ware+existing store map; UTC offset, дни доставки 1–7, разрешение день-в-день из книги источников |
| RRL_SAP_STORE_ORDER | PK/FK existing customer order; unique sender+order; content hash, raw/demand/result JSON, admission, операционный день/плановые времена/offset |
| RRL_SAP_STORE_MESSAGE | PK sender+message; raw hash/XML, immutable результат/actor; FK source order |
| RRL_SAP_STORE_ROW_GUARD | запрещает менять/удалять исходные SAP строки, добавлять строки после регистрации источника; обычные legacy заказы вне этой связи сохранены |
| RRL_SAP_STORE_HEAD_GUARD | запрещает менять идентичность/исходные даты/склад/адрес SAP заказа; lifecycle status и транспортные назначения отдельно |
| RRL_SAP_STORE_PICK_GUARD | запрещает создание picking plan для PENDING_LATE/REJECTED через любые существующие пути |

Normal admission ACCEPTED, late PENDING_LATE; legacy STATUS соответственно IMPORTED/DRAFT. Не изменяется legacy enum. Для позднего заказа ещё требуется отдельная команда логиста/рейс, следующие изменения NI02. Исходный план quantity сохраняется при дефиците. Код не заявляет справедливое распределение запасов или складское задание — это другие команды.

PK/unique ограничивают duplicate concurrency, общий source-map lock сериализует только импорт. Список ≤200, XML ≤4MiB, строки ≤1000. Slow SQL измерений нет; после разрешённых кейсов измерить conversion N+1 для 1000 строк (owner backend/Oracle, NI02): при дорогом SQL выполнить пакетное чтение metadata вместо расширения timeout. Rollback отказывается удалять непустые факты/календарь; откат не выполняется автоматически.
